import json
import pathlib
import sys
import argparse
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

def scan_directory(directory, system_dirs_list, max_depth=3, current_depth=0):
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
                    result["files"].append({
                        "name": entry.name,
                        "size": format_size(stat.st_size),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except OSError:
                    continue
            elif entry.is_dir():
                # Recursively scan subdirectories
                sub_result = scan_directory(entry, system_dirs_list, max_depth, current_depth + 1)
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
    
    args = parser.parse_args()
    
    root_path = pathlib.Path(args.path)
    
    if not root_path.exists():
        print(f"Error: Path {root_path} does not exist.")
        return

    print(f"Scanning {root_path} with max depth {args.depth}...")
    
    platform_name = sys.platform
    system_dirs = SYSTEM_DIRS.get(platform_name, [])
    
    data = scan_directory(root_path, system_dirs, max_depth=args.depth)
    
    # Ensure results directory exists if default is used or if path is inside a directory
    output_path = pathlib.Path(args.output)
    if output_path.parent.name:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Scan complete. Results saved to {args.output}")
    except IOError as e:
        print(f"Error saving output: {e}")

if __name__ == "__main__":
    main()
