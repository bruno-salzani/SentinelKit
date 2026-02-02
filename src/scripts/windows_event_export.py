import argparse
import subprocess
from support import write_json, timestamp

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channel", default="System")
    ap.add_argument("--hours", type=int, default=4)
    ap.add_argument("--level", default="")
    args = ap.parse_args()
    channel = args.channel
    hours = args.hours
    level = args.level or None
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        f"$h=(Get-Date).AddHours(-{hours});"
        f"$f=Get-WinEvent -FilterHashtable @{{LogName='{channel}';StartTime=$h}};"
        f"if('{level}' -ne $null -and '{level}' -ne ''){{$f=$f|Where-Object {{$_.LevelDisplayName -eq '{level}'}}}};"
        "$f|Select-Object TimeCreated,Id,LevelDisplayName,ProviderName,Message|ConvertTo-Json -Depth 4"
    ]
    data = {}
    try:
        out = subprocess.check_output(cmd, shell=False).decode("utf-8", errors="ignore")
        data = {"channel": channel, "hours": hours, "level": level, "events": []}
        import json
        try:
            obj = json.loads(out)
            if isinstance(obj, list):
                data["events"] = obj
            else:
                data["events"] = [obj]
        except Exception:
            data["raw"] = out
    except Exception as e:
        data = {"error": str(e)}
    meta = {"script": "windows_event_export", "ts": timestamp(), "host": None, "version": "1.0"}
    path = write_json("event_logs", f"events_{channel}", data, meta)
    print(path)

if __name__ == "__main__":
    main()
