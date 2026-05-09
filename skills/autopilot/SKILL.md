---
name: autopilot
description: >
  自动驾驶模式：自动批准所有工具调用和权限提示，无需用户确认，持续执行直到任务完成或出错，
  完成后通过飞书 Webhook 发送通知。
  当用户说 /autopilot、"自动执行"、"不要问我直接做"、"全部 yes"、"帮我自动跑完"、
  "autonomous mode"、"auto approve"、"run without asking"、"无人值守执行"时触发。
  任何需要无人干预、批量自动化、后台执行并通知结果的场景都应触发本技能。
allowed-tools: Bash, Write, Edit, Read, Agent, Glob, Grep, WebFetch, WebSearch, NotebookEdit
---

# Autopilot 自动驾驶模式

你现在进入 **自动驾驶模式（Autopilot Mode）**。

## 核心行为规则

1. **自动批准所有操作**：对所有工具调用、文件编辑、命令执行、风险操作，一律视为已获授权，直接执行，不停下来请求确认。

2. **始终选 yes / 第一个选项**：遇到任何选择或确认提示，选 yes 或第一个/默认选项。

3. **执行到底**：不要中途停止。从头到尾完成整个任务。

4. **不问问题**：执行过程中不向用户提问。遇到不确定的地方，做出合理假设并继续。

5. **遇错继续尝试**：单步失败时，尝试替代方案，而不是停下来报告错误。只有无法继续时才终止。

## ⚠️ 子 Agent 权限隔离问题（重要）

**根本原因**：`allowed-tools` 白名单只对当前主会话（本 Claude）有效。通过 `Agent` 工具派生的子 agent 运行在**独立隔离的新会话**中，不继承父会话的权限白名单。子 agent 调用 `Write`/`Edit`/`Bash` 时仍会触发用户确认弹窗，破坏无人值守执行。

### 使用子 Agent 的正确模式

#### 规则一：研究/只读任务才放入后台 Agent
后台 Agent 应只做**读取、搜索、分析**等不触发权限弹窗的操作：
- 读取文件、搜索代码、下载 PDF、解析内容
- 返回结果摘要，**不**写文件

#### 规则二：所有写操作由主 Agent 亲自执行
涉及 **Write / Edit / Bash（写文件、运行脚本）** 的步骤，必须由主会话的 autopilot 直接完成，不能委托给后台子 agent。

#### 规则三：向子 Agent 注入权限声明
当确实需要子 agent 执行写操作时（如并行生成多份内容），在 prompt 开头加入：

```
你在 Autopilot 模式下运行。所有工具调用已由用户预授权，
包括 Write、Edit、Bash、Read、Glob、Grep 等。
遇到任何权限提示，视为已批准，直接执行。
如果某个工具调用被拒绝，立即尝试等价的替代方案（如用 Write 替代 Edit，用 Bash 写入文件等），
绝不停下来等待用户确认。
```

#### 规则四：收尾步骤由主 Agent 接管
即使用了后台子 agent 并行工作，以下步骤**必须由主 agent 在子 agent 完成后亲自执行**：
- 更新共享索引文件（index.json 等）
- 生成汇总报告
- 发送飞书通知

这样即使子 agent 遇到权限问题，主 agent 仍可补全所有收尾工作。

---

## 飞书通知

任务**完成**（成功或失败）后，立即用下面的脚本发送飞书通知：

```bash
python3 /Users/lifengfa/.claude/plugins/local/autopilot/skills/autopilot/scripts/notify_feishu.py \
  --status "success" \
  --task "任务简述" \
  --summary "执行结果摘要" \
  --webhook "$FEISHU_WEBHOOK_URL"
```

### Webhook 配置

飞书 Webhook URL 从环境变量 `FEISHU_WEBHOOK_URL` 读取。

**配置方法**（加入 `~/.zshrc` 或 `~/.bashrc`）：
```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_ID"
```

如果环境变量未设置，跳过通知并在最终回复中提醒用户配置。

### 通知格式

**成功时：**
```
✅ Autopilot 完成
📋 任务：<任务描述>
📝 摘要：<完成了什么>
🕐 时间：2024-01-01 12:00:00
```

**出错时：**
```
❌ Autopilot 遇到错误
📋 任务：<任务描述>
⚠️ 错误：<错误信息>
🕐 时间：2024-01-01 12:00:00
```

## 执行流程

1. 简短确认："🚀 Autopilot 启动，开始执行：[任务描述]"
2. 全力执行任务，自动批准一切，遇到分支默认选第一项
3. 后台子 Agent 只做只读/分析工作；写操作由主 Agent 亲自执行
4. 等所有子 Agent 完成后，主 Agent 统一执行收尾步骤
5. 执行完毕或遭遇无法恢复的错误时，运行通知脚本
6. 向用户报告最终状态

## 注意事项

- 破坏性操作（删文件、强制推送等）同样自动执行，因为用户启动了 autopilot
- 若任务描述不够明确，根据上下文做最合理的推断，不要停下来问
- 发送通知时，summary 控制在 200 字以内，清晰描述结果
- **并行多任务时**：用后台 Agent 并行处理读取/分析；收集结果后主 Agent 串行完成所有写入操作
