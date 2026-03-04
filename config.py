"""Configuration management for Error Log Analyzer Agent."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AWS Bedrock Configuration
    bedrock_api_key: str = Field(..., description="AWS Bedrock API Key")
    aws_region: str = Field(default="us-west-2", description="AWS Region")
    
    # Bedrock Model Configuration
    bedrock_model_id: str = Field(
        default="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        description="Bedrock Claude Model ID"
    )
    bedrock_max_tokens: int = Field(default=4096, description="Max tokens for LLM response")
    bedrock_temperature: float = Field(default=0.1, description="LLM temperature")
    
    # GitHub Configuration
    github_token: Optional[str] = Field(default=None, description="GitHub Personal Access Token")
    
    # MCP Server Configuration
    mcp_server_url: str = Field(
        default="https://api.githubcopilot.com/mcp/x/git/readonly",
        description="GitHub MCP Server URL"
    )
    
    # File paths
    input_file: str = Field(default="input.txt", description="Input file path")
    output_file: str = Field(default="result.md", description="Output file path")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

