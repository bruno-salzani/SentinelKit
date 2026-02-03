import os
import sys
import subprocess
from support import results_dir, timestamp

def read_startup_folder():
    paths = []
    home = os.path.expanduser("~")
    paths.append(os.path.join(home, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup"))
    paths.append(os.path.join("C:\\", "ProgramData", "Microsoft", "Windows", "Start Menu", "Programs", "Startup"))
    items = []
    for p in paths:
        if os.path.isdir(p):
            for name in os.listdir(p):
                items.append({"path": os.path.join(p, name)})
    return items

def read_registry_runs():
    cmd = [
        "powershell","-NoProfile","-ExecutionPolicy","Bypass","-Command",
        "Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run';"
        "Get-ItemProperty 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'|ConvertTo-Json -Depth 4"
    ]
    try:
        out = subprocess.check_output(cmd, shell=False).decode("utf-8", errors="ignore")
        return out
    except Exception:
        return ""

def list_schtasks():
    try:
        out = subprocess.check_output(["schtasks","/Query","/V","/FO","LIST"], shell=False).decode("utf-8", errors="ignore")
        tasks = []
        t = {}
        for line in out.splitlines():
            s = line.strip()
            if not s:
                if t:
                    tasks.append(t)
                t = {}
                continue
            if ":" in s:
                k,v = s.split(":",1)
                t[k.strip()] = v.strip()
        if t:
            tasks.append(t)
        return tasks
    except Exception:
        return []

def flag_suspicious(path):
    if not path:
        return False
    low = path.lower()
    return any(x in low for x in ["\\temp\\","appdata\\","\\users\\public\\","\\system32\\drivers\\etc"])

def main():
    data = {
        "startup_folder": read_startup_folder(),
        "runs_registry_raw": read_registry_runs(),
        "scheduled_tasks": list_schtasks()
    }
    for item in data["startup_folder"]:
        item["suspicious"] = flag_suspicious(item.get("path"))
    out_dir = results_dir("autoruns")
    path = os.path.join(out_dir, f"autoruns_{timestamp()}.json")
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
