"""Main Error Log Analyzer Agent."""

import yaml
from typing import Optional
from pathlib import Path

from config import settings
from models import InputData, ParsedError, Report
from error_parser import ErrorParser
from mcp_client import GitHubMCPClient
from bedrock_client import BedrockClient
from report_generator import ReportGenerator


class ErrorLogAnalyzerAgent:
    """Main agent for analyzing error logs and identifying responsible code."""
    
    def __init__(self):
        """Initialize the agent with all required components."""
        self.error_parser = ErrorParser()
        self.mcp_client = GitHubMCPClient()
        self.bedrock_client = BedrockClient()
        self.report_generator = ReportGenerator()
    
    def run(self, input_file: str, output_file: str):
        """
        Run the complete analysis workflow.
        
        Args:
            input_file: Path to input file with error logs
            output_file: Path to output markdown file
        """
        print("🚀 Starting Error Log Analyzer Agent...")
        
        # Step 1: Read input file
        print(f"\n📖 Reading input from: {input_file}")
        input_data = self._read_input_file(input_file)
        if not input_data:
            print("❌ Failed to read input file")
            print("\nPlease ensure input.txt has the correct format:")
            print("""
repository: owner/repo-name

error_log: |
  [Paste your error log here]
            """)
            return False  # Return False to indicate failure
        
        print(f"   Repository: {input_data.repository}")
        
        # Step 2: Parse error log
        print("\n🔍 Parsing error log...")
        parsed_error = self.error_parser.parse(input_data.error_log)
        print(f"   Error Type: {parsed_error.error_type}")
        print(f"   Language: {parsed_error.language or 'Unknown'}")
        print(f"   Stack Frames: {len(parsed_error.stack_trace)}")
        
        if not parsed_error.stack_trace:
            print("⚠️  No stack trace found, using generic analysis")
        
        # Step 3: Fetch code from GitHub (using GitHub API directly)
        print("\n📥 Fetching code from GitHub...")
        code_content, file_path, line_number = self._fetch_relevant_code(
            input_data.repository,
            parsed_error
        )
        
        if not code_content:
            print("❌ Failed to fetch code from repository")
            self.mcp_client.close()
            return False  # Return False to indicate failure
        
        print(f"   Fetched: {file_path}:{line_number}")
        
        # Step 5: Analyze with Claude
        print("\n🤖 Analyzing with AWS Bedrock Claude...")
        analysis_result = self.bedrock_client.analyze_error(
            parsed_error,
            code_content,
            file_path,
            line_number
        )
        
        if not analysis_result:
            print("❌ Failed to analyze error with Claude")
            self.mcp_client.close()
            return False  # Return False to indicate failure
        
        print(f"   Confidence: {analysis_result.confidence:.0%}")
        
        # Step 6: Generate report
        print("\n📝 Generating report...")
        report = Report(
            repository=input_data.repository,
            error_type=parsed_error.error_type,
            error_message=parsed_error.error_message,
            analysis=analysis_result,
            raw_error_log=input_data.error_log
        )
        
        self.report_generator.save_to_file(report, output_file)
        
        # Cleanup
        self.mcp_client.close()

        print("\n✨ Analysis complete!")
        return True  # Return True to indicate success
    
    def _read_input_file(self, input_file: str) -> Optional[InputData]:
        """Read and parse input file."""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try YAML format first
            try:
                data = yaml.safe_load(content)
                return InputData(**data)
            except:
                # Try simple text format
                lines = content.strip().split('\n')
                if lines[0].startswith('repository:') or lines[0].startswith('Repository:'):
                    repo = lines[0].split(':', 1)[1].strip()
                    error_log = '\n'.join(lines[2:])  # Skip repository and blank line
                    return InputData(repository=repo, error_log=error_log)
                
                return None
        
        except Exception as e:
            print(f"Error reading input file: {e}")
            return None
    
    def _fetch_relevant_code(
        self, 
        repository: str, 
        parsed_error: ParsedError
    ) -> tuple[Optional[str], Optional[str], Optional[int]]:
        """
        Fetch relevant code from GitHub based on parsed error.
        
        Returns:
            Tuple of (code_content, file_path, line_number)
        """
        # Get the most relevant stack frame (usually the last one)
        if parsed_error.stack_trace:
            target_frame = parsed_error.stack_trace[-1]
            file_path = target_frame.file_path
            line_number = target_frame.line_number or 1
        else:
            # No stack trace, return None
            return None, None, None
        
        # Fetch file contents with context (±10 lines)
        line_start = max(1, line_number - 10)
        line_end = line_number + 10
        
        code_content = self.mcp_client.get_file_contents(
            repository=repository,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end
        )
        
        return code_content, file_path, line_number

