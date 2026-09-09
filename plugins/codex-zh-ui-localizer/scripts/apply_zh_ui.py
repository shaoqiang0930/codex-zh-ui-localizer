#!/usr/bin/env python3
"""Reapply Chinese UI labels for installed Codex skills and plugins.

Only writes UI-facing metadata:
- skills: agents/openai.yaml -> interface.display_name / short_description
- plugins: the installed plugin.json manifest -> interface.displayName etc.

Internal ASCII names and SKILL.md files are intentionally left untouched.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


CODEX_HOME = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))

# Key: skill folder name. Value: (Chinese title without the original id, Chinese blurb).
SKILL_LABELS = {
    "imagegen": ("图像生成", "生成或编辑网站、游戏所需的图片素材。"),
    "openai-docs": ("官方文档", "查询 OpenAI、Codex 的模型、技能、任务与设置等官方说明。"),
    "plugin-creator": ("插件创建器", "创建、更新并验证 Codex 插件及其清单结构。"),
    "skill-creator": ("技能创建器", "创建或更新结构规范、调用策略清晰的 Codex 技能。"),
    "skill-installer": ("技能安装器", "从精选列表或 GitHub 仓库安装 Codex 技能。"),
    "review-agent": ("代码审查代理", "只读审查代码改动，返回具体可执行的缺陷清单。"),
    "gstack": ("AI 工作流总控", "把需求路由到 gstack 系列技能：评审、QA、上线、排查、文档、设计等。"),
    "autoplan": ("自动评审管线", "自动依次运行各类方案评审，并按决策原则直接给出结论。"),
    "benchmark": ("性能回归基准", "用无头浏览器检测页面性能回归并对比改动前后指标。"),
    "benchmark-models": ("模型横评", "对不同模型运行同一批基准，比较性能、成本与质量。"),
    "browse": ("网页浏览测试", "用无头浏览器做网页测试、站点试用与截图检查。"),
    "canary": ("上线灰度监控", "部署后持续监控，发现回归或故障时及时通知。"),
    "careful": ("谨慎模式", "为高风险或破坏性操作增加确认与防护提示。"),
    "codex": ("Codex 封装", "按三种模式调用 Codex：直接执行、计划或自动评审。"),
    "context-restore": ("上下文恢复", "恢复此前保存的工作上下文、进度与结论。"),
    "context-save": ("上下文保存", "把当前任务上下文保存下来，供以后恢复。"),
    "cso": ("安全负责人模式", "从首席安全官角度审查安全策略、威胁与风险。"),
    "design-consultation": ("设计咨询", "理解产品并研究竞品，给出完整设计系统与方向建议。"),
    "design-html": ("设计落地", "把最终设计落成可直接运行的 HTML/CSS 页面。"),
    "design-review": ("设计走查", "检查视觉一致性、层级、间距与动效问题并修复。"),
    "design-shotgun": ("多方案设计", "生成多个设计变体，放入对比板收集意见后迭代。"),
    "devex-review": ("开发体验审查", "审查开发者体验、工作流效率与使用摩擦点。"),
    "diagram": ("图表生成", "把文字描述或 Mermaid 转成图表源文件与可编辑图。"),
    "document-generate": ("文档补全", "从零为功能、模块或仓库生成缺失文档。"),
    "document-release": ("发布文档更新", "上线后更新对应功能说明与发布文档。"),
    "freeze": ("编辑目录锁定", "把会话内的文件修改限制在指定目录。"),
    "gstack-upgrade": ("gstack 升级", "把本地 gstack 技能升级到最新版本。"),
    "guard": ("完整安全模式", "开启破坏性命令警告与目录级编辑限制。"),
    "health": ("质量仪表盘", "汇总代码质量、技术债与维护健康指标。"),
    "hackernews-frontpage": ("Hacker News 首页", "抓取 Hacker News 首页标题、评分与评论数。"),
    "investigate": ("系统排查", "对故障、报错与异常行为做根因分析和修复。"),
    "ios-clean": ("iOS 调试桥清理", "移除 iOS 项目中的调试桥依赖与调试接线。"),
    "ios-design-review": ("iOS 视觉审查", "在真机上审查 SwiftUI 应用的视觉与交互。"),
    "ios-fix": ("iOS 自动修复", "自主定位并修复 iOS 应用问题。"),
    "ios-qa": ("iOS 真机测试", "在真机设备上对 SwiftUI 应用做功能与视觉测试。"),
    "ios-sync": ("iOS 调试桥同步", "按上游模板重新生成 iOS 调试桥。"),
    "land-and-deploy": ("上线与部署", "合并变更并执行上线部署流程。"),
    "landing-report": ("上线队列看板", "只读查看当前待上线与发布队列状态。"),
    "learn": ("经验沉淀", "记录项目经验、常见问题与修复结论供以后复用。"),
    "make-pdf": ("PDF 制作", "把 Markdown 转成出版质量的 PDF。"),
    "office-hours": ("产品咨询", "从产品角度评估想法、方向、价值与是否值得做。"),
    "open-gstack-browser": ("打开测试浏览器", "启动带侧栏扩展的 GStack Chromium 浏览器。"),
    "pair-agent": ("远程结对", "把远程 AI 代理与你的浏览器配对协作。"),
    "plan-ceo-review": ("CEO 方案审查", "从创始人或 CEO 视角审查方案、挑战假设并思考更大机会。"),
    "plan-design-review": ("设计方案审查", "在设计阶段审查视觉方案、一致性与体验细节。"),
    "plan-devex-review": ("开发体验方案审查", "在设计阶段审查开发者体验与工作流。"),
    "plan-eng-review": ("工程方案审查", "从工程管理视角审查方案风险与实施细节。"),
    "plan-tune": ("方案提问调优", "调节方案审查的提问敏感度与角色画像。"),
    "qa": ("质量测试", "系统测试 Web 应用并自动修复发现的问题。"),
    "qa-only": ("只测不修", "只做 Web 应用质量测试并输出报告，不改代码。"),
    "retro": ("周期复盘", "分析提交与工作模式，生成本周工程复盘。"),
    "review": ("提交前代码审查", "审查变更中的缺陷、风险与测试缺口。"),
    "scrape": ("网页抓取", "从网页提取所需数据或内容。"),
    "setup-browser-cookies": ("浏览器 Cookie 配置", "把真实 Chromium Cookie 导入无头浏览会话。"),
    "setup-deploy": ("部署配置", "为上线部署工作流配置部署目标。"),
    "setup-gbrain": ("gbrain 初始化", "安装并初始化本地 gbrain 记忆与配置。"),
    "ship": ("发布流程", "合并分支、运行测试、审查差异、升版并创建 PR。"),
    "skillify": ("流程转技能", "把成功的抓取流程固化为可复用的浏览器技能。"),
    "spec": ("规格化", "把模糊想法转成精确可执行的分阶段规格。"),
    "sync-gbrain": ("gbrain 同步", "让仓库代码与 gbrain 搜索指引保持同步。"),
    "unfreeze": ("解锁编辑边界", "清除编辑目录锁定设置的修改限制。"),
    "gstack-openclaw-ceo-review": ("OpenClaw CEO 审查", "从高层视角审查方案、挑战提议并决定扩展或收缩范围。"),
    "gstack-openclaw-investigate": ("OpenClaw 问题调查", "调试、根因分析或处理用户报错时系统排查。"),
    "gstack-openclaw-office-hours": ("OpenClaw 产品讨论", "评估新想法、产品方向或需求可行性。"),
    "gstack-openclaw-retro": ("OpenClaw 团队复盘", "按提交历史生成周度工程复盘与成长反馈。"),
    "guizang-ppt-skill": ("网页 PPT 生成", "生成横滑网页 PPT，支持背景、章节封面与数据大字报模板。"),
    "setup-zh-ui": ("中文界面维护", "配置已安装技能与插件的中文显示，并创建每周自动维护。"),
    "cautious-editing": ("谨慎编辑", "写代码、审查或重构时避免过度复杂，只做外科手术式修改。"),
    "ponytail": ("极简优先", "强制采用最简单可行方案：YAGNI、标准库优先、不加多余抽象。"),
    "ponytail-audit": ("全库精简审计", "扫描整个代码库，列出可删除、简化或用标准库替换的代码。"),
    "ponytail-debt": ("极简待办账本", "收集代码中的延期决策，生成简洁的技术债清单。"),
    "ponytail-gain": ("极简成效看板", "以得分卡展示极简模式收益：更少代码、更低成本、更快速度。"),
    "ponytail-help": ("极简模式帮助", "快速查看极简模式各子命令与使用方式的速查卡。"),
    "ponytail-review": ("过度设计审查", "专门找出可删除的抽象、多余灵活性与重复造轮子。"),
    "pdf": ("PDF 文档", "读取、创建、渲染和校验 PDF 文件，重视版式一致性。"),
    "presentations": ("演示文稿", "创建、编辑并校验 PowerPoint 和 Google Slides 演示文稿。"),
}

# Key: plugin.json "name". Value: UI fields without the original id.
PLUGIN_LABELS = {
    "pdf": {
        "display": "PDF 文档",
        "short": "读取、创建、渲染和校验 PDF 文件",
        "long": "在本地读取、创建、检查、渲染、校验和导出 PDF 文件，适合需要严格视觉版式的 PDF 任务。",
    },
    "presentations": {
        "display": "演示文稿",
        "short": "创建与编辑演示文稿",
        "long": "在本地创建、编辑、检查、渲染、校验和导出演示文稿，包括 PPTX 编写与 Google Slides 交接指导。当最终产物是演示文稿、幻灯片、PowerPoint 或 Google Slides 时使用。",
    },
    "ponytail": {
        "display": "极简优先",
        "short": "强制使用最简单可行的方案",
        "long": "优先 YAGNI、标准库、原生能力与最小正确实现。用于编码、审查、设计任何代码任务，以及用户要求最小方案或抱怨过度工程时。不要用于非编码请求。",
    },
    "andrej-karpathy-skills": {
        "display": "Karpathy 编程准则",
        "short": "减少常见 AI 编码错误的准则",
        "long": "源自 Andrej Karpathy 对 LLM 编码常见问题的观察。写代码、审查或重构时避免过度复杂，保持外科手术式修改，明确假设并定义可验证的成功标准。",
    },
    "codex-zh-ui-localizer": {
        "display": "中文界面维护",
        "short": "技能与插件界面一键中文化",
        "long": "把已安装的 Codex 技能和插件 UI 元数据翻译为中文，保留内部英文标识符，并配置全局规则与每周自动维护。",
    },
}


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def find_interface_index(lines: list[str]) -> int | None:
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "interface:" or stripped.startswith("interface: "):
            return index
    return None


def ensure_interface_field(
    lines: list[str],
    interface_index: int,
    key: str,
    value: str,
) -> bool:
    """Insert or replace one interface field. Returns True when a line changed."""
    field_re = re.compile(r"^[ \t]+" + re.escape(key) + r"\s*:")
    for index in range(interface_index + 1, len(lines)):
        line = lines[index]
        stripped = line.strip()
        if field_re.match(line):
            replacement = f"  {key}: {yaml_quote(value)}"
            if line != replacement:
                lines[index] = replacement
                return True
            return False
        if stripped and not line[0].isspace():
            lines.insert(index, f"  {key}: {yaml_quote(value)}")
            return True
    lines.append(f"  {key}: {yaml_quote(value)}")
    return True


def update_skill_yaml(skill_md: Path, chinese_title: str, short_desc: str) -> bool:
    yaml_path = skill_md.parent / "agents" / "openai.yaml"
    original_name = skill_md.parent.name
    display = f"{chinese_title} {original_name}"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)

    existed = yaml_path.exists()
    text = yaml_path.read_text(encoding="utf-8-sig") if existed else "interface:\n"
    lines = text.splitlines()

    interface_index = find_interface_index(lines)
    changed = False
    if interface_index is None:
        if lines and lines[-1] != "":
            lines.append("")
        lines.append("interface:")
        interface_index = len(lines) - 1
        changed = True

    changed = ensure_interface_field(lines, interface_index, "display_name", display) or changed
    changed = ensure_interface_field(lines, interface_index, "short_description", short_desc) or changed

    if not changed and existed:
        return False

    content = "\n".join(lines) + "\n"
    if existed and content == text:
        return False
    yaml_path.write_text(content, encoding="utf-8", newline="")
    return True


def iter_plugin_manifests() -> list[Path]:
    cache = CODEX_HOME / "plugins" / "cache"
    manifests: list[Path] = []
    if not cache.exists():
        return manifests
    for market in cache.iterdir():
        if not market.is_dir():
            continue
        for plugin_dir in market.iterdir():
            if not plugin_dir.is_dir():
                continue
            for version_dir in plugin_dir.iterdir():
                if not version_dir.is_dir():
                    continue
                relative_candidates = (
                    Path(".codex-plugin") / "plugin.json",
                    Path(".claude-plugin") / "plugin.json",
                    Path(".cursor-plugin") / "plugin.json",
                )
                for relative in relative_candidates:
                    candidate = version_dir / relative
                    if candidate.is_file():
                        manifests.append(candidate)
                        break
    return manifests


def update_plugin_json(manifest: Path, labels: dict[str, str]) -> bool:
    text = manifest.read_text(encoding="utf-8-sig")
    data = json.loads(text)
    name = data["name"]
    changed = False

    def replace_field(content: str, key: str, value: str) -> tuple[str, bool]:
        pattern = re.compile(r'("' + re.escape(key) + r'"\s*:\s*)"(?:[^"\\]|\\.)*"')
        new_content, count = pattern.subn(
            lambda match: match.group(1) + json.dumps(value, ensure_ascii=False),
            content,
            count=1,
        )
        return new_content, count > 0

    def insert_interface(content: str) -> str:
        display_value = f"{labels['display']} {name}"
        short_value = labels["short"]
        long_value = labels["long"]
        newline = "\n" if content.endswith("\n") else ""
        body = content.rstrip("\n")
        closing = body.rfind("}")
        if closing < 0:
            raise ValueError(f"Malformed plugin manifest: {manifest}")
        head = body[:closing].rstrip()
        if not head.endswith(","):
            head += ","
        head += (
            '\n  "interface": {\n'
            f'    "displayName": {json.dumps(display_value, ensure_ascii=False)},\n'
            f'    "shortDescription": {json.dumps(short_value, ensure_ascii=False)},\n'
            f'    "longDescription": {json.dumps(long_value, ensure_ascii=False)}\n'
            "  }\n}"
        )
        return head + newline

    def insert_existing_interface_field(content: str, key: str, value: str) -> str:
        marker = '"interface": {'
        start = content.find(marker)
        if start < 0:
            raise ValueError(f"No interface block in plugin manifest: {manifest}")
        insert_at = content.index("\n", start) + 1
        field = f'    "{key}": {json.dumps(value, ensure_ascii=False)},\n'
        return content[:insert_at] + field + content[insert_at:]

    for key, value in (
        ("displayName", f"{labels['display']} {name}"),
        ("shortDescription", labels["short"]),
        ("longDescription", labels["long"]),
    ):
        text, found = replace_field(text, key, value)
        changed = changed or found
        if not found:
            if '"interface"' not in text:
                text = insert_interface(text)
            else:
                text = insert_existing_interface_field(text, key, value)
            changed = True

    if text == manifest.read_text(encoding="utf-8-sig"):
        return False
    manifest.write_text(text, encoding="utf-8", newline="")
    return True


def main() -> int:
    seen_skills: set[str] = set()
    changed_skills = 0
    local_skills = CODEX_HOME / "skills"
    if local_skills.exists():
        for skill_md in local_skills.rglob("SKILL.md"):
            name = skill_md.parent.name
            labels = SKILL_LABELS.get(name)
            if labels is None:
                continue
            seen_skills.add(name)
            if update_skill_yaml(skill_md, labels[0], labels[1]):
                changed_skills += 1

    plugin_cache = CODEX_HOME / "plugins" / "cache"
    if plugin_cache.exists():
        for market in plugin_cache.iterdir():
            if not market.is_dir():
                continue
            for plugin_dir in market.iterdir():
                if not plugin_dir.is_dir():
                    continue
                for version_dir in plugin_dir.iterdir():
                    if not version_dir.is_dir():
                        continue
                    skills_dir = version_dir / "skills"
                    if not skills_dir.is_dir():
                        continue
                    for skill_md in skills_dir.rglob("SKILL.md"):
                        name = skill_md.parent.name
                        labels = SKILL_LABELS.get(name)
                        if labels is None:
                            continue
                        seen_skills.add(name)
                        if update_skill_yaml(skill_md, labels[0], labels[1]):
                            changed_skills += 1

    changed_plugins = 0
    seen_plugins: set[str] = set()
    for manifest in iter_plugin_manifests():
        try:
            name = json.loads(manifest.read_text(encoding="utf-8-sig"))["name"]
        except (json.JSONDecodeError, KeyError):
            continue
        labels = PLUGIN_LABELS.get(name)
        if labels is None:
            continue
        seen_plugins.add(name)
        if update_plugin_json(manifest, labels):
            changed_plugins += 1

    missing_skills = sorted(set(SKILL_LABELS) - seen_skills)
    missing_plugins = sorted(set(PLUGIN_LABELS) - seen_plugins)
    if missing_skills:
        print("未找到的技能（可能已卸载，跳过）: " + ", ".join(missing_skills))
    if missing_plugins:
        print("未找到的插件（可能已卸载，跳过）: " + ", ".join(missing_plugins))

    print(f"技能界面元数据已更新: {changed_skills} 个")
    print(f"插件界面元数据已更新: {changed_plugins} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
