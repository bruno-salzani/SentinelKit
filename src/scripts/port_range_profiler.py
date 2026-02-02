import sys
import socket
import time
import argparse
from support import write_json, write_csv, timestamp

def probe(host, port):
    res = {"port": port, "open": False, "banner": "", "time_ms": None}
    t0 = time.time()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        s.connect((host, port))
        res["open"] = True
        try:
            data = s.recv(512)
            res["banner"] = data.decode("latin1", errors="ignore")
        except Exception:
            res["banner"] = ""
        s.close()
    except Exception:
        res["open"] = False
    res["time_ms"] = int((time.time() - t0) * 1000)
    return res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("host")
    ap.add_argument("range")
    ap.add_argument("--timeout", type=float, default=1.5)
    ap.add_argument("--csv", action="store_true")
    args = ap.parse_args()
    host = args.host
    parts = args.range.split("-")
    start = int(parts[0])
    end = int(parts[1])
    results = []
    for p in range(start, end + 1):
        results.append(probe(host, p))
    meta = {"script": "port_range_profiler", "ts": timestamp(), "host": host, "version": "1.0"}
    jpath = write_json("port_range", f"range_{host.replace(':','_')}_{start}_{end}", {"host": host, "start": start, "end": end, "results": results}, meta)
    print(jpath)
    if args.csv:
        rows = [["port","open","time_ms","banner"]]
        for it in results:
            rows.append([it.get("port"), it.get("open"), it.get("time_ms"), (it.get("banner") or "").replace("\r"," ").replace("\n"," ")])
        cpath = write_csv("port_range", f"range_{host.replace(':','_')}_{start}_{end}", rows[0], rows[1:])
        print(cpath)

if __name__ == "__main__":
    main()
