import json
import os
import pathlib
import sys
import argparse
import hashlib
from datetime import datetime
from support import format_size

# Common system directories to skip to speed up scanning or avoid permission issues
SYSTEM_DIRS = {
    "win32": [
        "Windows", "Program Files", "Program Files (x86)", "ProgramData",
        "$Recycle.Bin", "System Volume Information"
    ],
    "linux": [
        "bin", "boot", "dev", "etc", "lib", "lib64",
        "proc", "run", "sbin", "sys", "usr", "var"
    ],
    "darwin": [
        "System", "Library", "Applications", "Volumes", "private"
    ]
}

def is_system_path(path, system_dirs):
    """Checks if a path is a system directory."""
    parts = path.parts
    return any(part in system_dirs for part in parts)

def hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                b = f.read(8192)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()
    except Exception:
        return None

def scan_directory(directory, system_dirs_list, max_depth=3, current_depth=0, do_hash=False):
    """
    Recursively scans a directory.
    Returns a dictionary structure of the scan.
    """
    if current_depth > max_depth:
        return None

    result = {
        "path": str(directory),
        "files": [],
        "directories": []
    }
    
    try:
        # Scan current directory content
        for entry in directory.iterdir():
            # Skip system directories
            if entry.name in system_dirs_list or entry.name.startswith('.'):
                continue

            if entry.is_file():
                try:
                    stat = entry.stat()
                    item = {
                        "name": entry.name,
                        "size": format_size(stat.st_size),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
                    if do_hash:
                        item["sha256"] = hash_file(str(entry))
                    result["files"].append(item)
                except OSError:
                    continue
            elif entry.is_dir():
                # Recursively scan subdirectories
                sub_result = scan_directory(entry, system_dirs_list, max_depth, current_depth + 1, do_hash)
                if sub_result:
                    result["directories"].append(sub_result)

    except PermissionError:
        pass
    except OSError:
        pass

    return result

def main():
    parser = argparse.ArgumentParser(description="Scan directory structure.")
    parser.add_argument("--path", type=str, default=str(pathlib.Path.home()), help="Root directory to scan")
    parser.add_argument("--depth", type=int, default=2, help="Max recursion depth")
    parser.add_argument("--output", type=str, default="results/filesystem.json", help="Output JSON file")
    parser.add_argument("--hash", action="store_true", help="Compute SHA256 for files")
    
    args = parser.parse_args()
    
    root_path = pathlib.Path(args.path)
    
    if not root_path.exists():
        print(f"Error: Path {root_path} does not exist.")
        return

    print(f"Scanning {root_path} with max depth {args.depth}...")
    
    platform_name = sys.platform
    system_dirs = SYSTEM_DIRS.get(platform_name, [])
    
    data = scan_directory(root_path, system_dirs, max_depth=args.depth, do_hash=args.hash)
    
    # Normalize output path: ensure single project-level results folder and timestamped default
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_rel = "results/filesystem.json"
    output_path = pathlib.Path(args.output)
    if output_path.is_absolute():
        final_output = output_path
    else:
        if args.output == default_rel:
            out_dir = os.path.join(root, "results", "filesystem")
            os.makedirs(out_dir, exist_ok=True)
            final_output = pathlib.Path(os.path.join(out_dir, f"filesystem_{ts}.json"))
        else:
            final_output = pathlib.Path(os.path.join(root, args.output))
    final_output.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(str(final_output), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Scan complete. Results saved to {final_output}")
    except IOError as e:
        print(f"Error saving output: {e}")

if __name__ == "__main__":
    main()
