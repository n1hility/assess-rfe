#!/usr/bin/env python3
"""Preflight checks for an assessment run.

Checks environment variables and current run state, outputting structured
results for the coordinator to parse.

Usage:
    python3 scripts/preflight.py RHAIRFE
"""

import os
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: preflight.py PROJECT_KEY", file=sys.stderr)
        sys.exit(1)

    project = sys.argv[1]

    # Check env vars
    missing = []
    for var in ("JIRA_SERVER", "JIRA_USER", "JIRA_TOKEN"):
        if not os.environ.get(var):
            missing.append(var)

    print(f"ENV_OK={'true' if not missing else 'false'}")
    if missing:
        print(f"ENV_MISSING={','.join(missing)}")

    # Check cache
    cache_dir = os.path.join("/tmp/rfe-assess", project)
    cache_count = 0
    if os.path.isdir(cache_dir):
        cache_count = len([f for f in os.listdir(cache_dir) if f.endswith(".md")])
    print(f"CACHE_DIR={cache_dir}")
    print(f"CACHE_COUNT={cache_count}")

    # Check current run state
    assess_base = os.path.join("assessments", project)
    current_link = os.path.join(assess_base, "current")

    if os.path.islink(current_link):
        target = os.path.join(assess_base, os.readlink(current_link))
        if os.path.isdir(target):
            has_scores = os.path.exists(os.path.join(target, "scores.csv"))
            assessed = len([f for f in os.listdir(target) if f.endswith(".result.md")])
            print(f"CURRENT_RUN={os.path.abspath(target)}")
            print(f"CURRENT_ASSESSED={assessed}")
            print(f"CURRENT_COMPLETE={'true' if has_scores else 'false'}")
        else:
            print("CURRENT_RUN=none")
    else:
        print("CURRENT_RUN=none")


if __name__ == "__main__":
    main()
