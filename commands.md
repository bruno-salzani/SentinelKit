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
