import os
import time
import sys
import platform
try:
    import psutil
except Exception:
    print("psutil not found. Install with: pip install psutil")
    sys.exit(1)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    is_windows = platform.system() == "Windows"
    use_kb = False
    if is_windows:
        try:
            import msvcrt
            use_kb = True
        except Exception:
            use_kb = False

    while True:
        clear()
        print("Process Top Viewer")
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        print("")
        items = []
        for p in psutil.process_iter(attrs=["pid", "name"]):
            try:
                cpu = p.cpu_percent(interval=0.0)
                mem = p.memory_info().rss
                items.append((cpu, mem, p.info["pid"], p.info["name"]))
            except Exception:
                continue
        items.sort(key=lambda x: (x[0], x[1]), reverse=True)
        print("{0:>6}  {1:>6}  {2:<30}".format("PID", "CPU%", "NAME"))
        for cpu, mem, pid, name in items[:20]:
            print("{0:>6}  {1:>6.1f}  {2:<30}".format(pid, cpu, name[:30]))
        print("")
        print("Press Q to quit")
        if use_kb and msvcrt.kbhit():
            c = msvcrt.getch()
            if c in [b"q", b"Q"]:
                break
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
