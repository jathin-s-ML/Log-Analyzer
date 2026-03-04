"""GitHub MCP Client for fetching code from repositories."""

import httpx
import json
from typing import Optional, Dict, Any
from config import settings


class GitHubMCPClient:
    """Client for interacting with GitHub MCP Server in read-only mode."""

    def __init__(self):
        """Initialize MCP client in READ-ONLY mode."""
        # Use the GitHub MCP server in READONLY mode
        # This restricts the agent to only read operations - no write/modify/delete
        self.server_url = "https://api.githubcopilot.com/mcp/readonly"
        self.github_token = settings.github_token
        self.session_id = None
        self.client = httpx.Client(timeout=60.0)

        print("🔒 MCP Client initialized in READ-ONLY mode")
        
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for MCP requests."""
        headers = {
            "Content-Type": "application/json"
        }

        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"

        return headers
    
    def initialize(self) -> bool:
        """
        Initialize MCP session.

        Returns:
            True if initialization successful
        """
        try:
            response = self.client.post(
                f"{self.server_url}/initialize",
                headers=self._get_headers(),
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "clientInfo": {
                            "name": "error-log-analyzer",
                            "version": "1.0.0"
                        }
                    }
                }
            )

            if response.status_code == 200:
                # Response might be SSE format, just check status
                return True

            return False

        except Exception as e:
            print(f"Error initializing MCP session: {e}")
            return False
    
    def get_file_contents(
        self,
        repository: str,
        file_path: str,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None
    ) -> Optional[str]:
        """
        Get file contents from GitHub repository using MCP tools.

        Args:
            repository: Repository in format "owner/repo"
            file_path: Path to file in repository
            line_start: Optional starting line number
            line_end: Optional ending line number

        Returns:
            File contents as string, or None if error
        """
        try:
            print(f"   Fetching via MCP: {repository}/{file_path}")

            # Prepare MCP tool call in JSON-RPC 2.0 format
            owner, repo = repository.split('/')
            tool_params = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "get_file_contents",
                    "arguments": {
                        "owner": owner,
                        "repo": repo,
                        "path": file_path
                    }
                }
            }

            # Call MCP tool
            response = self.client.post(
                self.server_url,
                headers=self._get_headers(),
                json=tool_params
            )

            print(f"   MCP Status: {response.status_code}")
            # Don't print full response as it can be very large
            # print(f"   Response text (first 500 chars): {response.text[:500]}")

            if response.status_code == 200:
                # Check if response is SSE format
                if response.text.startswith("event:") or response.text.startswith("data:"):
                    print(f"   Response is SSE format, parsing...")
                    # Parse SSE format
                    lines = response.text.strip().split('\n')
                    json_data = None
                    for line in lines:
                        if line.startswith('data: '):
                            json_str = line[6:]  # Remove 'data: ' prefix
                            try:
                                json_data = json.loads(json_str)
                                if json_data:  # Found valid JSON
                                    break
                            except Exception as e:
                                print(f"   Warning: Could not parse line: {line[:100]}")
                                continue

                    if not json_data:
                        print(f"   ✗ Could not parse SSE response")
                        return None

                    data = json_data
                else:
                    try:
                        data = response.json()
                    except Exception as e:
                        print(f"   ✗ Could not parse JSON response: {e}")
                        return None

                # JSON-RPC 2.0 response format: {"jsonrpc": "2.0", "id": 1, "result": {"content": [...]}}
                if "result" in data:
                    result = data["result"]
                    if "content" in result and len(result["content"]) > 0:
                        # MCP returns content as array, may have text or resource type
                        # Prioritize resource type as it contains the actual file content
                        content = None
                        for item in result["content"]:
                            if item.get("type") == "resource":
                                # Resource type has nested text - this is the actual file content
                                resource = item.get("resource", {})
                                content = resource.get("text", "")
                                if content:
                                    break

                        # Fallback to text type if no resource found
                        if not content:
                            for item in result["content"]:
                                if item.get("type") == "text":
                                    content = item.get("text", "")
                                    if content:
                                        break

                        if not content:
                            print(f"   ✗ No text content found in MCP result")
                            print(f"   Content items: {len(result['content'])}")
                            for i, item in enumerate(result['content']):
                                print(f"   Item {i}: type={item.get('type')}, has_text={bool(item.get('text'))}, has_resource={bool(item.get('resource'))}")
                            return None

                        print(f"   ✓ Extracted content from MCP (length: {len(content)} chars)")
                    else:
                        print(f"   ✗ No content in MCP result")
                        print(f"   Result: {str(result)[:200]}")
                        return None
                elif "error" in data:
                    print(f"   ✗ MCP Error: {data['error']}")
                    return None
                else:
                    # Fallback: try direct content access
                    if "content" in data and len(data["content"]) > 0:
                        content = data["content"][0].get("text", "")
                    else:
                        print(f"   ✗ Unexpected MCP response format")
                        print(f"   Response: {str(data)[:200]}")
                        return None

                if not content:
                    print(f"   ✗ Empty content from MCP")
                    return None

                print(f"   Fetched {len(content)} characters")

                # If line range specified, extract those lines
                if line_start is not None or line_end is not None:
                    lines = content.split('\n')
                    print(f"   Total lines: {len(lines)}, extracting lines {line_start}-{line_end}")
                    start = (line_start - 1) if line_start else 0
                    end = min(line_end if line_end else len(lines), len(lines))

                    # Check if line range is valid
                    if start >= len(lines):
                        print(f"   ⚠️  Line {line_start} is beyond file end ({len(lines)} lines)")
                        print(f"   Returning last 50 lines instead")
                        start = max(0, len(lines) - 50)
                        end = len(lines)

                    content = '\n'.join(lines[start:end])
                    print(f"   Extracted {len(content)} characters from lines {start+1}-{end}")

                print(f"   ✓ Fetched {len(content)} characters")
                return content

            print(f"   ✗ MCP Error: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            return None

        except Exception as e:
            print(f"Error in get_file_contents: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def search_code(
        self,
        repository: str,
        query: str
    ) -> Optional[Dict[str, Any]]:
        """
        Search for code in repository using MCP tools.

        Args:
            repository: Repository in format "owner/repo"
            query: Search query

        Returns:
            Search results as dictionary
        """
        try:
            print(f"   Searching via MCP: {repository} for '{query}'")

            response = self.client.post(
                f"{self.server_url}/tools/call",
                headers=self._get_headers(),
                json={
                    "name": "search_code",
                    "arguments": {
                        "owner": repository.split('/')[0],
                        "repo": repository.split('/')[1],
                        "query": query
                    }
                }
            )

            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Search completed")
                return data

            print(f"   ✗ Search failed: {response.status_code}")
            return None

        except Exception as e:
            print(f"Error in search_code: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def close(self):
        """Close HTTP client."""
        self.client.close()

