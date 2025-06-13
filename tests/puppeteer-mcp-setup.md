# Setting up Puppeteer MCP for Claude Code

## Quick Install (Recommended)

```bash
# Install the MCP server
npx @modelcontextprotocol/install-mcp-server
# Select "Puppeteer" from the list
```

## Manual Configuration

1. **Find your Claude config file:**
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/claude/claude_desktop_config.json`

2. **Add Puppeteer MCP configuration:**

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
      "env": {}
    }
  }
}
```

3. **Restart Claude Desktop app**

## Verify Installation

Once installed, I should be able to use these commands:
- `puppeteer_navigate` - Navigate to URLs
- `puppeteer_screenshot` - Take screenshots
- `puppeteer_evaluate` - Execute JavaScript

## Test the Setup

Ask me to:
"Navigate to http://localhost:5000 and take a screenshot"

If it works, I'll be able to run the smoke tests!