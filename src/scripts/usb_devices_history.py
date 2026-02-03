import os
import subprocess
from support import results_dir, timestamp

def list_usb():
    cmd = [
        "powershell","-NoProfile","-ExecutionPolicy","Bypass","-Command",
        "Get-ChildItem 'HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\USB' -Recurse | ForEach-Object { $_.Name }"
    ]
    try:
        out = subprocess.check_output(cmd, shell=False).decode("utf-8", errors="ignore")
        items = []
        for line in out.splitlines():
            s = line.strip()
            if s:
                items.append(s)
        return items
    except Exception:
        return []

def main():
    data = {"keys": list_usb()}
    out_dir = results_dir("usb")
    path = os.path.join(out_dir, f"usb_{timestamp()}.json")
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    try:
        if os.name == "nt":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass
    print(path)

if __name__ == "__main__":
    main()
