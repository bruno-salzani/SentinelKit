import socket
import threading
import sys
import time
from queue import Queue
from datetime import datetime
import argparse

# Common ports to scan for a faster check
COMMON_PORTS = {
    20: "FTP Data", 21: "FTP Control", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 111: "RPC", 135: "RPC Endpoint",
    139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
    995: "POP3S", 3306: "MySQL", 3389: "RDP", 5900: "VNC", 8080: "HTTP-Proxy"
}

print_lock = threading.Lock()
open_ports = []

def port_scan(target, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1) # Fast timeout
        result = s.connect_ex((target, port))
        if result == 0:
            with print_lock:
                service = COMMON_PORTS.get(port, "Unknown")
                print(f"[+] Port {port} is OPEN ({service})")
                open_ports.append((port, service))
        s.close()
    except:
        pass

def worker(target, queue):
    while not queue.empty():
        port = queue.get()
        port_scan(target, port)
        queue.task_done()

def run_scanner(target, ports_mode='common', thread_count=50):
    print(f"\n[*] Starting Port Scan on target: {target}")
    print(f"[*] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if ports_mode == 'all':
        print("[*] Scanning ports 1-1024 (Standard range)...")
        ports_to_scan = range(1, 1025)
    else:
        print(f"[*] Scanning {len(COMMON_PORTS)} common ports...")
        ports_to_scan = sorted(COMMON_PORTS.keys())

    queue = Queue()
    
    for port in ports_to_scan:
        queue.put(port)
        
    thread_list = []
    
    print("-" * 50)
    
    for _ in range(thread_count):
        thread = threading.Thread(target=worker, args=(target, queue))
        thread_list.append(thread)
        thread.start()
        
    queue.join()
    
    print("-" * 50)
    print(f"Scan completed. Found {len(open_ports)} open ports.")
    
    return open_ports

def main():
    parser = argparse.ArgumentParser(description="Multi-threaded Port Scanner")
    parser.add_argument("target", help="Target IP address or Hostname")
    parser.add_argument("--mode", choices=['common', 'all'], default='common', help="Scan mode: 'common' (fast) or 'all' (1-1024)")
    
    args = parser.parse_args()
    
    # Resolve hostname if needed
    try:
        target_ip = socket.gethostbyname(args.target)
        if target_ip != args.target:
            print(f"[*] Resolved {args.target} to {target_ip}")
    except socket.gaierror:
        print(f"[!] Could not resolve hostname: {args.target}")
        sys.exit(1)
        
    start_time = time.time()
    run_scanner(target_ip, args.mode)
    end_time = time.time()
    
    print(f"[*] Duration: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
