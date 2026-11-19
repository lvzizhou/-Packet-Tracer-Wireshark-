# Packet Tracer 8.2.1 搭建步骤

本文件是构建说明，尚不是已验证的 .pkt 文件。Windows Python 和 Packet Tracer 互相独立，不向模拟网络发送真实 socket 报文。

## 放置与连接

放置 PC-PT 一台、2960 交换机两台、1941 路由器两台、Server-PT 一台。更名 PC1、SW1、R1、R2、SW2、Server1。从左到右摆放：PC1—SW1—R1—R2—SW2—Server1。

| 连接 | 线型 |
| --- | --- |
| PC1 FastEthernet0 ↔ SW1 FastEthernet0/1 | Copper Straight-Through |
| SW1 GigabitEthernet0/1 ↔ R1 GigabitEthernet0/0 | Copper Straight-Through |
| R1 GigabitEthernet0/1 ↔ R2 GigabitEthernet0/0 | Copper Cross-Over |
| R2 GigabitEthernet0/1 ↔ SW2 GigabitEthernet0/1 | Copper Straight-Through |
| SW2 FastEthernet0/1 ↔ Server1 FastEthernet0 | Copper Straight-Through |

## 路由器

每台路由器打开 CLI，首次询问 initial configuration dialog 时回答 no 并回车。在用户模式提示符下分别粘贴 R1-baseline.txt 和 R2-baseline.txt。检查无 Invalid input；不同型号接口名可能不同，本项目固定 1941。

## 服务器

Server1 → Desktop → IP Configuration：IPv4 10.20.0.2；掩码 255.255.255.0；网关 10.20.0.1；DNS 10.20.0.2。

Services → DNS → On；添加 Name `web.lab.test`、Type A Record、Address `10.20.0.2`，点击 Add。Services → HTTP → HTTP On；编辑 index.html 为简单课程主页并 Save。HTTP 使用端口 80，与 Windows 程序 8080 不同。

PC1 → Desktop → IP Configuration → DHCP，等待获取 10.10.0.21 及后续可用地址、网关 10.10.0.1、DNS 10.20.0.2。若 DHCP 失败，先检查链路和 R1 DHCP 池。

## 基线验收

等待交换机端口变绿。PC1 Command Prompt 执行 `ipconfig /all`、`ping 10.10.0.1`、`ping 10.0.0.2`、`ping 10.20.0.2`、`nslookup web.lab.test`。首次 ping 可因 ARP 学习丢包，应再次测试并记录。Web Browser 打开 `http://web.lab.test`，必须呈现主页。

R1/R2 执行 `show ip interface brief`、`show ip route`；R1 执行 `show ip dhcp binding`。保存 `baseline.pkt`。故障实验始终从此副本开始，避免上一故障残留。

Simulation 模式 → Edit Filters，保留 ARP、DHCP、DNS、ICMP、TCP、HTTP。浏览器重新发起请求，使用 Capture/Forward 逐步查看 Event List、OSI Model 和 Inbound/Outbound PDU Details。不要把模拟 PDU 截图标注成 Wireshark 真实抓包。
