import os
import sys
import socket
import subprocess
import json
import time
import threading
from queue import Queue
from datetime import datetime

def get_local_subnet():
    try:
        hn = socket.gethostname()
        ip = socket.gethostbyname(hn)
        parts = ip.split(".")
        if len(parts) == 4:
            return ".".join(parts[:3])
    except Exception:
        pass
    return None

def ping_one(ip):
    try:
        cmd = ["ping", "-n", "1", "-w", "700", ip]
        p = subprocess.run(cmd, capture_output=True, text=True)
        out = p.stdout or ""
        alive = "TTL=" in out
        ms = None
        for token in out.split():
            if token.lower().startswith("time=") or token.lower().startswith("tempo="):
                try:
                    ms = int("".join([c for c in token if c.isdigit()]))
                except Exception:
                    ms = None
                break
        return {"ip": ip, "alive": alive, "ms": ms}
    except Exception:
        return {"ip": ip, "alive": False, "ms": None}

def worker(q, results):
    while True:
        ip = q.get()
        if ip is None:
            break
        results.append(ping_one(ip))
        q.task_done()

def main():
    base = None
    if len(sys.argv) > 1:
        base = sys.argv[1]
    if not base:
        base = get_local_subnet()
    if not base:
        print("no subnet")
        sys.exit(1)
    ips = [f"{base}.{i}" for i in range(1, 255)]
    q = Queue()
    results = []
    for ip in ips:
        q.put(ip)
    threads = []
    tcount = 64
    for _ in range(tcount):
        t = threading.Thread(target=worker, args=(q, results))
        t.daemon = True
        t.start()
        threads.append(t)
    start = time.time()
    q.join()
    dur = time.time() - start
    alive = [r for r in results if r["alive"]]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "results")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"ping_sweep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"subnet": base, "duration_s": round(dur, 2), "alive": alive}, f, ensure_ascii=False, indent=2)
    print(path)

if __name__ == "__main__":
    main()
