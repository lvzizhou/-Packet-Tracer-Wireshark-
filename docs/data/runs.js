window.NETFAULT_RUNS = [
  {
    "timestamp": "2026-11-18T20:10:16.52206+08:00",
    "observations": {
      "dns": {
        "ok": true,
        "address": "127.0.0.1"
      },
      "direct_http": {
        "ok": true,
        "status": 200,
        "bytes": 1135966,
        "seconds": 0.00174,
        "mbps": 5222.532
      },
      "domain_http": {
        "ok": true,
        "status": 200,
        "bytes": 1135966,
        "seconds": 0.00149,
        "mbps": 6101.193
      }
    },
    "diagnosis": {
      "code": "REACHABLE",
      "summary": "DNS 与 HTTP 访问成功；性能需结合基线比较",
      "next": "比较多次下载耗时，查看重传与 RTT"
    },
    "experiment": {
      "scenario": "baseline",
      "environment": "real loopback sockets; no simulated routers"
    }
  },
  {
    "timestamp": "2026-11-18T20:10:18.581832+08:00",
    "observations": {
      "dns": {
        "ok": true,
        "address": "127.0.0.2"
      },
      "direct_http": {
        "ok": true,
        "status": 200,
        "bytes": 1135966,
        "seconds": 0.023644,
        "mbps": 384.353
      },
      "domain_http": {
        "ok": false,
        "kind": "refused",
        "error": "[WinError 10061] 由于目标计算机积极拒绝，无法连接。",
        "seconds": 2.033521
      }
    },
    "diagnosis": {
      "code": "DNS_MISMATCH",
      "summary": "域名解析结果与实验预期地址不一致",
      "next": "核对 DNS 记录及服务器地址"
    },
    "experiment": {
      "scenario": "dns",
      "environment": "real loopback sockets; no simulated routers"
    }
  },
  {
    "timestamp": "2026-11-18T20:10:23.141359+08:00",
    "observations": {
      "dns": {
        "ok": true,
        "address": "127.0.0.1"
      },
      "direct_http": {
        "ok": false,
        "kind": "refused",
        "error": "[WinError 10061] 由于目标计算机积极拒绝，无法连接。",
        "seconds": 2.043032
      },
      "domain_http": {
        "ok": false,
        "kind": "refused",
        "error": "[WinError 10061] 由于目标计算机积极拒绝，无法连接。",
        "seconds": 2.030753
      }
    },
    "diagnosis": {
      "code": "CONNECTION_REFUSED",
      "summary": "TCP 连接被拒绝",
      "next": "检查监听端口及防火墙 REJECT；用 ss 和抓包区分"
    },
    "experiment": {
      "scenario": "port",
      "environment": "real loopback sockets; no simulated routers"
    }
  },
  {
    "timestamp": "2026-11-18T20:10:27.254813+08:00",
    "observations": {
      "dns": {
        "ok": true,
        "address": "127.0.0.2"
      },
      "direct_http": {
        "ok": false,
        "kind": "refused",
        "error": "[WinError 10061] 由于目标计算机积极拒绝，无法连接。",
        "seconds": 2.032731
      },
      "domain_http": {
        "ok": false,
        "kind": "refused",
        "error": "[WinError 10061] 由于目标计算机积极拒绝，无法连接。",
        "seconds": 2.071374
      }
    },
    "diagnosis": {
      "code": "DNS_MISMATCH",
      "summary": "域名解析结果与实验预期地址不一致",
      "next": "核对 DNS 记录及服务器地址"
    },
    "experiment": {
      "scenario": "combined",
      "environment": "real loopback sockets; no simulated routers"
    }
  },
  {
    "timestamp": "2026-11-18T20:10:27.260683+08:00",
    "observations": {
      "dns": {
        "ok": true,
        "address": "127.0.0.1"
      },
      "direct_http": {
        "ok": true,
        "status": 200,
        "bytes": 1135966,
        "seconds": 0.001764,
        "mbps": 5152.942
      },
      "domain_http": {
        "ok": true,
        "status": 200,
        "bytes": 1135966,
        "seconds": 0.00177,
        "mbps": 5134.31
      }
    },
    "diagnosis": {
      "code": "REACHABLE",
      "summary": "DNS 与 HTTP 访问成功；性能需结合基线比较",
      "next": "比较多次下载耗时，查看重传与 RTT"
    },
    "experiment": {
      "scenario": "baseline",
      "environment": "real loopback sockets; no simulated routers"
    }
  }
];
