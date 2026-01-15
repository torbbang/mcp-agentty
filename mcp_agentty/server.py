import asyncio
import os
from fastmcp import FastMCP
from typing import Optional, List
from .session import SessionManager

# Initialize FastMCP server and Session Manager
mcp = FastMCP("AgenTTY")
session_manager = SessionManager()

@mcp.tool()
async def start_shell(shell: Optional[str] = None) -> str:
    """
    Starts a local shell session.
    Defaults to the SHELL environment variable, or /bin/bash if not set.
    """
    if shell is None:
        shell = os.environ.get("SHELL", "/bin/bash")

    try:
        sid = await asyncio.to_thread(session_manager.create_session, shell)
        return f"Shell session started. ID: {sid}"
    except Exception as e:
        return f"Error starting shell: {str(e)}"

@mcp.tool()
async def start_ssh(host: str, user: Optional[str] = None, port: int = 22) -> str:
    """
    Starts an SSH session.
    Returns the session ID.
    """
    args = []
    if port != 22:
        args.extend(["-p", str(port)])
    
    target = host
    if user:
        target = f"{user}@{host}"
    args.append(target)

    try:
        sid = await asyncio.to_thread(session_manager.create_session, "ssh", args)
        return f"SSH session started for {target}. ID: {sid}"
    except Exception as e:
        return f"Error starting SSH: {str(e)}"

@mcp.tool()
async def start_telnet(host: str, port: int = 23) -> str:
    """
    Starts a Telnet session.
    Returns the session ID.
    """
    try:
        sid = await asyncio.to_thread(session_manager.create_session, "telnet", [host, str(port)])
        return f"Telnet session started for {host}:{port}. ID: {sid}"
    except Exception as e:
        return f"Error starting Telnet: {str(e)}"

@mcp.tool()
async def send_command(session_id: str, command: str, add_newline: bool = True) -> str:
    """
    Sends a text command to a specific session.
    Set add_newline to False if you want to send raw text/keypresses without hitting Enter.
    """
    session = session_manager.get_session(session_id)
    if not session:
        return "Error: Session not found or inactive."
    
    try:
        text_to_send = command + ("\n" if add_newline else "")
        await asyncio.to_thread(session.write, text_to_send)
        return "Command sent."
    except Exception as e:
        return f"Error writing to session: {str(e)}"

@mcp.tool()
async def read_output(session_id: str, strip_ansi: bool = True, max_bytes: int = 100000) -> str:
    """
    Reads available output from a session.
    Defaults to stripping ANSI escape codes.
    max_bytes: Limits the response size (default 100k). Truncates from the beginning if exceeded.
    """
    session = session_manager.get_session(session_id)
    if not session:
        return "Error: Session not found or inactive."
    
    try:
        return await asyncio.to_thread(session.read, strip_ansi, max_bytes)
    except Exception as e:
        return f"Error reading from session: {str(e)}"

@mcp.tool()
async def list_sessions() -> str:
    """
    Lists all active session IDs and their commands.
    """
    # This is fast/in-memory, but good practice to thread if we add complex checks later
    sessions = await asyncio.to_thread(session_manager.list_sessions)
    if not sessions:
        return "No active sessions."
    
    report = "Active Sessions:\n"
    for sid, cmd in sessions.items():
        report += f"- [{sid}]: {cmd}\n"
    return report

@mcp.tool()
async def kill_session(session_id: str) -> str:
    """
    Terminates a specific session.
    """
    success = await asyncio.to_thread(session_manager.close_session, session_id)
    if success:
        return f"Session {session_id} closed."
    return "Error: Session not found."

def main():
    mcp.run()

if __name__ == "__main__":
    main()
