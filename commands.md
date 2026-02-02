# Script Usage Guide

This document provides instructions on how to run each script in the `src/scripts` directory.

## Prerequisites

Before running any script, ensure you have installed the required dependencies:

```bash
pip install -r requirements.txt
```

## Remote Desktop Tools

### 1. Quick Start (Local Testing)
To verify the remote desktop functionality on your own machine, you can run the launcher script.
This will open two new windows: one for the server (host) and one for the client (viewer).

**Command:**
```bash
python src/scripts/launch_session.py
```

### 2. Remote Host (`device_access.py`)
This script acts as the **Server**. Run this on the computer you want to access (the victim/target machine).
It captures the screen and listens for mouse/keyboard control commands.

**Command:**
```bash
python src/scripts/device_access.py
```
*The server will start listening on port 5000 (Video) and 5001 (Control).*

### 3. Remote Viewer (`remote_viewer.py`)
This script acts as the **Client**. Run this on your computer to see and control the remote machine.

**Command:**
```bash
python src/scripts/remote_viewer.py <TARGET_IP>
```

**Example:**
```bash
python src/scripts/remote_viewer.py 192.168.1.10
```
*A window will open showing the remote screen. Mouse interactions on this window will be sent to the remote machine.*

---

## Network & System Utilities

### 4. Network Info Scanner (`network_info.py`)
Gathers comprehensive information about the network you are connected to.
- **Public Info:** IP, City, Country, ISP.
- **WiFi Info:** SSID, Signal Strength, Channel.
- **Local Network:** Scans for other devices (ARP table).
- **Interfaces:** Details about all network adapters.

**Command:**
```bash
python src/scripts/network_info.py
```
*Results are saved to the `results/` folder.*

### 5. Device Details (`device_details.py`)
Gathers detailed information about the system (OS, CPU, Memory, Disk, Network) and saves it to a JSON file in the `results/` folder.

**Command:**
```bash
python src/scripts/device_details.py
```

### 6. Device Files Scanner (`device_files.py`)
Scans a directory structure and creates a JSON report of files and folders.

**Command (Default - scans user home directory):**
```bash
python src/scripts/device_files.py
```

**Command (Custom path and depth):**
```bash
python src/scripts/device_files.py --path "C:/Users/YourUser/Documents" --depth 3 --output results/filesystem.json
```

### 7. Camera Access (`camera_access.py`)
Lists available cameras and allows you to view the feed from a selected camera.

**Command:**
```bash
python src/scripts/camera_access.py
```
*Follow the on-screen prompts to select a camera. Press 'q' to quit the video feed.*

### 8. Router Details (`router_details.py`)
Attempts to login to a router and retrieve status information.

**Command:**
```bash
python src/scripts/router_details.py <ROUTER_IP> --username admin
```

If the router’s web UI requires JavaScript (shows a “browser does not support JavaScript” message), use JS mode:
```bash
python src/scripts/router_details.py <ROUTER_IP> --username admin --mode js
```
Results (summary JSON, raw HTML pages, and screenshots) are saved in the `results/` folder with a timestamped name.

**Example (Intelbras / admin credentials):**
```bash
python src/scripts/router_details.py http://10.0.0.1/ --username admin --password sucesso34 --mode js
```
If `10.0.0.1` is unreachable on your LAN, try the default gateway instead (commonly `10.0.1.1`):
```bash
python src/scripts/router_details.py http://10.0.1.1/ --username admin --password sucesso34 --mode js
```

### 9. Router Backup Restore (`router_access.py`)
Connects to a router via SSH to restore a backup file.

**Command:**
```bash
python src/scripts/router_access.py <HOST_IP> <USERNAME> <BACKUP_FILENAME>
```

### 10. SSH File Browser (`ssh_file_browser.py`)
List files over SSH/SFTP with sizes and download files or whole directories.

**List remote directory (depth=3):**
```bash
python src/scripts/ssh_file_browser.py <HOST> <USERNAME> --password <PASSWORD> --remote / --depth 3
```
Saves JSON to `results/ssh_listing_<HOST>_<timestamp>.json`.

**Download a single file:**
```bash
python src/scripts/ssh_file_browser.py <HOST> <USERNAME> --password <PASSWORD> --download /path/to/file --dest results/downloads
```

**Download a whole directory (recursive):**
```bash
python src/scripts/ssh_file_browser.py <HOST> <USERNAME> --password <PASSWORD> --download-dir /var/log --dest results/downloads
```

You can also use `--key <PRIVATE_KEY_PATH>` and filter names with `--pattern "<regex>"`.

**Auto-detect local host and username using latest network_info.json:**
```bash
python src/scripts/ssh_file_browser.py --auto --depth 3
```
Or specify the network info file explicitly:
```bash
python src/scripts/ssh_file_browser.py --auto --network-file results/network_info_20260124_165940.json --depth 3
```

**Probe SSH port reachability:**
```bash
python src/scripts/ssh_file_browser.py --auto --probe
```
If closed, enable OpenSSH Server (Windows Features), start service `sshd`, and allow TCP 22 in firewall:
- PowerShell (admin): 
  - Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
  - Start-Service sshd
  - Set-Service -Name sshd -StartupType Automatic
  - New-NetFirewallRule -Name OpenSSH -DisplayName OpenSSH -Enabled True -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22

**Enable OpenSSH automatically (run as Administrator) and probe:**
```bash
python src/scripts/ssh_file_browser.py --auto --enable-ssh
```

**Authentication tips**
- If you don’t pass `--password`, the script will prompt for it.
- Username formats to try on Windows: `bruno`, `.\bruno`, `DESKTOP-4ELVJ8D\bruno`.

## How To Use

- Start the host:
  
  ```
  python src/scripts/device_access.py
  ```
- Connect the viewer:
  
  ```
  python src/scripts/remote_viewer.py <TARGET_IP>
  ```
- Quick local test:
  
  ```
  python src/scripts/launch_session.py
  ```

## Interactive Menu

Launch the unified menu to access all tools:
```bash
python src/main.py
```

## New Tools

### Port Scanner (`port_scanner.py`)
Scan common ports or 1–1024 on a target:
```bash
python src/scripts/port_scanner.py <TARGET_IP> --mode common
python src/scripts/port_scanner.py <TARGET_IP> --mode all
```

### System Monitor Dashboard (`system_monitor.py`)
Terminal dashboard showing CPU, RAM and Disk usage (refresh every second). Press Q to quit:
```bash
python src/scripts/system_monitor.py
```

### Audio Recorder (`audio_recorder.py`)
Record microphone audio until you press Q and save to WAV:
```bash
python src/scripts/audio_recorder.py
```

### Camera Snapshots (extra)
Inside the camera viewer, press S to save a snapshot to `results/camera_captures`.

### WiFi Networks Scanner (`wifi_scan.py`)
List nearby WiFi networks (Windows):
```bash
python src/scripts/wifi_scan.py
```

### Process Top Viewer (`process_monitor.py`)
Show top processes by CPU and memory, refresh each second, press Q to quit:
```bash
python src/scripts/process_monitor.py
```

### Screenshot Capture (`screenshot.py`)
Capture the current screen and save to `results/screenshots`:
```bash
python src/scripts/screenshot.py
```

### Clipboard Dump (`clipboard_dump.py`)
Dump clipboard text to `results/clipboard`:
```bash
python src/scripts/clipboard_dump.py
```

### DNS Cache Dump (`dns_cache_dump.py`)
Export local DNS cache to `results/dns_cache_*.json`:
```bash
python src/scripts/dns_cache_dump.py
```

### LAN Ping Sweep (`ping_sweep.py`)
Scan a /24 subnet for alive hosts. Auto-detects local subnet if not provided:
```bash
python src/scripts/ping_sweep.py              # auto subnet
python src/scripts/ping_sweep.py 192.168.1    # specific base
```

### Banner Grabber (`banner_grabber.py`)
Grab service banners from ports:
```bash
python src/scripts/banner_grabber.py <HOST> 80,22,25
```

### System Monitor Logger (`system_monitor_log.py`)
Log CPU and memory to CSV every second. Optional duration in seconds:
```bash
python src/scripts/system_monitor_log.py
python src/scripts/system_monitor_log.py 120
```

### Service Fingerprint (`service_fingerprint.py`)
Run port scan and banner grabbing, saving a consolidated report:
```bash
python src/scripts/service_fingerprint.py <TARGET> common
python src/scripts/service_fingerprint.py <TARGET> all
```

### Task Scheduler (`task_scheduler.py`)
Create, delete, and list Windows scheduled tasks:
```bash
python src/scripts/task_scheduler.py create Sentinel_Ping "python c:\Users\bruno\Desktop\SentinelKit\src\scripts\ping_sweep.py" 10:00 DAILY
python src/scripts/task_scheduler.py delete Sentinel_Ping
python src/scripts\task_scheduler.py list
```

### GUI Launcher (`gui_launcher.py`)
Graphical interface with buttons and tooltips for all scripts:
```bash
python src/scripts/gui_launcher.py
```

## New UX Features

- Search field: type to filter matching tools; non-matching buttons are disabled.
- Category headers: tools grouped visually (Network, System, Windows, Web, SSH/SFTP, Utilities).
- Open Latest Result: opens the most recent file in a chosen subfolder under `results/`.

## JSON Output Schema (Envelope)

- All major outputs now use a common envelope:
  - `meta`: `{ script, ts, version, host }`
  - `data`: script-specific payload
- Example:
```json
{
  "meta": { "script": "tls_cert_inspector", "ts": "20260202_121314", "version": "1.0", "host": "example.com" },
  "data": { "cert": { "...": "..." }, "expires_in_days": 27 }
}
```

## Updated Commands (Argparse)

### SMB Shares Enumerator (`smb_shares_enumerator.py`)
```bash
python src/scripts/smb_shares_enumerator.py --host <HOST_OPTIONAL>
```

### Windows Event Logs Export (`windows_event_export.py`)
```bash
python src/scripts/windows_event_export.py --channel System --hours 4 --level Error
```

### Port Range Profiler (`port_range_profiler.py`)
```bash
python src/scripts/port_range_profiler.py <HOST> <START-END> --timeout 1.5
```

### HTTP Directory Bruteforce (advanced)
```bash
python src/scripts/http_directory_bruteforce.py http://example.com 200 --paths "admin/,login/,robots.txt" --concurrency 5 --status 200,301,302,401,403 --timeout 5
python src/scripts/http_directory_bruteforce.py http://example.com 200 --paths-file @c:\paths.txt
```
