# Packet Tracer 六个故障场景新手操作手册

适用：Packet Tracer 8.2.1；本项目既有双路由器拓扑。全部操作在 Packet Tracer 内完成，不用 Windows 命令行，不用虚拟机。本手册的现象为预期，实际结果请按你的操作记录。

## 一 先认清设备与操作入口

你的拓扑从左到右应为：

PC0 → Switch0 → 左侧路由器 → 右侧路由器 → Switch1 → Server0

| 手册称呼 | 画布初始名称 | 识别办法 |
| --- | --- | --- |
| 客户端 | PC0 | 最左侧电脑 |
| R1 | Router0，配置 hostname 后可能显示 R1 | 靠近 PC0 的左侧路由器 |
| R2 | Router1，配置 hostname 后可能显示 R2 | 靠近 Server0 的右侧路由器 |
| 服务器 | Server0 | 最右侧服务器 |

注意：初始名称 Router1 是右侧路由器，对应本手册 R2，不是 R1。以拓扑位置和接口地址确认。

本手册要求 R1 G0/0 接客户端交换机，R1 G0/1 接 R2 G0/0，R2 G0/1 接服务器交换机。

### 常用入口

- 输入路由命令：单击对应路由器 → CLI → 点击白色命令区 → 切到英文输入法。
- 客户端测试：单击 PC0 → Desktop → Command Prompt。
- 打开网页：PC0 → Desktop → Web Browser；URL 要写 http://，不要 https://。
- 修改服务：Server0 → Services → DNS 或 HTTP。
- 返回 Desktop 图标页：点击内嵌浏览器或命令窗口右上角的小 X；不要误关整个项目。
- 测试时先选择主界面右下角 Realtime。Simulation 用于后面逐步取证，停在 Simulation 但不推进事件可能造成等待。

### 路由器命令怎么输入

每一行输入后按 Enter。不要把 Router#、R1# 等提示符一起输入。先看左侧最后一行提示符：

| 提示符结尾 | 含义 | 如何回到本手册命令的起点 |
| --- | --- | --- |
| > | 普通模式 | 先输入 enable，变成 # |
| # 且没有括号 | 特权模式 | 可以开始输入配置命令 |
| (config)# 或 (config-if)# | 正在配置 | 输入 end，回到没有括号的 # |
| Would you like…[yes/no] | 首次启动向导 | 英文输入 no，Enter；出现 Press RETURN 再按 Enter，然后 enable |

下面各场景的路由命令统一从“没有括号的 #”开始。可逐行输入，也可粘贴多行后确认最后一行已执行；必要时再按一次 Enter。看到 Invalid input、Incomplete command 或 Ambiguous command 应先停止，检查设备、模式和拼写。

## 二 开始前必须完成正常基线

不要在原本就不通的网络上做故障实验，否则无法证明是你注入的故障导致失败。

1. 主界面右下角选择 Realtime，等待链路指示灯变绿。
2. PC0 → Desktop → IP Configuration，确认 IPv4 为 10.10.0.x，掩码 255.255.255.0，网关 10.10.0.1，DNS 10.20.0.2。DHCP 通常分配 10.10.0.21，但不要求必须等于 21。
3. Server0 → Desktop → IP Configuration：IP 10.20.0.2，掩码 255.255.255.0，网关 10.20.0.1，DNS 10.20.0.2。
4. Server0 → Services → DNS：On；存在 A 记录 web.lab.test → 10.20.0.2。
5. Server0 → Services → HTTP：HTTP On。
6. PC0 Command Prompt 逐行输入以下命令。首次 ping 因 ARP 可能丢一个包，可以再运行一次。

```text
ipconfig /all
ping 10.10.0.1
ping 10.20.0.2
nslookup web.lab.test
```

正常应有 Reply from…，解析应返回 10.20.0.2。若 nslookup 不被版本支持，使用浏览器和 Simulation 中 DNS 响应取证。

7. PC0 的 Web Browser 分别访问 http://10.20.0.2 和 http://web.lab.test。两者都应看到主页。务必点击 Go 发起请求。
8. File → Save As，保存 baseline.pkt。这是正常状态的备份。
9. 截图保存 PC 地址配置、正常 ping、域名访问成功和总拓扑。

基线失败时先停止下面实验。连网关都 ping 不通优先检查 PC 地址、左侧链路及 R1 G0/0 是否 no shutdown。

## 三 每个场景都这样保存

为避免故障互相影响，每个场景从 baseline.pkt 打开：

1. File → Open → baseline.pkt。
2. 马上 File → Save As → 对应故障文件名，例如 F1-link-down.pkt。
3. 按下面步骤制造故障、测试、截图。故障状态 Ctrl+S 保存，供答辩时复现。
4. 完成恢复和复测后，只保存恢复成功的截图，不另存恢复版 .pkt，也不要按 Ctrl+S 覆盖故障副本。
5. 下一个场景重新打开 baseline.pkt。若提示是否保存当前更改，确认故障副本已在恢复前保存后，选择 No（不保存），避免把正常状态覆盖到故障文件。


### 最终只需保存 8 个 .pkt 文件

| 文件名 | 保存时的状态 |
| --- | --- |
| baseline.pkt | 正常网络，IP 与域名访问均成功 |
| F1-link-down.pkt | R1 G0/0 已 shutdown |
| F2-no-route.pkt | R1 到服务器网段的静态路由已删除 |
| F3-wrong-dns.pkt | A 记录为 10.20.0.99，HTTP 开启 |
| F4-http-off.pkt | DNS 正确，HTTP 关闭 |
| F5-acl-block.pkt | R2 已绑定阻断 HTTP 的 ACL |
| F6-combined.pkt | DNS 错误且 HTTP 关闭 |
| F6-dns-repaired.pkt | DNS 已修好，但 HTTP 仍关闭 |

恢复后的有效配置应与 baseline 一致，因此用截图证明恢复即可，无需重复保存六个 restored.pkt。已有恢复版文件可以自行保留作备份，不必提交，也不必删除。

**关键顺序：故障设置完成 → 验证并截图 → Ctrl+S 保存故障状态 → 执行恢复 → 验证并截图 → 打开 baseline，提示保存时选择不保存。** F6 在仅修好 DNS 后额外使用 Save As 保存 F6-dns-repaired.pkt，再继续开启 HTTP，最终正常状态不覆盖此中间文件。

文件夹建议：packet-tracer、screenshots/F1 至 F6、records。截图用系统截图工具自行保存，例如 F1-01-shutdown.png、F1-02-failed-ping.png、F1-03-restored.png。

## 四 F1 关闭客户端侧路由接口

目的：观察本地网关接口关闭后，客户端为何连第一跳都到不了。

### 1 制造故障

打开 baseline 并另存 F1-link-down.pkt。单击左侧路由器 R1 → CLI，确认在没有括号的 # 下，输入：

```text
configure terminal
interface gigabitEthernet0/0
shutdown
end
show ip interface brief
```

应看到 G0/0 为 administratively down；对应链路可能变红。截图保存命令结果。

### 2 验证失败

PC0 → Desktop → Command Prompt：

```text
ping 10.10.0.1
ping 10.20.0.2
```

预期均失败，可能显示超时或目的不可达，以实际结果为准。截图。PC0 浏览器访问 http://10.20.0.2 也应失败。此场景不需要硬找 DNS 丢包，接口状态已经是直接证据。

### 3 恢复

R1 CLI，从 # 输入：

```text
configure terminal
interface gigabitEthernet0/0
no shutdown
end
show ip interface brief
```

等待链路转绿，G0/0 应为 up/up。再 ping 网关及服务器，浏览器访问域名主页。只保存恢复成功的截图，不另存 .pkt，不覆盖故障副本。

完成标准：有接口关闭证据、失败证据和恢复成功证据。

## 五 F2 删除去服务器的路由

目的：证明“能到网关”不等于“能到远端服务器”。

### 1 制造故障

重新打开 baseline，另存 F2-no-route.pkt。R1 CLI 从 # 输入：

```text
show ip route
configure terminal
no ip route 10.20.0.0 255.255.255.0 10.0.0.2
end
show ip route
```

删除前应有到 10.20.0.0/24 的 S 静态路由，删除后消失。若删除前没有该路由，说明不是本手册基线，应先检查正常配置。截图删除后路由表。

### 2 验证失败

PC0 Command Prompt：

```text
ping 10.10.0.1
ping 10.0.0.2
ping 10.20.0.2
```

前两项应成功，服务器项应失败。网页 IP 访问也失败。失败可能是 Destination host unreachable，也可能超时，不要求固定文案。截图。

### 3 恢复

R1 CLI：

```text
configure terminal
ip route 10.20.0.0 255.255.255.0 10.0.0.2
end
show ip route
```

确认静态路由恢复；PC0 再 ping 服务器、访问域名主页。只保存恢复成功的截图，不另存恢复文件。

完成标准：网关可达、远端失败，路由表缺失与恢复形成对照。

## 六 F3 把 DNS 地址改错

目的：观察“IP 能打开，域名打不开”的应用层故障。

### 1 制造故障

重新打开 baseline，另存 F3-wrong-dns.pkt。

1. 单击 Server0 → Services → DNS。
2. 保持 DNS 为 On。
3. 单击下方列表中的 web.lab.test 记录。
4. 如果可以修改 Address，将其改为 10.20.0.99，点击 Save；如果界面只能 Add/Remove，先选中原记录点 Remove，再填写 Name=web.lab.test、Type=A Record、Address=10.20.0.99，点 Add。
5. 确认列表只有一条 web.lab.test A 记录，且地址为 10.20.0.99。不要加 http://，不要把 DNS 服务关掉。
6. 截图错误记录。

### 2 验证失败与对照

PC0 Command Prompt：

```text
ping 10.20.0.2
nslookup web.lab.test
```

预期服务器 IP 可达，解析返回 10.20.0.99。

PC0 Web Browser：先访问 http://10.20.0.2，应成功；再访问 http://web.lab.test，应失败。DNS 返回一个错误但格式合法的地址时，可能是 Request Timeout，而不是 Host Name Unresolved。两种报错不要混为一谈。

若域名仍打开或 nslookup 仍是旧地址，按文末“DNS 缓存处理”操作。只有确认客户端收到错误地址后，才记录故障成立。

### 3 恢复

回到 Server0 DNS，把相同 A 记录改回 10.20.0.2。确认只有一条记录。PC0 重新解析，必要时处理缓存；再次访问 http://web.lab.test，应成功。

完成标准：记录错误地址、IP 成功/域名失败的对照，以及正确解析与主页恢复。

## 七 F4 关闭 HTTP 服务

目的：说明 IP 可达、DNS 正常，也不代表应用服务可用。

### 1 制造故障

重新打开 baseline，另存 F4-http-off.pkt。

1. Server0 → Services → HTTP。
2. 将 HTTP 切换为 Off。
3. 测试始终使用 http://。HTTPS 状态无需更改，因为本实验不使用它。
4. 截图 HTTP Off。

### 2 验证失败

PC0 Command Prompt：

```text
ping 10.20.0.2
nslookup web.lab.test
```

预期 ping 成功，DNS 返回正确地址。浏览器点击 Go，分别访问 http://10.20.0.2 和 http://web.lab.test，两者应失败。

若看见旧页面，关闭 PC0 内嵌 Web Browser 再打开，输入完整 URL 点击 Go；仍显示旧内容时改访问 http://10.20.0.2/index.html?case=F4，强制生成新的请求，并在 Simulation 中确认有新 TCP/HTTP 事件。不要只凭旧页面判定服务仍可用。

Packet Tracer 可能显示超时或其他连接错误，实际表现以观察为准。不能预写一定出现真实 TCP RST。

### 3 恢复

Server0 → Services → HTTP → On。PC0 再次点击 Go，确认网页恢复。只保存恢复成功的截图，不另存恢复文件。

完成标准：ping/DNS 正常但 HTTP 失败，服务开启后恢复。

## 八 F5 ACL 只阻断 HTTP

目的：比较网络连通性与按端口访问控制的差别。

### 1 制造故障

重新打开 baseline，另存 F5-acl-block.pkt。单击右侧路由器 R2（初始名称 Router1）→ CLI，从 # 输入：

```text
configure terminal
ip access-list extended BLOCK_WEB
deny tcp 10.10.0.0 0.0.0.255 host 10.20.0.2 eq 80
permit ip any any
exit
interface gigabitEthernet0/0
ip access-group BLOCK_WEB in
end
show access-lists
show ip interface gigabitEthernet0/0
```

ACL 第一条拒绝来自客户端网段、到服务器 TCP 80 端口的请求；第二条允许其他 IP 流量。不能漏掉 permit ip any any，否则 DNS 和 ping 也可能被隐含拒绝。

R2 的 G0/0 必须连接 R1。show ip interface 的输出中应显示 Inbound access list is BLOCK_WEB。输出出现 --More-- 时按空格翻页，不要输入新命令，直到回到 #。

### 2 验证选择性阻断

PC0 Command Prompt：

```text
ping 10.20.0.2
nslookup web.lab.test
```

预期两项正常。浏览器访问 http://10.20.0.2，点击 Go，应失败；域名访问也失败。

回 R2 CLI 输入：

```text
show access-lists
```

观察 deny tcp 行是否出现或增加 matches。模拟版本显示可能不同；若没有计数，不凭空补写，改用后面的 Simulation 查看 R2 丢弃的证据。

截图：ping/DNS 成功、网页失败、ACL 规则及命中数（若显示）。若 ping 也失败，检查是否漏了 permit、是否修改了错误设备或存在上一故障。

### 3 恢复

R2 CLI：

```text
configure terminal
interface gigabitEthernet0/0
no ip access-group BLOCK_WEB in
exit
no ip access-list extended BLOCK_WEB
end
show ip interface gigabitEthernet0/0
show access-lists
```

确认入方向不再绑定 BLOCK_WEB。PC0 再访问 IP 与域名主页，应成功。只保存恢复成功的截图，不另存恢复文件。

完成标准：其他流量可通、HTTP 被规则拒绝，解除后恢复。

## 九 F6 DNS 错误与 HTTP 关闭组合故障

目的：证明修复第一个问题后，仍要复测，可能还有第二个故障。

重新打开 baseline，另存 F6-combined.pkt。

### 第一步 同时制造两个故障

1. 按 F3 将 DNS A 记录改为 10.20.0.99。
2. 按 F4 将 HTTP 改为 Off。
3. PC0 查询域名，应得到错误地址；直接访问 http://10.20.0.2 也失败。
4. 截图错误解析、HTTP Off 和失败页面，保存故障副本。

### 第二步 只修 DNS

1. Server0 DNS A 记录改回 10.20.0.2。
2. HTTP 仍保持 Off，不要提前开启。
3. PC0 查询域名，确认已得到 10.20.0.2，必要时清理缓存。
4. 浏览器重新点击 Go。预期网页依然失败。
5. 截图“正确 DNS + HTTP 失败”，另存 F6-dns-repaired.pkt。

### 第三步 再修 HTTP

1. Server0 HTTP 切换 On。
2. PC0 再访问 http://web.lab.test，应成功。
3. 只保存网页恢复成功的截图，不另存恢复文件，也不要覆盖 F6-dns-repaired.pkt。

完成标准：三个阶段有独立记录。自己知道注入内容时称“组合故障实验”；由同学选择且不告诉你时才称“盲测”。

## 十 Simulation 取证怎么做

建议先用 Realtime 完成上面的现象验证，再在故障副本中补 Simulation 证据，不要求六项都截同一种报文。

1. 切到 Simulation。
2. Edit Filters：IPv4 保留 ARP、DHCP、DNS、ICMP；Misc 保留 TCP、HTTP；IPv6 和其他协议取消。它只是显示过滤，不会关闭协议。
3. PC0 浏览器输入 URL 并点击 Go；或 PC0 Command Prompt 发起一次 ping。
4. 回拓扑，反复点 Capture/Forward，推进事件。
5. Event List 找 Type 与 At Device。点该事件的彩色方块，打开 PDU Information。
6. OSI Model 查看各层处理说明；Inbound/Outbound PDU Details 查看具体地址、端口与标志。
7. 丢弃时可能看到红叉或 drops/discard/no route 等说明。方块颜色用于区分协议，红色不一定表示丢弃。某些广播包被无关设备忽略是正常行为，需确认与当前失败请求相关。
8. F2 重点看 R1 的路由处理，F3 看 DNS Answer 中的地址，F5 看 R2 的 ACL 处理。
9. 截图后回 Realtime，再做恢复验证。恢复网页操作也要生成新请求，不看缓存旧页面。

不要把 Simulation 截图称作 Wireshark 抓包。Wireshark 的真实协议实验另做。

## 十一 DNS 缓存处理

先在 PC0 Command Prompt 尝试：

```text
ipconfig /flushdns
```

如果该版本提示 Invalid Command，不反复尝试；可在当前故障副本中重启 PC0：PC0 → Physical，找到电源开关，关闭再打开。只重启 PC0，不点整个拓扑的 Power Cycle Devices。随后 PC0 → Desktop → IP Configuration → DHCP，重新确认地址、网关和 DNS，再 nslookup 与浏览器测试。

重启是清理客户端状态的辅助手段，不是 DNS 错误的修复方法；DNS 记录仍需要在服务器修改。

## 十二 实验结果记录与提交

每项至少保留三类证据：故障设置、失败现象、恢复成功。F6 额外保留仅修 DNS 后仍失败的中间阶段。不要只截配置而不验证结果。

| 场景 | 网关 ping | 服务器 ping | DNS 结果 | HTTP 访问 | 核心依据 | 恢复验证 |
| --- | --- | --- | --- | --- | --- | --- |
| 正常基线 | 待填 | 待填 | 待填 | 待填 | 正常地址/路由 | 待填 |
| F1 接口关闭 | 待填 | 待填 | 待填 | 待填 | administratively down | 待填 |
| F2 路由缺失 | 待填 | 待填 | 待填 | 待填 | 缺少静态路由 | 待填 |
| F3 DNS 错误 | 待填 | 待填 | 待填 | 待填 | 错误 A 记录、IP/域名对照 | 待填 |
| F4 HTTP 关闭 | 待填 | 待填 | 待填 | 待填 | 服务 Off | 待填 |
| F5 ACL 阻断 | 待填 | 待填 | 待填 | 待填 | ACL 绑定与命中/丢弃 | 待填 |
| F6 组合故障 | 待填 | 待填 | 待填 | 待填 | 两阶段修复 | 待填 |

无法查询时填写“查询失败”，没有做的测试填“未测”，不要猜测结果。最后交付下表列出的 8 个 .pkt 文件、截图与填写后的记录表，不要求恢复版 .pkt。后续前端页面将使用这些材料展示故障和定位过程。

