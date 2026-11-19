"""Linux-only orchestration. All topology changes are confined to nf-* namespaces."""
import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".state"
RESULTS = ROOT / "results"
NAMES = ("nf-client", "nf-router", "nf-server")
FAULTS = ("link", "route", "dns", "port", "firewall", "weak")


def command(*args, check=True):
    return subprocess.run(list(args), check=check, capture_output=True, text=True)


def ns(name, *args, check=True):
    return command("ip", "netns", "exec", name, *args, check=check)


def require_environment():
    if sys.platform != "linux" or os.geteuid() != 0:
        raise SystemExit("请在 Linux/WSL2 内以 sudo 运行此命令；Windows 可运行 unittest。")
    for tool in ("ip", "tc", "iptables", "tcpdump", "ss"):
        if not shutil.which(tool):
            raise SystemExit(f"缺少工具 {tool}；请按照 README 安装依赖。")


def start_service(kind):
    args = [sys.executable, "-m", "netfault.service", kind, "--port", "53" if kind == "dns" else "8080"]
    if kind == "dns":
        args += ["--record", str(STATE / "dns-record")]
    with (STATE / f"{kind}.log").open("a") as log:
        proc = subprocess.Popen(["ip", "netns", "exec", "nf-server", *args], cwd=ROOT,
                                stdout=log, stderr=subprocess.STDOUT)
    time.sleep(0.2)
    if proc.poll() is not None:
        raise RuntimeError(f"{kind} 服务启动失败，检查 .state/{kind}.log")


def stop_http():
    # Match both module and kind, and enumerate only processes inside our namespace.
    for pid in ns("nf-server", "ip", "netns", "pids", "nf-server").stdout.split():
        try:
            args = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
            if b"netfault.service" in args and b"http" in args:
                os.kill(int(pid), 15)
        except (FileNotFoundError, ProcessLookupError):
            pass
    time.sleep(0.2)


def owned():
    if not (STATE / "owned").exists():
        raise SystemExit("实验尚未创建，先运行 setup。")


def setup():
    existing = {line.split()[0] for line in command("ip", "netns", "list").stdout.splitlines()}
    if existing.intersection(NAMES):
        raise SystemExit("nf-* 命名空间已存在。若属于本项目，请先 teardown；不会覆盖现有网络。")
    STATE.mkdir(exist_ok=True)
    (STATE / "owned").write_text("netfault-lab-v1")
    try:
        for name in NAMES:
            command("ip", "netns", "add", name)
            ns(name, "ip", "link", "set", "lo", "up")
        # Create pairs directly inside namespaces; host interfaces/routes stay untouched.
        ns("nf-client", "ip", "link", "add", "eth0", "type", "veth", "peer", "name", "lan0", "netns", "nf-router")
        ns("nf-server", "ip", "link", "add", "eth0", "type", "veth", "peer", "name", "lan1", "netns", "nf-router")
        for name, iface, address in (("nf-client", "eth0", "10.10.0.2/24"),
                                     ("nf-router", "lan0", "10.10.0.1/24"),
                                     ("nf-router", "lan1", "10.20.0.1/24"),
                                     ("nf-server", "eth0", "10.20.0.2/24")):
            ns(name, "ip", "addr", "add", address, "dev", iface)
            ns(name, "ip", "link", "set", iface, "up")
        ns("nf-client", "ip", "route", "add", "default", "via", "10.10.0.1")
        ns("nf-server", "ip", "route", "add", "default", "via", "10.20.0.1")
        ns("nf-router", "sysctl", "-qw", "net.ipv4.ip_forward=1")
        (STATE / "dns-record").write_text("10.20.0.2")
        start_service("dns")
        start_service("http")
        print("拓扑创建完成。运行 diagnose 验证基线。")
    except BaseException:
        teardown()
        raise


def restore():
    owned()
    ns("nf-client", "ip", "link", "set", "eth0", "up")
    ns("nf-client", "ip", "route", "replace", "default", "via", "10.10.0.1")
    (STATE / "dns-record").write_text("10.20.0.2")
    ns("nf-router", "iptables", "-F", "FORWARD")
    ns("nf-router", "tc", "qdisc", "del", "dev", "lan1", "root", check=False)
    stop_http()
    start_service("http")
    (STATE / "scenario").write_text("baseline")


def inject(fault):
    restore()  # one controlled fault at a time
    if fault == "link":
        ns("nf-client", "ip", "link", "set", "eth0", "down")
    elif fault == "route":
        ns("nf-client", "ip", "route", "del", "default")
    elif fault == "dns":
        (STATE / "dns-record").write_text("10.20.0.99")
    elif fault == "port":
        stop_http()
    elif fault == "firewall":
        ns("nf-router", "iptables", "-A", "FORWARD", "-p", "tcp", "--dport", "8080", "-j", "DROP")
    elif fault == "weak":
        ns("nf-router", "tc", "qdisc", "add", "dev", "lan1", "root", "netem",
           "delay", "80ms", "loss", "1%", "rate", "5mbit")
    (STATE / "scenario").write_text(fault)
    print(f"已注入 {fault}；诊断器不会读取此标签。")


def diagnose():
    owned()
    RESULTS.mkdir(exist_ok=True)
    stamp = time.time_ns()
    output = RESULTS / f"probe-{stamp}.json"
    result = ns("nf-client", sys.executable, "-m", "netfault.probe", "--linux-local", "--output", str(output))
    print(result.stdout)
    return output


def collect():
    owned()
    directory = RESULTS / f"evidence-{time.time_ns()}"
    directory.mkdir(parents=True)
    for name in NAMES:
        chunks = []
        for args in (("ip", "-details", "addr"), ("ip", "route"), ("ip", "neigh"),
                     ("ss", "-lntup"), ("ss", "-ti"), ("iptables", "-nvL"),
                     ("tc", "-s", "qdisc", "show")):
            result = ns(name, *args, check=False)
            chunks.append("$ " + " ".join(args) + "\n" + result.stdout + result.stderr)
        (directory / f"{name}.txt").write_text("\n".join(chunks))
    processes, handles = [], []
    try:
        for name in ("nf-client", "nf-server"):
            log = (directory / f"{name}-capture.log").open("w")
            handles.append(log)
            processes.append(subprocess.Popen(["ip", "netns", "exec", name, "tcpdump", "-U", "-i", "eth0",
                                                "-w", str(directory / f"{name}.pcap"),
                                                "arp or icmp or port 53 or tcp port 8080"], stdout=log, stderr=log))
        time.sleep(0.5)
        if any(p.poll() is not None for p in processes):
            raise RuntimeError("抓包启动失败，查看 capture.log")
        # Clear client neighbor cache to observe ARP when link and route are healthy.
        ns("nf-client", "ip", "neigh", "flush", "dev", "eth0", check=False)
        output = diagnose()
        shutil.copy2(output, directory / "probe.json")
    finally:
        for proc in processes:
            if proc.poll() is None:
                proc.send_signal(2)
                proc.wait(timeout=5)
        for handle in handles:
            handle.close()
    print(f"证据目录：{directory}")


def benchmark():
    owned()
    rows = []
    try:
        for scenario in ("baseline", "weak"):
            if scenario == "baseline":
                restore()
            else:
                inject("weak")
            for trial in range(1, 6):
                path = diagnose()
                data = json.loads(path.read_text())
                measurement = data["observations"]["direct_http"]
                rows.append({"scenario": scenario, "trial": trial, "ok": measurement["ok"],
                             "seconds": measurement["seconds"], "mbps": measurement.get("mbps", ""),
                             "bytes": measurement.get("bytes", 0), "source": path.name})
        RESULTS.mkdir(exist_ok=True)
        path = RESULTS / f"benchmark-{time.time_ns()}.csv"
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"性能结果：{path}；失败试次保留，不计作成功吞吐量。")
    finally:
        restore()


def teardown():
    owned()
    existing = {line.split()[0] for line in command("ip", "netns", "list").stdout.splitlines()}
    for name in NAMES:
        if name not in existing:
            continue
        for pid in command("ip", "netns", "pids", name).stdout.split():
            try:
                os.kill(int(pid), 15)
            except ProcessLookupError:
                pass
        command("ip", "netns", "del", name)
    (STATE / "owned").unlink()
    print("实验命名空间已清理，结果保留。")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["setup", "inject", "restore", "diagnose", "collect", "benchmark", "teardown"])
    parser.add_argument("fault", nargs="?", choices=FAULTS)
    args = parser.parse_args()
    if args.action == "inject" and not args.fault:
        parser.error("inject 需要故障名")
    require_environment()
    os.chdir(ROOT)
    if args.action == "inject":
        inject(args.fault)
    else:
        globals()[args.action]()


if __name__ == "__main__":
    main()
