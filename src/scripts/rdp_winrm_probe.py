import argparse
import socket
import ssl
from support import write_json, timestamp

def check_port(host: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def rdp_probe(host: str, timeout: float):
    info = {"port": 3389, "open": False}
    try:
        with socket.create_connection((host, 3389), timeout=timeout) as s:
            s.settimeout(timeout)
            info["open"] = True
            try:
                data = s.recv(64)
                if data:
                    info["hello_sample_hex"] = data[:32].hex()
                    info["hello_len"] = len(data)
            except Exception:
                pass
            try:
                ctx = ssl.create_default_context()
                with ctx.wrap_socket(s, server_hostname=host) as tls:
                    tls.settimeout(timeout)
                    info["tls_handshake_ok"] = True
                    try:
                        cert = tls.getpeercert()
                        info["tls_cert"] = cert
                    except Exception:
                        pass
            except Exception:
                info["tls_handshake_ok"] = False
    except Exception as e:
        info["error"] = str(e)
    return info

def winrm_http_probe(host: str, timeout: float):
    info = {"port": 5985, "open": False}
    try:
        with socket.create_connection((host, 5985), timeout=timeout) as s:
            s.settimeout(timeout)
            info["open"] = True
            req = f"OPTIONS /wsman HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode("ascii", errors="ignore")
            try:
                s.sendall(req)
                buf = b""
                while True:
                    chunk = s.recv(1024)
                    if not chunk:
                        break
                    buf += chunk
                    if len(buf) > 65536:
                        break
                text = buf.decode("utf-8", errors="ignore")
                lines = text.split("\r\n")
                if lines:
                    info["status_line"] = lines[0]
                headers = {}
                for line in lines[1:]:
                    if not line.strip():
                        break
                    if ":" in line:
                        k, v = line.split(":", 1)
                        headers[k.strip()] = v.strip()
                wa = headers.get("WWW-Authenticate") or ""
                schemes = []
                for part in wa.split(","):
                    p = part.strip()
                    if p:
                        t = p.split(" ")[0].strip()
                        if t and t.upper() not in schemes:
                            schemes.append(t.upper())
                info["headers"] = {"Server": headers.get("Server"), "WWW-Authenticate": wa, "auth_schemes": schemes}
            except Exception:
                pass
    except Exception as e:
        info["error"] = str(e)
    return info

def winrm_https_probe(host: str, timeout: float):
    info = {"port": 5986, "open": False}
    try:
        with socket.create_connection((host, 5986), timeout=timeout) as sock:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(sock, server_hostname=host) as s:
                s.settimeout(timeout)
                info["open"] = True
                try:
                    cert = s.getpeercert()
                    info["tls_cert"] = cert
                except Exception:
                    pass
                try:
                    req = f"OPTIONS /wsman HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode("ascii", errors="ignore")
                    s.sendall(req)
                    buf = b""
                    while True:
                        chunk = s.recv(1024)
                        if not chunk:
                            break
                        buf += chunk
                        if len(buf) > 65536:
                            break
                    text = buf.decode("utf-8", errors="ignore")
                    lines = text.split("\r\n")
                    if lines:
                        info["status_line"] = lines[0]
                    headers = {}
                    for line in lines[1:]:
                        if not line.strip():
                            break
                        if ":" in line:
                            k, v = line.split(":", 1)
                            headers[k.strip()] = v.strip()
                    wa = headers.get("WWW-Authenticate") or ""
                    schemes = []
                    for part in wa.split(","):
                        p = part.strip()
                        if p:
                            t = p.split(" ")[0].strip()
                            if t and t.upper() not in schemes:
                                schemes.append(t.upper())
                    info["headers"] = {"Server": headers.get("Server"), "WWW-Authenticate": wa, "auth_schemes": schemes}
                except Exception:
                    pass
    except Exception as e:
        info["error"] = str(e)
    return info

def main():
    ap = argparse.ArgumentParser(description="Sondagem de RDP e WinRM")
    ap.add_argument("host", help="Host alvo")
    ap.add_argument("--timeout", type=float, default=3.0, help="Timeout de conexão (s)")
    args = ap.parse_args()
    host = args.host
    timeout = args.timeout
    rdp = rdp_probe(host, timeout)
    winrm_http = winrm_http_probe(host, timeout)
    winrm_https = winrm_https_probe(host, timeout)
    data = {
        "target": {"host": host},
        "services": {
            "rdp": rdp,
            "winrm_http": winrm_http,
            "winrm_https": winrm_https
        }
    }
    meta = {"script": "rdp_winrm_probe", "ts": timestamp(), "host": host, "version": "1.0"}
    path = write_json("rdp_winrm", f"probe_{host.replace(':','_')}", data, meta)
    print(path)

if __name__ == "__main__":
    main()
