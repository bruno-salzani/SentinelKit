import argparse
try:
    from support import write_json, http_get, timestamp
except Exception:
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from support import write_json, http_get, timestamp

def parse_cookies(headers: dict):
    cookies = []
    for k, v in headers.items():
        if k.lower() == "set-cookie":
            parts = [x.strip() for x in v.split(";")]
            cookies.append(parts)
    flags = {"secure": False, "httponly": False, "samesite": False}
    for c in cookies:
        for p in c:
            low = p.lower()
            if low == "secure":
                flags["secure"] = True
            elif low == "httponly":
                flags["httponly"] = True
            elif low.startswith("samesite"):
                flags["samesite"] = True
    return {"count": len(cookies), "flags": flags}

def main():
    ensure_dependencies(["requests"])
    ap = argparse.ArgumentParser()
    ap.add_argument("host")
    ap.add_argument("--port", type=int, default=80)
    ap.add_argument("--timeout", type=float, default=5)
    ap.add_argument("--retries", type=int, default=1)
    args = ap.parse_args()
    host = args.host
    port = args.port
    url = f"http://{host}:{port}/"
    data = {"target": {"host": host, "port": port}, "headers": {}, "checks": {}}
    try:
        r = http_get(url, timeout=args.timeout, allow_redirects=False, retries=args.retries, backoff=0.5)
        hdrs = {k: v for k, v in r.headers.items()}
        data["headers"] = hdrs
        low = {k.lower(): v for k, v in hdrs.items()}
        data["checks"]["hsts"] = bool(low.get("strict-transport-security"))
        data["checks"]["hsts_preload_flag"] = "preload" in (low.get("strict-transport-security","").lower())
        data["checks"]["csp"] = bool(low.get("content-security-policy"))
        data["checks"]["x_frame_options"] = low.get("x-frame-options","").upper() in ["DENY", "SAMEORIGIN"]
        data["checks"]["cookies"] = parse_cookies(hdrs)
        try:
            r2 = http_get(url, timeout=args.timeout, allow_redirects=True, retries=args.retries, backoff=0.5)
            data["checks"]["redirected_to_https"] = r2.url.startswith("https://")
        except Exception:
            data["checks"]["redirected_to_https"] = False
        data["status_code"] = r.status_code
    except Exception as e:
        data["error"] = str(e)
    meta = {"script": "http_security_check", "ts": timestamp(), "host": host, "version": "1.0"}
    path = write_json("http_security", f"security_{host.replace(':','_')}", data, meta)
    print(path)

if __name__ == "__main__":
    from support import safe_main
    safe_main(main)
