# 每周自动维护任务

按以下配置创建或更新 Codex 自动化：

- 名称：技能插件自动中文化
- 类型：heartbeat，附加到当前本地线程
- 频率：`FREQ=WEEKLY;INTERVAL=1`
- 状态：`ACTIVE`

提示词：

```text
后台维护任务：让 Codex 本机已安装/启用的技能与插件界面保持中文。每次运行：1) 先执行 python $CODEX_HOME/scripts/apply_zh_ui.py，修复已映射条目的中文展示元数据；2) 再扫描 $CODEX_HOME/skills、$CODEX_HOME/plugins/cache 以及当前项目下可能的项目级技能/插件目录（例如 .codex/skills、skills、.agents/plugins、plugins），找出仍缺中文 display_name 或 displayName 的条目；3) 对每个新条目，根据其英文名称和介绍翻译为“中文名 原标识符”格式，只写入技能目录的 agents/openai.yaml 或插件清单的 interface 字段；插件清单优先改 .codex-plugin/plugin.json，不存在时改 .claude-plugin/plugin.json，不要改 .openclaw、.cursor 等其他工具镜像；保留内部 ASCII 名称、SKILL.md、资源路径和原有字段；4) 把新增翻译条目追加到 $CODEX_HOME/scripts/apply_zh_ui.py 的映射表中；5) 如果没有任何需要翻译的条目，保持安静，不发送消息或通知；只有在完成新翻译或出现错误时，才用中文简要汇报结果。
```
