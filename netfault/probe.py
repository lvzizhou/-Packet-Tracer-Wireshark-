"""Active probes. Diagnosis uses observations, never the injected fault label."""
import argparse
import errno
import http.client
import json
import secrets
import socket
import struct
import time
from datetime import datetime, timezone
from pathlib import Path

DOMAIN = "web.lab.test"


def dns_query(server, port=53, timeout=2):
    ident = secrets.randbelow(65536)
    name = b"".join(bytes([len(label)]) + label.encode() for label in DOMAIN.split(".")) + b"\0"
    query = struct.pack("!HHHHHH", ident, 0x0100, 1, 0, 0, 0) + name + struct.pack("!HH", 1, 1)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.connect((server, port))
        sock.send(query)
        data = sock.recv(4096)
    if len(data) < 12:
        raise ValueError("truncated DNS header")
    rid, flags, qd, an, _, _ = struct.unpack("!HHHHHH", data[:12])
    if rid != ident or not flags & 0x8000 or flags & 0x0200 or flags & 15:
        raise ValueError("DNS transaction mismatch, truncation or error response")

    def skip_name(pos):
        while pos < len(data):
            size = data[pos]
            if size & 0xC0 == 0xC0:
                if pos + 1 >= len(data):
                    break
                return pos + 2
            pos += 1
            if size == 0:
                return pos
            if size > 63 or pos + size > len(data):
                break
            pos += size
        raise ValueError("malformed DNS name")

    pos = 12
    for _ in range(qd):
        pos = skip_name(pos) + 4
    for _ in range(an):
        pos = skip_name(pos)
        kind, klass, _, length = struct.unpack("!HHIH", data[pos:pos + 10])
        pos += 10
        if pos + length > len(data):
            raise ValueError("truncated DNS answer")
        if kind == 1 and klass == 1 and length == 4:
            return socket.inet_ntoa(data[pos:pos + 4])
        pos += length
    raise ValueError("no IPv4 A answer")


def error_kind(exc):
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return "timeout"
    if isinstance(exc, ConnectionRefusedError):
        return "refused"
    if isinstance(exc, OSError) and exc.errno in (errno.ENETUNREACH, errno.EHOSTUNREACH, errno.ENETDOWN):
        return "unreachable"
    return "error"


def http_probe(address, port=8080, timeout=4):
    start = time.perf_counter()
    conn = http.client.HTTPConnection(address, port, timeout=timeout)
    try:
        conn.request("GET", "/download", headers={"Host": DOMAIN, "Connection": "close"})
        response = conn.getresponse()
        body = response.read()
        elapsed = time.perf_counter() - start
        return {"ok": response.status == 200, "status": response.status,
                "bytes": len(body), "seconds": round(elapsed, 6),
                "mbps": round(len(body) * 8 / elapsed / 1e6, 3)}
    except (OSError, http.client.HTTPException) as exc:
        return {"ok": False, "kind": error_kind(exc), "error": str(exc),
                "seconds": round(time.perf_counter() - start, 6)}
    finally:
        conn.close()


def diagnose(observations, expected_ip):
    link = observations.get("link", {})
    route = observations.get("route", {})
    dns = observations["dns"]
    direct = observations["direct_http"]
    if link.get("up") is False:
        return {"code": "LINK_DOWN", "summary": "客户端接口未启用", "next": "检查客户端接口状态及虚拟链路"}
    if route.get("ok") is False:
        return {"code": "NO_ROUTE", "summary": "缺少到服务器的有效路由", "next": "检查默认路由和网关"}
    if dns.get("ok") and dns.get("address") != expected_ip:
        return {"code": "DNS_MISMATCH", "summary": "域名解析结果与实验预期地址不一致", "next": "核对 DNS 记录及服务器地址"}
    if not dns.get("ok") and direct.get("ok"):
        return {"code": "DNS_FAILURE", "summary": "IP 访问正常，但 DNS 查询失败", "next": "检查 DNS 服务、UDP 53 和解析配置"}
    if direct.get("kind") == "refused":
        return {"code": "CONNECTION_REFUSED", "summary": "TCP 连接被拒绝", "next": "检查监听端口及防火墙 REJECT；用 ss 和抓包区分"}
    if direct.get("kind") in ("timeout", "unreachable"):
        return {"code": "PATH_OR_FILTER", "summary": "路径异常或流量被丢弃，单凭客户端不能唯一定位", "next": "对比两端抓包、路由器转发状态与防火墙计数"}
    if direct.get("ok") and dns.get("ok") and observations.get("domain_http", {}).get("ok"):
        return {"code": "REACHABLE", "summary": "DNS 与 HTTP 访问成功；性能需结合基线比较", "next": "比较多次下载耗时，查看重传与 RTT"}
    return {"code": "INCONCLUSIVE", "summary": "证据不足，需进一步检查", "next": "检查服务日志并对比客户端与服务器抓包"}


def run_probe(server="10.20.0.2", dns_server=None, port=8080, dns_port=53,
              timeout=4, local_observations=None):
    obs = dict(local_observations or {})
    try:
        address = dns_query(dns_server or server, dns_port, timeout)
        obs["dns"] = {"ok": True, "address": address}
    except (OSError, ValueError, struct.error) as exc:
        obs["dns"] = {"ok": False, "kind": error_kind(exc), "error": str(exc)}
    obs["direct_http"] = http_probe(server, port, timeout)
    if obs["dns"].get("ok"):
        obs["domain_http"] = http_probe(obs["dns"]["address"], port, timeout)
    return {"timestamp": datetime.now(timezone.utc).isoformat(), "observations": obs,
            "diagnosis": diagnose(obs, server)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", default="10.20.0.2")
    parser.add_argument("--dns-server")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--dns-port", type=int, default=53)
    parser.add_argument("--timeout", type=float, default=4)
    parser.add_argument("--output")
    parser.add_argument("--linux-local", action="store_true")
    args = parser.parse_args()
    local = {}
    if args.linux_local:
        import subprocess
        link = subprocess.run(["ip", "-j", "link", "show", "dev", "eth0"], capture_output=True, text=True)
        if link.returncode == 0:
            entries = json.loads(link.stdout)
            local["link"] = {"up": "UP" in entries[0]["flags"], "raw": entries}
        route = subprocess.run(["ip", "-j", "route", "get", args.server], capture_output=True, text=True)
        local["route"] = {"ok": route.returncode == 0, "raw": route.stdout or route.stderr}
    result = run_probe(args.server, args.dns_server, args.port, args.dns_port, args.timeout, local)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
