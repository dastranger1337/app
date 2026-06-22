# Axiom Red-Team Terminal App - Quick Start

## What's Been Done

Your Axiom Red-Team app has been **fully converted from a web/mobile React Native app to a Linux terminal application** with the following:

### ✅ Core Components

1. **Terminal UI** (`axiom_cli.py`)
   - Rich, interactive command-line interface
   - Real-time chat with AI
   - Live command execution feedback
   - Tool status dashboard

2. **Execution Engine** (`axiom_exec.py`)
   - Direct bash command execution
   - Multi-language code runner (bash, python, nodejs, go, ruby, etc.)
   - Timeout protection (120s default)
   - Process signal handling
   - Persistent workspace at `/app/runtime_workspace/`

3. **AI Integration** (`axiom_chat.py`)
   - Emergent Universal LLM (Claude via emergentintegrations.com)
   - Custom OpenAI-compatible provider support
   - Streaming responses
   - System prompt optimized for red-teaming
   - Code block extraction for auto-execution

4. **Tool Management** (`axiom_tools.py`)
   - Automatic installation of 40+ pentest tools
   - Tool status verification
   - Installation idempotency (safe to run repeatedly)
   - Support for: nmap, sqlmap, nikto, whatweb, gobuster, hydra, john, hashcat, and more

5. **Setup Script** (`cli_run.sh`)
   - Automated virtual environment creation
   - Dependency installation
   - Configuration file generation
   - Interactive launch

### ✅ Features

- **Closed-loop AI execution**: AI emits commands → they execute → output fed back to AI
- **Auto-execution**: Code blocks automatically run (configurable, max 3 per turn)
- **Real-time output**: Instant feedback on command results
- **Tool inventory**: Check installed tools and their status
- **Command history**: Maintains context across multiple turns
- **Direct shell access**: Run any bash command manually
- **Sandboxed execution**: Each run gets isolated directory

### 📦 What You Get

```
/app/backend/
├── axiom_cli.py              # Main app (executable)
├── axiom_exec.py             # Execution engine
├── axiom_chat.py             # AI chat module
├── axiom_tools.py            # Tool management
├── cli_run.sh                # Setup script (executable)
├── requirements_cli.txt      # Python dependencies
├── CLI_README.md             # Full documentation
└── QUICK_START.md            # This file
```

## Quick Start (5 minutes)

### Step 1: Setup

```bash
cd /app/backend
bash cli_run.sh
```

This will:
- Create Python virtual environment
- Install dependencies (rich, httpx, python-dotenv)
- Generate `.env` configuration file
- Ask if you want to launch

### Step 2: Configure API Key

Edit `/app/backend/.env`:

**Option A: Emergent (Free, Claude-powered)**
```bash
EMERGENT_LLM_KEY=your_key_here
# Get free key at: https://emergentintegrations.com
```

**Option B: OpenAI/Groq/Mistral/etc (Custom)**
```bash
CUSTOM_LLM_BASE_URL=https://api.groq.com/openai/v1
CUSTOM_LLM_API_KEY=your_api_key
CUSTOM_LLM_MODEL=mixtral-8x7b-32768
```

### Step 3: Launch

```bash
cd /app/backend
source venv/bin/activate
python3 axiom_cli.py
```

Or use the setup script:
```bash
bash cli_run.sh
```

### Step 4: First Command

```
> /chat Scan scanme.nmap.org for open ports

Axiom: I'll scan scanme.nmap.org for open ports...
[Auto-executing bash]
[✓ Success]
Ports found: 22/ssh, 80/http, 9929/nping, 11371/pgp
```

## Available Commands

| Command | Example | Purpose |
|---------|---------|---------|
| `/chat` | `/chat Scan the target` | Send message to AI (triggers auto-exec) |
| `/exec` | `/exec nmap -F scanme.nmap.org` | Run bash command directly |
| `/tools` | `/tools` | List all installed tools |
| `/status` | `/status` | Check tool installation progress |
| `/auto-exec` | `/auto-exec` | Toggle automatic code execution |
| `/clear` | `/clear` | Clear chat history |
| `/help` | `/help` | Show all commands |
| `/quit` | `/quit` | Exit Axiom |

## Example Workflows

### Workflow 1: Basic Reconnaissance

```
> /chat Perform reconnaissance on scanme.nmap.org

Axiom: I'll start with a service scan...
[Auto-exec] nmap -sV -F scanme.nmap.org

Axiom: Found services. Let me check SSL certificate...
[Auto-exec] openssl s_client -connect scanme.nmap.org:443

Axiom: Certificate valid until 2024. Let me check for known vulnerabilities...
```

### Workflow 2: Web Application Testing

```
> /chat Check for SQL injection vulnerabilities on target.com/login

Axiom: I'll test with SQL injection payloads...
[Auto-exec] sqlmap -u "http://target.com/login" --forms --batch

Axiom: Target appears vulnerable. Let me enumerate databases...
[Auto-exec] sqlmap -u "http://target.com/login" --dbs

Axiom: Found databases: mysql, information_schema, webapp_db
```

### Workflow 3: Manual Commands

```
> /exec gobuster dir -u http://target.com -w /opt/SecLists/Discovery/Web-Content/common.txt

> /exec hydra -l admin -P /opt/SecLists/Passwords/Common-Credentials/100-most-used-passwords.txt ssh://192.168.1.1

> /exec whatweb http://target.com
```

## Architecture

### How It Works

```
User Types Command
        ↓
    CLI Parser
        ↓
    ┌───┴────────────────────┐
    ↓                        ↓
  /chat               /exec or other
    ↓                        ↓
Send to AI         Execute Directly
    ↓                        ↓
Get Response      Show Output
    ↓
Extract Code Blocks
    ↓
Auto-Execute? (if enabled)
    ↓
Run Commands
    ↓
Feed Output to AI
    ↓
Continue Loop
```

### Key Differences from Web App

| Aspect | Web App | CLI |
|--------|---------|-----|
| Interface | React Native web UI | Terminal (rich) |
| Backend | Separate FastAPI server | Integrated in CLI |
| Execution | HTTP API calls | Direct async execution |
| State | Browser-based | Chat history in memory |
| Tools | Browser shows results | Terminal displays output |
| Auth | Supabase login | None (local only) |

## Configuration

### Environment Variables

```bash
# AI Provider
EMERGENT_LLM_KEY=...          # Emergent Universal LLM key
CUSTOM_LLM_BASE_URL=...       # OpenAI-compatible base URL
CUSTOM_LLM_API_KEY=...        # API key for custom provider
CUSTOM_LLM_MODEL=...          # Model name for custom provider
DEFAULT_LLM_MODEL=...         # Default model to use

# Execution
EXEC_TIMEOUT_SECONDS=120      # Command timeout in seconds
```

### Where to Get API Keys

- **Emergent** (Free tier available): https://emergentintegrations.com
- **OpenAI**: https://platform.openai.com/api-keys
- **Groq** (Fast, free tier): https://console.groq.com
- **Mistral**: https://console.mistral.ai
- **Together**: https://www.together.ai
- **OpenRouter**: https://openrouter.io
- **Ollama** (Local): https://ollama.ai (free, no key needed)

## Troubleshooting

### Issue: "Python not found"
```bash
# Install Python 3.8+
sudo apt-get install python3 python3-venv
```

### Issue: "No LLM configured"
Check `.env` has one of:
- `EMERGENT_LLM_KEY=your_key`
- `CUSTOM_LLM_API_KEY=your_key` + `CUSTOM_LLM_BASE_URL`

### Issue: Tools not installing
```bash
cd /app/backend
bash ../backend/install_tools.sh
```

### Issue: Permission denied for nmap
```bash
sudo python3 axiom_cli.py
# OR
sudo bash cli_run.sh
```

### Issue: "nmap: command not found"
```bash
# Wait for background tool installation or force install:
sudo apt-get install -y nmap
```

## Next Steps

1. **Setup**: Run `bash cli_run.sh`
2. **Configure**: Add API key to `.env`
3. **Launch**: Execute `python3 axiom_cli.py`
4. **Learn**: Type `/help` for commands
5. **Explore**: Try `/chat Scan scanme.nmap.org`

## Files Created

```
/app/backend/
├── axiom_cli.py           ← Main terminal app
├── axiom_exec.py          ← Code/command executor
├── axiom_chat.py          ← AI integration
├── axiom_tools.py         ← Tool management
├── cli_run.sh             ← Setup script
├── requirements_cli.txt   ← Python packages
├── CLI_README.md          ← Full documentation
├── QUICK_START.md         ← This file
└── .env                   ← Configuration (generated by cli_run.sh)
```

## Security Reminders

⚠️ **Important**: 

- Only test systems you own or have written authorization to test
- Penetration testing without permission is illegal
- Keep API keys private (never commit `.env` to git)
- Tool output may contain sensitive data
- Commands execute with your user privileges

## Performance

- **Startup**: ~2-3 seconds (tool check)
- **Chat response**: 5-30 seconds (depends on AI provider)
- **Code execution**: Instant to 120s (timeout)
- **Tool installation**: ~5 minutes first run, then instant (cached)

## What's Different from the Web App

### Removed
- ❌ React Native UI components
- ❌ Mobile/tablet support
- ❌ Browser-based authentication
- ❌ HTTP API server (merged into CLI)
- ❌ Static web server (serve-dist.js)
- ❌ Supabase dependency for login

### Added
- ✅ Terminal user interface (rich library)
- ✅ Direct command-line input
- ✅ Instant terminal output
- ✅ Embedded execution engine
- ✅ No server overhead
- ✅ Truly local-first operation

### Same
- ✅ AI chat integration
- ✅ Auto-exec closed-loop
- ✅ Tool management
- ✅ Command execution
- ✅ Red-team workflows

## Further Customization

The CLI is modular and extensible:

- **Add custom commands**: Edit `axiom_cli.py` in the command handler
- **Change UI styling**: Modify rich colors/panels in `axiom_cli.py`
- **Add new tools**: Update `TOOLS_TO_INSTALL` in `axiom_tools.py`
- **Extend chat**: Modify `SYSTEM_PROMPT` in `axiom_chat.py`
- **Add execution languages**: Extend `LANG_RUNNERS` in `axiom_exec.py`

## Support

For full documentation, see: `/app/backend/CLI_README.md`

For issues:
1. Check `.env` configuration
2. Verify Python 3.8+ with `python3 --version`
3. Check tool status: `/status` in the app
4. Review `/app/backend/axiom_tools.py` for tool installation

---

**You're ready to use Axiom from the terminal!** 🚀

Start with: `bash /app/backend/cli_run.sh`
