# Axiom Red-Team CLI Documentation

## Getting Started

1. **[Quick Start](QUICK_START.md)** (5 minutes)
   - Installation
   - Configuration
   - First commands
   - Troubleshooting

2. **[Full Reference](REFERENCE.md)** (Complete guide)
   - All commands
   - Configuration options
   - Advanced usage
   - API reference

## Technical

- **[Conversion Summary](CONVERSION_SUMMARY.md)** — What changed from web app to CLI
  - Architecture differences
  - File structure
  - Performance notes

## Quick Reference

### Setup
```bash
cd /app/backend
bash cli_run.sh
```

### Commands
```
/chat <message>      — Chat with AI (auto-executes code)
/exec <command>      — Execute bash directly
/tools              — List installed tools
/status             — Check tool status
/auto-exec          — Toggle auto-execution
/help               — Show help
/quit               — Exit
```

### Configuration
Edit `/app/backend/.env`:
```bash
EMERGENT_LLM_KEY=your_key
# or
CUSTOM_LLM_BASE_URL=https://api.openai.com/v1
CUSTOM_LLM_API_KEY=your_key
CUSTOM_LLM_MODEL=gpt-4
```

## Example Workflows

### Reconnaissance
```
> /chat Scan target.com for open ports
[AI plans and executes nmap]
> /chat Check for web vulnerabilities
[AI runs whatweb, sqlmap, etc.]
```

### Manual Execution
```
> /exec gobuster dir -u http://target.com -w /opt/SecLists/Discovery/Web-Content/common.txt
> /exec hydra -l admin -P /opt/SecLists/Passwords/top-100.txt ssh://target.com
```

## File Structure

```
/app/
├── backend/
│   ├── axiom_cli.py           Main terminal app
│   ├── axiom_exec.py          Code execution
│   ├── axiom_chat.py          AI integration
│   ├── axiom_tools.py         Tool management
│   ├── cli_run.sh             Setup script
│   ├── install_tools.sh       Tool installer
│   └── requirements_cli.txt   Python packages
├── docs/                      Documentation
├── runtime_workspace/         Execution space
└── README.md                  Main readme
```

## Tools Available

40+ penetration testing tools including:
- **Network**: nmap, masscan, traceroute, dig, whois
- **Web**: nikto, whatweb, gobuster, sqlmap, wfuzz, dirb
- **Creds**: hydra, john, hashcat
- **Data**: curl, openssl, jq, exiftool

Full list in `/status` command or [REFERENCE.md](REFERENCE.md).

## Support

- Check `.env` configuration for API keys
- Run `/status` to verify tool installation
- See QUICK_START.md for common issues
- See REFERENCE.md for full command documentation
