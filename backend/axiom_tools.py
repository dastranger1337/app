"""
Axiom Red-Team Tool Management
Handles installation and verification of penetration testing tools.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


# Tools to install on startup
TOOLS_TO_INSTALL = {
    "nmap": {"apt": "nmap", "desc": "Network mapper for port scanning"},
    "nikto": {"apt": None, "desc": "Web server scanner"},
    "whatweb": {"apt": "whatweb", "desc": "Web technology fingerprinter"},
    "sqlmap": {"apt": "sqlmap", "desc": "SQL injection testing tool"},
    "gobuster": {"apt": "gobuster", "desc": "URI brute-forcing tool"},
    "hydra": {"apt": "hydra", "desc": "Credential brute-force tool"},
    "john": {"apt": "john", "desc": "Password cracker"},
    "hashcat": {"apt": "hashcat", "desc": "Advanced hash cracker"},
    "dig": {"apt": "dnsutils", "desc": "DNS lookup tool"},
    "whois": {"apt": "whois", "desc": "WHOIS lookup tool"},
    "nc": {"apt": "netcat", "desc": "Network utility"},
    "traceroute": {"apt": "traceroute", "desc": "Network path tracer"},
    "jq": {"apt": "jq", "desc": "JSON processor"},
    "openssl": {"apt": "openssl", "desc": "SSL/TLS utilities"},
    "dirb": {"apt": "dirb", "desc": "Directory brute-forcer"},
    "wfuzz": {"apt": "wfuzz", "desc": "Web fuzzer"},
    "exiftool": {"apt": "libimage-exiftool-perl", "desc": "EXIF data extractor"},
    "curl": {"apt": "curl", "desc": "HTTP client"},
    "masscan": {"apt": "masscan", "desc": "Fast port scanner"},
    "smbclient": {"apt": "samba-client", "desc": "SMB protocol client"},
}

INSTALL_LOCK = "/tmp/axiom-install.lock"
INSTALL_DONE = "/tmp/axiom-install.done"


def is_installed(tool: str) -> bool:
    """Check if a tool is installed."""
    return shutil.which(tool) is not None


def check_tool_status() -> Dict[str, bool]:
    """Get status of all tools."""
    return {tool: is_installed(tool) for tool in TOOLS_TO_INSTALL.keys()}


def install_tools_blocking() -> Tuple[int, int]:
    """Install all tools synchronously. Returns (total, installed)."""
    import os
    import threading
    import fcntl
    import time
    
    # Check if already done
    if Path(INSTALL_DONE).exists():
        installed = sum(1 for tool in TOOLS_TO_INSTALL if is_installed(tool))
        return len(TOOLS_TO_INSTALL), installed
    
    # Try to acquire lock
    try:
        lock_fd = open(INSTALL_LOCK, "w")
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            # Another process is installing, wait
            for _ in range(180):
                if Path(INSTALL_DONE).exists():
                    installed = sum(1 for tool in TOOLS_TO_INSTALL if is_installed(tool))
                    return len(TOOLS_TO_INSTALL), installed
                time.sleep(1)
            lock_fd = None
    except Exception:
        lock_fd = None
    
    try:
        # Update package list
        subprocess.run(
            ["apt-get", "update"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=120,
        )
        
        # Install each tool
        for tool, info in TOOLS_TO_INSTALL.items():
            if info["apt"]:
                subprocess.run(
                    ["apt-get", "install", "-y", info["apt"]],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                    timeout=120,
                )
        
        # Special: install nikto from GitHub if not already present
        if not is_installed("nikto"):
            subprocess.run(
                [
                    "git",
                    "clone",
                    "https://github.com/sullo/nikto.git",
                    "/opt/nikto",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=60,
            )
            nikto_script = Path("/opt/nikto/nikto.pl")
            if nikto_script.exists():
                subprocess.run(
                    ["ln", "-sf", str(nikto_script), "/usr/local/bin/nikto"],
                    check=False,
                )
        
        # Create nmap wrapper to auto-inject --unprivileged
        nmap_wrapper = Path("/usr/local/bin/nmap-unprivileged")
        nmap_wrapper.write_text(
            "#!/bin/bash\n/usr/bin/nmap --unprivileged \"$@\"\n"
        )
        nmap_wrapper.chmod(0o755)
        
        # Mark as done
        Path(INSTALL_DONE).touch()
        
        installed = sum(1 for tool in TOOLS_TO_INSTALL if is_installed(tool))
        return len(TOOLS_TO_INSTALL), installed
        
    except Exception as e:
        print(f"Error installing tools: {e}")
        return len(TOOLS_TO_INSTALL), sum(1 for tool in TOOLS_TO_INSTALL if is_installed(tool))
    finally:
        if lock_fd is not None:
            try:
                import fcntl
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
                lock_fd.close()
            except Exception:
                pass


def get_tools_info() -> Dict[str, Dict]:
    """Get detailed tool information."""
    return {
        tool: {
            "description": info["desc"],
            "installed": is_installed(tool),
        }
        for tool, info in TOOLS_TO_INSTALL.items()
    }
