import time
from mcp_agentty.session import SessionManager

def test_session_manager_shell():
    sm = SessionManager()
    
    # 1. Start a shell session
    sid = sm.create_session("/bin/bash")
    assert sid is not None
    assert sm.get_session(sid) is not None
    
    # Allow some time for the shell to start and print prompt
    time.sleep(0.5)
    
    # 2. Write a command
    # We use a unique string to verify output
    unique_str = "agentty_test_string"
    sm.get_session(sid).write(f"echo {unique_str}\n")
    
    # Allow time for execution
    time.sleep(0.5)
    
    # 3. Read output
    output = sm.get_session(sid).read()
    print(f"DEBUG OUTPUT: {output}")
    
    assert unique_str in output
    
def test_concurrent_sessions():
    sm = SessionManager()
    
    # Start two sessions
    sid1 = sm.create_session("/bin/bash")
    sid2 = sm.create_session("/bin/bash")
    
    assert sid1 != sid2
    
    # Write different commands to each
    sm.get_session(sid1).write("echo SESSION_ONE\n")
    sm.get_session(sid2).write("echo SESSION_TWO\n")
    
    time.sleep(0.5)
    
    # Check outputs are isolated
    out1 = sm.get_session(sid1).read()
    out2 = sm.get_session(sid2).read()
    
    assert "SESSION_ONE" in out1
    assert "SESSION_TWO" not in out1
    
    assert "SESSION_TWO" in out2
    assert "SESSION_ONE" not in out2
    
    sm.close_session(sid1)
    sm.close_session(sid2)

def test_output_truncation():
    sm = SessionManager()
    sid = sm.create_session("/bin/bash")
    
    # Generate a lot of output
    sm.get_session(sid).write("seq 1 10000\n")
    time.sleep(1.0)
    
    # Read with a small limit
    limit = 1000
    out = sm.get_session(sid).read(max_bytes=limit)
    
    assert len(out) <= limit + 100 # small buffer for the warning message
    assert "Output truncated" in out
    
    sm.close_session(sid)
