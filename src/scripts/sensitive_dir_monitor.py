import os
import sys
import json
import argparse
from support import snapshot_dir, diff_snapshots, write_json, timestamp

def main():
    ap = argparse.ArgumentParser(description="Monitor de diretório com snapshot+diff")
    ap.add_argument("--path", required=True, help="Diretório raiz a monitorar")
    ap.add_argument("--hash", action="store_true", help="Calcular SHA256 dos arquivos")
    ap.add_argument("--include", type=str, default="", help="Padrões de inclusão (csv, opcional)")
    ap.add_argument("--exclude", type=str, default="", help="Padrões de exclusão (csv, opcional)")
    ap.add_argument("--prev", type=str, default="", help="Snapshot anterior para diff (arquivo JSON, opcional)")
    args = ap.parse_args()
    root = args.path
    inc = [x.strip() for x in args.include.split(",") if x.strip()] if args.include else None
    exc = [x.strip() for x in args.exclude.split(",") if x.strip()] if args.exclude else None
    snap = snapshot_dir(root, do_hash=bool(args.hash), include=inc, exclude=exc)
    prev = None
    if args.prev:
        try:
            with open(args.prev, "r", encoding="utf-8") as f:
                prev = json.load(f)
        except Exception:
            prev = None
    diff = diff_snapshots(prev, snap) if prev else None
    data = {"root": root, "snapshot": snap, "diff_vs_prev": diff}
    safe = os.path.basename(root).replace(":", "_").replace("\\", "_").replace("/", "_") or "root"
    meta = {"script": "sensitive_dir_monitor", "ts": timestamp(), "host": None, "version": "1.0"}
    path = write_json("dir_monitor", f"snapshot_{safe}", data, meta)
    print(path)

if __name__ == "__main__":
    main()
