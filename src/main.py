import sys
import os
import subprocess
import time
import platform

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(r"""
   _____            _   _            _ _  ___ _   
  / ____|          | | (_)          | | |/ (_) |  
 | (___   ___ _ __ | |_ _ _ __   ___| | ' / _| |_ 
  \___ \ / _ \ '_ \| __| | '_ \ / _ \ |  < | | __|
  ____) |  __/ | | | |_| | | | |  __/ | . \| | |_ 
 |_____/ \___|_| |_|\__|_|_| |_|\___|_|_|\_\_|\__|
                                                  
      Cyber-Security Learning Toolkit
    """)

def run_script(script_name, args=[]):
    """Runs a script from the src/scripts directory."""
    # Determine absolute path to the script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, "scripts", script_name)
    
    # Check if script exists
    if not os.path.exists(script_path):
        print(f"[!] Error: Script not found at {script_path}")
        input("Press Enter to continue...")
        return

    cmd = [sys.executable, script_path] + args
    
    print(f"\n[*] Launching {script_name}...")
    try:
        # For .pyw scripts or specific interactive tools, we might want a new window
        # specifically on Windows if it's a GUI app or long running background process
        if script_name.endswith('.pyw') or script_name == 'device_access.py':
            if platform.system() == "Windows":
                creationflags = subprocess.CREATE_NEW_CONSOLE
                subprocess.Popen(cmd, creationflags=creationflags)
                print(f"[+] Started {script_name} in a new window.")
            else:
                # Fallback for non-Windows (though this kit is Windows focused)
                subprocess.Popen(cmd)
                print(f"[+] Started {script_name} in background.")
            
            # Brief pause to let the user read the message
            time.sleep(1.5)
        else:
            # Run blocking for standard scripts so we can see output
            subprocess.run(cmd)
            input("\nPress Enter to return to menu...")
            
    except KeyboardInterrupt:
        print("\n[!] Interrupted.")
    except Exception as e:
        print(f"\n[!] Error running script: {e}")
        input("Press Enter to continue...")

def main_menu():
    while True:
        clear_screen()
        print_banner()
        print("Select a module to launch:")
        print("  [1] Network Scanner (ARP & Local Info)")
        print("  [2] Port Scanner (Check Open Ports)")
        print("  [3] System Monitor Dashboard")
        print("  [4] Device Details (System Specs)")
        print("  [5] File System Scanner")
        print("  [6] Camera Access (Viewer)")
        print("  [7] Keyboard Input Recorder (Keylogger UI)")
        print("  [8] Remote Desktop (Host Mode)")
        print("  [9] Remote Desktop (Viewer Mode)")
        print("  [10] Dump WiFi & System Credentials")
        print("  [11] SSH/SFTP File Browser")
        print("  [12] Audio Recorder")
        print("  [13] WiFi Networks Scanner")
        print("  [14] Process Top Viewer")
        print("  [15] Screenshot Capture")
        print("  [16] Clipboard Dump")
        print("  [17] DNS Cache Dump")
        print("  [18] LAN Ping Sweep")
        print("  [19] Banner Grabber")
        print("  [20] System Monitor Logger")
        print("  [L] Quick Local Test (Server + Viewer)")
        print("  [0] Exit")
        
        choice = input("\nfsociety> ").strip().lower()
        
        if choice == '1':
            run_script("network_info.py")
        
        elif choice == '2':
            target = input("Enter Target IP to scan: ").strip()
            if target:
                mode = input("Scan mode [common/all] (default: common): ").strip().lower()
                args = [target]
                if mode == 'all':
                    args.extend(["--mode", "all"])
                run_script("port_scanner.py", args)
            else:
                print("[!] Target IP is required.")
                time.sleep(1)
            
        elif choice == '3':
            run_script("system_monitor.py")
            
        elif choice == '4':
            run_script("device_details.py")
            
        elif choice == '5':
            path = input("Enter path to scan (Press Enter for User Home): ").strip()
            args = []
            if path:
                args = ["--path", path]
            run_script("device_files.py", args)
            
        elif choice == '6':
            run_script("camera_access.py")
            
        elif choice == '7':
            print("Starting Keylogger with UI in a new window...")
            run_script("keyboard-inputs.pyw")
            
        elif choice == '8':
            print("Starting Remote Desktop Host Server...")
            run_script("device_access.py")
            
        elif choice == '9':
            ip = input("Enter Target IP Address: ").strip()
            if ip:
                run_script("remote_viewer.py", [ip])
            else:
                print("[!] IP Address is required.")
                time.sleep(1)
                
        elif choice == '10':
            print("Dumping credentials (requires Admin for best results)...")
            run_script("credentials.py", ["--elevate"])
            
        elif choice == '11':
            print("\n--- SSH Browser ---")
            host = input("Host IP: ").strip()
            if not host:
                continue
            user = input("Username: ").strip()
            password = input("Password (optional): ").strip()
            
            args = [host, user]
            if password:
                args.extend(["--password", password])
                
            # Ask for optional remote path
            remote_path = input("Remote Path (default /): ").strip()
            if remote_path:
                args.extend(["--remote", remote_path])
                
            run_script("ssh_file_browser.py", args)
        
        elif choice == '12':
            run_script("audio_recorder.py")
        
        elif choice == '13':
            run_script("wifi_scan.py")
        
        elif choice == '14':
            run_script("process_monitor.py")
        
        elif choice == '15':
            run_script("screenshot.py")
        
        elif choice == '16':
            run_script("clipboard_dump.py")
        
        elif choice == '17':
            run_script("dns_cache_dump.py")
        
        elif choice == '18':
            base = input("Base subnet (e.g., 192.168.1) [Enter for auto]: ").strip()
            args = [base] if base else []
            run_script("ping_sweep.py", args)
        
        elif choice == '19':
            host = input("Host: ").strip()
            ports = input("Ports (comma-separated, e.g., 80,22,25): ").strip()
            if host and ports:
                run_script("banner_grabber.py", [host, ports])
            else:
                print("[!] Host and Ports are required.")
                time.sleep(1)
        
        elif choice == '20':
            dur = input("Duration seconds (optional): ").strip()
            args = [dur] if dur else []
            run_script("system_monitor_log.py", args)
            
        elif choice == 'l':
            print("Launching Local Session (Server + Viewer)...")
            run_script("launch_session.py")

        elif choice == '0':
            print("Exiting...")
            sys.exit()
        else:
            print("Invalid selection.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit()
