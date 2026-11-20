"""Run a daily refresh step within the Ubuntu runner's shared work deadline."""

import argparse
import math
import os
import subprocess
import sys
import time


KILL_GRACE_SECONDS = 5
TRANSLATION_FINISH_SECONDS = 10


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("required", "optional", "translate"))
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if not args.command:
        parser.error("需要提供巡检步骤命令")
    try:
        deadline = int(os.environ["REFRESH_WORK_DEADLINE"])
    except (KeyError, ValueError) as exc:
        parser.error(f"巡检预算配置无效：{exc}")

    hard_limit = math.floor(deadline - time.time()) - KILL_GRACE_SECONDS
    finish_time = TRANSLATION_FINISH_SECONDS if args.mode == "translate" else 0
    if hard_limit <= finish_time:
        message = "[refresh-budget] 本轮工作时间不足，已进入发布预留窗口。"
        if args.mode == "required":
            print(f"::error::{message}", file=sys.stderr)
            return 1
        print(f"{message} 跳过本步骤。")
        return 0

    command = args.command
    if args.mode == "translate":
        try:
            translation_limit = float(os.environ.get("AI_BODIES_BUDGET_SECONDS", "900"))
        except ValueError:
            parser.error("AI_BODIES_BUDGET_SECONDS 必须是有限的非负秒数")
        if not math.isfinite(translation_limit) or translation_limit < 0:
            parser.error("AI_BODIES_BUDGET_SECONDS 必须是有限的非负秒数")
        soft_limit = hard_limit - finish_time
        if translation_limit:
            soft_limit = min(soft_limit, translation_limit)
        hard_limit = math.ceil(soft_limit) + finish_time
        command += ["--ai-bodies-budget-seconds", f"{soft_limit:g}"]
        print(f"[refresh-budget] 翻译预算 {soft_limit:g}s，另留 {finish_time}s 落盘校验。", flush=True)
    print(f"[refresh-budget] 本步骤最长 {hard_limit + KILL_GRACE_SECONDS}s。", flush=True)
    result = subprocess.run(
        ["timeout", f"--kill-after={KILL_GRACE_SECONDS}s", f"{hard_limit}s", *command],
        check=False,
    )
    if result.returncode in (124, 137):
        print("::warning::[refresh-budget] 本步骤触及硬截止时间。", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
