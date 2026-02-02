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

def script_path(name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, name)

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

def open_latest_result():
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(root, "results")
        sub = simpledialog.askstring("Open Latest Result", "Subfolder (ex.: http_security, tls, smb, event_logs):")
        if not sub:
            return
        target = os.path.join(results_dir, sub)
        if not os.path.isdir(target):
            messagebox.showerror("Error", "Subfolder not found.")
            return
        files = [os.path.join(target, f) for f in os.listdir(target) if os.path.isfile(os.path.join(target, f))]
        if not files:
            messagebox.showinfo("Info", "No files found in subfolder.")
            return
        latest = max(files, key=lambda p: os.path.getmtime(p))
        if os.name == "nt":
            os.startfile(latest)
        else:
            subprocess.Popen(["xdg-open", latest])
    except Exception as e:
        messagebox.showerror("Error", str(e))

def open_latest_presets():
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        results_dir = os.path.join(root, "results")
        win = tk.Toplevel()
        win.title("Open Latest — Presets")
        frm = ttk.Frame(win, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)
        def _open(sub):
            target = os.path.join(results_dir, sub)
            if not os.path.isdir(target):
                messagebox.showerror("Error", "Subfolder not found.")
                return
            files = [os.path.join(target, f) for f in os.listdir(target) if os.path.isfile(os.path.join(target, f))]
            if not files:
                messagebox.showinfo("Info", "No files found in subfolder.")
                return
            latest = max(files, key=lambda p: os.path.getmtime(p))
            if os.name == "nt":
                os.startfile(latest)
            else:
                subprocess.Popen(["xdg-open", latest])
        ttk.Button(frm, text="Defender/Firewall", command=lambda: _open("defender_firewall")).pack(fill=tk.X, pady=4)
        ttk.Button(frm, text="Services/Drivers", command=lambda: _open("services_drivers")).pack(fill=tk.X, pady=4)
        ttk.Button(frm, text="RDP/WinRM", command=lambda: _open("rdp_winrm")).pack(fill=tk.X, pady=4)
        ttk.Button(frm, text="Dir Monitor", command=lambda: _open("dir_monitor")).pack(fill=tk.X, pady=4)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    root.title("SentinelKit — GUI Launcher")
    root.geometry("650x620")
    root.minsize(650, 620)
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except:
        pass
    style.configure("TButton", padding=(10, 6), font=("Segoe UI", 10))
    style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
    style.configure("Category.TLabel", font=("Segoe UI", 12, "bold"))
    header = ttk.Frame(root, padding=(10, 8))
    header.pack(fill=tk.X)
    ttk.Label(header, text="SentinelKit — Tools", style="Header.TLabel").pack(side=tk.LEFT)
    ttk.Button(header, text="Open Results", command=open_results_folder).pack(side=tk.RIGHT)
    frame = ttk.Frame(root, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)
    target_var = tk.StringVar()
    search_var = tk.StringVar()
    idx = {"value": 0}
    line_holder = {"frame": None}
    entries = []
    top = ttk.Frame(frame)
    top.pack(fill=tk.X, pady=6)
    ttk.Label(top, text="Target IP/Host").pack(side=tk.LEFT)
    ttk.Entry(top, textvariable=target_var, width=30).pack(side=tk.LEFT, padx=6)
    ttk.Label(top, text="Search").pack(side=tk.LEFT, padx=(12, 4))
    ttk.Entry(top, textvariable=search_var, width=20).pack(side=tk.LEFT)

    def add_entry(label, tooltip, command, help_text):
        if idx["value"] % 2 == 0:
            line_holder["frame"] = tk.Frame(frame)
            line_holder["frame"].pack(anchor="w", pady=6)
        row = tk.Frame(line_holder["frame"])
        row.pack(side=tk.LEFT, padx=6)
        btn = ttk.Button(row, text=label, width=30, command=command)
        btn.pack(side=tk.LEFT)
        Tooltip(btn, tooltip)
        help_btn = ttk.Button(row, text="?", width=3, command=lambda: messagebox.showinfo(label, help_text))
        help_btn.pack(side=tk.LEFT, padx=6)
        idx["value"] += 1
        entries.append({"label": label.lower(), "btn": btn, "help": help_btn})
    ttk.Label(frame, text="Rede", style="Category.TLabel").pack(anchor="w", pady=(10,4))
    def apply_search(*args):
        q = (search_var.get() or "").lower().strip()
        for e in entries:
            match = (not q) or (q in e["label"])
            try:
                e["btn"]["state"] = tk.NORMAL if match else tk.DISABLED
                e["help"]["state"] = tk.NORMAL if match else tk.DISABLED
            except Exception:
                pass
    search_var.trace_add("write", apply_search)

    add_entry(
        "Network Info",
        "Scanner de rede: IP público, WiFi, interfaces, ARP",
        lambda: run_simple("network_info.py"),
        "Coleta IP público, WiFi, interfaces e vizinhos ARP.\nUso: executar e aguardar.\nSaída: results/network/network_info_*.json."
    )
    add_entry(
        "Port Scanner",
        "Verifica portas comuns ou 1-1024 em um alvo",
        lambda: run_simple("port_scanner.py", [target_var.get() or simpledialog.askstring("Port Scanner", "Target IP/Host:"), "--mode", (simpledialog.askstring("Port Scanner", "Mode [common/all]:") or "common")]),
        "Verifica portas abertas em um alvo.\nUso: informe IP/Host e modo common/all.\nSaída: exibida no terminal."
    )
    add_entry(
        "Service Fingerprint",
        "Port scan + banner grabbing consolidado",
        lambda: run_simple("service_fingerprint.py", [target_var.get() or simpledialog.askstring("Service FP", "Target IP/Host:"), (simpledialog.askstring("Service FP", "Mode [common/all]:") or "common")]),
        "Executa port scan e coleta banners em seguida.\nUso: informe IP/Host e modo.\nSaída: results/fingerprint/fingerprint_*.json."
    )
    add_entry(
        "System Monitor",
        "Dashboard de CPU/RAM/Disk em tempo real",
        lambda: run_simple("system_monitor.py"),
        "Mostra uso de CPU, RAM e Disco em tempo real.\nUso: apenas executar, pressione Q para sair."
    )
    ttk.Label(frame, text="Sistema", style="Category.TLabel").pack(anchor="w", pady=(10,4))
    add_entry(
        "Device Details",
        "Relatório estático de OS/CPU/Memória/Disco/Rede",
        lambda: run_simple("device_details.py"),
        "Gera inventário do sistema.\nUso: executar e aguardar.\nSaída: results/system/device_details_YYYY-MM-DD.json."
    )
    add_entry(
        "File System Scanner",
        "Escaneia diretórios com profundidade e opcional hashing",
        lambda: run_simple("device_files.py", ["--path", (simpledialog.askstring("FS Scanner", "Path:") or os.path.expanduser("~")), "--depth", (simpledialog.askstring("FS Scanner", "Depth:") or "2")]),
        "Escaneia arquivos e diretórios.\nUso: informe Path e Depth; suporte a --hash pelo menu principal.\nSaída: results/filesystem/filesystem_*.json."
    )
    add_entry(
        "Sensitive Dir Monitor",
        "Snapshot+diff de diretório sensível",
        lambda: (
            (lambda p, h, inc, exc, prev: run_simple(
                "sensitive_dir_monitor.py",
                ["--path", p] +
                (["--hash"] if (h or "").lower().startswith("s") else []) +
                ([] if not inc else ["--include", inc]) +
                ([] if not exc else ["--exclude", exc]) +
                ([] if not prev else ["--prev", prev])
            ))(
                simpledialog.askstring("Dir Monitor", "Path do diretório:") or os.path.expanduser("~"),
                simpledialog.askstring("Dir Monitor", "Calcular hash? (s/n):") or "n",
                simpledialog.askstring("Dir Monitor", "Include patterns CSV (opcional):") or "",
                simpledialog.askstring("Dir Monitor", "Exclude patterns CSV (opcional):") or "",
                simpledialog.askstring("Dir Monitor", "Snapshot anterior para diff (arquivo JSON, opcional):") or ""
            )
        ),
        "Gera snapshot do diretório e opcionalmente diff com snapshot anterior.\nSuporta include/exclude CSV e hash opcional.\nSaída: results/dir_monitor/snapshot_*.json."
    )
    add_entry(
        "Camera Viewer",
        "Visualizador de câmera com snapshot (S)",
        lambda: run_simple("camera_access.py"),
        "Abre câmera selecionada.\nControles: S salva foto em results/camera_captures, Q sai."
    )
    add_entry(
        "Keylogger UI",
        "Gravador de teclas com UI visível",
        lambda: run_simple("keyboard_inputs.pyw", new_window=True),
        "Grava entradas de teclado com janela visível.\nUso: abrir e digitar; salva em results/inputs.\nPara sair, feche a janela."
    )
    add_entry(
        "Remote Desktop Host",
        "Servidor de desktop remoto local",
        lambda: run_simple("device_access.py", new_window=True),
        "Inicia servidor de vídeo/controle nas portas 5000/5001.\nUso: execute aqui e conecte pelo Viewer."
    )
    add_entry(
        "Remote Desktop Viewer",
        "Cliente de visualização remota",
        lambda: run_simple("remote_viewer.py", [target_var.get() or simpledialog.askstring("Remote Viewer", "Target IP:")]),
        "Conecta ao Host informado.\nUso: informe IP do Host.\nControles: Q para sair."
    )
    add_entry(
        "Credentials Dump",
        "WiFi, Credential Manager, arquivos .env, histórico PS",
        lambda: run_simple("credentials.py", ["--elevate"]),
        "Coleta credenciais e histórico.\nUso: pode requerer Admin; salva em results/credentials/credentials_*.json."
    )
    add_entry(
        "SSH File Browser",
        "Listar e baixar via SSH/SFTP",
        lambda: run_simple("ssh_file_browser.py", [simpledialog.askstring("SSH", "Host:"), simpledialog.askstring("SSH", "User:"), "--password", (simpledialog.askstring("SSH", "Password:") or "")]),
        "Lista e baixa arquivos via SSH/SFTP.\nUso: informe host, usuário e senha.\nSaída: results/ssh/listing_*.json."
    )
    add_entry(
        "LAN Ping Sweep",
        "Descoberta de hosts vivos no /24",
        lambda: run_simple("ping_sweep.py", [simpledialog.askstring("Ping Sweep", "Base subnet (ex.: 192.168.1) ou vazio:") or ""]),
        "Varre hosts ativos na sub-rede.\nUso: informe base ou deixe vazio para auto.\nSaída: results/ping_sweep/ping_sweep_*.json."
    )
    add_entry(
        "Banner Grabber",
        "Captura banners de portas para fingerprint",
        lambda: run_simple("banner_grabber.py", [target_var.get() or simpledialog.askstring("Banner", "Host:"), simpledialog.askstring("Banner", "Ports (ex.: 80,22,25):")]),
        "Captura banners de serviços.\nUso: informe host e portas separadas por vírgula.\nSaída: results/banners/banners_*.json."
    )
    add_entry(
        "Process Top Viewer",
        "Top processos por CPU em tempo real",
        lambda: run_simple("process_monitor.py"),
        "Mostra processos com maior uso de CPU.\nUso: executar; pressione Q para sair."
    )
    add_entry(
        "Screenshot Capture",
        "Captura screenshot do monitor principal",
        lambda: run_simple("screenshot.py"),
        "Salva imagem da tela.\nUso: executar; saída em results/screenshots."
    )
    add_entry(
        "Clipboard Dump",
        "Exporta texto do clipboard para arquivo",
        lambda: run_simple("clipboard_dump.py"),
        "Exporta o texto do clipboard.\nUso: executar; instala pywin32 se necessário.\nSaída: results/clipboard/clipboard_*.txt."
    )
    add_entry(
        "DNS Cache Dump",
        "Exporta cache DNS para JSON",
        lambda: run_simple("dns_cache_dump.py"),
        "Exporta entradas do cache DNS local.\nUso: executar; saída em results/dns/dns_cache_*.json."
    )
    add_entry(
        "Audio Recorder",
        "Gravação do microfone até Q, salva WAV",
        lambda: run_simple("audio_recorder.py"),
        "Grava áudio do microfone em WAV.\nUso: executar e pressionar Q para parar.\nSaída: results/audio/audio_*.wav."
    )
    add_entry(
        "WiFi Scan",
        "Lista redes WiFi próximas (Windows)",
        lambda: run_simple("wifi_scan.py"),
        "Lista redes WiFi detectadas.\nUso: executar; saída em results/wifi/wifi_networks_*.json."
    )
    add_entry(
        "System Monitor Logger",
        "Log CPU/Memória em CSV",
        lambda: run_simple("system_monitor_log.py", [simpledialog.askstring("Monitor Log", "Duration seconds (optional):") or ""]),
        "Grava CPU e Memória por segundo em CSV.\nUso: informe duração opcional.\nSaída: results/monitor_logs/log_*.csv."
    )
    add_entry(
        "HTTP Security Check",
        "Avalia cabeçalhos HSTS/CSP/X-Frame-Options",
        lambda: run_simple("http_security_check.py", [target_var.get() or simpledialog.askstring("HTTP Sec", "Host:"), simpledialog.askstring("HTTP Sec", "Port (80):") or "80"]),
        "Verifica cabeçalhos de segurança HTTP.\nUso: informe host e porta.\nSaída: results/http_security/security_*.json."
    )
    add_entry(
        "TLS Cert Inspector",
        "Analisa certificado TLS e expiração",
        lambda: run_simple("tls_cert_inspector.py", [target_var.get() or simpledialog.askstring("TLS", "Host:"), simpledialog.askstring("TLS", "Port (443):") or "443"]),
        "Captura certificado TLS, emissor e validade.\nUso: informe host:porta.\nSaída: results/tls/tls_*.json."
    )
    add_entry(
        "SMB Shares Enumerator",
        "Lista compartilhamentos SMB acessíveis",
        lambda: run_simple("smb_shares_enumerator.py", ["--host", (simpledialog.askstring("SMB", "Host (vazio para LAN):") or "")]),
        "Enumera \\HOST shares e permissões básicas.\nUso: informe host ou deixe vazio.\nSaída: results/smb/shares_*.json."
    )
    add_entry(
        "Windows Event Logs",
        "Exporta eventos por canal/tempo/nível",
        lambda: run_simple("windows_event_export.py", ["--channel", (simpledialog.askstring("Event Logs", "Channel (System/Security/Application):") or "System"), "--hours", (simpledialog.askstring("Event Logs", "Last N hours:") or "4"), "--level", (simpledialog.askstring("Event Logs", "Level (Info/Warning/Error, opcional):") or "")]),
        "Exporta eventos do Windows.\nUso: escolher canal, horas e nível.\nSaída: results/event_logs/events_*.json."
    )
    add_entry(
        "Autoruns Audit",
        "Itens de inicialização e tarefas",
        lambda: run_simple("autoruns_startup_audit.py"),
        "Lista Startup folders, Run keys e tarefas.\nUso: executar.\nSaída: results/autoruns/autoruns_*.json."
    )
    add_entry(
        "Installed Programs",
        "Inventário Win32/MSIX instalados",
        lambda: run_simple("installed_programs_inventory.py"),
        "Lista programas instalados com versão/publisher.\nUso: executar.\nSaída: results/programs/programs_*.json."
    )
    add_entry(
        "Firewall Rules Dump",
        "Exporta regras do Windows Firewall",
        lambda: run_simple("firewall_rules_dump.py"),
        "Exporta regras básicas do firewall.\nUso: executar.\nSaída: results/firewall/firewall_*.json."
    )
    add_entry(
        "Defender/Firewall Audit",
        "Estado Defender e perfis Firewall",
        lambda: run_simple("windows_defender_firewall_audit.py"),
        "Coleta status do Windows Defender, perfis do Firewall e estatísticas de eventos recentes.\nSaída: results/defender_firewall/defender_firewall_*.json."
    )
    add_entry(
        "Scheduled Tasks Audit",
        "Lista tarefas e falhas",
        lambda: run_simple("scheduled_tasks_audit.py"),
        "Audita tarefas agendadas e falhas.\nUso: executar.\nSaída: results/scheduled_tasks/tasks_*.json."
    )
    add_entry(
        "Services/Drivers Audit",
        "Serviços automáticos e drivers",
        lambda: (
            (lambda s_st, s_stt, d_sm, d_st: run_simple(
                "services_drivers_audit.py",
                ([] if not s_stt else ["--svc-starttype", s_stt]) +
                ([] if not s_st else ["--svc-state", s_st]) +
                ([] if not d_sm else ["--drv-startmode", d_sm]) +
                ([] if not d_st else ["--drv-state", d_st])
            ))(
                simpledialog.askstring("Services Audit", "Service Status (Running/Stopped/All):") or "All",
                simpledialog.askstring("Services Audit", "Service StartType (Automatic/Manual/Disabled/All):") or "All",
                simpledialog.askstring("Drivers Audit", "Driver StartMode (Auto/Manual/All):") or "All",
                simpledialog.askstring("Drivers Audit", "Driver State (Running/Stopped/All):") or "All"
            )
        ),
        "Audita serviços e drivers com filtros por StartType/Status/StartMode/State.\nSaída: results/services_drivers/services_drivers_*.json."
    )
    add_entry(
        "USB Devices History",
        "Histórico de dispositivos USB",
        lambda: run_simple("usb_devices_history.py"),
        "Lista chaves de dispositivos USB no sistema.\nUso: executar.\nSaída: results/usb/usb_*.json."
    )
    add_entry(
        "Browser Snapshot",
        "Chrome/Edge/Firefox: versões/extensões",
        lambda: run_simple("browser_profiles_snapshot.py"),
        "Coleta dados não sensíveis dos navegadores.\nUso: executar.\nSaída: results/browser/browser_*.json."
    )
    add_entry(
        "HTTP Dir Bruteforce",
        "Paths comuns com rate-limit e concorrência",
        lambda: (
            (lambda base, rate, paths_in, conc, status_csv, timeout_s: (
                run_simple(
                    "http_directory_bruteforce.py",
                    [base or "", rate or "200"] +
                    ((["--paths-file", paths_in[1:]] if paths_in and paths_in.strip().startswith("@") else (["--paths", paths_in] if paths_in else []))) +
                    ([] if not conc else ["--concurrency", conc]) +
                    ([] if not status_csv else ["--status", status_csv]) +
                    ([] if not timeout_s else ["--timeout", timeout_s])
                )
            ))(
                simpledialog.askstring("Dir Bruteforce", "Base URL:"),
                simpledialog.askstring("Dir Bruteforce", "Rate ms (200):"),
                simpledialog.askstring("Dir Bruteforce", "Paths CSV ou arquivo (@caminho, opcional):"),
                simpledialog.askstring("Dir Bruteforce", "Concorrência (1):"),
                simpledialog.askstring("Dir Bruteforce", "Status filter CSV (ex.: 200,301,302,401,403, opcional):"),
                simpledialog.askstring("Dir Bruteforce", "Timeout segundos (5, opcional):")
            )
        ),
        "Testa paths comuns em um site com rate-limit e concorrência.\nUso: informe base URL; opcionalmente paths CSV ou arquivo (@caminho), concorrência, filtro de status e timeout.\nSaída: results/http_bruteforce/dir_bruteforce_*.json."
    )
    add_entry(
        "Port Range Profiler",
        "Perfil por faixa com banners e tempo",
        lambda: run_simple("port_range_profiler.py", [target_var.get() or simpledialog.askstring("Range", "Host:"), simpledialog.askstring("Range", "Start-End (ex.: 30000-30100):") or "30000-30100"]),
        "Perfila uma faixa de portas.\nUso: informe host e faixa.\nSaída: results/port_range/range_*.json."
    )
    add_entry(
        "RDP/WinRM Probe",
        "Detecta exposição de RDP/WinRM",
        lambda: run_simple("rdp_winrm_probe.py", [target_var.get() or simpledialog.askstring("RDP/WinRM", "Host:")]),
        "Sonda as portas 3389, 5985 e 5986 para detectar RDP/WinRM.\nUso: informe host.\nSaída: results/rdp_winrm/probe_*.json."
    )
    add_entry(
        "Open Results Folder",
        "Abrir a pasta de resultados na raiz do projeto",
        open_results_folder,
        "Abre o diretório results/ contendo subpastas organizadas por tipo.\nUso: clique para abrir no Explorer."
    )
    add_entry(
        "Open Latest Result",
        "Abrir o arquivo mais recente de uma subpasta",
        open_latest_result,
        "Solicita a subpasta e abre o arquivo mais recente.\nEx.: http_security, tls, smb."
    )
    add_entry(
        "Open Latest Presets",
        "Abrir último por categoria",
        open_latest_presets,
        "Seleciona automaticamente subpastas: defender_firewall, services_drivers, rdp_winrm, dir_monitor."
    )

    root.mainloop()

if __name__ == "__main__":
    main()
