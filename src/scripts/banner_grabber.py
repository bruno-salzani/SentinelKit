import socket
import sys
import json
import os
from support import results_dir, timestamp

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
    out_dir = results_dir("banners")
    path = os.path.join(out_dir, f"banners_{host.replace(':', '_')}_{timestamp()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"host": host, "results": out}, f, ensure_ascii=False, indent=2)
    print(path)

if __name__ == "__main__":
    main()
