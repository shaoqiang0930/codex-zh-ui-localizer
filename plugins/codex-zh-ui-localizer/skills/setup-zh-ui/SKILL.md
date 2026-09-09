---
name: setup-zh-ui
description: 一键把已安装的 Codex 技能与插件界面名称和介绍翻译为中文，写入全局规则并创建或更新每周自动维护。当用户要求配置中文界面、应用中文界面维护插件、恢复中文显示或运行本插件的一键安装流程时使用。
---

# 中文界面维护

一次性完成以下目标，然后向用户报告结果：

1. 把本插件的 `scripts/apply_zh_ui.py` 复制到 `$CODEX_HOME/scripts/apply_zh_ui.py`（Windows 默认是 `C:\Users\<用户名>\.codex\scripts\apply_zh_ui.py`），保留原脚本内容。
2. 用系统 Python 执行该脚本，把已安装技能和插件的中文展示元数据补齐。
3. 运行本插件的 `scripts/add_agents_rules.py`，传入当前项目根目录作为 `--project-root`；该脚本会向全局 `AGENTS.md` 和项目 `AGENTS.md` 写入“中文界面规则”（已有则跳过）。
4. 读取 [references/automation.md](references/automation.md)，用其中的名称、频率和提示词创建或更新每周自动维护任务。先检查 `$CODEX_HOME/automations` 中是否已有同名任务；存在就更新，不存在就创建。
5. 再次执行复制后的 `apply_zh_ui.py`，确认第二次运行无改动；随后额外扫描全局技能目录、插件缓存以及当前项目下可能的项目级技能/插件目录（例如 `.codex\skills`、`skills`、`.agents\plugins`、`plugins`），如仍有未翻译的新条目，根据其英文名称和介绍翻译为“中文名 原标识符”，只改 UI 展示字段，并追加到该脚本的映射表。

## 边界

- 保留技能的 ASCII 内部名称、`SKILL.md`、目录名、资源路径和已有 `policy`。
- 插件只改 Codex 实际读取的清单：优先 `.codex-plugin/plugin.json`，不存在时改 `.claude-plugin/plugin.json`；不改 `.openclaw`、`.cursor` 等其他工具镜像。
- 不删除用户已有配置，不收集或上传任何数据。
- 若当前环境没有创建自动化的工具，跳过步骤 4，并告诉用户新建一个对话后发送：创建技能插件自动中文化每周任务。

## 完成报告

全部完成后用中文简短说明：已配置多少个技能和插件的中文显示、全局规则是否写入、每周任务是否已创建或更新。若没有任何新增改动，说明“配置已完成，无需重复修改”。
