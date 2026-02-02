import socket
import psutil
import requests
import json
import os
import subprocess
import re
import platform
import uuid
from datetime import datetime
from support import results_dir, timestamp

def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))

def get_public_ip_info():
    """Retrieves public IP and geolocation info."""
    try:
        response = requests.get('https://ipinfo.io/json', timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    return None

def get_local_interfaces():
    """Retrieves details about local network interfaces."""
    interfaces = {}
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()

    for name, snics in addrs.items():
        if name not in interfaces:
            interfaces[name] = {}
        
        # Get status (up/down, speed)
        if name in stats:
            interfaces[name]['is_up'] = stats[name].isup
            interfaces[name]['speed_mbps'] = stats[name].speed
            interfaces[name]['mtu'] = stats[name].mtu

        # Get addresses (IPv4, IPv6, MAC)
        interfaces[name]['addresses'] = []
        for snic in snics:
            addr_info = {
                'family': str(snic.family),
                'address': snic.address,
                'netmask': snic.netmask,
                'broadcast': snic.broadcast
            }
            interfaces[name]['addresses'].append(addr_info)
            
    return interfaces

def get_wifi_info_windows():
    """Parses 'netsh wlan show interfaces' for WiFi details on Windows."""
    if platform.system() != "Windows":
        return {"error": "Not supported on non-Windows systems"}
        
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode('utf-8', errors='ignore')
        wifi_data = {}
        for line in output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                wifi_data[key.strip()] = value.strip()
        return wifi_data
    except Exception as e:
        return {"error": str(e)}

def scan_network_arp():
    """
    Scans the local network neighbor table (ARP cache).
    Note: This only shows devices the computer has recently communicated with.
    """
    devices = []
    try:
        # Run arp -a command
        output = subprocess.check_output("arp -a", shell=True).decode('utf-8', errors='ignore')
        
        # Simple regex to find IP and MAC addresses
        # Format usually:  192.168.1.1    00-11-22-33-44-55   dynamic
        pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]{17}|[0-9a-fA-F:]{17})\s+(\w+)')
        
        for line in output.split('\n'):
            match = pattern.search(line)
            if match:
                devices.append({
                    "ip": match.group(1),
                    "mac": match.group(2),
                    "type": match.group(3)
                })
    except Exception as e:
        return {"error": str(e)}
        
    return devices

def get_gateway_info():
    """Attempts to find default gateway."""
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output("ipconfig", shell=True).decode('utf-8', errors='ignore')
            # Look for "Default Gateway . . . . . . . . . : 192.168.1.1"
            gateways = []
            for line in output.split('\n'):
                if "Default Gateway" in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        gw = parts[1].strip()
                        if gw:
                            gateways.append(gw)
            return gateways
    except:
        pass
    return ["Unknown"]

def main():
    print("Gathering Network Information...")
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "local_mac": get_mac_address(),
        "public_network_info": get_public_ip_info(),
        "gateway_info": get_gateway_info(),
        "wifi_details": get_wifi_info_windows(),
        "local_interfaces": get_local_interfaces(),
        "network_neighbors_arp": scan_network_arp()
    }
    
    # Print summary
    print(f"\n--- Public IP Info ---")
    if data['public_network_info']:
        print(f"IP: {data['public_network_info'].get('ip')}")
        print(f"Org: {data['public_network_info'].get('org')}")
        print(f"City: {data['public_network_info'].get('city')}")
        print(f"Country: {data['public_network_info'].get('country')}")
    
    print(f"\n--- WiFi Info ---")
    if 'SSID' in data['wifi_details']:
        print(f"SSID: {data['wifi_details']['SSID']}")
        print(f"Signal: {data['wifi_details'].get('Signal', 'N/A')}")
        print(f"Radio Type: {data['wifi_details'].get('Radio type', 'N/A')}")
    else:
        print("No WiFi connection details found.")

    print(f"\n--- Local Network Neighbors (ARP) ---")
    for device in data['network_neighbors_arp']:
        print(f"IP: {device['ip']} \t MAC: {device['mac']}")

    out_dir = results_dir("network")
    filename = os.path.join(out_dir, f"network_info_{timestamp()}.json")
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"\n[+] Full report saved to: {filename}")

if __name__ == "__main__":
    main()
