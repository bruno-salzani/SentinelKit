import subprocess
import json
import os
from datetime import datetime

def parse():
    try:
        out = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=bssid"]).decode("utf-8", errors="ignore")
    except Exception as e:
        return {"error": str(e), "networks": []}
    nets = []
    current = {}
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("SSID ") and ":" in s:
            if current:
                nets.append(current)
            current = {}
            parts = s.split(":", 1)
            current["ssid"] = parts[1].strip()
        elif s.startswith("Authentication") and ":" in s:
            current["auth"] = s.split(":", 1)[1].strip()
        elif s.startswith("Encryption") and ":" in s:
            current["encryption"] = s.split(":", 1)[1].strip()
        elif s.startswith("BSSID") and ":" in s:
            current.setdefault("bssids", [])
            current["bssids"].append(s.split(":", 1)[1].strip())
        elif s.startswith("Signal") and ":" in s:
            current.setdefault("signals", [])
            current["signals"].append(s.split(":", 1)[1].strip())
        elif s.startswith("Channel") and ":" in s:
            current.setdefault("channels", [])
            current["channels"].append(s.split(":", 1)[1].strip())
    if current:
        nets.append(current)
    return {"timestamp": datetime.now().isoformat(), "networks": nets}

def main():
    data = parse()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "results")
    os.makedirs(out_dir, exist_ok=True)
    fname = "wifi_networks_{0}.json".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
    path = os.path.join(out_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(path)

if __name__ == "__main__":
    main()
