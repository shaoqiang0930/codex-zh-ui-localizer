# Codex 中文界面维护

一个可分享的 Codex 插件，用来把已安装技能和插件的界面名称、介绍自动翻译成中文，并让以后的安装也保持中文。

## 它能做什么

- 把本机已安装的技能和插件卡片改为中文，例如“谨慎编辑 cautious-editing”。
- 保留内部英文标识符，所以 `$技能` 原命令和路由不会失效。
- 写入全局规则：以后在对话里安装、启用或更新技能/插件时，自动完成中文化，不需要每次重复说明。
- 创建每周自动维护任务：界面里自行安装或更新插件后，也会被后台任务自动补成中文。
- 不收集、不上传你的任何数据。

## 技能介绍：setup-zh-ui

`setup-zh-ui` 是这个插件内置的一键配置技能。安装插件后，只要在 Codex 对话里说“执行 setup-zh-ui”或“帮我配置中文界面”，它就会自动完成翻译脚本安装、已装技能/插件中文化、全局规则写入和每周维护任务创建。

## 一键安装

### 方式一：GitHub 市场（推荐）

打开 Codex，在新对话中粘贴下面这句话即可：

```text
请添加 GitHub 插件市场 https://github.com/shaoqiang0930/codex-zh-ui-localizer，
安装插件 codex-zh-ui-localizer，
然后执行 setup-zh-ui 完成中文界面配置，并创建每周自动维护任务。
```

### 方式二：本地文件夹或 ZIP

1. 让对方从仓库首页的 `Code → Download ZIP` 下载并解压，或直接把整个仓库文件夹发给对方。
2. 对方解压后，在 Codex 新对话中粘贴：

```text
请安装本地插件 <解压路径>\plugins\codex-zh-ui-localizer，
然后执行 setup-zh-ui 完成中文界面配置，并创建每周自动维护任务。
```

建议安装完成后重启一次 Codex，让新写入的全局规则和界面中文名称立即完整生效。

## 安装后会做什么

`setup-zh-ui` 会依次完成：

1. 把中文翻译脚本安装到 `$CODEX_HOME/scripts/apply_zh_ui.py` 并执行。
2. 把已安装技能与插件的中文 UI 元数据补齐。
3. 在全局 `AGENTS.md` 和当前项目 `AGENTS.md` 写入“中文界面规则”（已有则跳过）。
4. 创建或更新名为“技能插件自动中文化”的每周后台任务。
5. 验证脚本幂等，没有新增内容时保持安静。

## 兼容规则

- 只改 UI 展示字段：技能写 `agents/openai.yaml`，插件写 `.codex-plugin/plugin.json` 或 `.claude-plugin/plugin.json`。
- 不改 `SKILL.md`、内部 ASCII 名称、目录名、资源路径和已有策略。
- 已禁用或未安装的缓存不会主动改动。

## 开发与验证

```powershell
python -m py_compile plugins/codex-zh-ui-localizer/scripts/*.py
python plugins/codex-zh-ui-localizer/scripts/apply_zh_ui.py
python plugins/codex-zh-ui-localizer/scripts/add_agents_rules.py --project-root .
```

重复运行不应产生新增改动。
