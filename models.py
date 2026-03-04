"""Data models for Error Log Analyzer Agent."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ErrorUnderstanding(BaseModel):
    """LLM's understanding of the error - used for intelligent routing."""
    error_type: str
    error_message: str
    has_file_location: bool = False
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    search_strategy: Optional[str] = None
    search_keywords: List[str] = Field(default_factory=list)
    language: Optional[str] = None
    severity: str = "medium"
    needs_code: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StackFrame(BaseModel):
    """Represents a single frame in a stack trace."""
    file_path: str
    line_number: Optional[int] = None
    function_name: Optional[str] = None
    code_snippet: Optional[str] = None


class ParsedError(BaseModel):
    """Parsed error information from error logs."""
    error_type: str
    error_message: str
    stack_trace: List[StackFrame] = Field(default_factory=list)
    raw_log: str
    language: Optional[str] = None


class InputData(BaseModel):
    """Input data from input.txt file."""
    repository: str
    error_log: str


class CodeContext(BaseModel):
    """Code context fetched from GitHub."""
    file_path: str
    line_number: int
    code_content: str
    surrounding_lines: Optional[str] = None


class AnalysisResult(BaseModel):
    """Analysis result from Claude."""
    file_path: str
    line_number: int
    function_name: Optional[str] = None
    root_cause: str
    code_snippet: str
    recommendation: str
    confidence: Optional[float] = None


class Report(BaseModel):
    """Final analysis report."""
    repository: str
    generated_at: datetime = Field(default_factory=datetime.now)
    error_type: str
    error_message: str
    analysis: AnalysisResult
    raw_error_log: str

