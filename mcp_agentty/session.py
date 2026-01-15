import pexpect
import uuid
import logging
import re
import atexit
from typing import Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ANSI escape code regex
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

class Session:
    def __init__(self, command: str, args: list[str] = None):
        self.id = str(uuid.uuid4())
        self.command = command
        self.args = args or []
        self.process: Optional[pexpect.spawn] = None
        self.buffer = ""

    def start(self):
        try:
            # encoding='utf-8' ensures we send/receive strings
            # dimensions: reasonable default for a terminal
            self.process = pexpect.spawn(self.command, self.args, encoding='utf-8', dimensions=(24, 80))
            logger.info(f"Started session {self.id}: {self.command} {' '.join(self.args)}")
            return self.id
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            raise

    def write(self, data: str):
        if not self.process or not self.process.isalive():
            raise RuntimeError("Session is not active")
        self.process.send(data)

    def read(self, strip_ansi: bool = True, max_bytes: int = 100000) -> str:
        """
        Reads available output. 
        max_bytes: Maximum number of bytes to return. If output is larger, it will be truncated.
        """
        if not self.process:
            return ""
        
        output = ""
        try:
            # Read available data
            # We use a smaller chunk size and a limit on iterations to be safe
            for _ in range(100): # Safety limit for draining the buffer
                chunk = self.process.read_nonblocking(size=8192, timeout=0.01)
                output += chunk
                if len(output) > max_bytes * 2: # Stop if we are way over limit to save CPU
                    break
        except pexpect.TIMEOUT:
            pass
        except pexpect.EOF:
            output += "\n[Process finished]"
        
        if strip_ansi and output:
            output = ANSI_ESCAPE.sub('', output)
            
        # Truncation logic (keep the tail of the output if it's too big)
        if len(output) > max_bytes:
            trunc_msg = f"\n\n[WARNING: Output truncated from {len(output)} bytes to {max_bytes} bytes. Use smaller commands or check logs.]"
            # Keep the end of the string (the most recent output)
            output = output[-(max_bytes - len(trunc_msg)):]
            output = trunc_msg + output

        return output

    def close(self):
        if self.process:
            if self.process.isalive():
                try:
                    self.process.close(force=True)
                except Exception:
                    pass # Ignore errors during close
            self.process = None
        logger.info(f"Closed session {self.id}")

    def is_alive(self) -> bool:
        return self.process is not None and self.process.isalive()


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        # Register cleanup on interpreter exit
        atexit.register(self.cleanup_all)

    def create_session(self, command: str, args: list[str] = None) -> str:
        session = Session(command, args)
        sid = session.start()
        self._sessions[sid] = session
        return sid

    def get_session(self, session_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        # Lazy cleanup: if we try to get a session and it's dead, we could handle it here,
        # but for now we just return it so the user can see the [Process finished] message once.
        return session

    def list_sessions(self) -> Dict[str, str]:
        """Returns a dict of id -> command string. Cleans up dead sessions."""
        active = {}
        dead_ids = []
        for sid, s in self._sessions.items():
            if s.is_alive():
                active[sid] = f"{s.command} {' '.join(s.args)}"
            else:
                # Keep dead sessions in the list? Or remove them?
                # Let's keep them in the manager but mark them, 
                # or simpler: just show active ones in this list.
                # Actually, let's auto-cleanup completely dead ones from this list view
                # strictly if we want to be "clean".
                # But maybe the user wants to read the last output?
                # We'll leave them in memory until explicit close or cleanup, 
                # but only return is_alive ones here.
                pass
        return active

    def close_session(self, session_id: str):
        if session_id in self._sessions:
            self._sessions[session_id].close()
            del self._sessions[session_id]
            return True
        return False

    def cleanup_all(self):
        """Terminate all active sessions."""
        for session in self._sessions.values():
            session.close()
        self._sessions.clear()
