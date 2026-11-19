import socket
import struct
import threading
import unittest
from http.server import ThreadingHTTPServer
from netfault.service import Handler, dns_response, BODY
from netfault.probe import diagnose, dns_query, http_probe, run_probe


class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()

    def test_real_dns_http_flow(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
            def server():
                data, peer = sock.recvfrom(2048)
                sock.sendto(dns_response(data, "127.0.0.1"), peer)
            thread = threading.Thread(target=server)
            thread.start()
            result = run_probe("127.0.0.1", port=self.http.server_port, dns_port=port, timeout=1)
            thread.join(timeout=2)
        self.assertEqual(result["diagnosis"]["code"], "REACHABLE")
        self.assertEqual(result["observations"]["domain_http"]["bytes"], len(BODY))

    def test_refused_port(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
            # Bound but not listening: no unrelated service can take this port.
            self.assertEqual(http_probe("127.0.0.1", port, 5)["kind"], "refused")

    def test_dns_timeout(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("127.0.0.1", 0))
            with self.assertRaises(TimeoutError):
                dns_query("127.0.0.1", sock.getsockname()[1], .05)

    def test_malformed_dns(self):
        self.assertIsNone(dns_response(b"bad", "127.0.0.1"))
        packet = struct.pack("!HHHHHH", 1, 0, 1, 0, 0, 0) + b"\xc0\x0c"
        self.assertIsNone(dns_response(packet, "127.0.0.1"))

    def test_evidence_diagnosis_and_uncertainty(self):
        base = {"dns": {"ok": True, "address": "10.20.0.2"}, "direct_http": {"ok": False, "kind": "timeout"}}
        self.assertEqual(diagnose(base, "10.20.0.2")["code"], "PATH_OR_FILTER")
        self.assertEqual(diagnose(dict(base, link={"up": False}), "10.20.0.2")["code"], "LINK_DOWN")
        self.assertEqual(diagnose(dict(base, route={"ok": False}), "10.20.0.2")["code"], "NO_ROUTE")
        wrong = dict(base, dns={"ok": True, "address": "10.20.0.99"})
        self.assertEqual(diagnose(wrong, "10.20.0.2")["code"], "DNS_MISMATCH")


if __name__ == "__main__":
    unittest.main()
