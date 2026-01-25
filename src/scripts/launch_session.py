import subprocess
import sys
import time
import os

def launch_session():
    """
    Launches the device_access.py (server) and remote_viewer.py (client) 
    in the background (hidden windows) for easy local testing.
    
    The script keeps running to monitor the Client. 
    When the Client (viewer) is closed, the Server is automatically terminated.
    """
    
    # Get the absolute paths to the scripts
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    server_script = os.path.join(current_dir, "device_access.py")
    client_script = os.path.join(current_dir, "remote_viewer.py")
    
    print(f"Project Root: {project_root}")
    print(f"Server Script: {server_script}")
    print(f"Client Script: {client_script}")

    # Windows specific flag to hide the console window
    CREATE_NO_WINDOW = 0x08000000

    print("-" * 50)
    print("Starting session...")
    print("NOTE: Console windows are hidden.")
    print("Close the Remote Desktop Viewer window to end the session.")
    print("-" * 50)

    # Launch Server (device_access.py)
    # Redirect output to DEVNULL so it doesn't clutter the main terminal
    print("Launching Server (device_access.py)...")
    server_process = subprocess.Popen(
        [sys.executable, server_script],
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=project_root
    )

    # Give the server a moment to start
    time.sleep(2)

    # Launch Client (remote_viewer.py)
    print("Launching Client (remote_viewer.py)...")
    client_process = subprocess.Popen(
        [sys.executable, client_script, "127.0.0.1"],
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=project_root
    )

    print("Session is running.")
    print("Waiting for client to close...")

    try:
        # Monitor the client process
        while client_process.poll() is None:
            time.sleep(1)
            
            # Optional: Check if server died unexpectedly
            if server_process.poll() is not None:
                print("Warning: Server process terminated unexpectedly.")
                break

    except KeyboardInterrupt:
        print("\nForce stopping session...")

    finally:
        # Cleanup
        print("Cleaning up...")
        
        if client_process.poll() is None:
            print("Terminating Client...")
            client_process.terminate()
            
        if server_process.poll() is None:
            print("Terminating Server...")
            server_process.terminate()
            
        print("Session ended.")

if __name__ == "__main__":
    launch_session()
