#!/usr/bin/env python3
"""Append the Chinese UI rule to global and project AGENTS files.

The rule is applied only when the marker heading is missing, so repeated runs
do not create duplicates.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


RULE = """## 中文界面规则

安装、启用或更新任何技能或插件后，在同一轮任务内自动把它们的界面名称和介绍改为中文，不要等用户再次提醒。修改范围只包括 UI 展示元数据：技能写 `agents/openai.yaml` 的 `interface.display_name` 和 `short_description`；插件优先写 `.codex-plugin/plugin.json`，不存在时写 `.claude-plugin/plugin.json`，更新 `interface.displayName`、`shortDescription` 和 `longDescription`，不要改 `.openclaw`、`.cursor` 等其他工具镜像。展示名使用“中文名 原标识符”的格式，保留内部 ASCII 名称、`SKILL.md`、资源路径和原有字段；新翻译的条目同时追加到 `$CODEX_HOME/scripts/apply_zh_ui.py` 的映射表中。"""


def ensure_rule(path: Path) -> bool:
    marker = "## 中文界面规则"
    if path.exists():
        text = path.read_text(encoding="utf-8-sig")
        if marker in text:
            return False
        content = text.rstrip() + "\n\n" + RULE + "\n"
    else:
        content = RULE + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=None)
    args = parser.parse_args()

    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    changed_global = ensure_rule(codex_home / "AGENTS.md")
    changed_project = False
    if args.project_root is not None:
        changed_project = ensure_rule(args.project_root / "AGENTS.md")

    print(f"全局规则已写入: {changed_global}")
    print(f"项目规则已写入: {changed_project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
