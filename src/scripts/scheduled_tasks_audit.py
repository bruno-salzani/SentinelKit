import os
import subprocess
from support import results_dir, timestamp

def list_tasks():
    try:
        out = subprocess.check_output(["schtasks","/Query","/V","/FO","LIST"], shell=False).decode("utf-8", errors="ignore")
        tasks = []
        t = {}
        for line in out.splitlines():
            s = line.strip()
            if not s:
                if t:
                    tasks.append(t)
                t = {}
                continue
            if ":" in s:
                k,v = s.split(":",1)
                t[k.strip()] = v.strip()
        if t:
            tasks.append(t)
        return tasks
    except Exception:
        return []

def main():
    tasks = list_tasks()
    failures = [t for t in tasks if "Last Run Result" in t and "0x0" not in t.get("Last Run Result","")]
    data = {"tasks": tasks, "failures": failures}
    out_dir = results_dir("scheduled_tasks")
    path = os.path.join(out_dir, f"tasks_{timestamp()}.json")
    import json
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    try:
        if os.name == "nt":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass
    print(path)

if __name__ == "__main__":
    main()
