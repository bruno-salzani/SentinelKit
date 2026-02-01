import cv2
import sys
import os
from datetime import datetime

def list_cameras(limit=10):
    """
    Lists available cameras by checking indices up to `limit`.
    """
    cameras = []
    print(f"Checking for cameras (0 to {limit-1})...")
    for index in range(limit):
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) # CAP_DSHOW is faster on Windows
        if not cap.isOpened():
            cap.release()
            continue
        
        cameras.append(index)
        cap.release()
    return cameras

def main():
    cameras = list_cameras()
    
    if not cameras:
        print("No cameras found.")
        return

    print("Available cameras:")
    for i, camera in enumerate(cameras):
        print(f"{i+1}. Camera Index {camera}")

    try:
        choice = input("Choose camera to access (number): ")
        choice_idx = int(choice) - 1
        
        if 0 <= choice_idx < len(cameras):
            camera_index = cameras[choice_idx]
        else:
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return

    print(f"Accessing camera {camera_index}...")
    print("Controls:")
    print("  [S] Save Snapshot")
    print("  [Q] Quit")
    
    cap = cv2.VideoCapture(camera_index)
    
    # Ensure results directory exists
    # If running from src/scripts, go up to project root
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(cur_dir))
    save_dir = os.path.join(root_dir, "results", "camera_captures")
    os.makedirs(save_dir, exist_ok=True)

    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Camera', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cam_{camera_index}_{timestamp}.png"
                filepath = os.path.join(save_dir, filename)
                cv2.imwrite(filepath, frame)
                print(f"[+] Snapshot saved: {filepath}")
                
        else:
            print("Failed to grab frame.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
