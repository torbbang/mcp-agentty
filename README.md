> [!IMPORTANT]
> ## 🚚 This project has moved to [git.torbjorn.dev](https://git.torbjorn.dev/torbbang/mcp-agentty)
> This GitHub repository is archived and no longer maintained.

---

# AgenTTY (mcp-agentty)

An MCP server that exposes a TTY client. It allows you to run local shells, SSH, and Telnet sessions through MCP tools.

> [!WARNING]
> **DISCLAIMER:** This MCP server provides direct terminal and shell access with **no built-in guardrails**. It is intended for **experimental and local development use only**. Granting an LLM or remote agent access to this server allows it to execute arbitrary commands, modify files, and access remote systems as the user running the server. Use with extreme caution and never expose it to untrusted environments.

## LLM Usage Guide

When an agent interacts with AgenTTY, it should follow this typical loop:

1.  **Initialize**: Call `start_shell()` to get a `session_id`.
2.  **Observe**: Call `read_output(session_id)` to see the initial prompt or welcome message.
3.  **Act**: Call `send_command(session_id, "your command here")`.
4.  **Wait & Read**: Call `read_output(session_id)` again to see the result.
5.  **Repeat**: Continue the send/read loop until the task is complete.

### Example Interaction Flow

- **Agent**: `start_shell()` -> "Shell session started. ID: `1234-abcd`"
- **Agent**: `read_output("1234-abcd")` -> "agent@mcp-agentty:~$ "
- **Agent**: `send_command("1234-abcd", "ip addr")` -> "Command sent."
- **Agent**: `read_output("1234-abcd")` -> "1: lo: ... 2: eth0: ..."

### Benchmarking Advantages

The provided Docker container includes a rich set of pre-installed tools (`git`, `jq`, `curl`, `vim`, `ping`, `sudo`, etc.). An agent can:
- **Debug Networks**: Use `dig`, `traceroute`, or `nc` to test connectivity.
- **Process Data**: Pipe complex output into `jq` or `grep`.
- **Self-Heal**: If a tool is missing, the agent has `sudo` access to `apt-get install` it.

## Features

- **Concurrent Sessions**: Manage multiple terminal sessions simultaneously.
- **Local Shell**: Start `/bin/bash` or any other local shell.
- **SSH/Telnet**: Connect to remote hosts using system-available clients.
- **PTY Powered**: Uses `pexpect` to handle pseudo-terminals, ensuring interactive commands work correctly.

## Installation

```bash
uv pip install .
```

## Tools

- `start_shell(shell="/bin/bash")`: Start a local shell.
- `start_ssh(host, user=None, port=22)`: Start an SSH session.
- `start_telnet(host, port=23)`: Start a Telnet session.
- `send_command(session_id, command, add_newline=True)`: Send text to a session.
- `read_output(session_id)`: Read available output from a session.
- `list_sessions()`: List active sessions.
- `kill_session(session_id)`: Terminate a session.