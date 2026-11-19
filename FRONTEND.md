# 前端展示使用说明

直接双击 docs/index.html 即可打开，无需 npm 或后端，内置诊断数据通过本地 JavaScript 加载。也可以把 docs/ 发布到 GitHub Pages。

功能：点击拓扑节点查看配置；切换六类故障查看预期与恢复；选择五次真实回环运行；导入单次诊断 JSON（不上传）；下载当前 JSON 和真实抓包。

Packet Tracer 六类场景统一标注“待补充线下实测”。完成后提供截图、工程和结果表，再更新页面；不可将预期说明改成已通过而不附实测依据。

内置 JSON 来自此前实际运行；网页抓包来自另一批次，帧号已经 tshark 核实，但不是这五份 JSON 的同次抓包。捕获丢失 5 包已在页面注明。

本页不调用 Python，不自动制造故障。实际诊断需在项目根目录运行 python -m netfault.windows_lab，再将结果导入。Windows/抓包步骤见 docs/windows-guide.md。

验收：Node 语法检查通过；Python 五项单元测试通过。尚未完成浏览器视觉验收和 GitHub 发布。
