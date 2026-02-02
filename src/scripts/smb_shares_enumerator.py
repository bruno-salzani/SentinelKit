import sys
import subprocess
import argparse
from support import write_json, timestamp

def list_hosts():
    try:
        out = subprocess.check_output(["net", "view"], shell=True).decode("utf-8", errors="ignore")
        hosts = []
        for line in out.splitlines():
            s = line.strip()
            if s.startswith("\\\\"):
                hosts.append(s.strip("\\").strip())
        return hosts
    except Exception:
        return []

def list_shares(host):
    try:
        out = subprocess.check_output(["net", "view", f"\\\\{host}"], shell=True).decode("utf-8", errors="ignore")
        shares = []
        capture = False
        for line in out.splitlines():
            if "Shared resources at" in line:
                capture = True
                continue
            if capture:
                parts = line.split()
                if parts and not line.startswith("The command"):
                    name = parts[0]
                    shares.append({"name": name})
        return shares
    except Exception:
        return []

def probe_share_access(host, share):
    try:
        out = subprocess.check_output(["cmd","/c", f"dir \\\\{host}\\{share}"], shell=False).decode("utf-8", errors="ignore")
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        count = sum(1 for l in lines if "<DIR>" in l or ":" in l)
        return {"accessible": True, "items_count": count}
    except Exception:
        return {"accessible": False, "items_count": 0}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="")
    args = ap.parse_args()
    target = args.host.strip() or None
    hosts = [target] if target else list_hosts()
    results = []
    for h in hosts:
        if not h:
            continue
        shares = list_shares(h)
        for s in shares:
            p = probe_share_access(h, s["name"])
            s.update(p)
        results.append({"host": h, "shares": shares})
    meta = {"script": "smb_shares_enumerator", "ts": timestamp(), "host": target, "version": "1.0"}
    path = write_json("smb", "shares", {"hosts": results}, meta)
    print(path)

if __name__ == "__main__":
    main()
