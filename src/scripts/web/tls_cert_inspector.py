import argparse
import socket
import ssl
from datetime import datetime
try:
    from support import write_json, timestamp, ensure_dependencies
except Exception:
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from support import write_json, timestamp, ensure_dependencies

def main():
    ensure_dependencies(["cryptography", "requests"])
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.x509.oid import AuthorityInformationAccessOID

    ap = argparse.ArgumentParser()
    ap.add_argument("host")
    ap.add_argument("--port", type=int, default=443)
    ap.add_argument("--timeout", type=float, default=6)
    ap.add_argument("--check-crl", action="store_true")
    args = ap.parse_args()
    host = args.host
    port = args.port
    data = {"target": {"host": host, "port": port}}
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=args.timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                data["cert"] = cert
                not_after = cert.get("notAfter")
                exp_dt = None
                if not_after:
                    exp_dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                if exp_dt:
                    days = (exp_dt - datetime.utcnow()).days
                    data["expires_in_days"] = days
                    data["expiring_soon"] = days <= 30
                if x509 and default_backend:
                    try:
                        der = ssock.getpeercert(True)
                        leaf = x509.load_der_x509_certificate(der, default_backend())
                        data["subject"] = leaf.subject.rfc4514_string()
                        data["issuer"] = leaf.issuer.rfc4514_string()
                        try:
                            aia = leaf.extensions.get_extension_for_class(x509.AuthorityInformationAccess)
                            urls = []
                            for ad in aia.value:
                                try:
                                    if AuthorityInformationAccessOID and ad.access_method.dotted_string == AuthorityInformationAccessOID.CA_ISSUERS.dotted_string:
                                        urls.append(getattr(ad.access_location, "value", None))
                                except Exception:
                                    pass
                            data["aia_ca_issuers"] = urls
                        except Exception:
                            pass
                        if args.check_crl:
                            crl_urls = []
                            try:
                                crldp = leaf.extensions.get_extension_for_class(x509.CRLDistributionPoints)
                                for dp in crldp.value:
                                    for gn in (dp.full_name or []):
                                        v = getattr(gn, "value", None)
                                        if v:
                                            crl_urls.append(v)
                            except Exception:
                                pass
                            crl_revoked_count = None
                            errors = []
                            if crl_urls:
                                import requests
                                for u in crl_urls:
                                    try:
                                        r = requests.get(u, timeout=4)
                                        content = r.content
                                        try:
                                            crl = x509.load_der_x509_crl(content, default_backend())
                                        except Exception:
                                            try:
                                                crl = x509.load_pem_x509_crl(content, default_backend())
                                            except Exception as e2:
                                                errors.append(str(e2))
                                                continue
                                        crl_revoked_count = len(list(crl))
                                        break
                                    except Exception as e:
                                        errors.append(str(e))
                            data["revocation_check"] = {"crl_revoked_count": crl_revoked_count, "errors": errors}
                    except Exception as e:
                        data["parse_error"] = str(e)
    except Exception as e:
        data["error"] = str(e)
    meta = {"script": "tls_cert_inspector", "ts": timestamp(), "host": host, "version": "1.0"}
    path = write_json("tls", f"tls_{host.replace(':','_')}", data, meta)
    print(path)

if __name__ == "__main__":
    from support import safe_main
    safe_main(main)
