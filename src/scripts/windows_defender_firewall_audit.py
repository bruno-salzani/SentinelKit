import os
import sys
import json
import subprocess
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
    data = {}
    mp = run_ps("Get-MpComputerStatus | ConvertTo-Json -Depth 3")
    data["defender"] = safe_load_json(mp)
    fw_profiles = run_ps("Get-NetFirewallProfile | Select Name, Enabled, DefaultInboundAction, DefaultOutboundAction | ConvertTo-Json -Depth 3")
    data["firewall_profiles"] = safe_load_json(fw_profiles)
    sec_count = run_ps("$t=(Get-Date).AddHours(-24);(Get-WinEvent -LogName Security -FilterHashtable @{StartTime=$t} | Measure-Object).Count | ConvertTo-Json")
    sys_count = run_ps("$t=(Get-Date).AddHours(-24);(Get-WinEvent -LogName System -FilterHashtable @{StartTime=$t} | Measure-Object).Count | ConvertTo-Json")
    try:
        data["recent_events"] = {"security_last_24h": json.loads(sec_count), "system_last_24h": json.loads(sys_count)}
    except Exception:
        data["recent_events"] = {"security_last_24h": sec_count, "system_last_24h": sys_count}
    meta = {"script": "windows_defender_firewall_audit", "ts": timestamp(), "host": None, "version": "1.0"}
    path = write_json("defender_firewall", "defender_firewall", data, meta)
    print(path)

if __name__ == "__main__":
    from support import safe_main
    safe_main(main)
