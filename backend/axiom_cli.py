#!/usr/bin/env python3
"""
Axiom Red-Team CLI
Terminal-based AI red-team operator with direct shell access.
"""

import asyncio
import re
import os
import sys
import json
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.markdown import Markdown
from rich.align import Align
from rich.syntax import Syntax

# Import our modules
from axiom_exec import execute_bash, execute_code
from axiom_chat import chat_with_ai, extract_code_blocks, format_message
from axiom_tools import install_tools_blocking, check_tool_status, get_tools_info

console = Console()

# Chat history
chat_history: List[dict] = []
auto_exec_enabled = True
auto_exec_count = 0
MAX_AUTO_EXEC = 3


def display_banner():
    """Display Axiom banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                  AXIOM RED-TEAM CLI                   ║
    ║                                                       ║
    ║    Autonomous AI-powered penetration testing         ║
    ║    Direct shell access • Real-time tool execution    ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="cyan bold")


def display_help():
    """Display help information."""
    help_text = """
[bold cyan]Commands:[/bold cyan]
  /help          - Show this help
  /tools         - List installed tools
  /exec <cmd>    - Execute bash command
  /chat <msg>    - Send message to AI
  /auto-exec     - Toggle auto-execution of AI code blocks
  /clear         - Clear chat history
  /status        - Show tool installation status
  /quit          - Exit Axiom

[bold cyan]Examples:[/bold cyan]
  /chat Scan scanme.nmap.org
  /exec nmap -F scanme.nmap.org
  /auto-exec

[bold cyan]Tips:[/bold cyan]
  • AI automatically executes code blocks when auto-exec is enabled
  • Chat maintains context across multiple turns
  • Tool output is fed back to AI for analysis
    """
    console.print(Panel(help_text, title="[bold]Axiom Commands[/bold]", expand=False))


async def display_tools():
    """Display installed tools."""
    tools = get_tools_info()
    
    table = Table(title="Red-Team Tools", show_header=True, header_style="bold magenta")
    table.add_column("Tool", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Description")
    
    for tool, info in sorted(tools.items()):
        status = "✓ Ready" if info["installed"] else "✗ Missing"
        status_style = "green" if info["installed"] else "red"
        table.add_row(tool, Text(status, style=status_style), info["description"])
    
    console.print(table)


async def display_status():
    """Display installation status."""
    console.print("\n[bold cyan]Tool Installation Status[/bold cyan]")
    status = check_tool_status()
    installed = sum(1 for v in status.values() if v)
    total = len(status)
    
    progress_bar = "█" * installed + "░" * (total - installed)
    console.print(f"Progress: [{progress_bar}] {installed}/{total}")
    
    if installed < total:
        missing = [tool for tool, ready in status.items() if not ready]
        console.print(f"\n[yellow]Missing: {', '.join(missing)}[/yellow]")
    else:
        console.print("\n[green]All tools installed![/green]")


async def execute_command(command: str) -> str:
    """Execute a bash command."""
    try:
        result = await execute_bash(command, timeout=120)
        return result.get("output", "No output")
    except Exception as e:
        return f"[ERROR] {str(e)}"


async def chat_turn(user_message: str) -> None:
    """Send message to AI and get response."""
    global auto_exec_count, auto_exec_enabled
    
    # Add user message to history
    chat_history.append(format_message("user", user_message))
    
    console.print(f"\n[bold blue]You:[/bold blue] {user_message}\n")
    
    # Get AI response
    console.print("[bold green]Axiom:[/bold green] ", end="", flush=True)
    
    full_response = ""
    try:
        async for chunk in chat_with_ai(chat_history):
            console.print(chunk, end="", flush=True)
            full_response += chunk
    except Exception as e:
        console.print(f"\n[red][ERROR] {str(e)}[/red]")
        return
    
    console.print("\n")
    
    # Add assistant message to history
    chat_history.append(format_message("assistant", full_response))
    
    # Auto-execute code blocks if enabled
    if auto_exec_enabled:
        await auto_exec_blocks(full_response)


async def auto_exec_blocks(response: str) -> None:
    """Extract and execute code blocks from AI response."""
    global auto_exec_count
    
    if auto_exec_count >= MAX_AUTO_EXEC:
        console.print("[yellow]Auto-exec limit reached (3 hops per turn)[/yellow]\n")
        return
    
    blocks = extract_code_blocks(response)
    if not blocks:
        return
    
    for lang, code in blocks:
        auto_exec_count += 1
        console.print(f"\n[bold magenta]Auto-executing ({lang})[/bold magenta]")
        
        try:
            result = await execute_code(lang, code, timeout=120)
            output = result.get("output", "No output")
            
            # Display execution result
            if result.get("success"):
                console.print(f"[green][✓ Success][/green]\n{output}\n")
            else:
                console.print(f"[red][✗ Failed][/red]\n{output}\n")
            
            # Add to chat history so AI can analyze
            chat_history.append(format_message("user", f"[Auto-exec result]\n```\n{output}\n```"))
        except Exception as e:
            console.print(f"[red][ERROR] {str(e)}[/red]\n")


async def main():
    """Main CLI loop."""
    # Install tools in background
    console.print("[cyan]Installing tools...[/cyan]")
    total, installed = install_tools_blocking()
    console.print(f"[green]Tools ready: {installed}/{total}[/green]\n")
    
    display_banner()
    console.print("Type [bold]/help[/bold] for commands or start chatting.\n")
    
    # Main loop
    while True:
        try:
            # Get user input
            user_input = console.input("[bold cyan]>[/bold cyan] ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                args = cmd_parts[1] if len(cmd_parts) > 1 else ""
                
                if cmd == "/help":
                    display_help()
                elif cmd == "/tools":
                    await display_tools()
                elif cmd == "/status":
                    await display_status()
                elif cmd == "/auto-exec":
                    auto_exec_enabled = not auto_exec_enabled
                    status = "enabled" if auto_exec_enabled else "disabled"
                    console.print(f"[cyan]Auto-exec {status}[/cyan]\n")
                elif cmd == "/exec" and args:
                    console.print(f"\n[bold magenta]Executing:[/bold magenta] {args}\n")
                    output = await execute_command(args)
                    console.print(output + "\n")
                elif cmd == "/chat" and args:
                    auto_exec_count = 0
                    await chat_turn(args)
                elif cmd == "/clear":
                    chat_history.clear()
                    console.print("[cyan]Chat history cleared[/cyan]\n")
                elif cmd == "/quit" or cmd == "/exit":
                    console.print("[bold yellow]Exiting Axiom...[/bold yellow]")
                    break
                else:
                    console.print("[red]Unknown command. Type /help for available commands.[/red]\n")
            else:
                # Regular chat
                auto_exec_count = 0
                await chat_turn(user_input)
                
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Exiting Axiom...[/bold yellow]")
            break
        except Exception as e:
            console.print(f"[red][ERROR] {str(e)}[/red]\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        console.print("\n[cyan]Goodbye![/cyan]")
