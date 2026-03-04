#!/usr/bin/env python3
"""Main entry point for Error Log Analyzer Agent."""

import sys
from pathlib import Path
from config import settings
from agent import ErrorLogAnalyzerAgent


def main():
    """Main function to run the agent."""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║               Log Analyzer Agent                          ║
║         GitHub MCP + AWS Bedrock Claude                   ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Get input and output file paths
    input_file = settings.input_file
    output_file = settings.output_file
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"❌ Error: Input file '{input_file}' not found!")
        print(f"\nPlease create '{input_file}' with the following format:")
        print("""
repository: owner/repo-name

error_log: |
  [Paste your error log here]
        """)
        sys.exit(1)
    
    # Create and run agent
    try:
        agent = ErrorLogAnalyzerAgent()
        success = agent.run(input_file, output_file)

        if success:
            print(f"\n{'='*60}")
            print(f"✅ Success! Check '{output_file}' for the analysis report.")
            print(f"{'='*60}\n")
        else:
            print(f"\n{'='*60}")
            print(f"❌ Analysis failed. Please check the errors above.")
            print(f"{'='*60}\n")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

