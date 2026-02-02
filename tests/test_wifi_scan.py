import sys
import os

def run():
    import wifi_scan

    sample = """
SSID 1 : MyWifi
    Authentication : WPA2-Personal
    Encryption : CCMP
    BSSID 1 : 00:11:22:33:44:55
    Signal : 85%
    Channel : 6
SSID 2 : GuestNet
    Authentication : WPA2-Personal
    Encryption : CCMP
    BSSID 1 : 66:77:88:99:AA:BB
    Signal : 40%
    Channel : 11
""".strip()

    class FakeProc:
        @staticmethod
        def check_output(args):
            return sample.encode("utf-8")

    wifi_scan.subprocess = FakeProc
    data = wifi_scan.parse()
    assert "networks" in data and len(data["networks"]) == 2
    assert data["networks"][0]["ssid"] == "MyWifi"
    assert data["networks"][1]["ssid"] == "GuestNet"
    print("wifi_scan OK")

if __name__ == "__main__":
    run()
