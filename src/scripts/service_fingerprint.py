import sys
import os
import json
import socket
from port_scanner import run_scanner
from banner_grabber import probe

from support import results_dir, timestamp

def main():
    if len(sys.argv) < 2:
        print("usage: service_fingerprint.py <TARGET> [common|all]")
        sys.exit(1)
    target = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "common"
    try:
        ip = socket.gethostbyname(target)
    except Exception:
        ip = target
    ports = run_scanner(ip, mode)
    out = []
    for p, svc in ports:
        b = probe(ip, p)
        out.append({"port": p, "service": svc, "banner": b.get("banner", ""), "error": b.get("error")})
    out_dir = results_dir("fingerprint")
    path = os.path.join(out_dir, f"fingerprint_{ip.replace(':', '_')}_{timestamp()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"target": ip, "results": out}, f, ensure_ascii=False, indent=2)
    print(path)

if __name__ == "__main__":
    main()
