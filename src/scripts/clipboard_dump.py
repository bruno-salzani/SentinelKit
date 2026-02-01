import os
import sys
from datetime import datetime
try:
    import win32clipboard
    import win32con
except Exception:
    print("pywin32 not found. Install with: pip install pywin32")
    sys.exit(1)

def main():
    cur = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(cur))
    out_dir = os.path.join(root, "results", "clipboard")
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_path = os.path.join(out_dir, "clipboard_{0}.txt".format(ts))
    win32clipboard.OpenClipboard()
    try:
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(data)
            print(txt_path)
        else:
            print("No text in clipboard")
    finally:
        win32clipboard.CloseClipboard()

if __name__ == "__main__":
    main()
