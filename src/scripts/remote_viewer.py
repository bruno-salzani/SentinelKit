import socket
import struct
import cv2
import numpy as np
import threading
import json
import sys
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
from support import VIDEO_PORT, CONTROL_PORT

def get_target_ip():
    """
    Retrieves the target IP from command line args or a GUI dialog.
    """
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    # Initialize Tkinter but hide the main window
    root = tk.Tk()
    root.withdraw()
    
    ip = simpledialog.askstring("Remote Viewer", "Enter the Target IP Address:", parent=root)
    
    if not ip:
        messagebox.showerror("Error", "No IP Address provided. Exiting.")
        sys.exit(1)
        
    root.destroy()
    return ip

def receive_video_stream(host):
    """
    Connects to the video stream and displays it.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, VIDEO_PORT))
        print(f"[Video] Connected to {host}:{VIDEO_PORT}")
    except ConnectionRefusedError:
        print(f"[Video] Could not connect to {host}:{VIDEO_PORT}")
        return

    data = b""
    payload_size = struct.calcsize(">Q")

    cv2.namedWindow("Remote Desktop", cv2.WINDOW_NORMAL)

    try:
        while True:
            # Retrieve message size
            while len(data) < payload_size:
                packet = client_socket.recv(4096)
                if not packet:
                    return
                data += packet
            
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">Q", packed_msg_size)[0]

            # Retrieve frame data
            while len(data) < msg_size:
                packet = client_socket.recv(4096)
                if not packet:
                    return
                data += packet
            
            frame_data = data[:msg_size]
            data = data[msg_size:]

            # Decode and display
            frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
            
            if frame is not None:
                cv2.imshow("Remote Desktop", frame)
                
                # 'q' to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
    except Exception as e:
        print(f"[Video] Error: {e}")
    finally:
        client_socket.close()
        cv2.destroyAllWindows()
        print("[Video] Stream closed.")
        # Signal main thread to exit
        sys.exit(0)

def send_control_commands(host):
    """
    Captures mouse/keyboard inputs on the OpenCV window and sends them to the host.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Wait a bit for video connection to be established first
    time.sleep(1)
    
    try:
        client_socket.connect((host, CONTROL_PORT))
        print(f"[Control] Connected to {host}:{CONTROL_PORT}")
    except ConnectionRefusedError:
        print(f"[Control] Could not connect to {host}:{CONTROL_PORT}")
        return

    def mouse_callback(event, x, y, flags, param):
        command = None
        
        if event == cv2.EVENT_MOUSEMOVE:
            command = {"type": "MOUSE_MOVE", "x": x, "y": y}
        elif event == cv2.EVENT_LBUTTONDOWN:
            command = {"type": "MOUSE_CLICK", "button": "left", "pressed": True}
        elif event == cv2.EVENT_LBUTTONUP:
            command = {"type": "MOUSE_CLICK", "button": "left", "pressed": False}
        elif event == cv2.EVENT_RBUTTONDOWN:
            command = {"type": "MOUSE_CLICK", "button": "right", "pressed": True}
        elif event == cv2.EVENT_RBUTTONUP:
            command = {"type": "MOUSE_CLICK", "button": "right", "pressed": False}
            
        if command:
            try:
                msg = json.dumps(command) + "\n"
                client_socket.sendall(msg.encode('utf-8'))
            except Exception:
                pass

    # Set mouse callback for the window created in video thread
    attempts = 0
    while attempts < 10:
        try:
            if cv2.getWindowProperty("Remote Desktop", cv2.WND_PROP_VISIBLE) >= 1:
                cv2.setMouseCallback("Remote Desktop", mouse_callback)
                print("[Control] Mouse control active.")
                break
        except Exception:
            pass
        time.sleep(0.5)
        attempts += 1

    # Keep connection alive
    try:
        while True:
            time.sleep(1)
    except Exception:
        pass
    finally:
        client_socket.close()

def main():
    host = get_target_ip()
    print(f"Connecting to {host}...")
    
    # Start Video Thread
    video_thread = threading.Thread(target=receive_video_stream, args=(host,))
    video_thread.start()
    
    # Start Control Thread
    control_thread = threading.Thread(target=send_control_commands, args=(host,))
    control_thread.start()
    
    video_thread.join()
    control_thread.join()

if __name__ == "__main__":
    support.ensure_dependencies(["cv2", "numpy"])
    main()
