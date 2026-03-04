"""Error log parser to extract meaningful information from stack traces."""

import re
from typing import Optional
from models import ParsedError, StackFrame


class ErrorParser:
    """Parse error logs and extract structured information."""
    
    # Regex patterns for different error formats
    PYTHON_TRACEBACK_PATTERN = r'File "([^"]+)", line (\d+)(?:, in (\w+))?'
    PYTHON_ERROR_PATTERN = r'(\w+Error|Exception): (.+?)(?:\n|$)'
    
    JAVASCRIPT_ERROR_PATTERN = r'(\w+Error): (.+?)(?:\n|$)'
    JAVASCRIPT_STACK_PATTERN = r'at (?:(\w+) )?\(([^:]+):(\d+):(\d+)\)'
    
    JAVA_ERROR_PATTERN = r'([\w\.]+Exception): (.+?)(?:\n|$)'
    JAVA_STACK_PATTERN = r'at ([\w\.$]+)\(([^:]+):(\d+)\)'
    
    def parse(self, error_log: str) -> ParsedError:
        """
        Parse error log and return structured error information.
        
        Args:
            error_log: Raw error log string
            
        Returns:
            ParsedError object with extracted information
        """
        # Detect language and error type
        language = self._detect_language(error_log)
        
        if language == "python":
            return self._parse_python_error(error_log)
        elif language == "javascript":
            return self._parse_javascript_error(error_log)
        elif language == "java":
            return self._parse_java_error(error_log)
        else:
            return self._parse_generic_error(error_log)
    
    def _detect_language(self, error_log: str) -> Optional[str]:
        """Detect programming language from error format."""
        if "Traceback (most recent call last)" in error_log or "File \"" in error_log:
            return "python"
        elif "at " in error_log and ("Error:" in error_log or "Exception:" in error_log):
            if ".java:" in error_log:
                return "java"
            return "javascript"
        return None
    
    def _parse_python_error(self, error_log: str) -> ParsedError:
        """Parse Python traceback."""
        stack_frames = []
        
        # Extract stack frames
        for match in re.finditer(self.PYTHON_TRACEBACK_PATTERN, error_log):
            file_path = match.group(1)
            line_number = int(match.group(2))
            function_name = match.group(3) if match.group(3) else None
            
            stack_frames.append(StackFrame(
                file_path=file_path,
                line_number=line_number,
                function_name=function_name
            ))
        
        # Extract error type and message
        error_match = re.search(self.PYTHON_ERROR_PATTERN, error_log)
        if error_match:
            error_type = error_match.group(1)
            error_message = error_match.group(2).strip()
        else:
            error_type = "UnknownError"
            error_message = "Could not parse error message"
        
        return ParsedError(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_frames,
            raw_log=error_log,
            language="python"
        )
    
    def _parse_javascript_error(self, error_log: str) -> ParsedError:
        """Parse JavaScript/TypeScript error."""
        stack_frames = []
        
        # Extract stack frames
        for match in re.finditer(self.JAVASCRIPT_STACK_PATTERN, error_log):
            function_name = match.group(1)
            file_path = match.group(2)
            line_number = int(match.group(3))
            
            stack_frames.append(StackFrame(
                file_path=file_path,
                line_number=line_number,
                function_name=function_name
            ))
        
        # Extract error type and message
        error_match = re.search(self.JAVASCRIPT_ERROR_PATTERN, error_log)
        if error_match:
            error_type = error_match.group(1)
            error_message = error_match.group(2).strip()
        else:
            error_type = "UnknownError"
            error_message = "Could not parse error message"
        
        return ParsedError(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_frames,
            raw_log=error_log,
            language="javascript"
        )
    
    def _parse_java_error(self, error_log: str) -> ParsedError:
        """Parse Java stack trace."""
        stack_frames = []
        
        # Extract stack frames
        for match in re.finditer(self.JAVA_STACK_PATTERN, error_log):
            function_name = match.group(1)
            file_path = match.group(2)
            line_number = int(match.group(3))
            
            stack_frames.append(StackFrame(
                file_path=file_path,
                line_number=line_number,
                function_name=function_name
            ))
        
        # Extract error type and message
        error_match = re.search(self.JAVA_ERROR_PATTERN, error_log)
        if error_match:
            error_type = error_match.group(1)
            error_message = error_match.group(2).strip()
        else:
            error_type = "UnknownError"
            error_message = "Could not parse error message"
        
        return ParsedError(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_frames,
            raw_log=error_log,
            language="java"
        )
    
    def _parse_generic_error(self, error_log: str) -> ParsedError:
        """Parse generic error when language cannot be detected."""
        return ParsedError(
            error_type="GenericError",
            error_message=error_log.split('\n')[0] if '\n' in error_log else error_log,
            stack_trace=[],
            raw_log=error_log,
            language=None
        )

