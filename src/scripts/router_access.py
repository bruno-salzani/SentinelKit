import argparse
import paramiko
import sys
import getpass

def restore_router_backup(host, username, password, backup_filename):
    """
    Restores a router backup via SSH.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host}...")
        ssh.connect(host, username=username, password=password, timeout=10)
        
        # NOTE: This command is specific to certain router models (e.g., MikroTik or similar).
        # Adjust as needed for the target device.
        command = f'system restore filename={backup_filename}'
        print(f"Executing: {command}")
        
        stdin, stdout, stderr = ssh.exec_command(command)
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if output:
            print(f"Output: {output}")
        if error:
            print(f"Error output: {error}")
            
    except paramiko.AuthenticationException:
        print("Authentication failed.")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        ssh.close()
        print("Connection closed.")

def main():
    parser = argparse.ArgumentParser(description="Restore router backup via SSH.")
    parser.add_argument("host", help="Router IP address")
    parser.add_argument("username", help="SSH Username")
    parser.add_argument("--password", help="SSH Password (will prompt if not provided)")
    parser.add_argument("backup_file", help="Name of the backup file on the router")
    
    args = parser.parse_args()
    
    password = args.password
    if not password:
        password = getpass.getpass("Enter SSH Password: ")
        
    restore_router_backup(args.host, args.username, password, args.backup_file)

if __name__ == "__main__":
    main()
