# 实验验收清单

- Packet Tracer：按 packet-tracer/BUILD.md 搭建并保存 baseline.pkt，DHCP 获取成功，DNS/HTTP 成功。
- 按 packet-tracer/FAULTS.md 完成 F1–F6，每项记录现象、独立证据及恢复结果。
- Wireshark：按 wireshark.md 抓取真实 DNS、TCP 握手、HTTP 和连接拒绝。
- Windows：保留 baseline、dns、port、combined、恢复各次实际 JSON。
- 报告区分模拟 PDU 与真实抓包，说明组合故障需多次诊断。
- GitHub：提交拓扑、配置、代码、脱敏证据；检查 Actions 与 Pages 实际状态。

结果表：场景 / 运行环境 / 时间 / 诊断 / 报文帧号或设备证据 / 恢复后结果。未执行部分填“待实测”，不写成功。
