#!/usr/bin/env python3
"""Remove the Hermes QQBot community patch from a Hermes Agent checkout."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

PATCH = Path(__file__).parent / "patches" / "hermes-qqbot-community.patch"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("hermes_repo", type=Path)
    args = parser.parse_args()
    repo = args.hermes_repo.expanduser().resolve()

    check = subprocess.run(
        ["git", "apply", "--reverse", "--check", str(PATCH)],
        cwd=repo,
    )
    if check.returncode != 0:
        print("Patch cannot be cleanly removed from this checkout.")
        print("No files were changed.")
        return check.returncode

    subprocess.run(
        ["git", "apply", "--reverse", str(PATCH)],
        cwd=repo,
        check=True,
    )
    print("Patch code removed. User config.yaml and credentials were left untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
