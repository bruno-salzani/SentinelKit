import os
import subprocess
from support import results_dir, timestamp

def list_win32():
    cmd = [
        "powershell","-NoProfile","-ExecutionPolicy","Bypass","-Command",
        "Get-ItemProperty 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | ConvertTo-Json -Depth 3"
    ]
    try:
        out = subprocess.check_output(cmd, shell=False).decode("utf-8", errors="ignore")
        import json
        try:
            obj = json.loads(out)
            return obj if isinstance(obj, list) else [obj]
        except Exception:
            return []
    except Exception:
        return []

def list_msix():
    cmd = [
        "powershell","-NoProfile","-ExecutionPolicy","Bypass","-Command",
        "Get-AppxPackage | Select-Object Name, Version, Publisher | ConvertTo-Json -Depth 3"
    ]
    try:
        out = subprocess.check_output(cmd, shell=False).decode("utf-8", errors="ignore")
        import json
        try:
            obj = json.loads(out)
            return obj if isinstance(obj, list) else [obj]
        except Exception:
            return []
    except Exception:
        return []

def main():
    data = {
        "win32": list_win32(),
        "msix": list_msix()
    }
    out_dir = results_dir("programs")
    path = os.path.join(out_dir, f"programs_{timestamp()}.json")
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
