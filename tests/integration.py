"""Requires root Linux. Run on a dedicated runner, never concurrently."""
import json
from netfault.lab import setup, teardown, restore, inject, diagnose, collect, require_environment


def main():
    require_environment()
    setup()
    try:
        expected = {"link": "LINK_DOWN", "route": "NO_ROUTE", "dns": "DNS_MISMATCH",
                    "port": "CONNECTION_REFUSED", "firewall": "PATH_OR_FILTER", "weak": "REACHABLE"}
        assert json.loads(diagnose().read_text())["diagnosis"]["code"] == "REACHABLE"
        for fault, code in expected.items():
            inject(fault)
            result = json.loads(diagnose().read_text())
            assert result["diagnosis"]["code"] == code, (fault, result)
            restore()
            assert json.loads(diagnose().read_text())["diagnosis"]["code"] == "REACHABLE"
        collect()
    finally:
        teardown()
    # Verify full teardown and re-creation as well as initial setup.
    setup()
    teardown()


if __name__ == "__main__":
    main()
