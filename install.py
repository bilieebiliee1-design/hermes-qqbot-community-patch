#!/usr/bin/env python3
"""Install the Hermes QQBot community patch into a Hermes Agent checkout."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PATCH = Path(__file__).parent / "patches" / "hermes-qqbot-community.patch"
REQUIRED = ("gateway", "hermes_cli", "toolsets.py", "web")


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("hermes_repo", type=Path, help="Path to a Hermes-Agent checkout")
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    repo = args.hermes_repo.expanduser().resolve()

    missing = [name for name in REQUIRED if not (repo / name).exists()]
    if missing:
        parser.error(f"not a Hermes-Agent checkout; missing: {', '.join(missing)}")
    if not PATCH.exists():
        parser.error(f"patch file missing: {PATCH}")

    try:
        run(["git", "apply", "--check", str(PATCH)], repo)
        run(["git", "apply", str(PATCH)], repo)
        if not args.skip_tests:
            run(
                [
                    "scripts/run_tests.sh",
                    "tests/gateway/test_qqbot.py",
                    "tests/tools/test_qqbot_messaging_tool.py",
                    "tests/hermes_cli/test_web_server.py",
                    "-q",
                ],
                repo,
            )
            run(["npm", "run", "check"], repo / "web")
            run(["npm", "run", "build"], repo / "web")
    except subprocess.CalledProcessError as exc:
        print(f"Installation stopped: command failed with exit code {exc.returncode}", file=sys.stderr)
        print("No automatic conflict resolution was attempted.", file=sys.stderr)
        return exc.returncode or 1

    print("Patch installed. Restart Hermes Gateway to load the changes.")
    print("Open hermes dashboard, then Channels > QQBot to configure it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
