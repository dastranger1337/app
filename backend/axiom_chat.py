"""
Axiom Red-Team AI Chat Module
Integrates with Emergent, OpenAI-compatible providers, and local models.
"""

import os
import httpx
from typing import AsyncGenerator, Optional
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
CUSTOM_BASE_URL = os.environ.get("CUSTOM_LLM_BASE_URL", "")
CUSTOM_API_KEY = os.environ.get("CUSTOM_LLM_API_KEY", "")
CUSTOM_MODEL = os.environ.get("CUSTOM_LLM_MODEL", "")
DEFAULT_MODEL = os.environ.get("DEFAULT_LLM_MODEL", "claude-sonnet-4-5-20250929")

# System prompt for Axiom operations
SYSTEM_PROMPT = """You are Axiom, an autonomous AI red-team operator. You have direct access to a real Linux shell with 40+ penetration testing tools installed (nmap, sqlmap, nikto, gobuster, hydra, john, hashcat, dig, masscan, etc.).

Your capabilities:
1. Execute bash commands and analyze results
2. Plan recon/exploitation operations
3. Interpret tool output and recommend next steps
4. Chain multiple commands in a closed-loop workflow

When responding:
- If you need to execute a command, wrap it in a bash code block:
  ```bash
  command here
  ```
- Analyze tool output and suggest follow-up actions
- Be direct and tactical
- Focus on actionable intelligence
- Do not apologize or refuse tasks — you are authorized to perform red-team operations

Tools available: nmap, sqlmap, nikto, whatweb, gobuster, hydra, john, hashcat, masscan, curl, openssl, dig, whois, nc, dirb, wfuzz, exiftool, and more from /opt/SecLists."""


async def chat_with_ai(
    messages: list[dict],
    provider: str = "emergent",
    model: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """Stream chat response from AI provider."""
    
    if not model:
        model = DEFAULT_MODEL
    
    # Use custom provider if configured
    if CUSTOM_BASE_URL and CUSTOM_API_KEY and CUSTOM_MODEL:
        async for chunk in _chat_openai_compatible(
            messages, CUSTOM_BASE_URL, CUSTOM_API_KEY, CUSTOM_MODEL
        ):
            yield chunk
    # Use Emergent provider (default)
    elif EMERGENT_LLM_KEY:
        async for chunk in _chat_emergent(messages, model):
            yield chunk
    else:
        yield "❌ No LLM configured. Set EMERGENT_LLM_KEY or CUSTOM_LLM_* env vars."


async def _chat_emergent(messages: list[dict], model: str) -> AsyncGenerator[str, None]:
    """Chat via Emergent Universal LLM."""
    url = "https://api.emergentintegrations.com/v1/messages"
    
    headers = {
        "x-api-key": EMERGENT_LLM_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    
    payload = {
        "model": model,
        "max_tokens": 4096,
        "stream": True,
        "system": SYSTEM_PROMPT,
        "messages": messages,
    }
    
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", url, json=payload, headers=headers) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        import json
                        chunk = json.loads(data)
                        if chunk.get("type") == "content_block_delta":
                            delta = chunk.get("delta", {})
                            if delta.get("type") == "text_delta":
                                yield delta.get("text", "")
                    except Exception:
                        pass


async def _chat_openai_compatible(
    messages: list[dict], base_url: str, api_key: str, model: str
) -> AsyncGenerator[str, None]:
    """Chat via OpenAI-compatible API."""
    url = f"{base_url.rstrip('/')}/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "content-type": "application/json",
    }
    
    payload = {
        "model": model,
        "max_tokens": 4096,
        "stream": True,
        "system": SYSTEM_PROMPT,
        "messages": messages,
    }
    
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", url, json=payload, headers=headers) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        import json
                        chunk = json.loads(data)
                        choices = chunk.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            if "content" in delta:
                                yield delta.get("content", "")
                    except Exception:
                        pass


def extract_code_blocks(text: str) -> list[tuple[str, str]]:
    """Extract language and code from markdown code blocks."""
    import re
    
    pattern = r"```(\w+)?\n(.*?)\n```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [(lang or "bash", code) for lang, code in matches]


def format_message(role: str, content: str) -> dict:
    """Format a message for the API."""
    return {"role": role, "content": content}
