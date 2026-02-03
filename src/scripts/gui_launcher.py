import os
import sys
import subprocess
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
    def show(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") if self.widget.winfo_exists() else (0,0,0,0)
        x = x + self.widget.winfo_rootx() + 20
        y = y + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
    def hide(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

CATEGORIES_DIRS = ["network", "system", "remote", "ssh", "web", "windows", "utils"]

def script_path(name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(base_dir, name)
    if os.path.exists(p):
        return p
    for d in CATEGORIES_DIRS:
        cand = os.path.join(base_dir, d, name)
        if os.path.exists(cand):
            return cand
    return p

def run_cmd(cmd, new_window=False):
    try:
        if new_window and os.name == "nt":
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(cmd)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def run_simple(name, args=None, new_window=False):
    p = script_path(name)
    if not os.path.exists(p):
        messagebox.showerror("Error", f"Script not found: {name}")
        return
    cmd = [sys.executable, p] + (args or [])
    run_cmd(cmd, new_window=new_window)

def open_results_folder():
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(root, "results")
        os.makedirs(results_dir, exist_ok=True)
        if os.name == "nt":
            os.startfile(results_dir)
        else:
            subprocess.Popen(["xdg-open", results_dir])
    except Exception as e:
        messagebox.showerror("Error", str(e))

def open_specific_result(subdir):
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(root, "results", subdir)
        if not os.path.isdir(results_dir):
            messagebox.showinfo("Info", f"No results folder yet for '{subdir}'")
            return
        files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) if os.path.isfile(os.path.join(results_dir, f))]
        if not files:
            messagebox.showinfo("Info", "No files found.")
            return
        latest = max(files, key=lambda p: os.path.getmtime(p))
        if os.name == "nt":
            os.startfile(latest)
        else:
            subprocess.Popen(["xdg-open", latest])
    except Exception as e:
        messagebox.showerror("Error", str(e))

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SentinelKit — Security Suite")
        self.geometry("1100x850")
        self.minsize(1024, 768)
        
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except:
            pass
        self.style.configure("TButton", padding=(10, 6), font=("Segoe UI", 9))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        self.style.configure("Sub.TLabel", font=("Segoe UI", 10, "bold"), foreground="#555")
        
        # Header
        header = ttk.Frame(self, padding=(15, 10))
        header.pack(fill=tk.X)
        ttk.Label(header, text="SentinelKit Integrated Console", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(header, text="Open All Results", command=open_results_folder).pack(side=tk.RIGHT)
        
        # Search Bar
        search_frame = ttk.Frame(self, padding=(15, 5))
        search_frame.pack(fill=tk.X)
        ttk.Label(search_frame, text="Target IP/Host:").pack(side=tk.LEFT)
        self.target_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.target_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="Search Tool:").pack(side=tk.LEFT, padx=(20, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_tools)
        ttk.Entry(search_frame, textvariable=self.search_var, width=25).pack(side=tk.LEFT)

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tabs = {}
        self.tools = [] # List of all tool widgets to filter
        
        self.create_tabs()
        
    def create_tabs(self):
        categories = {
            "Network & Protocols": [
                ("Network Info", "network_info.py", "network", "Scanner básico (IP, WiFi, ARP)", []),
                ("Port Scanner", "port_scanner.py", "port_scan", "Verifica portas abertas", ["TARGET", "MODE"]),
                ("Ping Sweep", "ping_sweep.py", "ping_sweep", "Descobre hosts na subnet", ["SUBNET"]),
                ("Service Fingerprint", "service_fingerprint.py", "fingerprint", "Banner grabbing + Port Scan", ["TARGET", "MODE"]),
                ("SNMP Inventory", "snmp_inventory.py", "snmp", "Coleta dados via SNMP (Basic)", ["TARGET", "COMMUNITY", "PORT"]),
                ("SMB Enumerator", "smb_shares_enumerator.py", "smb", "Lista shares e permissões", ["TARGET", "USER", "PASS"]),
                ("RDP/WinRM Probe", "rdp_winrm_probe.py", "rdp_winrm", "Verifica serviços remotos Windows", ["TARGET"])
            ],
            "Web & TLS": [
                ("HTTP Security", "http_security_check.py", "http_security", "Headers, HSTS, Cookies, Redirects", ["TARGET", "PORT"]),
                ("TLS Inspector", "tls_cert_inspector.py", "tls", "Certificados, validade, cadeia, CRL", ["TARGET", "PORT"]),
                ("DNS Cache Dump", "dns_cache_dump.py", "dns", "Dump do cache DNS local", []),
            ],
            "System & Security": [
                ("Defender/Firewall", "windows_defender_firewall_audit.py", "defender_firewall", "Status e logs recentes", []),
                ("Services & Drivers", "services_drivers_audit.py", "services_drivers", "Auditoria de auto-start", ["FILTERS"]),
                ("System Monitor", "system_monitor.py", "", "Dashboard CPU/RAM em tempo real", []),
                ("Device Details", "device_details.py", "system", "Inventário de hardware/OS", []),
                ("Process Monitor", "process_monitor.py", "", "Top processos (console)", []),
            ],
            "Files & Data": [
                ("Sensitive Dir Monitor", "sensitive_dir_monitor.py", "dir_monitor", "Snapshot e Diff de diretórios", ["PATH", "HASH"]),
                ("File System Scanner", "device_files.py", "filesystem", "Varredura profunda de arquivos", ["PATH", "DEPTH"]),
                ("Credentials Dump", "credentials.py", "credentials", "Extrai credenciais salvas (Admin)", []),
                ("Clipboard Dump", "clipboard_dump.py", "clipboard", "Monitora área de transferência", []),
            ],
            "Remote & Spy": [
                ("Remote Host", "device_access.py", "", "Servidor para acesso remoto", []),
                ("Remote Viewer", "remote_viewer.py", "", "Cliente para acesso remoto", ["TARGET"]),
                ("SSH File Browser", "ssh_file_browser.py", "ssh", "Browser SFTP/SSH", ["TARGET", "USER", "PASS"]),
                ("Keylogger UI", "keyboard_inputs.pyw", "inputs", "Monitor de teclado", []),
                ("Camera Viewer", "camera_access.py", "camera_captures", "Visualiza webcam", []),
                ("Audio Recorder", "audio_recorder.py", "audio", "Grava microfone", []),
                ("Screenshot", "screenshot.py", "screenshots", "Captura tela atual", []),
            ]
        }
        
        for cat_name, tools_list in categories.items():
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=cat_name)
            self.tabs[cat_name] = frame
            
            # Scrollable area
            canvas = tk.Canvas(frame, bg="#f5f5f7", highlightthickness=0)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e, c=canvas: c.configure(scrollregion=c.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add tools
            for title, script, res_dir, desc, params in tools_list:
                self.add_tool_card(scrollable_frame, title, script, res_dir, desc, params)

    def add_tool_card(self, parent, title, script, res_dir, desc, params):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid")
        card.pack(fill=tk.X, padx=10, pady=5)
        
        # Left: Info
        info_frame = tk.Frame(card, bg="white")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(info_frame, text=title, font=("Segoe UI", 11, "bold"), bg="white", anchor="w").pack(fill=tk.X)
        tk.Label(info_frame, text=desc, font=("Segoe UI", 9), fg="#666", bg="white", anchor="w").pack(fill=tk.X)
        
        # Right: Actions
        action_frame = tk.Frame(card, bg="white")
        action_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Run Button
        run_btn = ttk.Button(action_frame, text="Run", command=lambda: self.launch_tool(script, params))
        run_btn.pack(side=tk.LEFT, padx=2)
        
        # View Result Button
        if res_dir:
            view_btn = ttk.Button(action_frame, text="View Last", command=lambda: open_specific_result(res_dir))
            view_btn.pack(side=tk.LEFT, padx=2)
            
        self.tools.append((title.lower(), desc.lower(), card))

    def launch_tool(self, script, params):
        args = []
        target = self.target_var.get().strip()
        
        if "TARGET" in params:
            t = target or simpledialog.askstring("Input", "Target Host/IP:")
            if not t: return
            args.append(t)
            
        if "PORT" in params:
            p = simpledialog.askinteger("Input", "Port (default varies):")
            if p: args.extend(["--port", str(p)])
            
        if "MODE" in params:
            m = simpledialog.askstring("Input", "Mode [common/all] (default: common):")
            if m: args.append(m)
            
        if "COMMUNITY" in params:
            c = simpledialog.askstring("Input", "SNMP Community (default: public):")
            if c: args.extend(["--community", c])
            
        if "USER" in params:
            u = simpledialog.askstring("Input", "Username:")
            if u: args.extend(["--user", u])
            
        if "PASS" in params:
            p = simpledialog.askstring("Input", "Password:")
            if p: args.extend(["--password", p])
            
        if "SUBNET" in params:
            s = simpledialog.askstring("Input", "Subnet (e.g. 192.168.1) or empty for auto:")
            if s: args.append(s)

        if "PATH" in params:
            p = simpledialog.askstring("Input", "Directory Path:")
            if p: args.extend(["--path", p])
            
        if "DEPTH" in params:
            d = simpledialog.askstring("Input", "Depth (default 2):")
            if d: args.extend(["--depth", d])
            
        if "HASH" in params:
            if messagebox.askyesno("Input", "Calculate Hashes? (Slow)"):
                args.append("--hash")
                
        if "FILTERS" in params:
            # For services/drivers, simplified interface
            pass 
            
        run_simple(script, args, new_window=True)

    def filter_tools(self, *args):
        query = self.search_var.get().lower().strip()
        for title, desc, widget in self.tools:
            if not query or query in title or query in desc:
                widget.pack(fill=tk.X, padx=10, pady=5) # Restore
            else:
                widget.pack_forget()

if __name__ == "__main__":
    app = App()
    app.mainloop()
