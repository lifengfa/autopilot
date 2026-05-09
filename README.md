# Autopilot — Claude Code Skill

自动驾驶模式：自动批准所有工具调用和权限提示，无需用户确认，持续执行直到任务完成或出错，完成后通过飞书 Webhook 发送通知。

## 功能

- **自动批准**所有工具调用、文件编辑、命令执行
- **执行到底**，不中途停止，遇到分支默认选第一项
- **飞书通知**：任务完成（成功/失败）后发送通知

## 触发方式

- `/autopilot <任务描述>`
- 说 "自动执行"、"不要问我直接做"、"全部 yes"
- "autonomous mode"、"auto approve"、"run without asking"

## 安装

```bash
claude plugin install https://github.com/lifengfa/autopilot
```

## 飞书通知配置

在 `~/.zshrc` 或 `~/.bashrc` 中添加：

```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_ID"
```

## 使用示例

```
/autopilot 帮我把所有测试跑一遍，修复失败的测试
```

```
/autopilot 更新所有依赖到最新版本
```

## 文件结构

```
autopilot/
├── .claude-plugin/
│   └── plugin.json          # 插件元数据
├── skills/
│   └── autopilot/
│       ├── SKILL.md          # 技能提示词
│       └── scripts/
│           └── notify_feishu.py  # 飞书通知脚本
└── README.md
```

## 通知格式

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
