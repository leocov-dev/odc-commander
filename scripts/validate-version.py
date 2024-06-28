# /// script
# requires-python = ">=3.9,<3.11"
# dependencies = [
#    "toml",
# ]
# ///
"""
Assert that various version strings all match.

such as:
- git tag
- pyproject.toml version

Only intended to be used by CI pipeline.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


__repo = Path(__file__).parent.parent

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-tag", action="store_true")

    args = parser.parse_args()

    versions_to_match = {}

    check_against = subprocess.check_output(["hatch", "version"], text=True).strip()
    versions_to_match["pyproject"] = check_against

    if args.check_tag:
        # git tag version in github workflows
        versions_to_match["git_tag"] = os.environ.get("TAG", "")

    if not all(v == check_against for v in versions_to_match.values()):
        print(f"versions did not match: {versions_to_match}")
        sys.exit(1)

    print(f"version strings <{check_against}> OK")
