# Error Log Analyzer Agent

A Python agent that analyzes error logs and identifies responsible code lines in GitHub repositories using GitHub MCP Server (read-only) and AWS Bedrock Claude Haiku.

## Features

✅ **Read-only GitHub Access** - Safe analysis without modifying repositories  
✅ **File-based I/O** - Simple input.txt → result.md workflow  
✅ **Multi-language Support** - Python, JavaScript, Java error parsing  
✅ **AWS Bedrock Claude** - Cost-effective code analysis with Claude Haiku 4.5  
✅ **Minimal MCP Tools** - Only uses necessary read operations  

## Architecture

```
input.txt → Agent → GitHub MCP (readonly) → AWS Bedrock Claude → result.md
```

## Installation

### 1. Clone Repository

```bash
cd code-triager
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` (credentials are pre-configured):

```env
# AWS Bedrock API Key (already configured)
BEDROCK_API_KEY=
AWS_REGION=us-west-2

# GitHub Token (optional, for private repos)
GITHUB_TOKEN=your_github_token
```

**Note**: AWS credentials are already configured. If you need to use different credentials, set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables.

## Usage

### 1. Create Input File

Edit `input.txt`:

```yaml
repository: owner/repo-name

error_log: |
  Traceback (most recent call last):
    File "app.py", line 45, in authenticate
      user_id = user.get('id')
  AttributeError: 'NoneType' object has no attribute 'get'
```

### 2. Run Agent

```bash
python main.py
```

### 3. Check Results

Open `result.md` to see the analysis report.

## Example Output

```markdown
# Error Analysis Report

**Generated**: 2024-03-04 10:30:00  
**Repository**: `pallets/flask`

## 📍 Location
- **File**: `app.py`
- **Line**: 45

## 💻 Code Snippet
```python
43 | def authenticate(token):
44 |     user = get_user_from_token(token)
45 |     user_id = user.get('id')  # ❌ ERROR HERE
46 |     return user_id
```

## 🔍 Root Cause
Variable `user` is None because `get_user_from_token()` returns None for invalid tokens...

## ✅ Recommendation
Add null check before accessing user object...
```

## Configuration

### MCP Server

- **URL**: `https://api.githubcopilot.com/mcp/x/git/readonly`
- **Mode**: Read-only
- **Whitelisted Tools**: `get_file_contents`, `search_code`, `list_directory`

### AWS Bedrock

- **Model**: Claude Haiku 4.5 (`us.anthropic.claude-haiku-4-5-20251001-v1:0`)
- **Region**: us-west-2
- **Temperature**: 0.1 (consistent analysis)

## Project Structure

```
code-triager/
├── agent.py              # Main agent logic
├── mcp_client.py         # GitHub MCP client
├── bedrock_client.py     # AWS Bedrock client
├── error_parser.py       # Error log parser
├── report_generator.py   # Markdown report generator
├── models.py             # Data models
├── config.py             # Configuration
├── main.py               # Entry point
├── requirements.txt      # Dependencies
├── input.txt             # Input file
└── result.md             # Output file
```

## Supported Error Types

- **Python**: AttributeError, TypeError, ValueError, KeyError, IndexError
- **JavaScript**: TypeError, ReferenceError, SyntaxError
- **Java**: NullPointerException, ArrayIndexOutOfBoundsException

## Troubleshooting

### MCP Connection Issues
- Ensure GitHub token is valid (if using private repos)
- Check internet connectivity

### AWS Bedrock Errors
- Verify AWS credentials in `.env`
- Ensure Bedrock is enabled in your AWS region
- Check IAM permissions for Bedrock access

### Parsing Errors
- Ensure error log format is correct
- Check that repository name is in `owner/repo` format

## License

MIT

