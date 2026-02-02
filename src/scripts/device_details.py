import os
import sys
import json
import platform
import socket
from datetime import datetime
from support import format_size, results_dir, timestamp

try:
    import psutil
except ImportError:
    print("Error: 'psutil' module not found. Please install it using: pip install psutil")
    sys.exit(1)

def get_os_info():
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "platform": platform.platform()
    }

def get_cpu_info():
    return {
        "cores_logical": os.cpu_count(),
        "architecture": platform.machine(),
        "processor": platform.processor() or "Unknown"
    }

def get_memory_info():
    try:
        mem = psutil.virtual_memory()
        return {
            "total": format_size(mem.total),
            "available": format_size(mem.available),
            "used": format_size(mem.used),
            "percent": mem.percent
        }
    except Exception as e:
        return {"error": str(e)}

def get_disk_info():
    disks = []
    try:
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({
                    "mount": part.mountpoint,
                    "fstype": part.fstype,
                    "total": format_size(usage.total),
                    "used": format_size(usage.used),
                    "free": format_size(usage.free),
                    "percent": usage.percent
                })
            except PermissionError:
                continue
    except Exception as e:
        return {"error": str(e)}
    return disks

def get_network_info():
    try:
        hostname = socket.gethostname()
        return {
            "hostname": hostname,
            "ip": socket.gethostbyname(hostname)
        }
    except Exception as e:
        return {"error": str(e)}

def build_report():
    return {
        "timestamp": datetime.now().isoformat(),
        "os": get_os_info(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "network": get_network_info()
    }

def main():
    print("Gathering device details...")
    data = build_report()
    
    out_dir = results_dir("system")
    filename = os.path.join(out_dir, f"device_details_{timestamp('%Y-%m-%d')}.json")
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Report saved to {filename}")
    except IOError as e:
        print(f"Error saving report: {e}")

if __name__ == "__main__":
    main()
