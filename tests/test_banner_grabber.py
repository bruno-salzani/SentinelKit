def run():
    import banner_grabber as bg

    class FakeSocket:
        def settimeout(self, t):
            pass
        def connect(self, addr):
            pass
        def sendall(self, data):
            pass
        def recv(self, n):
            return b"FAKE BANNER"
        def close(self):
            pass

    class FakeSockModule:
        AF_INET = 0
        SOCK_STREAM = 0
        def socket(self, *args, **kwargs):
            return FakeSocket()

    bg.socket = FakeSockModule()
    res = bg.probe("example.com", 80)
    assert res.get("banner") == "FAKE BANNER"
    print("banner_grabber OK")

if __name__ == "__main__":
    run()
