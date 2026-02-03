import socket
import threading
import json
import struct
import time
import sys
import support
from support import VIDEO_PORT, CONTROL_PORT

def start_video_stream(host='0.0.0.0', port=VIDEO_PORT):
    """
    Captures screen and streams it to the connected client.
    """
    import mss
    import numpy as np
    import cv2
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"[Video] Listening on {host}:{port}...")

    conn, addr = server_socket.accept()
    print(f"[Video] Connected to {addr}")

    with mss.mss() as sct:
        # Capture the primary monitor
        monitor = sct.monitors[1]
        
        try:
            while True:
                # Capture screen
                img = np.array(sct.grab(monitor))
                
                # Compress image (JPEG)
                # Lower quality = faster stream. 50-70 is a good balance.
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                _, frame = cv2.imencode('.jpg', img, encode_param)
                data = frame.tobytes()
                
                # Send message length first using struct (unsigned long long, big endian)
                message_size = struct.pack(">Q", len(data))
                conn.sendall(message_size + data)
                
                # Limit FPS to save CPU/Bandwidth (e.g., ~30 FPS)
                # time.sleep(0.03) 
                
        except (ConnectionResetError, BrokenPipeError):
            print("[Video] Client disconnected.")
        except Exception as e:
            print(f"[Video] Error: {e}")
        finally:
            conn.close()
            server_socket.close()

def handle_control_command(command, mouse, keyboard):
    """
    Executes mouse/keyboard commands received from client.
    """
    from pynput.mouse import Button
    from pynput.keyboard import Key
    
    try:
        cmd_type = command.get('type')
        
        if cmd_type == 'MOUSE_MOVE':
            x, y = command['x'], command['y']
            # Scale coordinates if necessary, but for now assume 1:1 or handled by client
            # pyautogui.moveTo(x, y) # pyautogui is slower, pynput is preferred for background
            mouse.position = (x, y)
            
        elif cmd_type == 'MOUSE_CLICK':
            button = command['button']
            pressed = command['pressed']
            btn = Button.left if button == 'left' else Button.right if button == 'right' else Button.middle
            if pressed:
                mouse.press(btn)
            else:
                mouse.release(btn)
                
        elif cmd_type == 'KEY_PRESS':
            key_str = command['key']
            # Handle special keys
            if hasattr(Key, key_str):
                key = getattr(Key, key_str)
            else:
                key = key_str
            
            keyboard.press(key)
            keyboard.release(key) # Simple press/release for now
            
    except Exception as e:
        # print(f"[Control] Command Error: {e}") # Verbose
        pass

def start_control_server(host='0.0.0.0', port=CONTROL_PORT):
    """
    Listens for control commands (mouse/keyboard).
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"[Control] Listening on {host}:{port}...")

    conn, addr = server_socket.accept()
    print(f"[Control] Connected to {addr}")

    mouse = MouseController()
    keyboard = KeyboardController()

    buffer = ""
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            # Simple delimiter-based protocol (newline)
            buffer += data.decode('utf-8')
            while '\n' in buffer:
                message, buffer = buffer.split('\n', 1)
                if message:
                    try:
                        command = json.loads(message)
                        handle_control_command(command, mouse, keyboard)
                    except json.JSONDecodeError:
                        pass
                        
    except Exception as e:
        print(f"[Control] Error: {e}")
    finally:
        conn.close()
        server_socket.close()

def main():
    print("Starting Remote Desktop Host...")
    print("Press Ctrl+C to stop.")
    
    # Start Video Thread
    video_thread = threading.Thread(target=start_video_stream, daemon=True)
    video_thread.start()
    
    # Start Control Thread
    control_thread = threading.Thread(target=start_control_server, daemon=True)
    control_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        sys.exit(0)

if __name__ == "__main__":
    support.ensure_dependencies(["mss", "numpy", "cv2", "pyautogui", "pynput"])
    main()
