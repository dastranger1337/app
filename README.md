# Axiom Red-Team CLI

> An autonomous, AI-powered penetration testing operator for Linux. Command any LLM
> to execute real reconnaissance and exploitation attacks with 40+ integrated tools.

**Axiom Red-Team CLI** is a terminal-based offensive-security framework that gives you
direct access to a Linux shell with 40+ pre-installed penetration testing tools
(`nmap`, `sqlmap`, `nikto`, `whatweb`, `gobuster`, `hydra`, `john`, `hashcat`,
`dig`, `masscan`, `wfuzz`, `smbclient`, and more). Chat with Claude, GPT, or any
LLM—it analyzes your target, emits shell commands, the runtime executes them in
real-time, and feeds results back into the next conversational turn.
Fully autonomous, fully closed-loop.

## 🚀 Quick Start

```bash
# 1. Setup (installs dependencies and creates venv)
cd /app/backend && bash cli_run.sh

# 2. Configure your AI provider in .env
# (Emergent key is free: https://emergentintegrations.com)

# 3. Launch Axiom
python3 axiom_cli.py
```

Then:
```
> /chat Scan scanme.nmap.org for open ports
Axiom: I'll perform a service scan...
[Auto-executing bash]
[✓ Success] Found ports: 22/ssh, 80/http, 443/https
```

See [Quick Start Guide](docs/QUICK_START.md) for full setup instructions.

---

## Features

### Three Ways to Use Axiom

| Method | Example | Use Case |
|--------|---------|----------|
| **AI Chat** | `/chat Scan scanme.nmap.org` | Autonomous planning + execution |
| **Direct Command** | `/exec nmap -F scanme.nmap.org` | Manual tool usage |
| **Auto-Exec** | Enabled by default | Chain commands in closed loop |

### AI Engines (toggle in config)

- **Emergent Universal LLM** (default) — Claude 4.5 / Haiku via `emergentintegrations`
- **Custom OpenAI-compatible** — OpenAI, Groq, Mistral, Together, Ollama, LM Studio, etc.

### Installed Tools

**Network Scanning**: nmap, masscan, traceroute, netdiscover  
**Web Testing**: nikto, whatweb, gobuster, wfuzz, sqlmap, dirb  
**Credential Attack**: hydra, john, hashcat  
**DNS**: dig, nslookup, whois  
**Data**: curl, openssl, nc, jq, exiftool  
**Wordlists**: /opt/SecLists (OWASP complete tree)  
**Total**: 40+ tools pre-installed

### Commands

| Command | Purpose |
|---------|---------|
| `/chat <msg>` | Send to AI (triggers auto-exec) |
| `/exec <cmd>` | Run bash directly |
| `/tools` | List installed tools |
| `/status` | Check tool install progress |
| `/auto-exec` | Toggle auto code execution |
| `/clear` | Clear chat history |
| `/help` | Show all commands |

---

## Installation

### Requirements

- Linux/Unix system (Ubuntu, Debian, CentOS, macOS, WSL)
- Python 3.8+
- ~2GB disk space (for tools)
- Sudo access (for tool installation)

### Setup

```bash
cd /app/backend
bash cli_run.sh
```

This will:
1. Create Python virtual environment
2. Install dependencies (rich, httpx, python-dotenv)
3. Generate `.env` template
4. Optionally launch Axiom

### Configuration

Edit `/app/backend/.env`:

**Option 1: Emergent Universal LLM (Free)**
```bash
EMERGENT_LLM_KEY=your_key_here
# Get key at: https://emergentintegrations.com
```

**Option 2: OpenAI or Compatible**
```bash
CUSTOM_LLM_BASE_URL=https://api.openai.com/v1
CUSTOM_LLM_API_KEY=sk-...
CUSTOM_LLM_MODEL=gpt-4
```

### Launch

```bash
python3 /app/backend/axiom_cli.py
```

---

## Examples

### Example 1: Reconnaissance

```
> /chat Perform recon on example.com

Axiom: I'll start with DNS enumeration...
[Auto-exec] nmap -F example.com

Axiom: Found open ports. Let me check services...
[Auto-exec] whatweb http://example.com

Axiom: Running Apache. Let me search for directories...
[Auto-exec] gobuster dir -u http://example.com -w /opt/SecLists/Discovery/Web-Content/common.txt

Axiom: Found /admin. Appears vulnerable to SQLi. Attempting exploitation...
```

### Example 2: Manual Command

```
> /exec sqlmap -u "http://target.com/page.php?id=1" --batch --dbs

[Output...]
Database: information_schema
Database: mysql
Database: webapp_db
```

### Example 3: Workflow

```
> /chat Check for Shellshock vulnerability on target.com

Axiom: Testing for Shellshock...
[Auto-exec] curl -H "User-Agent: () { :; }; echo vulnerable" http://target.com

Axiom: Vulnerable! Let me test command injection...
```

---

## Architecture

### Directory Structure

```
/app/
├── backend/                    # CLI application
│   ├── axiom_cli.py           # Main CLI app
│   ├── axiom_exec.py          # Code executor
│   ├── axiom_chat.py          # AI integration
│   ├── axiom_tools.py         # Tool management
│   ├── cli_run.sh             # Setup script
│   ├── install_tools.sh       # Tool installer
│   ├── requirements_cli.txt   # Python packages
│   ├── server.py              # FastAPI (reference)
│   └── .env                   # Configuration
│
├── docs/                       # Documentation
│   ├── QUICK_START.md         # 5-minute setup
│   ├── CLI_README.md          # Full reference
│   └── CONVERSION_SUMMARY.md  # Technical details
│
├── runtime_workspace/         # Execution space
│   └── run-*/                 # Per-execution dirs
│
├── memory/                    # Project documentation
├── README.md                  # This file
└── LICENSE
```

### Execution Flow

```
User Input
    ↓
CLI Parser
    ↓
    ├─ /chat → AI → Extract Code → Execute → Feed Back
    ├─ /exec → Direct Execution
    └─ /tools, /help, etc. → Display Info
```

---

## Documentation

- **[Quick Start](docs/QUICK_START.md)** — 5-minute setup guide
- **[CLI Reference](docs/CLI_README.md)** — Full command reference and examples  
- **[Technical Details](docs/CONVERSION_SUMMARY.md)** — Architecture and changes

---

## Security

⚠️ **Important**:

- Only test systems you own or have written authorization to penetrate test
- Penetration testing without permission is **illegal**
- Keep `.env` private (never commit to git)
- Tool output may contain sensitive data
- Run with appropriate privileges for your tools

```bash
# Most tools work without sudo, but nmap/masscan may need it
sudo python3 axiom_cli.py
```

---

## Key Differences from Web App

| Aspect | Web App | CLI |
|--------|---------|-----|
| Interface | React Native web | Terminal (rich) |
| Backend | Separate FastAPI server | Integrated |
| Execution | HTTP API | Direct async |
| Auth | Browser login | None (local) |
| Startup | Server + browser | Single command |
| Performance | Network overhead | Instant |

---

## Troubleshooting

### "No LLM configured"
Check `.env` has `EMERGENT_LLM_KEY=...` or custom OpenAI settings.

### Tools not installing
```bash
bash /app/backend/install_tools.sh
```

### Permission denied
```bash
sudo python3 /app/backend/axiom_cli.py
```

### "command not found"
Wait for background tool installation, or install manually:
```bash
sudo apt-get install -y nmap sqlmap nikto whatweb gobuster hydra john hashcat
```

---

## Performance

- **Startup**: 2-3 seconds
- **First run**: 5+ minutes (tool installation)
- **Chat response**: 5-30 seconds (provider dependent)
- **Code execution**: Instant to 120s (timeout)

---

## File Structure

```
backend/
├── axiom_cli.py              ← Main terminal app (450 lines)
├── axiom_exec.py             ← Execution engine (200 lines)
├── axiom_chat.py             ← AI integration (180 lines)
├── axiom_tools.py            ← Tool management (200 lines)
├── cli_run.sh                ← Setup script (executable)
├── install_tools.sh          ← Tool installer
├── requirements_cli.txt      ← Python packages
├── server.py                 ← FastAPI reference (optional)
├── .env                      ← Configuration
└── venv/                     ← Virtual environment
```

---

## License
  is used by chat, terminal and agents, so a green selftest = all three work.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND  (Expo / React-Native-Web — static export)        │
│  /app/frontend/                                             │
│  Served by /app/frontend/serve-dist.js on port 3000         │
│                                                             │
│   • Chat tab    → /api/chat        (SSE)                    │
│   • Terminal    → /api/exec                                 │
│   • Agents      → /api/functions/v1/axiom-agent + /api/exec │
│   • God Func    → /api/god         (SSE autonomous loop)    │
│   • Config      → /api/functions/v1/get-secrets, prompts    │
│   • Build       → embeds full source + AI rewrite artifact  │
│   • Login       → Supabase (OnSpace) OR god bypass          │
└───────────────────────────┬─────────────────────────────────┘
                            │ /api/* (k8s ingress)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND  (FastAPI + uvicorn)                               │
│  /app/backend/server.py    — port 8001                      │
│                                                             │
│   /api/health        runtime heartbeat                      │
│   /api/exec          execute code in container shell        │
│   /api/chat          SSE chat (Emergent or custom OpenAI)   │
│   /api/selftest      parallel 38-tool smoke test            │
│   /api/tools         which CLI tools are on PATH            │
│   /api/tools/install force-rerun the apt installer          │
│   /api/god           autonomous plan→exec→analyze (SSE)     │
│   /api/functions/v1/axiom-agent   structured agent planner  │
│   /api/functions/v1/axiom-attack  structured attack planner │
│   /api/functions/v1/axiom-chat    legacy chat alias         │
│   /api/functions/v1/code-exec     legacy exec alias         │
│   /api/functions/v1/get-secrets   real runtime config       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  RUNTIME  (this container's bash)                           │
│  /app/runtime_workspace/run-<uuid>/   per-execution scratch │
│                                                             │
│   nmap (wrapped: --unprivileged auto-injected)              │
│   sqlmap (wrapped: --batch auto-injected)                   │
│   ssh/scp/sftp (wrapped: BatchMode + accept-new)            │
│   ftp (wrapped: -n -p -v)                                   │
│   sudo (no-op — already root)                               │
│   + all standard pentest tooling                            │
│                                                             │
│  All wrappers + tools auto-installed at startup via         │
│  /app/backend/install_tools.sh (idempotent, flock-guarded). │
└─────────────────────────────────────────────────────────────┘
```

---

## Project layout

```
/app
├── README.md                 ← you are here
├── LICENSE
├── .gitignore
├── .emergent/                ← Emergent platform metadata
├── memory/
│   └── PRD.md                ← product requirements / decision log
│
├── backend/                  ← FastAPI runtime
│   ├── server.py             (~900 lines, all endpoints)
│   ├── install_tools.sh      (idempotent apt + SecLists installer)
│   ├── requirements.txt
│   └── .env                  (MONGO_URL, EMERGENT_LLM_KEY, DB_NAME, …)
│
└── frontend/                 ← Expo / React-Native-Web
    ├── app/                  (expo-router screens)
    │   ├── login.tsx
    │   ├── _layout.tsx
    │   ├── profile.tsx
    │   └── (tabs)/
    │       ├── _layout.tsx
    │       ├── index.tsx        ← Chat
    │       ├── terminal.tsx     ← Terminal
    │       ├── agents.tsx       ← Agent runner
    │       ├── ops.tsx          ← Saved attacks / ops
    │       ├── intel.tsx        ← MITRE intel + playbooks
    │       ├── files.tsx        ← Files browser
    │       ├── config.tsx       ← Settings + GOD MODE toggle
    │       └── build.tsx        ← Source export + AI rewrite artifact
    │
    ├── components/
    │   ├── build/ArtifactRewritePanel.tsx
    │   ├── chat/                 (MessageBubble, TTPTracker, …)
    │   └── ui/
    │
    ├── services/                 (business logic)
    │   ├── aiService.ts          (chat streaming, custom provider, god mode)
    │   ├── autoExec.ts           (code-block extraction + /api/exec wrapper)
    │   ├── godUser.ts            (login bypass + god mode flag)
    │   ├── selfUpdateService.ts  (system prompt, KB, custom AI provider)
    │   ├── sessionStorage.ts
    │   ├── executionLog.ts
    │   └── attackStorage.ts
    │
    ├── hooks/                    (useChat, useChatContext)
    ├── contexts/                 (ChatContext)
    ├── constants/                (theme, mitre, prompts)
    ├── template/                 (auth + UI primitives)
    ├── serve-dist.js             (tiny static server for the built dist)
    ├── app.json
    ├── package.json
    ├── tsconfig.json
    ├── babel.config.js
    └── .env                      (EXPO_PUBLIC_* runtime URLs + Supabase)
```

---

## Setup

### Prereqs
- Linux container (the runtime expects `/usr/bin`, `apt-get`, `bash`).
- Python 3.11+
- Node 20+ and `yarn`
- (Optional) MongoDB if you want execution-log persistence beyond AsyncStorage.

### 1 — Backend
```bash
cd backend
pip install -r requirements.txt
# Edit backend/.env if you want a different LLM key / model
bash install_tools.sh                    # installs the full red-team tool surface
uvicorn server:app --host 0.0.0.0 --port 8001
```

The first request to `/api/exec` or `/api/selftest` will trigger
`install_tools.sh` automatically if any tool is missing (idempotent + locked
so reload children don't race).

### 2 — Frontend
```bash
cd frontend
yarn install
# Edit frontend/.env — set EXPO_PUBLIC_AXIOM_RUNTIME_URL to point at your backend.
CI=true yarn build:web                   # exports to ./dist
node serve-dist.js                       # serves dist on :3000
```

Or, for dev mode with hot-reload (requires high inotify limits):
```bash
yarn expo-start --web --port 3000
```

### 3 — Open the app
- http://localhost:3000
- Login screen will appear. Either:
  - Use your OnSpace Supabase account, **or**
  - Type any email + password `AXIOM-ASCEND-OMNIPOTENT-1337` to enter as the
    god user (no Supabase round-trip).

---

## Verification

Hit the self-test endpoint to confirm everything is green:

```bash
curl -s http://localhost:8001/api/selftest | python3 -m json.tool
```

Expected:
```json
{
  "summary": {"total": 38, "passed": 38, "failed": 0, "pass_rate": 100.0},
  "results": [
    {"tool": "nmap", "ok": true, "exitCode": 0, "durationMs": 73, …},
    {"tool": "sqlmap", "ok": true, "exitCode": 0, "durationMs": 412, …},
    …
  ]
}
```

A real end-to-end test:
```bash
curl -s -X POST http://localhost:8001/api/exec \
  -H 'Content-Type: application/json' \
  -d '{"language":"bash","code":"nmap -F scanme.nmap.org","timeout":30}' \
  | python3 -m json.tool
```

Should return real port-scan output for 22/ssh and 80/http.

---

## Environment variables

### Backend (`backend/.env`)
| Var | Purpose | Default |
|---|---|---|
| `MONGO_URL` | Mongo connection string (optional, for future persistence) | `mongodb://localhost:27017` |
| `DB_NAME` | Mongo DB name | `axiom_redteam` |
| `EMERGENT_LLM_KEY` | Universal LLM key for Emergent-managed calls | provided |
| `DEFAULT_LLM_PROVIDER` | Default emergent integration provider | `anthropic` |
| `DEFAULT_LLM_MODEL` | Default LLM model id | `claude-sonnet-4-5-20250929` |
| `EXEC_TIMEOUT_SECONDS` | Default `/api/exec` timeout | `120` |

### Frontend (`frontend/.env`)
| Var | Purpose |
|---|---|
| `EXPO_PUBLIC_AXIOM_RUNTIME_URL` | URL of the FastAPI backend (this is the runtime!) |
| `EXPO_PUBLIC_SUPABASE_URL` | OnSpace Supabase URL (login only) |
| `EXPO_PUBLIC_SUPABASE_ANON_KEY` | OnSpace Supabase anon JWT |

---

## Tools installed at runtime

`install_tools.sh` (idempotent) installs everything below on every backend
boot, because Kubernetes containers have ephemeral `/usr` between restarts.

**Network / recon:** nmap, masscan, nikto, whatweb, sqlmap, gobuster, dirb,
wfuzz, dig, whois, nc, ncat, traceroute, curl, wget, openssl, jq

**Auth / passwords:** hydra, john, hashcat (+ 14.3M-line rockyou.txt
extracted from SecLists)

**Service clients:** smbclient, enum4linux, ldap-utils, snmp, ftp,
telnet, openssh-client

**Wordlists:** Debian `dirb/common.txt`, full SecLists tree at
`/opt/SecLists/` (symlinked into `/usr/share/wordlists/seclists/`),
metasploit-style users + passwords lists.

**Languages:** python3 + requests + bs4 + dnspython, node, go, ruby, perl

**Utilities:** unzip, zip, tree, file, binutils, xxd, exiftool, sudo

**Wrappers (in `/usr/local/bin/`):**
- `nmap` → auto-injects `--unprivileged` (raw sockets are blocked in
  the container)
- `sqlmap` → auto-injects `--batch` (never blocks on prompts)
- `ssh`/`scp`/`sftp` → `BatchMode=yes`, `StrictHostKeyChecking=accept-new`
- `ftp` → `-n -p -v`

---

## Legal / ethics

This is an offensive-security tool. Authorized use only. Every command
the runtime executes leaves logs in your own container. You are
responsible for ensuring you have written permission to test every
target you point this at. The God-Mode prompt assumes operator
authorization is established by the act of toggling god mode — meaning
**you** confirm authorization, not the AI.

Don't be the reason someone gets a `403`.

---

## License

MIT. See [LICENSE](LICENSE).
