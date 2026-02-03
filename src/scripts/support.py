import os
from datetime import datetime
import json
import time
VERSION = "1.0"

def format_size(bytes_size: float) -> str:
    try:
        bytes_size = float(bytes_size)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_size < 1024:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.2f} PB"
    except (ValueError, TypeError):
        return "0 B"

VIDEO_PORT = 5000
CONTROL_PORT = 5001
CHUNK_SIZE = 4096
USER_AGENT = "SentinelKit/1.0"

def timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    return datetime.now().strftime(fmt)

def results_dir(*parts: str) -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "results", *parts)
    os.makedirs(path, exist_ok=True)
    return path

def write_json(subdir: str, prefix: str, data: dict, meta: dict = None) -> str:
    out_dir = results_dir(subdir)
    ts = timestamp()
    path = os.path.join(out_dir, f"{prefix}_{ts}.json")
    envelope = {
        "meta": {
            "script": prefix,
            "ts": ts,
            "version": (meta.get("version") if meta else VERSION),
            "host": (meta.get("host") if meta else None)
        },
        "data": data
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2)
    return path

def http_get(url: str, timeout: float = 5.0, allow_redirects: bool = False, headers: dict = None, retries: int = 0, backoff: float = 0.5):
    import requests
    h = {"User-Agent": USER_AGENT}
    if headers:
        h.update(headers)
    last_exc = None
    for attempt in range(retries + 1):
        try:
            return requests.get(url, timeout=timeout, allow_redirects=allow_redirects, headers=h)
        except Exception as e:
            last_exc = e
            if attempt < retries:
                time.sleep(backoff * (2 ** attempt))
    if last_exc:
        raise last_exc

def write_csv(subdir: str, prefix: str, headers: list, rows: list) -> str:
    out_dir = results_dir(subdir)
    path = os.path.join(out_dir, f"{prefix}_{timestamp()}.csv")
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if headers:
            w.writerow(headers)
        for r in rows:
            w.writerow(r)
    return path

def snapshot_dir(root_path: str, do_hash: bool = False, include: list = None, exclude: list = None) -> dict:
    import hashlib
    import fnmatch
    files = {}
    root_path = os.path.abspath(root_path)
    for dirpath, dirnames, filenames in os.walk(root_path):
        if exclude:
            dirnames[:] = [d for d in dirnames if not any(fnmatch.fnmatch(d, pat) for pat in exclude)]
        for name in filenames:
            if include and not any(fnmatch.fnmatch(name, pat) for pat in include):
                continue
            full = os.path.join(dirpath, name)
            try:
                st = os.stat(full)
                rel = os.path.relpath(full, root_path)
                info = {"size": st.st_size, "mtime": st.st_mtime}
                if do_hash:
                    h = hashlib.sha256()
                    with open(full, "rb") as f:
                        while True:
                            b = f.read(8192)
                            if not b:
                                break
                            h.update(b)
                    info["sha256"] = h.hexdigest()
                files[rel] = info
            except Exception:
                continue
    return {"root": root_path, "count": len(files), "files": files}

def diff_snapshots(old: dict, new: dict) -> dict:
    old_files = old.get("files", {}) if old else {}
    new_files = new.get("files", {}) if new else {}
    added = [p for p in new_files.keys() if p not in old_files]
    removed = [p for p in old_files.keys() if p not in new_files]
    modified = []
    for p in new_files.keys():
        if p in old_files:
            o = old_files[p]
            n = new_files[p]
            if (o.get("size") != n.get("size")) or (o.get("mtime") != n.get("mtime")) or (o.get("sha256") != n.get("sha256")):
                modified.append({"path": p, "old": o, "new": n})
    return {"added": added, "removed": removed, "modified": modified}

def safe_main(fn):
    import sys
    try:
        fn()
    except KeyboardInterrupt:
        print("Operação cancelada pelo usuário")
        sys.exit(0)
    except SystemExit as e:
        raise
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)

def ensure_dependencies(packages: list):
    import importlib
    import subprocess
    import sys
    
    # Mapping for packages where import name != pip name
    PIP_MAPPING = {
        "cv2": "opencv-python",
        "PIL": "Pillow",
        "win32api": "pywin32",
        "win32con": "pywin32",
        "win32security": "pywin32",
        "win32net": "pywin32",
        "sounddevice": "sounddevice",
        "pysnmp": "pysnmp",
        "smbprotocol": "smbprotocol",
        "cryptography": "cryptography",
        "paramiko": "paramiko",
        "requests": "requests",
        "psutil": "psutil",
        "pynput": "pynput",
        "mss": "mss",
        "numpy": "numpy",
        "pyautogui": "pyautogui"
    }
    
    missing = []
    for pkg in packages:
        # Check if we can import it
        try:
            importlib.import_module(pkg)
        except ImportError:
            # If import fails, find the pip name
            pip_name = PIP_MAPPING.get(pkg, pkg)
            if pip_name not in missing:
                missing.append(pip_name)
    
    if missing:
        print(f"Instalando dependências ausentes: {', '.join(missing)}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("Dependências instaladas com sucesso.")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao instalar dependências: {e}")
            sys.exit(1)

