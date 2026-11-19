# 课程设计报告框架

题目：基于 Packet Tracer 与 Wireshark 的跨层网络故障诊断综合实验

## 摘要

本设计围绕 Web 访问故障，在 Packet Tracer 中搭建双路由器网络，配置地址分配、静态路由、DNS、HTTP 与 ACL；同时使用 Windows Python 实现真实回环 DNS/HTTP 服务及诊断，以 Wireshark 观察协议证据。通过链路、路由、解析、服务、访问控制和组合故障，建立现象、分层检查、证据与恢复的实验闭环。

## 1 需求与创新

目标是解释访问失败原因而不只测试连通性。特色为模拟与真实报文对照、诊断证据与故障标签分离，以及组合故障逐层恢复。不是新协议或机器学习算法创新。

## 2 原理与设计

引用 BUILD.md 中拓扑、地址、接口与服务。解释 DHCP、ARP、IP 路由与 TTL、TCP、UDP DNS、HTTP。说明物理层只涉及链路启停，未模拟信号；未实现 VLAN、动态路由或完整协议栈。

## 3 实现

Packet Tracer 设备配置与六类故障见 packet-tracer/。Windows windows_lab 管理本地服务生命周期，probe 发送 DNS 与 HTTP 探测。诊断器不读场景标签，优先输出当前证据支持的问题。两种实验环境互不联通；53535 是本机 DNS 教学端口，模拟 DNS 为 53。

## 4 实验结果

待实际运行补充：Packet Tracer 基线和 F1–F6 的截图、Windows JSON、Wireshark 帧号与字段、每项恢复结果。对照 HTTP Off 的模拟行为与真实端口拒绝，不能预填两者完全一致。

## 5 讨论

接口正常不代表路径可达；ping 成功不代表 HTTP 成功；RST 不唯一来自服务退出，超时不唯一来自 ACL。组合故障首次定位 DNS 后仍需继续验证传输与服务。回环环境不代表真实网络性能，故本版不报告弱网吞吐量。

## 6 总结与参考资料

按真实实验完成情况填写收获、限制与改进。参考课程教材（补作者与版本）、RFC 1035、RFC 9293、RFC 9110、Cisco Packet Tracer 帮助及 Wireshark 用户指南。
