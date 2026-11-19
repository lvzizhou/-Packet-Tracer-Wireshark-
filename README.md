# NetFault Lab 无虚拟机版

课程选题：基于 Packet Tracer 与 Wireshark 的跨层网络故障诊断综合实验平台设计与实现。

## 两个独立、互相对照的实验环境

- Packet Tracer 8.2.1：PC—交换机—R1—R2—交换机—服务器，覆盖 DHCP、ARP、静态路由、DNS、TCP/HTTP 和 ACL。
- Windows Python + Wireshark：真实回环 DNS/HTTP 通信，覆盖正常、DNS 错误、服务未监听、组合故障与恢复。

Wireshark 不直接捕获 Packet Tracer 的模拟报文。Packet Tracer 使用 Simulation 取证，Windows 使用 Npcap 回环适配器取证。两边协议现象可对照，不声称网络互通。

## 立即运行

在项目根目录 PowerShell 执行：

```powershell
python -m netfault.windows_lab
```

输入 baseline、dns、port、combined、probe、quit。场景命令自动运行探测，JSON 保存到 results/windows/；baseline 同时恢复 DNS 与 HTTP。组合故障应先改为 port（只修好 DNS），再 baseline，观察两阶段恢复。

非交互验证：`python -m netfault.windows_lab --batch`。
单元测试：`python -m unittest discover -s tests -v`。

HTTP 只绑定 127.0.0.1:8080，DNS 只绑定 127.0.0.1:53535，不改 Windows 防火墙、路由或系统 DNS。若端口占用，可加 --http-port 18080 --dns-port 53536，并同步调整抓包过滤器。真实 DNS 数据包使用教学端口，需要在 Wireshark Decode As 中指定 DNS。

## 操作入口

1. [Packet Tracer 搭建](packet-tracer/BUILD.md)：设备、连线、IP、DHCP、DNS/HTTP 与基线验收。
2. [六类故障](packet-tracer/FAULTS.md)：注入、证据与恢复，设备配置位于同目录。
3. [Wireshark 抓包](docs/wireshark.md)：安装与回环抓包步骤。
4. [报告框架](docs/report.md)、[答辩脚本](docs/demo.md)、[验收清单](docs/experiments.md)。

## GitHub 与展示

创建空仓库后在项目根目录执行：

```powershell
git init
git add .
git commit -m "Add Packet Tracer and Wireshark diagnosis lab"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/netfault-lab.git
git push -u origin main
```

Settings → Pages → Source 选择 GitHub Actions。Pages 工作流发布 docs/ 静态网站；Tests 运行 Windows/Linux 回环测试。Packet Tracer 必须通过软件实测，不能由回环 CI 代替。

结果目录默认不提交。选取不含无关流量的实验 JSON、PCAPNG、截图放入 evidence/ 后提交，并核对无敏感信息。真实流量抓取仅限 Npcap 回环适配器和本实验端口。

## 当前状态

已完成 Windows 故障程序、设备配置、搭建/实验指导和网站。Wireshark/Npcap 已安装并采集真实回环抓包；Packet Tracer 实验由使用者线下完成，尚未提供已验收 .pkt。具体状态见 VERIFICATION.md。原 Linux 命名空间代码仅作可选旧版保留，本版无需执行 netfault.lab。

