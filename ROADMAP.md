# 优化路线 / Roadmap

当前发布的是已经可用的 v1.1。以下均为计划，不代表已实现。

| 优先级 | 优化 | 验收条件 |
| --- | --- | --- |
| P0 | 换行和格式保留 | 多段、列表和空行不被模型合并；异常结果保留原剪贴板 |
| P0 | 保护链接、数字和名称 | 用合成用例验证日期、数量、URL和人名；检测到不应修改的内容时阻止复制 |
| P0 | 覆盖更多设备和 App | 记录系统、设备、入口、检查、取消与粘贴结果；不包含真实聊天 |
| P1 | 修改位置更清楚 | 在预览中突出增删内容，同时重新验证不切换 App 的体验 |
| P1 | 润色风格 | 自然、商务、简洁可选；检查模式仍保持最小修改 |
| P1 | 更方便安装 | 提供经过核对的 Apple 快捷指令分享链接和版本更新步骤 |
| P1 | 中英文界面 | 用相同工作流生成不同界面文案；提示词和安全检查保持一致 |
| P2 | 长文本分段 | 保留段落、控制等待时间，部分失败时不写入不完整结果 |
| P2 | 可复用生成模块 | 提示词、输入保护和交互流程能独立复用，避免复制整份实现 |

首要方向是提高可靠性和分享体验。保持现有键盘和设备端处理；更复杂的界面必须重新通过真机入口验收后再加入。

The priorities are formatting and protected-content fidelity, broader device coverage, clearer edit previews, optional polish styles, easier installation, and bilingual labels. These items are planned, not shipped. Changes must preserve explicit confirmation and be re-tested on device.
