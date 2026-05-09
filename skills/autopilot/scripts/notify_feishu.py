#!/usr/bin/env python3
"""Send a notification to Feishu (Lark) via webhook."""

import argparse
import json
import sys
import urllib.request
from datetime import datetime


def send_feishu_notification(webhook_url: str, status: str, summary: str, task: str = "") -> bool:
    status_emoji = "✅" if status == "success" else "❌"
    status_text = "Autopilot 完成" if status == "success" else "Autopilot 遇到错误"
    summary_label = "📝 摘要" if status == "success" else "⚠️ 错误"

    lines = [f"{status_emoji} {status_text}"]
    if task:
        lines.append(f"📋 任务：{task}")
    lines.append(f"{summary_label}：{summary}")
    lines.append(f"🕐 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    message = "\n".join(lines)

    payload = {
        "msg_type": "text",
        "content": {"text": message},
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
            if result.get("code") == 0:
                print("✅ 飞书通知发送成功")
                return True
            else:
                print(f"❌ 飞书返回错误：{result}", file=sys.stderr)
                return False
    except Exception as e:
        print(f"❌ 发送飞书通知失败：{e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Send Feishu (Lark) notification")
    parser.add_argument(
        "--status", choices=["success", "error"], required=True,
        help="Execution status: success or error"
    )
    parser.add_argument(
        "--summary", required=True,
        help="Task summary (success) or error message (error)"
    )
    parser.add_argument(
        "--task", default="",
        help="Brief task description"
    )
    parser.add_argument(
        "--webhook", required=True,
        help="Feishu webhook URL"
    )

    args = parser.parse_args()

    success = send_feishu_notification(
        webhook_url=args.webhook,
        status=args.status,
        summary=args.summary,
        task=args.task,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
