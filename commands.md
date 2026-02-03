# Script Usage Guide

This document provides instructions on how to run each script in the `src/scripts` directory.

## Prerequisites

Before running any script, ensure you have installed the required dependencies:

```bash
pip install -r requirements.txt
```

## GUI Launcher (Recommended)

The easiest way to explore and run all tools is via the integrated GUI.

**Command:**
```bash
python src/scripts/gui_launcher.py
```

---

## Network & Protocols

### SNMP Inventory (`snmp_inventory.py`)
Performs a basic SNMP inventory (System Description, Uptime, Interfaces) on a target.

**Command:**
```bash
python src/scripts/network/snmp_inventory.py <TARGET_IP> --community public --port 161
```

### SMB Enumerator (`smb_shares_enumerator.py`)
Lists SMB shares and attempts to check permissions and list files.
Supports authentication for advanced enumeration.

**Command:**
```bash
python src/scripts/smb_shares_enumerator.py <TARGET_IP> [--user USER] [--password PASS]
```

### RDP & WinRM Probe (`rdp_winrm_probe.py`)
Probes for Remote Desktop (3389) and WinRM (5985/5986) services, checking for authentication schemes and TLS certificates.

**Command:**
```bash
python src/scripts/rdp_winrm_probe.py <TARGET_IP>
```

---

## Web & TLS

### HTTP Security Check (`http_security_check.py`)
Analyzes HTTP headers for security best practices (HSTS, CSP, Cookies flags) and redirect behavior.

**Command:**
```bash
python src/scripts/web/http_security_check.py <TARGET_HOST>
```

### TLS Inspector (`tls_cert_inspector.py`)
Retrieves TLS certificate chain, checks validity dates, and attempts CRL/OCSP revocation checks.

**Command:**
```bash
python src/scripts/web/tls_cert_inspector.py <TARGET_HOST> --port 443
```

---

## System & Security

### Windows Defender & Firewall Audit (`windows_defender_firewall_audit.py`)
Exports the status of Windows Defender, Firewall Profiles, and recent security event statistics.

**Command:**
```bash
python src/scripts/windows_defender_firewall_audit.py
```

### Services & Drivers Audit (`services_drivers_audit.py`)
Lists services and drivers, filtering for auto-start or specific states.

**Command:**
```bash
python src/scripts/services_drivers_audit.py --svc-starttype Automatic --svc-state Running
```

### Sensitive Directory Monitor (`sensitive_dir_monitor.py`)
Creates a snapshot of a directory and compares it with a previous snapshot to detect changes (added/removed/modified files). Supports hashing.

**Command:**
```bash
python src/scripts/sensitive_dir_monitor.py --path "C:\Users\Admin\Desktop" --hash
```

---

## Remote Desktop Tools

### 1. Remote Host (`device_access.py`)
This script acts as the **Server**. Run this on the computer you want to access.

**Command:**
```bash
python src/scripts/device_access.py
```

### 2. Remote Viewer (`remote_viewer.py`)
This script acts as the **Client**.

**Command:**
```bash
python src/scripts/remote_viewer.py <TARGET_IP>
```

---

## Other Utilities

### Network Info Scanner (`network_info.py`)
Gathers public IP, local interfaces, WiFi info, and ARP table.

**Command:**
```bash
python src/scripts/network_info.py
```

### Device Details (`device_details.py`)
Gathers detailed system hardware and OS information.

**Command:**
```bash
python src/scripts/device_details.py
```
