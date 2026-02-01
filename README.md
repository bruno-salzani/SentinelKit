# SentinelKit — Cyber‑Security Learning Toolkit

A practical toolkit to explore device, network, and user‑environment information on Windows, with a focus on ethical, consent‑based security learning. It includes local remote‑desktop demos, SSH/SFTP browsing, router interrogation tools, system and network scanners, and structured result outputs.

## Quick Start

- Install Python 3.10+ and ensure you can run PowerShell as Administrator when needed.
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- **Launch the Interactive Menu:**
  ```bash
  python src/main.py
  ```
- Most scripts save structured JSON and artifacts under `results/`.
- Detailed usage lives in [commands.md](./commands.md).

## Features

- Remote desktop demo (local or LAN) with screen capture and control.
- SSH/SFTP file browser with recursive listing, size reporting, and downloads.
- Network scanner and device/system inventory saved as JSON.
- Router interrogation (HTTP/JS and SSH paths) with snapshot archiving.
- Consent‑based keyboard input recorder with visible UI and 5‑second batching.
- Unified utilities and consistent output structure under `results/`.

## Scripts

- Remote host:
  ```bash
  python src/scripts/device_access.py
  ```
- Remote viewer:
  ```bash
  python src/scripts/remote_viewer.py <TARGET_IP>
  ```
- Quick local test:
  ```bash
  python src/scripts/launch_session.py
  ```
- SSH/SFTP browser:
  ```bash
  python src/scripts/ssh_file_browser.py <HOST> <USERNAME> --password <PASSWORD> --remote / --depth 3
  ```
- System details:
  ```bash
  python src/scripts/device_details.py
  ```
- Filesystem scan:
  ```bash
  python src/scripts/device_files.py --path "%USERPROFILE%" --depth 3
  ```
- Network info:
  ```bash
  python src/scripts/network_info.py
  ```
- Router details (HTTP/JS):
  ```bash
  python src/scripts/router_details.py <ROUTER_IP> --username admin --mode js
  ```
- Router access (SSH restore):
  ```bash
  python src/scripts/router_access.py <HOST_IP> <USERNAME> <BACKUP_FILENAME>
  ```
- Camera access:
  ```bash
  python src/scripts/camera_access.py
  ```
- Keyboard recorder (visible UI):
  ```bash
  python src/scripts/keyboard-inputs.pyw
  ```

## Installation

- Dependencies (Windows):
  - OpenCV, PyAutoGUI, MSS, Pillow for capture and UI control
  - Paramiko for SSH/SFTP
  - Psutil, Requests for system/network info
  - Selenium (optional, for router JS mode)
  - PyWin32 for Windows credential APIs
  - Pynput for keyboard recording
  - See [requirements.txt](./requirements.txt)

## Usage Highlights

- Remote desktop (host):
  ```bash
  python src/scripts/device_access.py
  ```
- Remote desktop (viewer):
  ```bash
  python src/scripts/remote_viewer.py <TARGET_IP>
  ```
- Quick local test:
  ```bash
  python src/scripts/launch_session.py
  ```
- SSH file listing (depth=3) and downloads:
  ```bash
  python src/scripts/ssh_file_browser.py <HOST> <USERNAME> --password <PASSWORD> --remote / --depth 3
  python src/scripts/ssh_file_browser.py <HOST> <USERNAME> --password <PASSWORD> --download /path/to/file --dest results/downloads
  python src/scripts/ssh_file_browser.py <HOST> <USERNAME> --password <PASSWORD> --download-dir /var/log --dest results/downloads
  ```
- Auto mode and probe (Windows OpenSSH):
  ```bash
  python src/scripts/ssh_file_browser.py --auto --probe
  python src/scripts/ssh_file_browser.py --auto --enable-ssh
  ```
- System and network reports:
  ```bash
  python src/scripts/device_details.py
  python src/scripts/network_info.py
  python src/scripts/device_files.py --path "%USERPROFILE%" --depth 3
  ```
- Keyboard recorder (visible UI, batches every 5s to `results/inputs`):
  ```bash
  python src/scripts/keyboard-inputs.pyw
  ```

## Results and Structure

- JSON and artifacts are saved to `results/` with timestamped filenames.
- Examples:
  - `results/ssh_listing_<host>_<timestamp>.json`
  - `results/network_info_<timestamp>.json`
  - `results/device_details_<timestamp>.json`
  - `results/inputs/keyboard_inputs_<date>.json`
- Source layout:
  - `src/scripts/` — individual tools
  - `src/scripts/support.py` — shared helpers/constants
  - `commands.md` — consolidated usage guide

## Windows OpenSSH Notes

- If probing SSH shows port 22 closed, enable OpenSSH Server, start `sshd`, and allow firewall inbound TCP 22.
- The SSH browser can attempt enablement automatically with `--enable-ssh` (run as Administrator).
- Username formats that work on Windows include `bruno`, `.\bruno`, or `MACHINE\bruno`.

## Security and Ethics

- Use only on systems you own or have explicit permission to test.
- The keyboard recorder provides a visible toggle UI and stores app‑scoped inputs; avoid covert recording.
- Do not hardcode or publish credentials. Examples must use placeholders.

## Troubleshooting

- SSH “Authentication failed”: verify username/password or use `--key`.
- SSH port closed: run `--auto --probe` and enable OpenSSH Server if needed.
- Admin operations: some features require elevated PowerShell; run as Administrator.
- Missing dependencies: re‑install with `pip install -r requirements.txt`.
- Keyboard accents/dead keys: the recorder handles common Portuguese layouts; update OS keyboard settings if needed.

## License

Educational use only. You are responsible for complying with local laws and regulations when using these tools.
