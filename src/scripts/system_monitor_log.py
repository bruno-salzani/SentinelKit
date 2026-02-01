import os
import sys
import time
from datetime import datetime
try:
    import psutil
except Exception:
    print("psutil not found. Install with: pip install psutil")
    sys.exit(1)

def main():
    dur = None
    if len(sys.argv) > 1:
        try:
            dur = int(sys.argv[1])
        except Exception:
            dur = None
    cur = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(cur))
    out_dir = os.path.join(root, "results", "monitor_logs")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "log_{0}.csv".format(datetime.now().strftime("%Y%m%d_%H%M%S")))
    start = time.time()
    with open(path, "w", encoding="utf-8") as f:
        f.write("timestamp,cpu_total,memory_percent\n")
        while True:
            now = datetime.now().isoformat()
            cpu = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory().percent
            f.write("{0},{1:.1f},{2:.1f}\n".format(now, cpu, mem))
            f.flush()
            if dur is not None and (time.time() - start) >= dur:
                break
            time.sleep(0.9)
    print(path)

if __name__ == "__main__":
    main()
