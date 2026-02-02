import subprocess
import json
import os
from support import results_dir, timestamp
import re

def parse():
    try:
        out = subprocess.check_output(["ipconfig", "/displaydns"], shell=False).decode("utf-8", errors="ignore")
    except Exception as e:
        return {"error": str(e), "entries": []}
    entries = []
    entry = {}
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("Record Name") and ":" in s:
            if entry:
                entries.append(entry)
            entry = {"name": s.split(":", 1)[1].strip()}
        elif s.startswith("Record Type") and ":" in s:
            entry["type"] = s.split(":", 1)[1].strip()
        elif s.startswith("Time To Live") and ":" in s:
            entry["ttl"] = s.split(":", 1)[1].strip()
        elif s.startswith("Data") and ":" in s:
            entry.setdefault("data", [])
            entry["data"].append(s.split(":", 1)[1].strip())
    if entry:
        entries.append(entry)
    return {"timestamp": datetime.now().isoformat(), "entries": entries}

def main():
    data = parse()
    out_dir = results_dir("dns")
    path = os.path.join(out_dir, f"dns_cache_{timestamp()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(path)

if __name__ == "__main__":
    main()
