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

def bar(p, w=30):
    f = int((p if p <= 100 else 100) * w / 100)
    return "[" + "#" * f + "-" * (w - f) + f"] {0:.1f}%".format(p)

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
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        print("System Monitor")
        print(now)
        print("")

        cpu_total = psutil.cpu_percent(interval=0.1)
        print("CPU Total")
        print(bar(cpu_total))
        cores = psutil.cpu_percent(interval=0.1, percpu=True)
        for i, c in enumerate(cores):
            print("Core {0}".format(i))
            print(bar(c))

        print("")
        vm = psutil.virtual_memory()
        print("Memory")
        print(bar(vm.percent))
        print("Total: {0} MB".format(int(vm.total / (1024 * 1024))))
        print("Used: {0} MB".format(int(vm.used / (1024 * 1024))))
        print("Avail: {0} MB".format(int(vm.available / (1024 * 1024))))

        print("")
        print("Disk")
        parts = []
        try:
            for p in psutil.disk_partitions(all=False):
                try:
                    u = psutil.disk_usage(p.mountpoint)
                    parts.append((p.mountpoint, u.percent, u.total, u.used, u.free))
                except Exception:
                    continue
        except Exception:
            parts = []
        for m, pct, total, used, free in parts[:6]:
            print(m)
            print(bar(pct))
            print("Total: {0} GB  Used: {1} GB  Free: {2} GB".format(int(total / (1024**3)), int(used / (1024**3)), int(free / (1024**3))))

        print("")
        print("Press Q to quit")

        if use_kb and msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in [b"q", b"Q"]:
                break
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
