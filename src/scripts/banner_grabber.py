import socket
import sys
import json
import os
from datetime import datetime

def probe(host, port):
    data = ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((host, port))
        if port == 80:
            s.sendall(b"HEAD / HTTP/1.0\r\nHost: %b\r\n\r\n" % host.encode("ascii", "ignore"))
        elif port == 443:
            pass
        elif port == 21:
            pass
        elif port == 25:
            s.sendall(b"EHLO sentinelkit\r\n")
        else:
            pass
        try:
            data = s.recv(1024)
        except Exception:
            data = b""
        s.close()
        txt = data.decode("latin1", errors="ignore")
        return {"port": port, "banner": txt}
    except Exception as e:
        return {"port": port, "error": str(e)}

def main():
    if len(sys.argv) < 3:
        print("usage: banner_grabber.py <HOST> <PORT1,PORT2,...>")
        sys.exit(1)
    host = sys.argv[1]
    ports = []
    for p in sys.argv[2].split(","):
        try:
            ports.append(int(p.strip()))
        except Exception:
            pass
    out = []
    for port in ports:
        out.append(probe(host, port))
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "results")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "banners_{0}_{1}.json".format(host.replace(":", "_"), datetime.now().strftime("%Y%m%d_%H%M%S")))
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"host": host, "results": out}, f, ensure_ascii=False, indent=2)
    print(path)

if __name__ == "__main__":
    main()
