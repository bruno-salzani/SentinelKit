def run():
    import dns_cache_dump

    sample = """
    Record Name . . . . . : example.com
    Record Type . . . . . : 1
    Time To Live  . . . . : 300
    Data . . . . . . . .  : 93.184.216.34

    Record Name . . . . . : test.local
    Record Type . . . . . : 5
    Time To Live  . . . . : 120
    Data . . . . . . . .  : alias.local
    """.strip()

    class FakeProc:
        @staticmethod
        def check_output(args):
            return sample.encode("utf-8")

    dns_cache_dump.subprocess = FakeProc
    data = dns_cache_dump.parse()
    assert "entries" in data and len(data["entries"]) == 2
    assert data["entries"][0]["name"] == "example.com"
    assert "data" in data["entries"][0] and data["entries"][0]["data"][0] == "93.184.216.34"
    print("dns_cache_dump OK")

if __name__ == "__main__":
    run()
