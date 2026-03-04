"""AWS Bedrock Claude client for code analysis."""

import boto3
import json
import os
from typing import Optional
from botocore.config import Config
from config import settings
from models import ParsedError, AnalysisResult, ErrorUnderstanding


class BedrockClient:
    """Client for AWS Bedrock Claude Haiku using API Key (bearer token)."""

    def __init__(self):
        """Initialize Bedrock client."""
        # Use the provided ABSK API key as bearer token
        self.api_key = settings.bedrock_api_key
        self.region = settings.aws_region
        self.model_id = settings.bedrock_model_id
        self.max_tokens = settings.bedrock_max_tokens
        self.temperature = settings.bedrock_temperature

        # Set the bearer token as environment variable for boto3
        os.environ['AWS_BEARER_TOKEN_BEDROCK'] = self.api_key

        # Configure Bedrock client with timeouts
        bedrock_config = Config(
            read_timeout=120,
            connect_timeout=60,
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            }
        )

        # Initialize boto3 Bedrock client
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=self.region,
            config=bedrock_config
        )

    def understand_error(self, error_log: str) -> ErrorUnderstanding:
        """
        First LLM call: Let Claude understand the error and determine analysis strategy.

        This is the key to making the agent universal - Claude decides what to do!
        """
        prompt = f"""You are an expert at analyzing error logs. Examine this log and determine the best analysis strategy.

**Error Log:**
```
{error_log}
```

Analyze this error and respond in JSON format with these fields:

{{
    "error_type": "Type of error (e.g., AttributeError, HTTP422Error, DatabaseError, etc.)",
    "error_message": "Brief description of what went wrong",
    "has_file_location": true/false,  // Do we have a specific file path and line number?
    "file_path": "path/to/file.py or null",  // Extract from stack trace if available
    "line_number": 123 or null,  // Extract from stack trace if available
    "search_strategy": "What to search for in codebase if no file path",  // e.g., "Search for /v1/fault-ledger endpoint"
    "search_keywords": ["keyword1", "keyword2"],  // Important terms to search for
    "language": "Python/JavaScript/Java/etc or Unknown",
    "severity": "critical/high/medium/low",
    "needs_code": true/false,  // Do we need to fetch code from repository?
    "metadata": {{}}  // Any additional context (API endpoint, HTTP method, field names, etc.)
}}

**Examples:**

For a Python stack trace:
{{
    "error_type": "AttributeError",
    "error_message": "'NoneType' object has no attribute 'job_id'",
    "has_file_location": true,
    "file_path": "backend/src/server/apis_v1/webhooks.py",
    "line_number": 250,
    "search_strategy": null,
    "search_keywords": ["new_triage", "job_id"],
    "language": "Python",
    "severity": "high",
    "needs_code": true,
    "metadata": {{"function": "grafana_webhook"}}
}}

For an API error without stack trace:
{{
    "error_type": "HTTP422ValidationError",
    "error_message": "configured_duration must be a valid number",
    "has_file_location": false,
    "file_path": null,
    "line_number": null,
    "search_strategy": "Search for /v1/fault-ledger POST endpoint definition and configured_duration field validation",
    "search_keywords": ["fault-ledger", "configured_duration", "POST", "422"],
    "language": "API",
    "severity": "medium",
    "needs_code": true,
    "metadata": {{
        "endpoint": "/v1/fault-ledger",
        "method": "POST",
        "status_code": 422,
        "field": "configured_duration"
    }}
}}

For a generic application log:
{{
    "error_type": "ApplicationError",
    "error_message": "Service failed to start",
    "has_file_location": false,
    "file_path": null,
    "line_number": null,
    "search_strategy": "Search for service initialization and startup code",
    "search_keywords": ["startup", "initialize", "service"],
    "language": "Unknown",
    "severity": "high",
    "needs_code": false,
    "metadata": {{}}
}}

Be intelligent about extracting information. Look for:
- File paths in stack traces
- Line numbers
- API endpoints in URLs
- HTTP status codes
- Field names in validation errors
- Function/method names
- Error types and messages

Respond ONLY with valid JSON, no additional text."""

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,  # Smaller for JSON response
                "temperature": 0.1,  # Low temperature for structured output
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })

            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body
            )

            response_body = json.loads(response['body'].read())
            json_text = response_body['content'][0]['text']

            # Parse JSON response
            # Remove markdown code blocks if present
            json_text = json_text.strip()
            if json_text.startswith('```'):
                json_text = json_text.split('```')[1]
                if json_text.startswith('json'):
                    json_text = json_text[4:]
            json_text = json_text.strip()

            understanding_dict = json.loads(json_text)

            # Convert to ErrorUnderstanding model
            return ErrorUnderstanding(**understanding_dict)

        except Exception as e:
            print(f"Error in understand_error: {e}")
            import traceback
            traceback.print_exc()

            # Fallback: return basic understanding
            return ErrorUnderstanding(
                error_type="UnknownError",
                error_message="Failed to parse error",
                has_file_location=False,
                needs_code=False,
                severity="medium"
            )

        # Configure Bedrock client with timeouts
        bedrock_config = Config(
            read_timeout=120,
            connect_timeout=60,
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            }
        )

        # Initialize boto3 Bedrock client
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=self.region,
            config=bedrock_config
        )
    
    def analyze_error(
        self,
        parsed_error: ParsedError,
        code_content: str,
        file_path: str,
        line_number: int
    ) -> Optional[AnalysisResult]:
        """
        Analyze error with code context using Claude via Bedrock API Key.

        Args:
            parsed_error: Parsed error information
            code_content: Code content from the file
            file_path: Path to the file
            line_number: Line number where error occurred

        Returns:
            AnalysisResult with root cause and recommendations
        """
        prompt = self._build_analysis_prompt(
            parsed_error,
            code_content,
            file_path,
            line_number
        )

        try:
            # Prepare request body for Claude
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })

            # Invoke Bedrock model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body
            )

            # Parse response
            response_body = json.loads(response['body'].read())
            analysis_text = response_body['content'][0]['text']

            return self._parse_analysis_response(
                analysis_text,
                file_path,
                line_number,
                code_content
            )

        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_analysis_prompt(
        self,
        parsed_error: ParsedError,
        code_content: str,
        file_path: str,
        line_number: int
    ) -> str:
        """Build comprehensive prompt for Claude analysis."""
        prompt = f"""You are a senior software engineer and debugging expert. Provide a comprehensive analysis of this error.

**Error Information:**
- Type: {parsed_error.error_type}
- Message: {parsed_error.error_message}
- Language: {parsed_error.language or 'Unknown'}
- File: {file_path}
- Line: {line_number}

**Code Context (lines around error):**
```
{code_content}
```

**Full Stack Trace:**
```
{parsed_error.raw_log}
```

Please provide a COMPREHENSIVE analysis with the following sections:

## 1. CODE SNIPPET
Show the exact problematic code with 5-10 lines of context. Highlight the error line with a comment.

## 2. ROOT CAUSE ANALYSIS
Provide a detailed explanation (4-6 sentences) covering:
- WHAT is the immediate cause of the error?
- WHY did this happen? (trace back the logic)
- WHEN does this occur? (conditions/triggers)
- WHERE in the code flow does this originate?

## 3. IMPACT ASSESSMENT
Explain:
- What happens when this error occurs?
- Does it affect other parts of the system?
- Is data lost or corrupted?
- What is the severity?

## 4. DETAILED RECOMMENDATIONS
Provide 2-3 different solutions with:
- Solution name
- Code example
- Pros and cons
- When to use this approach

## 5. PREVENTION STRATEGIES
Suggest:
- Unit tests to add
- Code patterns to follow
- Monitoring/logging improvements
- Design improvements

## 6. DEBUGGING STEPS
List 3-5 steps to:
- Reproduce the error
- Verify the fix
- Test edge cases

## 7. RELATED CONCERNS
Mention:
- Similar patterns in the code that might have the same issue
- Dependencies or related files to check
- Potential race conditions or async issues

## 8. CONFIDENCE SCORE
Rate your confidence (0.0 to 1.0) and explain why.

Be thorough, technical, and actionable. Provide specific code examples and clear explanations."""

        return prompt
    
    def _parse_analysis_response(
        self,
        analysis_text: str,
        file_path: str,
        line_number: int,
        code_content: str
    ) -> AnalysisResult:
        """Parse Claude's comprehensive response into AnalysisResult."""

        # Extract all sections from comprehensive analysis
        code_snippet = self._extract_section(analysis_text, "CODE SNIPPET", "ROOT CAUSE")
        root_cause = self._extract_section(analysis_text, "ROOT CAUSE", "IMPACT")
        impact = self._extract_section(analysis_text, "IMPACT", "DETAILED RECOMMENDATIONS")
        recommendations = self._extract_section(analysis_text, "DETAILED RECOMMENDATIONS", "PREVENTION")
        prevention = self._extract_section(analysis_text, "PREVENTION", "DEBUGGING")
        debugging = self._extract_section(analysis_text, "DEBUGGING", "RELATED")
        related = self._extract_section(analysis_text, "RELATED", "CONFIDENCE")
        confidence_str = self._extract_section(analysis_text, "CONFIDENCE", None)

        # Parse confidence score
        confidence = 0.8  # Default
        try:
            import re
            conf_match = re.search(r'(\d+\.?\d*)', confidence_str)
            if conf_match:
                confidence = float(conf_match.group(1))
                if confidence > 1.0:
                    confidence = confidence / 100.0
        except:
            pass

        # Build comprehensive root cause with impact and related concerns
        comprehensive_root_cause = f"""{root_cause.strip()}

**Impact Assessment:**
{impact.strip()}

**Related Concerns:**
{related.strip()}""".strip()

        # Build comprehensive recommendations with prevention and debugging
        comprehensive_recommendations = f"""{recommendations.strip()}

**Prevention Strategies:**
{prevention.strip()}

**Debugging Steps:**
{debugging.strip()}""".strip()

        # If code snippet not extracted, use surrounding lines
        if not code_snippet or len(code_snippet.strip()) < 10:
            lines = code_content.split('\n')
            start = max(0, line_number - 5)
            end = min(len(lines), line_number + 5)
            code_snippet = '\n'.join(f"{i+start+1}: {line}" for i, line in enumerate(lines[start:end]))

        return AnalysisResult(
            file_path=file_path,
            line_number=line_number,
            root_cause=comprehensive_root_cause if comprehensive_root_cause else "Unable to determine root cause",
            code_snippet=code_snippet.strip() if code_snippet else code_content[:500],
            recommendation=comprehensive_recommendations if comprehensive_recommendations else "No recommendation available",
            confidence=confidence
        )
    
    def _extract_section(self, text: str, start_marker: str, end_marker: Optional[str]) -> str:
        """Extract section between markers."""
        try:
            start_idx = text.find(start_marker)
            if start_idx == -1:
                return ""
            
            start_idx = text.find(":", start_idx) + 1
            
            if end_marker:
                end_idx = text.find(end_marker, start_idx)
                if end_idx == -1:
                    return text[start_idx:].strip()
                return text[start_idx:end_idx].strip()
            else:
                return text[start_idx:].strip()
        except:
            return ""

