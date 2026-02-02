import sys
import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from support import results_dir, timestamp, write_json, http_get

COMMON_PATHS = [
    "robots.txt","admin/","login/","dashboard/","setup/",".git/","server-status","api/","config/"
]

def main():
    if len(sys.argv) < 2:
        print("usage: http_directory_bruteforce.py <BASE_URL> [RATE_MS] [--paths <csv>] [--paths-file <file>] [--concurrency <N>] [--status <csv>] [--timeout <s>]")
        return
    base = sys.argv[1].rstrip("/") + "/"
    rate_ms = 200
    try:
        if len(sys.argv) > 2:
            rate_ms = int(sys.argv[2])
    except Exception:
        rate_ms = 200
    paths = []
    paths_csv = None
    paths_file = None
    concurrency = 1
    timeout_s = 5
    status_filter = []
    i = 3
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--paths" and i + 1 < len(sys.argv):
            paths_csv = sys.argv[i+1]
            i += 2
            continue
        if arg == "--paths-file" and i + 1 < len(sys.argv):
            paths_file = sys.argv[i+1]
            i += 2
            continue
        if arg == "--concurrency" and i + 1 < len(sys.argv):
            try:
                concurrency = int(sys.argv[i+1])
            except Exception:
                concurrency = 1
            i += 2
            continue
        if arg == "--status" and i + 1 < len(sys.argv):
            try:
                status_filter = [int(x.strip()) for x in sys.argv[i+1].split(",") if x.strip()]
            except Exception:
                status_filter = []
            i += 2
            continue
        if arg == "--timeout" and i + 1 < len(sys.argv):
            try:
                timeout_s = float(sys.argv[i+1])
            except Exception:
                timeout_s = 5
            i += 2
            continue
        i += 1
    if paths_csv:
        for x in paths_csv.split(","):
            s = x.strip()
            if s:
                paths.append(s)
    if paths_file and os.path.isfile(paths_file):
        try:
            with open(paths_file, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s:
                        paths.append(s)
        except Exception:
            pass
    if not paths:
        paths = COMMON_PATHS[:]
    def fetch(p):
        url = base + p
        t0 = time.time()
        entry = {"path": p, "status": None, "length": None, "time_ms": None}
        try:
            r = http_get(url, timeout=timeout_s, allow_redirects=False, headers=None, retries=1, backoff=0.5)
            entry["status"] = r.status_code
            entry["length"] = len(r.content or b"")
        except Exception as e:
            entry["error"] = str(e)
        entry["time_ms"] = int((time.time() - t0) * 1000)
        time.sleep(rate_ms / 1000.0)
        return entry
    results = []
    if concurrency > 1:
        with ThreadPoolExecutor(max_workers=max(1, concurrency)) as ex:
            futs = {ex.submit(fetch, p): p for p in paths}
            for fut in as_completed(futs):
                entry = fut.result()
                if status_filter and isinstance(entry.get("status"), int):
                    if entry["status"] not in status_filter:
                        continue
                results.append(entry)
    else:
        for p in paths:
            entry = fetch(p)
            if status_filter and isinstance(entry.get("status"), int):
                if entry["status"] not in status_filter:
                    continue
            results.append(entry)
    meta = {"script": "http_directory_bruteforce", "ts": timestamp(), "host": None, "version": "1.0"}
    path = write_json("http_bruteforce", "dir_bruteforce", {"base_url": base, "rate_ms": rate_ms, "concurrency": concurrency, "timeout_s": timeout_s, "status_filter": status_filter, "results": results}, meta)
    print(path)

if __name__ == "__main__":
    main()
