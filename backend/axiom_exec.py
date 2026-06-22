"""
Axiom Red-Team Command Execution Module
Handles bash/code execution with timeout, signal handling, and output capture.
"""

import asyncio
import os
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
import signal


# Working directory for executions
WORK_DIR = Path("/app/runtime_workspace")
WORK_DIR.mkdir(parents=True, exist_ok=True)

# Language -> (command template, file extension, optional compile step)
LANG_RUNNERS = {
    "bash": {"file": "script.sh", "run": ["bash", "{file}"]},
    "sh": {"file": "script.sh", "run": ["sh", "{file}"]},
    "python": {"file": "main.py", "run": ["python3", "{file}"]},
    "python3": {"file": "main.py", "run": ["python3", "{file}"]},
    "javascript": {"file": "main.js", "run": ["node", "{file}"]},
    "node": {"file": "main.js", "run": ["node", "{file}"]},
    "go": {"file": "main.go", "run": ["go", "run", "{file}"]},
    "ruby": {"file": "main.rb", "run": ["ruby", "{file}"]},
    "php": {"file": "main.php", "run": ["php", "{file}"]},
    "perl": {"file": "main.pl", "run": ["perl", "{file}"]},
    "lua": {"file": "main.lua", "run": ["lua", "{file}"]},
}

# Base environment for all executions
_BASE_EXEC_ENV = {
    **os.environ,
    "TERM": "xterm-256color",
    "HOME": "/root",
    "USER": "root",
    "LOGNAME": "root",
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "DEBIAN_FRONTEND": "noninteractive",
    "PYTHONUNBUFFERED": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/SecLists/bin",
    "PAGER": "cat",
    "NO_COLOR": "1",
}


async def _run(
    cmd: list, cwd: Path, stdin_data: Optional[str], timeout: int
) -> Dict[str, Any]:
    """Run a subprocess, capture stdout/stderr/exit code/duration."""
    t0 = time.time()
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if stdin_data else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd),
            env=_BASE_EXEC_ENV,
            start_new_session=True,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(
                    input=stdin_data.encode() if stdin_data else None
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            # Kill process group
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                proc.kill()
            try:
                await proc.wait()
            except Exception:
                pass
            return {
                "stdout": "",
                "stderr": f"[TIMEOUT] Command exceeded {timeout}s and was killed.",
                "exitCode": 124,
                "signal": "SIGKILL",
                "durationMs": int((time.time() - t0) * 1000),
            }
        return {
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
            "exitCode": proc.returncode,
            "signal": None,
            "durationMs": int((time.time() - t0) * 1000),
        }
    except FileNotFoundError as e:
        return {
            "stdout": "",
            "stderr": f"[ERROR] Runtime not installed: {e}",
            "exitCode": 127,
            "signal": None,
            "durationMs": int((time.time() - t0) * 1000),
        }


def _build_output(parts: Dict[str, Any]) -> str:
    """Format execution output."""
    out = []
    if parts.get("compileStderr"):
        out.append(f"[COMPILE ERROR]\n{parts['compileStderr'].strip()}")
    if parts.get("compileStdout"):
        out.append(f"[COMPILE]\n{parts['compileStdout'].strip()}")
    if parts.get("stdout"):
        out.append(parts["stdout"].rstrip())
    if parts.get("stderr") and (parts.get("exitCode") != 0 or not parts.get("stdout")):
        out.append(f"[STDERR]\n{parts['stderr'].strip()}")
    if parts.get("signal"):
        out.append(f"[KILLED] Signal: {parts['signal']}")
    elif parts.get("exitCode") not in (0, None):
        out.append(f"[EXIT {parts['exitCode']}]")
    return "\n".join(out)


async def execute_code(
    language: str, code: str, stdin: Optional[str] = None, timeout: int = 120
) -> Dict[str, Any]:
    """Execute code/shell command and return result."""
    lang = (language or "bash").lower().strip()
    runner = LANG_RUNNERS.get(lang)

    if not runner:
        return {
            "success": False,
            "error": f"Unsupported language: {language}",
            "output": f"[ERROR] Unsupported language: {language}",
            "exitCode": 2,
        }

    # Create per-execution dir
    run_dir = WORK_DIR / f"run-{uuid.uuid4().hex[:8]}"
    run_dir.mkdir(parents=True, exist_ok=True)

    try:
        file_path = run_dir / runner["file"]
        file_path.write_text(code)

        rcmd = [c.format(file=str(file_path)) for c in runner["run"]]
        rres = await _run(rcmd, run_dir, stdin, timeout)

        output = _build_output(rres)
        return {
            "success": rres["exitCode"] == 0,
            "language": lang,
            "stdout": rres["stdout"],
            "stderr": rres["stderr"],
            "exitCode": rres["exitCode"],
            "signal": rres.get("signal"),
            "durationMs": rres["durationMs"],
            "output": output,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output": f"[ERROR] {str(e)}",
            "exitCode": 1,
        }


async def execute_bash(command: str, timeout: int = 120) -> Dict[str, Any]:
    """Execute a bash command directly."""
    return await execute_code("bash", command, timeout=timeout)
