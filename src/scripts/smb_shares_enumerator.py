import argparse
import sys
import os
import json
import socket

try:
    from support import write_json, timestamp, ensure_dependencies
except ImportError:
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from support import write_json, timestamp, ensure_dependencies

def check_port(host, port=445, timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except:
        return False

def list_shares_smbprotocol(host, user, password, domain):
    # smbprotocol doesn't have a high-level "list shares" easily accessible without RPC usually,
    # but we can try to connect to IPC$ and do some magic, OR we can just try common share names if we can't enumerate.
    # Actually, listing shares usually requires MS-SRVS via RPC (named pipe).
    # Implementing full RPC here is too much.
    # We will fall back to a simple "Access Check" on common shares if enumeration isn't easy,
    # OR we use the "net view" legacy method for enumeration if possible, then verify with smbprotocol.
    
    # However, to be "Advanced", we should try to use python. 
    # Let's rely on the user providing a list OR use "net view" to get the list, then probe with smbprotocol.
    
    # Fallback to net view for DISCOVERY
    shares = []
    try:
        import subprocess
        cmd = ["net", "view", f"\\\\{host}"]
        if user and password:
            # net view doesn't easily take auth inline without "net use" first.
            pass 
        
        out = subprocess.check_output(cmd, shell=True).decode("utf-8", errors="ignore")
        capture = False
        for line in out.splitlines():
            if "Shared resources at" in line:
                capture = True
                continue
            if capture:
                parts = line.split()
                if parts and not line.startswith("The command"):
                    name = parts[0]
                    shares.append(name)
    except Exception:
        # If net view fails, try common shares
        shares = ["C$", "ADMIN$", "IPC$", "Users", "Temp", "Share"]

    results = []
    
    try:
        conn = Connection(uuid.uuid4(), host, 445)
        conn.connect(timeout=5)
        session = Session(conn, user, password, domain)
        session.connect()
        
        for share_name in shares:
            share_res = {"name": share_name, "accessible": False, "files": []}
            try:
                tree = TreeConnect(session, f"\\\\{host}\\{share_name}")
                tree.connect()
                share_res["accessible"] = True
                
                # Try to list files
                try:
                    # Root directory
                    file_open = Open(tree, "", FilePipePrinterAccessMask.FILE_LIST_DIRECTORY, 
                                     FileAttributes.FILE_ATTRIBUTE_DIRECTORY,
                                     ShareAccess.FILE_SHARE_READ,
                                     CreateDisposition.FILE_OPEN,
                                     CreateOptions.FILE_DIRECTORY_FILE)
                    file_open.create()
                    
                    # Query directory
                    files = file_open.query_directory("*", FileInformationClass.FILE_NAMES_INFORMATION)
                    file_list = []
                    for f in files:
                         file_list.append(f.file_name.decode('utf-16-le'))
                    share_res["files"] = file_list[:20] # Limit to 20
                    share_res["file_count"] = len(file_list)
                    
                    file_open.close()
                except Exception as e:
                    share_res["listing_error"] = str(e)
                
            except Exception as e:
                share_res["error"] = str(e)
            
            results.append(share_res)
            
    except Exception as e:
        return {"error": str(e), "shares_checked": shares}

    return results

def main():
    ensure_dependencies(["smbprotocol"])
    from smbprotocol.connection import Connection
    from smbprotocol.session import Session
    from smbprotocol.tree import TreeConnect
    from smbprotocol.open import Open, CreateDisposition, FilePipePrinterAccessMask, FileAttributes, ShareAccess, CreateOptions, FileInformationClass
    from smbprotocol.structure import BytesField

    ap = argparse.ArgumentParser(description="Enumerador SMB Avançado")
    ap.add_argument("host", help="Host alvo")
    ap.add_argument("--user", default="", help="Usuário")
    ap.add_argument("--password", default="", help="Senha")
    ap.add_argument("--domain", default=".", help="Domínio")
    args = ap.parse_args()
    
    if "smbprotocol.connection" not in sys.modules:
        # Fallback to the old basic script if library missing? 
        # Or just print error. User asked for implementation.
        # I'll try to run a basic check if library missing.
        print("Aviso: smbprotocol não instalado. Funcionalidade reduzida (instale: pip install smbprotocol).")
        # Call legacy logic here or exit? Let's exit to encourage install.
        # But for resilience, I'll do a simple port check.
        if not check_port(args.host):
             print(json.dumps({"error": "Port 445 closed or library missing"}))
             return

    import uuid
    
    results = list_shares_smbprotocol(args.host, args.user, args.password, args.domain)
    
    data = {
        "target": args.host,
        "results": results
    }
    
    meta = {"script": "smb_shares_enumerator", "ts": timestamp(), "host": args.host, "version": "2.0"}
    path = write_json("smb", f"shares_{args.host.replace(':','_')}", data, meta)
    print(path)

if __name__ == "__main__":
    from support import safe_main
    safe_main(main)
