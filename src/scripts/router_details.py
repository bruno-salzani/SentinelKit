import argparse
import getpass
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin

try:
    import requests
except ImportError:
    print("Error: 'requests' module not found. Please install it using: pip install requests")
    sys.exit(1)


def normalize_base_url(ip_or_url: str) -> str:
    """
    Returns a base URL (e.g., http://10.0.0.1/) from either an IP or full URL.
    """
    ip_or_url = ip_or_url.strip()
    if ip_or_url.startswith("http://") or ip_or_url.startswith("https://"):
        parsed = urlparse(ip_or_url)
        base = f"{parsed.scheme}://{parsed.netloc}/"
        return base
    return f"http://{ip_or_url}/"


def is_url_reachable(url: str, timeout: int = 4) -> bool:
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True)
        return r.status_code < 500
    except requests.RequestException:
        return False


def get_gateway_candidates() -> list:
    cands = []
    if sys.platform.startswith("win"):
        try:
            out = subprocess.check_output("ipconfig", shell=True).decode("utf-8", errors="ignore")
            for line in out.splitlines():
                if "Default Gateway" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        gw = parts[1].strip()
                        if gw:
                            cands.append(gw)
        except Exception:
            pass
    return cands


def try_basic_auth(session: requests.Session, base_url: str, username: str, password: str) -> bool:
    """
    Attempts HTTP Basic Auth against the base URL.
    Returns True on success (HTTP 200), False otherwise.
    """
    resp = session.get(base_url, auth=(username, password), timeout=10)
    if resp.status_code == 200:
        return True
    return False


def try_form_logins(session: requests.Session, base_url: str, username: str, password: str) -> bool:
    """
    Attempts several common router login form endpoints/payloads.
    Returns True if any attempt results in a successful authenticated request.
    """
    candidates = [
        ("login.cgi", {"username": username, "password": password}),
        ("login.cgi", {"user": username, "passwd": password}),
        ("login.cgi", {"usr": username, "pwd": password}),
        ("login.cgi", {"password": password}),
        ("userRpm/LoginRpm.htm", {"UserName": username, "Password": password}),
        ("login.html", {"username": username, "password": password}),
        ("cgi-bin/login", {"username": username, "password": password}),
    ]
    for path, payload in candidates:
        url = urljoin(base_url, path)
        try:
            resp = session.post(url, data=payload, timeout=10)
            if resp.status_code == 200:
                test = session.get(base_url, timeout=10)
                if test.status_code == 200 and "login" not in test.text.lower():
                    return True
        except requests.RequestException:
            continue
    return False


def fetch_pages(session: requests.Session, base_url: str) -> dict:
    """
    Attempts to fetch a variety of common router pages. Returns a dict of {endpoint: html_text}.
    """
    endpoints = [
        "", "index.asp", "status.asp", "status.html", "home.asp",
        "system.asp", "deviceinfo.asp", "sysinfo.cgi", "wan.asp", "lan.asp",
        "wireless.asp", "wlstatus.asp", "lan_dhcp_clients.asp", "dhcp_clients.asp",
        "admin/status", "cgi-bin/status", "cgi-bin/diagnostic", "userRpm/StatusRpm.htm",
    ]
    pages = {}
    for ep in endpoints:
        url = urljoin(base_url, ep)
        try:
            r = session.get(url, timeout=10)
            if r.status_code == 200 and r.text:
                pages[ep or "/"] = r.text
        except requests.RequestException:
            pass
        time.sleep(0.2)
    return pages


def extract_summary(pages: dict) -> dict:
    """
    Performs coarse regex-based extraction from fetched HTML pages.
    Tries to find SSID, WAN IP, LAN IP, MAC addresses, firmware version and DHCP clients.
    """
    html_concat = "\n".join(pages.values())
    summary = {
        "ssid": None,
        "wan_ip": None,
        "lan_ip": None,
        "firmware": None,
        "mac_addresses": [],
        "dhcp_clients": [],
    }

    ssid = re.search(r"(?:SSID|Network Name)[:\s]*([^\r\n<]+)", html_concat, re.IGNORECASE)
    if ssid:
        summary["ssid"] = ssid.group(1).strip()

    ip_pattern = r"(\d{1,3}(?:\.\d{1,3}){3})"
    wan = re.search(r"(?:WAN IP|Internet IP|IP Address)[^0-9]*" + ip_pattern, html_concat, re.IGNORECASE)
    if wan:
        summary["wan_ip"] = wan.group(1).strip()

    lan = re.search(r"(?:LAN IP|Gateway IP|Default Gateway)[^0-9]*" + ip_pattern, html_concat, re.IGNORECASE)
    if lan:
        summary["lan_ip"] = lan.group(1).strip()

    fw = re.search(r"(?:Firmware Version|Software Version)[:\s]*([^\r\n<]+)", html_concat, re.IGNORECASE)
    if fw:
        summary["firmware"] = fw.group(1).strip()

    for m in re.finditer(r"([0-9A-Fa-f]{2}(?:[:-][0-9A-Fa-f]{2}){5})", html_concat):
        mac = m.group(1).upper().replace(":", "-")
        if mac not in summary["mac_addresses"]:
            summary["mac_addresses"].append(mac)

    for line in html_concat.splitlines():
        m = re.findall(ip_pattern, line)
        macs = re.findall(r"([0-9A-Fa-f]{2}(?:[:-][0-9A-Fa-f]{2}){5})", line)
        if len(m) >= 1 and len(macs) >= 1:
            summary["dhcp_clients"].append({"ip": m[0], "mac": macs[0].upper().replace(":", "-")})

    return summary


def collect_router_details(ip_or_url: str, username: str, password: str, dump_dir: str) -> dict:
    """
    Orchestrates login attempts and scraping, saves pages to disk, and returns a summary dict.
    """
    base_url = normalize_base_url(ip_or_url)
    session = requests.Session()

    authed = try_basic_auth(session, base_url, username, password)
    if not authed:
        authed = try_form_logins(session, base_url, username, password)

    result = {
        "target": base_url,
        "authenticated": authed,
        "login_method": "basic" if authed and session.auth else "form" if authed else "none",
        "fetched_endpoints": [],
        "summary": {},
        "dump_path": dump_dir,
    }

    os.makedirs(dump_dir, exist_ok=True)
    pages = fetch_pages(session, base_url) if authed else {}
    result["fetched_endpoints"] = list(pages.keys())

    # Save raw pages for later inspection
    pages_dir = os.path.join(dump_dir, "pages")
    os.makedirs(pages_dir, exist_ok=True)
    for ep, html in pages.items():
        safe_name = ep.replace("/", "_") or "root"
        with open(os.path.join(pages_dir, f"{safe_name}.html"), "w", encoding="utf-8") as f:
            f.write(html)

    # Extract coarse summary
    result["summary"] = extract_summary(pages)
    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch router details via web interface.")
    parser.add_argument("ip_or_url", help="Router IP (e.g., 10.0.0.1) or full URL (e.g., http://10.0.0.1/)")
    parser.add_argument("--username", default="admin", help="Router admin username (default: admin)")
    parser.add_argument("--password", help="Router admin password (prompted if not provided)")
    parser.add_argument("--output", default=None, help="Output JSON file (default: results/router_<ip>_<timestamp>.json)")
    parser.add_argument("--mode", choices=["auto", "http", "js"], default="auto", help="Scrape mode: auto tries HTTP then JS")

    args = parser.parse_args()

    password = args.password or getpass.getpass("Enter Router Password: ")

    base_url = normalize_base_url(args.ip_or_url)

    if not is_url_reachable(base_url):
        gateways = get_gateway_candidates()
        for gw in gateways:
            alt = normalize_base_url(gw)
            if is_url_reachable(alt):
                print(f"Target {base_url} unreachable. Using gateway {alt} instead.")
                base_url = alt
                break

    ip_part = urlparse(base_url).netloc.split(":")[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_output = args.output or os.path.join("results", f"router_{ip_part}_{timestamp}.json")
    dump_dir = os.path.join("results", f"router_{ip_part}_{timestamp}")

    details = None
    if args.mode in ("auto", "http"):
        details = collect_router_details(args.ip_or_url, args.username, password, dump_dir)

    def _needs_js(d: dict) -> bool:
        if not d or not d.get("authenticated"):
            return True
        pages_dir = os.path.join(dump_dir, "pages")
        for name in d.get("fetched_endpoints", []):
            try:
                safe_name = name.replace("/", "_") or "root"
                with open(os.path.join(pages_dir, f"{safe_name}.html"), "r", encoding="utf-8") as f:
                    txt = f.read().lower()
                    if "does not support javascript" in txt or "enable javascript" in txt:
                        return True
            except Exception:
                pass
        return False

    if args.mode == "js" or (args.mode == "auto" and _needs_js(details or {})):
        try:
            # Lazy import Selenium so it is optional
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.edge.options import Options as EdgeOptions
        except Exception as e:
            print(f"Selenium not available: {e}")
            print("Install with: pip install selenium")
            sys.exit(1)

        def get_edge_driver():
            opts = EdgeOptions()
            opts.add_argument("--headless=new")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--no-sandbox")
            return webdriver.Edge(options=opts)

        def login_with_js(driver, base_url, username, password):
            driver.get(base_url)
            try:
                WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
            except Exception:
                pass

            # Try filling username/password
            selectors_user = ["input[name='username']", "input#username", "input[name='UserName']"]
            selectors_pass = ["input[type='password']", "input[name='password']", "input#password"]
            user_el = None
            pass_el = None
            for sel in selectors_user:
                try:
                    user_el = driver.find_element(By.CSS_SELECTOR, sel)
                    break
                except Exception:
                    continue
            for sel in selectors_pass:
                try:
                    pass_el = driver.find_element(By.CSS_SELECTOR, sel)
                    break
                except Exception:
                    continue
            if pass_el:
                if user_el:
                    try:
                        user_el.clear()
                        user_el.send_keys(username)
                    except Exception:
                        pass
                try:
                    pass_el.clear()
                    pass_el.send_keys(password)
                except Exception:
                    pass
                # Try clicking submit buttons
                btn_selectors = ["button[type='submit']", "input[type='submit']", "#loginBtn", ".btn-login"]
                clicked = False
                for sel in btn_selectors:
                    try:
                        driver.find_element(By.CSS_SELECTOR, sel).click()
                        clicked = True
                        break
                    except Exception:
                        continue
                if not clicked:
                    try:
                        pass_el.submit()
                    except Exception:
                        pass
                time.sleep(2)

        def fetch_pages_js(driver, base_url):
            endpoints = [
                "", "index.asp", "status.asp", "status.html", "home.asp",
                "system.asp", "deviceinfo.asp", "sysinfo.cgi", "wan.asp", "lan.asp",
                "wireless.asp", "wlstatus.asp", "lan_dhcp_clients.asp", "dhcp_clients.asp",
                "admin/status", "cgi-bin/status", "cgi-bin/diagnostic", "userRpm/StatusRpm.htm",
            ]
            pages_local = {}
            shots_dir = os.path.join(dump_dir, "screenshots")
            os.makedirs(shots_dir, exist_ok=True)
            for ep in endpoints:
                url = urljoin(base_url, ep)
                try:
                    driver.get(url)
                    WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
                    html = driver.page_source
                    pages_local[ep or "/"] = html
                    safe_name = (ep.replace("/", "_") or "root") + ".png"
                    driver.save_screenshot(os.path.join(shots_dir, safe_name))
                except Exception:
                    pass
                time.sleep(0.2)
            return pages_local

        base = base_url
        driver = None
        try:
            driver = get_edge_driver()
            login_with_js(driver, base, args.username, password)
            pages = fetch_pages_js(driver, base)

            # Dump pages (overwriting any HTTP-mode ones with JS-rendered content)
            pages_dir = os.path.join(dump_dir, "pages")
            os.makedirs(pages_dir, exist_ok=True)
            for ep, html in pages.items():
                safe_name = ep.replace("/", "_") or "root"
                with open(os.path.join(pages_dir, f"{safe_name}.html"), "w", encoding="utf-8") as f:
                    f.write(html)

            details = {
                "target": base,
                "authenticated": True,
                "login_method": "js",
                "fetched_endpoints": list(pages.keys()),
                "summary": extract_summary(pages),
                "dump_path": dump_dir,
            }
        finally:
            try:
                if driver:
                    driver.quit()
            except Exception:
                pass

    try:
        os.makedirs(os.path.dirname(default_output), exist_ok=True)
        with open(default_output, "w", encoding="utf-8") as f:
            json.dump(details, f, indent=2, ensure_ascii=False)
        print(f"Router details saved to {default_output}")
        print(f"Fetched pages saved to {os.path.join(dump_dir, 'pages')}")
        shots_dir = os.path.join(dump_dir, "screenshots")
        if os.path.isdir(shots_dir):
            print(f"Screenshots saved to {shots_dir}")
    except IOError as e:
        print(f"Error saving file: {e}")


if __name__ == "__main__":
    main()
