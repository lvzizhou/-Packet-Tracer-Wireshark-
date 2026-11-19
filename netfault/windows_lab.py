"""Interactive, loopback-only real DNS/HTTP fault experiments."""
import argparse
import json
from pathlib import Path
import socket
import threading
import time
from http.server import ThreadingHTTPServer
from .service import Handler, dns_response
from .probe import run_probe


class Lab:
    def __init__(self, http_port=8080, dns_port=53535):
        self.http_port, self.dns_port = http_port, dns_port
        self.record = "127.0.0.1"
        self.http = None
        self.http_thread = None
        self.stop = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", dns_port))
        self.sock.settimeout(.2)
        self.dns_thread = threading.Thread(target=self.serve_dns, daemon=True)
        self.dns_thread.start()
        try:
            self.start_http()
        except BaseException:
            self.close()
            raise

    def serve_dns(self):
        while not self.stop.is_set():
            try:
                data, peer = self.sock.recvfrom(4096)
                reply = dns_response(data, self.record)
                if reply:
                    self.sock.sendto(reply, peer)
            except socket.timeout:
                continue

    def start_http(self):
        if self.http is None:
            self.http = ThreadingHTTPServer(("127.0.0.1", self.http_port), Handler)
            self.http_port = self.http.server_port
            self.http_thread = threading.Thread(target=self.http.serve_forever, daemon=True)
            self.http_thread.start()

    def stop_http(self):
        if self.http:
            self.http.shutdown()
            self.http.server_close()
            self.http_thread.join(timeout=2)
            self.http = None

    def scenario(self, name):
        self.record = "127.0.0.2" if name in ("dns", "combined") else "127.0.0.1"
        if name in ("port", "combined"):
            self.stop_http()
        else:
            self.start_http()

    def probe(self, name):
        result = run_probe("127.0.0.1", dns_server="127.0.0.1", port=self.http_port,
                           dns_port=self.sock.getsockname()[1], timeout=5)
        # The label is attached after diagnosis, and is never used by diagnose().
        result["experiment"] = {"scenario": name, "environment": "real loopback sockets; no simulated routers"}
        directory = Path("results") / "windows"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{time.time_ns()}-{name}.json"
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"Saved: {path}")
        return result

    def close(self):
        self.stop_http()
        self.stop.set()
        self.dns_thread.join(timeout=2)
        self.sock.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--http-port", type=int, default=8080)
    parser.add_argument("--dns-port", type=int, default=53535)
    parser.add_argument("--batch", action="store_true", help="run all local scenarios without interaction")
    args = parser.parse_args()
    lab = Lab(args.http_port, args.dns_port)
    try:
        print(f"HTTP 127.0.0.1:{lab.http_port}; DNS 127.0.0.1:{lab.sock.getsockname()[1]}")
        print("Wireshark: select Npcap Loopback Adapter; decode UDP 53535 as DNS and TCP 8080 as HTTP.")
        if args.batch:
            for name in ("baseline", "dns", "port", "combined", "baseline"):
                lab.scenario(name)
                lab.probe(name)
        else:
            print("Commands: baseline / dns / port / combined / probe / quit")
            current = "baseline"
            while True:
                value = input("netfault> ").strip().lower()
                if value == "quit":
                    break
                if value in ("baseline", "dns", "port", "combined"):
                    current = value
                    lab.scenario(value)
                elif value != "probe":
                    continue
                lab.probe(current)
    finally:
        lab.close()


if __name__ == "__main__":
    main()
