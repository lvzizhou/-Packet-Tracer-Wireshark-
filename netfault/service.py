"""Small, deliberately restricted DNS/HTTP services for the isolated lab."""
import argparse
import http.server
import json
import socket
import struct
from pathlib import Path

DOMAIN = "web.lab.test"
BODY = b"netfault-lab\n" * 87382  # approximately 1 MiB; deterministic download


def dns_response(packet, address):
    if len(packet) < 12:
        return None
    ident, flags, questions = struct.unpack("!HHH", packet[:6])
    if flags & 0x8000 or questions != 1:
        return None
    pos, labels = 12, []
    while pos < len(packet):
        length = packet[pos]
        pos += 1
        if length == 0:
            break
        if length > 63 or pos + length > len(packet):
            return None
        labels.append(packet[pos:pos + length].decode("ascii", errors="replace"))
        pos += length
    else:
        return None
    if pos + 4 > len(packet):
        return None
    kind, klass = struct.unpack("!HH", packet[pos:pos + 4])
    question = packet[12:pos + 4]
    known = ".".join(labels).lower() == DOMAIN
    answerable = known and kind == 1 and klass == 1
    # Preserve RD; this authoritative teaching server does not provide recursion.
    response_flags = 0x8400 | (flags & 0x0100) | (0 if known else 3)
    header = struct.pack("!HHHHHH", ident, response_flags, 1, int(answerable), 0, 0)
    answer = struct.pack("!HHHIH", 0xC00C, 1, 1, 0, 4) + socket.inet_aton(address)
    return header + question + (answer if answerable else b"")


def serve_dns(bind, port, record):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((bind, port))
        while True:
            packet, peer = sock.recvfrom(4096)
            try:
                address = Path(record).read_text().strip()
                reply = dns_response(packet, address)
                if reply:
                    sock.sendto(reply, peer)
            except (OSError, ValueError, struct.error):
                continue


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        if self.path == "/download":
            body, content_type, status = BODY, "application/octet-stream", 200
        elif self.path == "/":
            body = json.dumps({"service": "netfault-lab", "download": "/download"}).encode()
            content_type, status = "application/json", 200
        else:
            body, content_type, status = b"not found\n", "text/plain", 404
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["dns", "http"])
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--record")
    args = parser.parse_args()
    if args.kind == "dns":
        if not args.record:
            parser.error("DNS requires --record")
        serve_dns(args.bind, args.port, args.record)
    else:
        http.server.ThreadingHTTPServer((args.bind, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
