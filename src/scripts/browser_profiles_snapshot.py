import os
import json
from support import results_dir, timestamp

def chrome_info():
    home = os.path.expanduser("~")
    base = os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
    info = {"path": base, "profiles": []}
    try:
        ls = os.listdir(base)
    except Exception:
        return info
    for name in ls:
        p = os.path.join(base, name)
        if os.path.isdir(p) and (name.startswith("Default") or name.startswith("Profile")):
            local_state = os.path.join(base, "Local State")
            ver = None
            try:
                with open(local_state, "r", encoding="utf-8") as f:
                    j = json.load(f)
                    ver = j.get("browser", {}).get("last_version")
            except Exception:
                pass
            ext_dir = os.path.join(p, "Extensions")
            exts = []
            try:
                for e in os.listdir(ext_dir):
                    exts.append(e)
            except Exception:
                pass
            info["profiles"].append({"name": name, "version": ver, "extensions": exts})
    return info

def edge_info():
    home = os.path.expanduser("~")
    base = os.path.join(home, "AppData", "Local", "Microsoft", "Edge", "User Data")
    info = {"path": base, "profiles": []}
    try:
        ls = os.listdir(base)
    except Exception:
        return info
    for name in ls:
        p = os.path.join(base, name)
        if os.path.isdir(p) and (name.startswith("Default") or name.startswith("Profile")):
            ext_dir = os.path.join(p, "Extensions")
            exts = []
            try:
                for e in os.listdir(ext_dir):
                    exts.append(e)
            except Exception:
                pass
            info["profiles"].append({"name": name, "extensions": exts})
    return info

def firefox_info():
    home = os.path.expanduser("~")
    base = os.path.join(home, "AppData", "Roaming", "Mozilla", "Firefox")
    profiles_ini = os.path.join(base, "profiles.ini")
    info = {"path": base, "profiles": []}
    try:
        with open(profiles_ini, "r", encoding="utf-8") as f:
            txt = f.read()
        names = []
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith("Name="):
                names.append(s.split("=",1)[1])
        for n in names:
            info["profiles"].append({"name": n})
    except Exception:
        pass
    return info

def main():
    data = {
        "chrome": chrome_info(),
        "edge": edge_info(),
        "firefox": firefox_info()
    }
    out_dir = results_dir("browser")
    path = os.path.join(out_dir, f"browser_{timestamp()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(path)

if __name__ == "__main__":
    main()
