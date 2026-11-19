"""Portable loopback demo; not a substitute for Linux topology experiments."""
import json
from pathlib import Path
import socket
import threading
from http.server import ThreadingHTTPServer
from .service import Handler, dns_response
from .probe import run_probe


def main():
    stop = threading.Event()
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    http_thread = threading.Thread(target=server.serve_forever, daemon=True)
    http_thread.start()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.settimeout(.2)
        def dns_server():
            while not stop.is_set():
                try:
                    packet, peer = sock.recvfrom(4096)
                    reply = dns_response(packet, "127.0.0.1")
                    if reply:
                        sock.sendto(reply, peer)
                except socket.timeout:
                    continue
        thread = threading.Thread(target=dns_server, daemon=True)
        thread.start()
        try:
            result = run_probe("127.0.0.1", port=server.server_port, dns_port=sock.getsockname()[1])
            result["environment"] = "Windows/Linux loopback demo; not namespace topology"
            output = Path("results") / "loopback-demo.json"
            output.parent.mkdir(exist_ok=True)
            rendered = json.dumps(result, ensure_ascii=False, indent=2)
            output.write_text(rendered, encoding="utf-8")
            print(rendered)
            print(f"Saved: {output}")
        finally:
            stop.set()
            thread.join(timeout=2)
            server.shutdown()
            server.server_close()
            http_thread.join(timeout=2)


if __name__ == "__main__":
    main()
