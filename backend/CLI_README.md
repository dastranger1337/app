# Axiom Red-Team CLI

A terminal-based AI red-team operator with direct shell access and 40+ penetration testing tools. Command any LLM (Claude, GPT, local models) to execute real reconnaissance and exploitation attacks.

## Installation

### Quick Start

```bash
cd /app/backend
bash cli_run.sh
```

This will:
1. Check Python 3.8+
2. Create a virtual environment
3. Install dependencies
4. Configure `.env` with API key placeholders
5. Optionally launch Axiom

### Manual Setup

```bash
cd /app/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_cli.txt
python3 axiom_cli.py
```

## Configuration

Edit `/app/backend/.env` to configure your AI provider:

### Option 1: Emergent Universal LLM (Default)

```bash
EMERGENT_LLM_KEY=your_key_here
DEFAULT_LLM_MODEL=claude-sonnet-4-5-20250929
```

Get a free Emergent key at: https://emergentintegrations.com

### Option 2: OpenAI-Compatible Provider

Works with OpenAI, Groq, Mistral, Together, OpenRouter, Ollama, LM Studio, vLLM, etc.

```bash
CUSTOM_LLM_BASE_URL=https://api.openai.com/v1
CUSTOM_LLM_API_KEY=sk-...
CUSTOM_LLM_MODEL=gpt-4
```

## Features

### Command-Line Interface

```
/help              Show available commands
/chat <message>    Send message to AI (enables auto-exec)
/exec <command>    Execute bash command directly
/tools             List installed tools
/status            Show tool installation status
/auto-exec         Toggle automatic code execution
/clear             Clear chat history
/quit              Exit Axiom
```

### Automatic Execution (Auto-Exec)

When enabled (default), Axiom automatically:
1. Executes bash code blocks from AI responses
2. Captures output (stdout, stderr, exit code)
3. Feeds results back to AI for analysis
4. Continues for up to 3 hops per user turn

Example:
```
> /chat Scan scanme.nmap.org for open ports
Axiom: I'll scan that target with nmap...
[Auto-executing bash]
[Output fed back to Axiom]
Axiom: The scan found ports 22 (SSH) and 80 (HTTP) open...
```

### Closed-Loop Workflow

1. **Plan**: You describe an objective
2. **Execute**: AI suggests and runs commands
3. **Analyze**: AI reviews output and recommends next steps
4. **Repeat**: Chain multiple commands autonomously

Example:
```
> /chat Perform a basic recon on scanme.nmap.org

Axiom: Starting recon...
[Auto-exec] Running nmap scan
[Output] Found SSH and HTTP open

Axiom: Now checking HTTP version with whatweb...
[Auto-exec] Running whatweb
[Output] Apache 2.4.41 detected

Axiom: The target is running Apache 2.4.41. Let me check for known vulnerabilities...
```

### Installed Tools

- **Network Scanning**: nmap, masscan, traceroute
- **Web Testing**: nikto, whatweb, gobuster, wfuzz, sqlmap, dirb
- **Authentication**: hydra, john, hashcat
- **DNS**: dig, whois
- **Utilities**: curl, openssl, nc, jq, exiftool
- **Wordlists**: /opt/SecLists (complete OWASP wordlist tree)
- **And more**: 40+ penetration testing tools total

## Usage Examples

### Example 1: Basic Network Scan

```
> /chat Scan target.com for open ports and services

Axiom: I'll perform a service scan on target.com...
[Auto-exec] nmap -sV -F target.com
[Output] 22/ssh (OpenSSH), 80/http (Apache), 443/https

Axiom: Found three services. Let me fingerprint the web server...
[Auto-exec] curl -I target.com
[Output] Server: Apache/2.4.41

Axiom: Target is running Apache 2.4.41. This version may be vulnerable to...
```

### Example 2: SQL Injection Testing

```
> /exec sqlmap -u "http://target.com/login.php?id=1" --dbs

> /chat Analyze the target for SQL injection vulnerabilities

Axiom: I'll run a comprehensive SQL injection test...
[Auto-exec] sqlmap -u "http://target.com/page.php?id=1" --batch --dbs
[Output] Target appears vulnerable, databases found: mysql, information_schema...
```

### Example 3: Credential Brute-Force

```
> /chat Attempt brute-force on SSH service with common credentials

Axiom: I'll launch a targeted brute-force attack...
[Auto-exec] hydra -l admin -P /opt/SecLists/Passwords/Common-Credentials/10-million-password-list-top-10.txt ssh://192.168.1.1
```

### Example 4: Manual Commands

```
> /exec nmap -sT -Pn target.com

> /exec whatweb target.com

> /exec gobuster dir -u http://target.com -w /opt/SecLists/Discovery/Web-Content/common.txt
```

## Architecture

### Modules

- **axiom_cli.py** - Terminal UI, chat loop, command dispatch
- **axiom_exec.py** - Code/bash execution with timeout and signal handling
- **axiom_chat.py** - AI integration (Emergent, OpenAI-compatible)
- **axiom_tools.py** - Tool installation and verification

### Execution Flow

```
User Input
    ↓
Parse Command
    ↓
    ├─ /chat → Send to AI → Get response
    │    ↓
    │    └─ Auto-exec enabled?
    │         ↓
    │         Extract code blocks
    │         ↓
    │         Execute in sandbox
    │         ↓
    │         Feed output back to AI
    │
    ├─ /exec → Execute directly in shell
    │    ↓
    │    Display output
    │
    └─ /tools, /status, /help, etc. → Display info
```

### Sandboxing

Each execution runs in an isolated directory:
- `/app/runtime_workspace/run-<uuid>/`
- File writes persist between runs
- Process timeout: 120 seconds (configurable)
- Signal: SIGKILL on timeout
- Environment: Real Linux (no container restrictions for nmap)

## Security Notes

⚠️ **Disclaimer**: Axiom executes real commands on the system. Use responsibly:

- Only run against systems you own or have authorization to test
- Penetration testing without permission is illegal
- Tool output may contain sensitive data
- Store API keys securely in `.env`
- Never commit `.env` to version control

## Advanced Configuration

### Custom Timeout

```bash
export EXEC_TIMEOUT_SECONDS=300  # 5 minutes
python3 axiom_cli.py
```

### Disable Auto-Exec by Default

```bash
# In axiom_cli.py, change:
auto_exec_enabled = False
```

### Local LLM (Ollama)

```bash
# Start Ollama
ollama serve

# In .env:
CUSTOM_LLM_BASE_URL=http://localhost:11434/v1
CUSTOM_LLM_API_KEY=ollama
CUSTOM_LLM_MODEL=mistral
```

## Troubleshooting

### "No LLM configured"

Check `.env` has either:
- `EMERGENT_LLM_KEY=...` (Emergent), OR
- `CUSTOM_LLM_*` + key (OpenAI-compatible)

### Tools not installing

```bash
cd /app/backend
bash ../backend/install_tools.sh
```

### Permission denied errors

Run with sudo or in a container with root privileges:
```bash
sudo python3 axiom_cli.py
```

### nmap requires root

Axiom auto-injects `--unprivileged` flag for nmap. If that fails, run with sudo.

## API Reference

### Execute Code/Command

```python
from axiom_exec import execute_bash, execute_code

result = await execute_bash("nmap -F scanme.nmap.org")
print(result)
# {
#     'success': True,
#     'stdout': '...',
#     'stderr': '',
#     'exitCode': 0,
#     'durationMs': 1234,
#     'output': '...'
# }
```

### Chat with AI

```python
from axiom_chat import chat_with_ai, format_message

messages = [
    format_message("user", "Scan scanme.nmap.org"),
]

async for chunk in chat_with_ai(messages):
    print(chunk, end="", flush=True)
```

### Check Tools

```python
from axiom_tools import check_tool_status, get_tools_info

status = check_tool_status()  # {'nmap': True, 'sqlmap': False, ...}

info = get_tools_info()  # {tool: {installed, description}, ...}
```

## File Structure

```
/app/backend/
├── axiom_cli.py           # Main CLI app
├── axiom_exec.py          # Code execution
├── axiom_chat.py          # AI integration
├── axiom_tools.py         # Tool management
├── cli_run.sh             # Setup and launch script
├── requirements_cli.txt   # Python dependencies
├── .env                   # Configuration (local)
└── venv/                  # Python virtual environment
```

## Future Enhancements

- [ ] Command history and autocomplete
- [ ] Session persistence (save/load chats)
- [ ] Custom command templates
- [ ] Multi-target scanning with parallelization
- [ ] Real-time output streaming visualization
- [ ] Report generation (JSON, HTML)
- [ ] Webhook integration for automation
- [ ] Persistent tool cache

## Support

For issues or feature requests:
1. Check `.env` configuration
2. Verify Python 3.8+ installed
3. Review tool installation status: `/status`
4. Check system permissions for tools like nmap

## License

Same as Axiom Red-Team parent project.

---

**Axiom Red-Team CLI** — Autonomous AI-powered penetration testing from your terminal.
