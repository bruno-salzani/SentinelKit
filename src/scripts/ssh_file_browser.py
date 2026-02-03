import argparse
import json
import os
import posixpath
import re
import stat
import sys
from datetime import datetime
import glob
import getpass
import socket
import subprocess
import platform
try:
    import ctypes
except Exception:
    ctypes = None

import support

try:
    from support import format_size
except Exception:
    def format_size(x):
        try:
            x = float(x)
            units = ["B", "KB", "MB", "GB", "TB", "PB"]
            i = 0
            while x >= 1024 and i < len(units) - 1:
                x /= 1024
                i += 1
            return f"{x:.2f} {units[i]}"
        except Exception:
            return "0 B"

def connect_ssh(host, port, username, password=None, key_path=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        if key_path and os.path.exists(key_path):
            client.connect(
                hostname=host, 
                port=port, 
                username=username, 
                key_filename=key_path, 
                timeout=10,
                look_for_keys=False 
            )
        else:
            client.connect(
                hostname=host, 
                port=port, 
                username=username, 
                password=password, 
                timeout=10
            )
        return client
    except Exception as e:
        raise e

def setup_authorized_keys(host, port, username, password, pub_key_path):
    """Lê a chave pública local e a adiciona ao authorized_keys remoto via senha."""
    if not os.path.exists(pub_key_path):
        print(f"Erro: Chave pública não encontrada em {pub_key_path}")
        return False

    with open(pub_key_path, 'r') as f:
        pub_key = f.read().strip()

    print(f"Tentando configurar authorized_keys em {host} para o usuário {username}...")
    try:
        client = connect_ssh(host, port, username, password=password)
        
        # Comandos para criar a pasta .ssh e adicionar a chave (compatível com Windows OpenSSH)
        commands = [
            'powershell -Command "if (!(Test-Path $HOME\\.ssh)) { New-Item -ItemType Directory -Path $HOME\\.ssh }"',
            f'powershell -Command "Add-Content -Path $HOME\\.ssh\\authorized_keys -Value \'{pub_key}\'"'
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd)
            err = stderr.read().decode()
            if err:
                print(f"Aviso no comando: {err.strip()}")
        
        client.close()
        print("Sucesso! Chave pública adicionada ao servidor.")
        return True
    except Exception as e:
        print(f"Falha ao configurar chave via senha: {e}")
        return False

def list_dir_recursive(sftp, root, max_depth=3, current_depth=0, pattern=None):
    if current_depth > max_depth:
        return None
    result = {"path": root, "files": [], "directories": []}
    try:
        entries = sftp.listdir_attr(root)
    except IOError:
        return result
    for e in entries:
        name = e.filename
        remote_path = posixpath.join(root, name)
        is_dir = stat.S_ISDIR(e.st_mode)
        if is_dir:
            sub = list_dir_recursive(sftp, remote_path, max_depth, current_depth + 1, pattern)
            if sub:
                result["directories"].append(sub)
        else:
            ok = True
            if pattern:
                ok = re.search(pattern, name) is not None
            if ok:
                result["files"].append(
                    {"name": name, "path": remote_path, "size": e.st_size, "size_h": format_size(e.st_size)}
                )
    return result

def pick_private_ipv4(addrs):
    for a in addrs:
        if a.get("family") == "2":
            ip = a.get("address")
            if ip and not ip.startswith("127."):
                if ip.startswith("10.") or ip.startswith("192.168.") or (ip.startswith("172.") and 16 <= int(ip.split(".")[1]) <= 31):
                    return ip
    return None

def resolve_local_defaults(network_file=None):
    host = None
    user = getpass.getuser() # Detecta o usuário atual do sistema
    if network_file and os.path.isfile(network_file):
        try:
            with open(network_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data.get("local_interfaces"), dict):
                for iface in data["local_interfaces"].values():
                    ip = pick_private_ipv4(iface.get("addresses", []))
                    if ip:
                        host = ip
                        break
        except Exception:
            pass
    if not host:
        try:
            h = socket.gethostname()
            host = socket.gethostbyname(h)
        except Exception:
            host = "127.0.0.1"
    return host, user

def main():
    support.ensure_dependencies(["paramiko"])
    global paramiko
    import paramiko
    
    p = argparse.ArgumentParser(description="List and download files over SSH/SFTP.")
    p.add_argument("host", nargs="?", default=None, help="SSH host")
    p.add_argument("--port", type=int, default=22, help="SSH port")
    p.add_argument("username", nargs="?", default=None, help="SSH username")
    p.add_argument("--password", help="SSH password")
    p.add_argument("--key", help="Path to private key file")
    p.add_argument("--remote", default="/", help="Remote root path to list")
    p.add_argument("--depth", type=int, default=3, help="Max recursion depth for listing")
    p.add_argument("--pattern", help="Regex to filter files")
    p.add_argument("--auto", action="store_true", help="Auto-detect host and username")
    p.add_argument("--setup-key", action="store_true", help="Install public key on remote host using password")
    args = p.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.auto or not args.host or not args.username:
        host_auto, user_auto = resolve_local_defaults()
        args.host = args.host or host_auto
        args.username = args.username or user_auto

    # Tenta configurar a chave se solicitado
    if args.setup_key:
        if not args.password:
            args.password = getpass.getpass(f"Digite a SENHA de {args.username} para configurar a chave: ")
        pub_key = args.key + ".pub" if args.key else None
        if pub_key:
            setup_authorized_keys(args.host, args.port, args.username, args.password, pub_key)
        else:
            print("Erro: Forneça o caminho da chave privada com --key para localizar a .pub")
        return

    client = None
    try:
        client = connect_ssh(args.host, args.port, args.username, password=args.password, key_path=args.key)
        sftp = client.open_sftp()
        data = list_dir_recursive(sftp, args.remote, max_depth=args.depth, pattern=args.pattern)
        
        from support import results_dir
        out_dir = results_dir("ssh")
        out_path = os.path.join(out_dir, f"listing_{args.host}_{ts}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Conectado com sucesso! Listagem salva em {out_path}")

    except paramiko.AuthenticationException:
        print("Erro de Autenticação. Tente rodar com --setup-key primeiro para instalar sua chave no servidor.")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    main()
