# 🔍 Error Log Analyzer Agent

**An intelligent, universal error analysis agent** that uses **LLM-first architecture** to analyze ANY type of error log from GitHub repositories.

**Powered by**: GitHub MCP (Read-Only) + AWS Bedrock Claude Haiku 4.5

---

## ✨ Key Features

### **🤖 LLM-First Architecture**
- **Claude decides everything** - No brittle regex patterns!
- **Universal error handling** - Works with ANY log format
- **Intelligent routing** - Automatically determines analysis strategy
- **Self-adapting** - No code updates needed for new error types

### **📊 Supported Error Types**
✅ **Stack Traces** - Python, JavaScript, Java, Go, Rust, etc.
✅ **API Errors** - HTTP 4xx/5xx validation errors
✅ **Application Logs** - Structured logs with emojis, timestamps
✅ **Database Errors** - SQLAlchemy, connection errors
✅ **Generic Errors** - Any unstructured error text

### **🔒 Security & Safety**
✅ **Read-Only Mode** - Cannot modify any GitHub repositories
✅ **MCP Tools** - Uses GitHub's official MCP server
✅ **Private Repos** - Works with private repositories (requires GitHub PAT)
✅ **File-based I/O** - Simple input.txt → result.md workflow

### **📝 Comprehensive Analysis**
✅ **Root Cause** - WHAT, WHY, WHEN, WHERE analysis
✅ **Impact Assessment** - Severity, cascading failures, data loss
✅ **Multiple Solutions** - 2-3 different approaches with pros/cons
✅ **Prevention Strategies** - Tests, monitoring, code improvements
✅ **Debugging Steps** - Concrete reproduction and verification steps
✅ **Related Concerns** - Similar patterns, async issues, race conditions

---

## 🏗️ Architecture

### **LLM-First Workflow**

```
ANY Error Log
    ↓
┌─────────────────────────────────────────┐
│ Step 1: Claude Understands Error       │
│ • What type of error?                  │
│ • Has file location?                   │
│ • Needs code search?                   │
│ • What keywords to search?             │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 2: Intelligent Code Fetching      │
│ ├─ Has file path? → Direct fetch       │
│ ├─ Needs search? → Search & fetch      │
│ └─ No code needed? → Skip              │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 3: Comprehensive Analysis          │
│ • Root cause (with/without code)       │
│ • Impact assessment                     │
│ • Multiple solutions                    │
│ • Prevention strategies                 │
└─────────────────────────────────────────┘
    ↓
Detailed Markdown Report (result.md)
```

### **Why LLM-First?**

| Traditional Approach | LLM-First (This Agent) |
|---------------------|------------------------|
| 100+ regex patterns | Claude decides |
| 800+ lines of code | 600 lines |
| Fixed error formats | ANY format |
| Constant updates | Zero updates |
| Brittle & breaks | Robust & adapts |

---

## Installation

### 1. Clone Repository

```bash
cd Log-Analyzer
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

## 🚀 Usage

### 1. Create Input File

Edit `input.txt` with **ANY** error log format:

#### **Example 1: Python Stack Trace**
```yaml
repository: maplelabs/ai-sre-ops

error_log: |
  Traceback (most recent call last):
    File "backend/src/server/apis_v1/webhooks.py", line 250, in grafana_webhook
      new_triage.job_id = triage_job_id
  AttributeError: 'NoneType' object has no attribute 'job_id'
```

#### **Example 2: API Error (No Stack Trace)**
```yaml
repository: maplelabs/fault-injector

error_log: |
  📤 POST to SRE: 422
  🔗 POST URL: http://api.example.com/v1/fault-ledger
  ❌ SRE API failed: 422 - {"detail":[{"type":"float_type","loc":["body","configured_duration"],"msg":"Input should be a valid number","input":null}]}
```

#### **Example 3: JavaScript Error**
```yaml
repository: facebook/react

error_log: |
  TypeError: Cannot read property 'setState' of undefined
    at Component.render (packages/react/src/ReactBaseClasses.js:25:10)
    at renderWithHooks (packages/react-reconciler/src/ReactFiberHooks.js:120:5)
```

#### **Example 4: Generic Application Log**
```yaml
repository: your-org/your-app

error_log: |
  [2026-01-06 12:51:41] ERROR: Service initialization failed
  Connection to database timed out after 30 seconds
  Host: db.example.com:5432
```

### 2. Run Agent

```bash
source venv/bin/activate
python main.py
```

### 3. Check Results

Open `result.md` to see the comprehensive analysis report (500+ lines of detailed analysis!).

## 📊 Example Output

The agent generates a **comprehensive 500+ line report** with:

### **Console Output**
```
🤖 Claude is analyzing the error type and determining strategy...
   ✓ Error Type: AttributeError
   ✓ Severity: high
   ✓ Language: Python
   ✓ Has File Location: true
   ✓ Needs Code: true

📥 Fetching code from: backend/src/server/apis_v1/webhooks.py
   🔒 MCP Client initialized in READ-ONLY mode
   ✓ Fetched 65423 characters
   ✓ Extracted lines 240-260

🧠 Claude is performing deep analysis...
   ✓ Analysis complete

📄 Generating report...
   ✓ Report saved to: result.md

✅ Success! Check 'result.md' for the analysis report.
```

### **Generated Report (result.md)**

```markdown
# 🔍 Comprehensive Error Analysis Report

**Generated**: 2026-03-04 12:15:23
**Repository**: maplelabs/ai-sre-ops

## 📋 Error Summary
- **Error Type**: AttributeError
- **Message**: 'NoneType' object has no attribute 'job_id'
- **File**: backend/src/server/apis_v1/webhooks.py
- **Line**: 250
- **Confidence**: 95% 🟢

## 💻 Code Context
```python
245 |     triage_job_id = enqueue_triage_job(
246 |         alert_id=new_alert.id,
247 |         triage_id=thread_id,
248 |         queue_name=triage_queue_name
249 |     )
250 |     new_triage.job_id = triage_job_id  # ❌ ERROR HERE
251 |     new_triage.status = Status.QUEUED
252 |     await session.commit()
```

## 🔍 Root Cause Analysis

**WHAT**: The error occurs because `new_triage` is `None` when attempting to access its `job_id` attribute...

**WHY**: This happens when the database session fails to create the TriageDBModel instance...

**WHEN**: Occurs during webhook processing when automatic triage is enabled...

**WHERE**: In the grafana_webhook function after attempting to enqueue a triage job...

**Impact Assessment:**
- Severity: HIGH
- Webhook processing fails completely
- Alert triage is not initiated
- No data is persisted to database

**Related Concerns:**
- Similar pattern may exist in EvaluationDBModel creation
- Async session handling needs review
- Transaction rollback may leave inconsistent state

## ✅ Recommendations & Solutions

### **Solution 1: Add Null Check (Defensive)**
```python
if new_triage is None:
    logger.error(f"Failed to create triage record for alert {new_alert.external_id}")
    raise ValueError("Triage record creation failed")

new_triage.job_id = triage_job_id
```
**Pros**: Quick fix, prevents crash
**Cons**: Doesn't fix root cause
**When to use**: Immediate hotfix

### **Solution 2: Fix Database Transaction (Root Cause)**
```python
new_triage = TriageDBModel(...)
session.add(new_triage)
await session.flush()  # Ensure DB write completes
await session.refresh(new_triage)  # Reload from DB

if new_triage is None:
    raise DatabaseError("Failed to persist triage record")
```
**Pros**: Fixes root cause
**Cons**: Requires testing
**When to use**: Permanent fix

### **Prevention Strategies:**
- Add unit test for triage creation failure
- Add integration test for webhook with DB errors
- Implement retry logic for transient DB failures
- Add monitoring for triage creation failures

### **Debugging Steps:**
1. Check database logs for constraint violations
2. Verify session.add() is called before session.flush()
3. Test with database connection failures
4. Review transaction isolation level
5. Check for race conditions in concurrent requests
```
```

## 🔍 Root Cause
Variable `user` is None because `get_user_from_token()` returns None for invalid tokens...

## ✅ Recommendation
Add null check before accessing user object...
```

## ⚙️ Configuration

### **GitHub MCP Server**

- **URL**: `https://api.githubcopilot.com/mcp/readonly`
- **Mode**: 🔒 **Read-Only** (Cannot modify repositories)
- **Available Tools**: 25 read-only tools
  - ✅ `get_file_contents` - Fetch file contents (ACTIVELY USED)
  - ⚠️ `search_code` - Search codebase (Available but limited)
  - ⚠️ `list_issues`, `list_pull_requests`, `get_commit`, etc. (24 more tools)
- **Authentication**: GitHub Personal Access Token (PAT)

### **AWS Bedrock Claude**

- **Model**: Claude Haiku 4.5 (`us.anthropic.claude-haiku-4-5-20251001-v1:0`)
- **Region**: us-west-2
- **Max Tokens**: 4096
- **Temperature**:
  - 0.1 for error understanding (structured output)
  - 0.1 for analysis (consistent results)
- **Authentication**: AWS Bedrock API Key (Bearer Token)

### **LLM Calls Per Analysis**

1. **First Call**: Error Understanding (~500 tokens)
   - Determines error type, file location, search strategy
   - Returns structured JSON

2. **Second Call**: Comprehensive Analysis (~3000 tokens)
   - Deep analysis with code context
   - Generates detailed recommendations

```
## 📁 Project Structure

```
Log-Analyzer/
├── Core Agent Files
│   ├── main.py                  # Entry point
│   ├── agent.py                 # Main agent orchestration (LLM-first workflow)
│   ├── bedrock_client.py        # AWS Bedrock Claude client (2 LLM calls)
│   ├── mcp_client.py            # GitHub MCP client (read-only)
│   ├── error_parser.py          # Minimal validation (Claude does parsing)
│   ├── report_generator.py      # Markdown report generator
│   ├── models.py                # Data models (ErrorUnderstanding, etc.)
│   └── config.py                # Configuration management
│
├── Configuration
│   ├── .env                     # Your credentials (API keys)
│   ├── .env.example             # Template
│   ├── requirements.txt         # Python dependencies
│   └── setup.sh                 # Setup script
│
├── Documentation
│   ├── README.md                # This file
│   ├── USAGE_GUIDE.md           # Detailed usage guide
│   └── AVAILABLE_TOOLS.md       # MCP tools documentation
│
├── Input/Output
│   ├── input.txt                # Input error logs
│   └── result.md                # Generated analysis report
│
└── venv/                        # Virtual environment
```

## 🎯 Supported Error Types

### **With Stack Traces** (Direct File Fetch)
- ✅ **Python**: AttributeError, TypeError, ValueError, KeyError, IndexError, etc.
- ✅ **JavaScript/TypeScript**: TypeError, ReferenceError, SyntaxError, etc.
- ✅ **Java**: NullPointerException, ArrayIndexOutOfBoundsException, etc.
- ✅ **Go**: panic, runtime errors
- ✅ **Rust**: panic, unwrap errors

### **Without Stack Traces** (Search or Log-Only Analysis)
- ✅ **API Errors**: HTTP 4xx/5xx with validation details
- ✅ **Database Errors**: Connection, query, constraint violations
- ✅ **Application Logs**: Structured logs with timestamps/emojis
- ✅ **Generic Errors**: Any unstructured error text

**Note**: Claude's LLM-first approach means it can handle formats we haven't even thought of!

## 🛠️ Troubleshooting

### **MCP Connection Issues**
```
❌ MCP Error: 400/401/403
```
**Solutions**:
- Verify GitHub token is valid: `echo $GITHUB_TOKEN`
- Check token has repo access (for private repos)
- Ensure internet connectivity
- Try regenerating GitHub PAT

### **AWS Bedrock Errors**
```
❌ Error calling Bedrock: UnrecognizedClientException
```
**Solutions**:
- Verify `BEDROCK_API_KEY` in `.env` is correct
- Check AWS region is `us-west-2`
- Ensure Bedrock is enabled in your AWS account
- Verify API key format (starts with `ABSK`)

### **File Not Found**
```
❌ Failed to fetch code from repository
```
**Solutions**:
- Check file path in error log matches actual repo structure
- Verify repository name is in `owner/repo` format
- Ensure file exists in the default branch
- For private repos, verify GitHub token has access

### **Search Failures**
```
⚠️ No code found via search, will analyze log only
```
**This is OK!** The agent will:
- Analyze the error log without code
- Provide recommendations based on error message
- Suggest what to search for manually

### **JSON Parsing Errors**
```
❌ Failed to parse error understanding
```
**Solutions**:
- Claude's response might not be valid JSON
- Agent will fall back to basic understanding
- Check if error log is too large (>10KB)

---

## 💡 Benefits of This Agent

### **For Developers**
- ✅ **Save Time**: Instant root cause analysis instead of hours of debugging
- ✅ **Learn Patterns**: See how experts would debug the same error
- ✅ **Multiple Solutions**: Get 2-3 different approaches to fix
- ✅ **Prevention**: Learn how to prevent similar errors

### **For Teams**
- ✅ **Knowledge Sharing**: Detailed reports can be shared with team
- ✅ **Onboarding**: New developers learn from comprehensive analysis
- ✅ **Documentation**: Auto-generated debugging guides
- ✅ **Consistency**: Same quality analysis every time

### **For Operations**
- ✅ **Incident Response**: Quick analysis during outages
- ✅ **Post-Mortems**: Detailed root cause for reports
- ✅ **Monitoring**: Integrate with alerting systems
- ✅ **Automation**: File-based I/O enables CI/CD integration

---

## 📈 Future Enhancements

- [ ] Full MCP search implementation for API errors
- [ ] Multi-file analysis (trace errors across files)
- [ ] Historical error pattern detection
- [ ] Integration with GitHub Issues
- [ ] Slack/Teams notifications
- [ ] Web UI for easier interaction
- [ ] Support for more languages (PHP, Ruby, C++, etc.)

---

## 🤝 Contributing

Contributions welcome! The LLM-first architecture makes it easy to add features without complex regex patterns.

---

## 📄 License

MIT

---

## 🙏 Acknowledgments

- **GitHub MCP Server** - For read-only repository access
- **AWS Bedrock Claude** - For intelligent error analysis
- **Anthropic** - For Claude Haiku 4.5 model

---
