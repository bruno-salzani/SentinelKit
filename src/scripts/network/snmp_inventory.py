import argparse
import sys
import os
import json

try:
    from support import write_json, timestamp, ensure_dependencies
except ImportError:
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from support import write_json, timestamp, ensure_dependencies

def snmp_get(target, community, oid, port=161):
    from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
    try:
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community, mpModel=1),
                   UdpTransportTarget((target, port), timeout=2.0, retries=1),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )
        if errorIndication:
            return {"error": str(errorIndication)}
        elif errorStatus:
            return {"error": str(errorStatus)}
        else:
            for varBind in varBinds:
                return str(varBind[1])
    except Exception as e:
        return {"error": str(e)}

def snmp_walk(target, community, oid, port=161):
    results = []
    try:
        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),
            UdpTransportTarget((target, port), timeout=2.0, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False
        ):
            if errorIndication:
                break
            elif errorStatus:
                break
            else:
                for varBind in varBinds:
                    results.append(str(varBind[1]))
    except Exception:
        pass
    return results

def main():
    ensure_dependencies(["pysnmp"])
    ap = argparse.ArgumentParser(description="Inventário SNMP Básico")
    ap.add_argument("host", help="Host alvo")
    ap.add_argument("--community", default="public", help="Comunidade SNMP (default: public)")
    ap.add_argument("--port", type=int, default=161, help="Porta SNMP (default: 161)")
    args = ap.parse_args()

    target = args.host
    comm = args.community
    port = args.port

    print(f"Iniciando inventário SNMP em {target}...")

    # System Info
    sys_descr = snmp_get(target, comm, "1.3.6.1.2.1.1.1.0", port)
    sys_uptime = snmp_get(target, comm, "1.3.6.1.2.1.1.3.0", port)
    sys_contact = snmp_get(target, comm, "1.3.6.1.2.1.1.4.0", port)
    sys_name = snmp_get(target, comm, "1.3.6.1.2.1.1.5.0", port)
    sys_location = snmp_get(target, comm, "1.3.6.1.2.1.1.6.0", port)

    # Interfaces
    # ifDescr
    if_descrs = snmp_walk(target, comm, "1.3.6.1.2.1.2.2.1.2", port)
    
    data = {
        "target": target,
        "system": {
            "description": sys_descr,
            "uptime": sys_uptime,
            "contact": sys_contact,
            "name": sys_name,
            "location": sys_location
        },
        "interfaces": if_descrs
    }

    meta = {"script": "snmp_inventory", "ts": timestamp(), "host": target, "version": "1.0"}
    path = write_json("snmp", f"inventory_{target.replace(':','_')}", data, meta)
    print(f"Resultado salvo em: {path}")
    print(path) # Required for GUI integration to capture output

if __name__ == "__main__":
    from support import safe_main
    safe_main(main)
