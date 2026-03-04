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
        
        # Step 2: Let Claude understand the error (LLM-First Approach!)
        print("\n🤖 Claude is analyzing the error type and determining strategy...")
        error_understanding = self.bedrock_client.understand_error(input_data.error_log)

        print(f"   ✓ Error Type: {error_understanding.error_type}")
        print(f"   ✓ Severity: {error_understanding.severity}")
        print(f"   ✓ Language: {error_understanding.language or 'Unknown'}")
        print(f"   ✓ Has File Location: {error_understanding.has_file_location}")
        print(f"   ✓ Needs Code: {error_understanding.needs_code}")

        # Step 3: Fetch code based on Claude's understanding
        code_content = None
        file_path = "unknown"
        line_number = 0

        if error_understanding.has_file_location and error_understanding.file_path:
            # Traditional flow: We have exact file location
            print(f"\n📥 Fetching code from: {error_understanding.file_path}")
            file_path = error_understanding.file_path
            line_number = error_understanding.line_number or 0

            code_content = self.mcp_client.get_file_contents(
                repository=input_data.repository,
                file_path=file_path,
                line_start=max(1, line_number - 10),
                line_end=line_number + 10
            )

            if not code_content:
                print("❌ Failed to fetch code from repository")
                self.mcp_client.close()
                return False

            print(f"   ✓ Fetched: {file_path}:{line_number}")

        elif error_understanding.needs_code and error_understanding.search_strategy:
            # New flow: Search for code
            print(f"\n🔍 Searching for code: {error_understanding.search_strategy}")
            print(f"   Keywords: {', '.join(error_understanding.search_keywords)}")

            code_content = self.mcp_client.search_and_fetch(
                repository=input_data.repository,
                search_query=error_understanding.search_strategy,
                keywords=error_understanding.search_keywords
            )

            if code_content:
                print("   ✓ Found relevant code via search")
            else:
                print("   ⚠️  No code found via search, will analyze log only")
        else:
            # No code needed - analyze log only
            print("\n📝 No code fetch needed - analyzing log directly")

        # Parse error for compatibility (simplified now)
        parsed_error = self.error_parser.parse(input_data.error_log)
        
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

