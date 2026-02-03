import os
import subprocess
from support import results_dir, timestamp

def dump_rules():
    cmd = [
        "powershell","-NoProfile","-ExecutionPolicy","Bypass","-Command",
        "Get-NetFirewallRule | Select-Object DisplayName, Enabled, Direction, Profile, Action | ConvertTo-Json -Depth 3"
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
    data = {"rules": dump_rules()}
    out_dir = results_dir("firewall")
    path = os.path.join(out_dir, f"firewall_{timestamp()}.json")
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
