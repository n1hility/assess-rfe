#!/usr/bin/env python3
"""Wait for a wave of assessment agents to finish.

Blocks (polling on disk) until every key in the wave has produced a
``<key>.result.md`` in the run directory, or until ``--max-wait`` seconds
elapse. This replaces the coordinator reasoning about agent completion in its
own context (e.g. "27/30 done, waiting on RHAIRFE-227") — which is lost when
the conversation is compacted. The wave's keys live on disk, so completion is
always re-derivable.

Exit codes:
    0  all wave keys have result files (wave complete)
    3  some keys still pending after --max-wait (caller should re-run)

Usage:
    python3 scripts/wait_wave.py /path/to/run_dir --keys-file /path/to/wave.txt
    python3 scripts/wait_wave.py /path/to/run_dir --keys-file wave.txt --max-wait 90 --interval 5

Output (stdout):
    COMPLETED=27
    PENDING=3
    WAVE_SIZE=30
    ---
    RHAIRFE-227
    RHAIRFE-238
    RHAIRFE-239
"""

import argparse
import os
import sys
import time


def _pending_keys(run_dir, keys):
    """Return the subset of keys that have no .result.md yet."""
    return [k for k in keys if not os.path.exists(os.path.join(run_dir, f"{k}.result.md"))]


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("run_dir", help="Run directory containing the .result.md files")
    parser.add_argument(
        "--keys-file", required=True, help="File with one wave key per line (the launched batch)"
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=90,
        help="Max seconds to block before returning pending (default: 90)",
    )
    parser.add_argument(
        "--interval", type=int, default=5, help="Seconds between polls (default: 5)"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.run_dir):
        print(f"ERROR: {args.run_dir} is not a directory", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(args.keys_file):
        print(f"ERROR: keys file not found: {args.keys_file}", file=sys.stderr)
        sys.exit(1)

    with open(args.keys_file, "r", encoding="utf-8") as f:
        keys = [line.strip() for line in f if line.strip()]

    if not keys:
        # Empty wave — nothing to wait for.
        print("COMPLETED=0")
        print("PENDING=0")
        print("WAVE_SIZE=0")
        print("---")
        return

    # Poll until complete or the deadline passes. Always poll at least once.
    deadline = time.monotonic() + max(args.max_wait, 0)
    interval = max(args.interval, 1)
    while True:
        pending = _pending_keys(args.run_dir, keys)
        if not pending or time.monotonic() >= deadline:
            break
        time.sleep(min(interval, max(deadline - time.monotonic(), 0)))

    print(f"COMPLETED={len(keys) - len(pending)}")
    print(f"PENDING={len(pending)}")
    print(f"WAVE_SIZE={len(keys)}")
    print("---")
    for key in pending:
        print(key)

    if pending:
        sys.exit(3)


if __name__ == "__main__":
    main()
