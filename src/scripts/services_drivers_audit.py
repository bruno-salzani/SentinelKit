import os
import sys
import json
import subprocess
import argparse
from support import write_json, timestamp

def run_ps(cmd: str) -> str:
    try:
        out = subprocess.check_output(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-Command", cmd], shell=False)
        return out.decode("utf-8", errors="ignore")
    except Exception as e:
        return json.dumps({"error": str(e)})

def safe_load_json(txt: str):
    try:
        return json.loads(txt)
    except Exception:
        return {"raw": txt}

def main():
    ap = argparse.ArgumentParser(description="Auditoria de serviços e drivers")
    ap.add_argument("--svc-starttype", type=str, default="", help="Filtro StartType de serviços (Automatic/Manual/Disabled/All)")
    ap.add_argument("--svc-state", type=str, default="", help="Filtro Status de serviços (Running/Stopped/All)")
    ap.add_argument("--drv-startmode", type=str, default="", help="Filtro StartMode de drivers (Auto/Manual/All)")
    ap.add_argument("--drv-state", type=str, default="", help="Filtro State de drivers (Running/Stopped/All)")
    args = ap.parse_args()
    svc_filters = []
    if args.svc_starttype and args.svc_starttype.lower() != "all":
        svc_filters.append(f"$_.StartType -eq '{args.svc_starttype}'")
    if args.svc_state and args.svc_state.lower() != "all":
        svc_filters.append(f"$_.Status -eq '{args.svc_state}'")
    svc_where = ""
    if svc_filters:
        svc_where = " | Where-Object {" + " -and ".join(svc_filters) + "}"
    services = run_ps(f"Get-Service{svc_where} | Select Name, DisplayName, Status, StartType | ConvertTo-Json -Depth 3")
    drv_filters = []
    if args.drv_startmode and args.drv_startmode.lower() != "all":
        drv_filters.append(f"$_.StartMode -eq '{args.drv_startmode}'")
    if args.drv_state and args.drv_state.lower() != "all":
        drv_filters.append(f"$_.State -eq '{args.drv_state}'")
    drv_where = ""
    if drv_filters:
        drv_where = " | Where-Object {" + " -and ".join(drv_filters) + "}"
    drivers = run_ps(f"Get-CimInstance Win32_SystemDriver{drv_where} | Select Name, State, StartMode, PathName | ConvertTo-Json -Depth 3")
    data = {
        "filters": {
            "services": {"StartType": args.svc_starttype or "All", "Status": args.svc_state or "All"},
            "drivers": {"StartMode": args.drv_startmode or "All", "State": args.drv_state or "All"}
        },
        "services": safe_load_json(services),
        "drivers": safe_load_json(drivers)
    }
    meta = {"script": "services_drivers_audit", "ts": timestamp(), "host": None, "version": "1.0"}
    path = write_json("services_drivers", "services_drivers", data, meta)
    print(path)

if __name__ == "__main__":
    from support import safe_main
    safe_main(main)
