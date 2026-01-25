import cv2
import sys

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

    print(f"Accessing camera {camera_index}... Press 'q' to quit.")
    cap = cv2.VideoCapture(camera_index)

    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
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
