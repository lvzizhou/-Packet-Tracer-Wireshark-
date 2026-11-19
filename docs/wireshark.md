# Wireshark 真实协议实验

安装官方 Wireshark 与 Npcap。无需虚拟机；管理员安装和账号认证由本人操作。

1. 打开 Wireshark，选择 Adapter for loopback traffic capture / Npcap Loopback Adapter，不选 Wi-Fi 或以太网。
2. 在开始抓包前填写捕获过滤器：`udp port 53535 or tcp port 8080`，再启动。
3. 在项目根目录运行 `python -m netfault.windows_lab`。
4. 输入 baseline。停止抓包，保存 baseline.pcapng。
5. UDP 53535 不自动识别时，选 UDP 包 → Analyze → Decode As → UDP port 53535 → DNS。TCP 8080 必要时 Decode As HTTP。
6. 开始新抓包，分别输入 dns、port、combined，保存独立文件。程序一次诊断先 DNS、再直接 IP HTTP、最后解析 IP HTTP，因此基线含两次下载。
7. 组合故障先输入 port（只修复 DNS），再输入 baseline（恢复服务），分别抓取并保存。
8. 完成后输入 quit，服务自动关闭。

显示过滤器：`dns`、`tcp.port == 8080`、`http`、`tcp.flags.syn == 1`、`tcp.flags.reset == 1`。拒绝连接的时序因 Windows 内核而异，不根据等待长短单独判断原因。

回环通信没有真实以太网 ARP，也不经过路由器；ARP、跨网段 MAC 改变、TTL 和 ACL 用 Packet Tracer Simulation 展示。回环 TCP 校验和或分段表现受系统抓包机制影响，不据此断言网络错误。

每份截图标出场景、帧号、地址/端口和关键字段；不要将另一次运行的 JSON 时间与当前 PCAP 冒充同一次证据。DNS 错误指向 127.0.0.2，但 HTTP 只绑定 127.0.0.1，因此直接 IP 可成功而错误地址失败。
