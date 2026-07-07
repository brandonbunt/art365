#!/usr/bin/env python3
"""Publish today's artwork selection to today.json.

Run daily by the GitHub Action (or by hand). Every natureCube reads
today.json rather than choosing locally, so all devices worldwide show
the same piece on the same day.

    python3 pick_daily.py            # deterministic pick from UTC date
    python3 pick_daily.py --id 42    # curatorial override for today

The deterministic formula (ASCII sum of YYYY-MM-DD mod N) intentionally
matches the natureCube server's offline fallback, so a device that can't
reach today.json usually still agrees with the fleet.
"""

import argparse
import json
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, default=None,
                        help="force a specific artwork id for today")
    args = parser.parse_args()

    with open("manifest.json") as f:
        manifest = json.load(f)
    images = manifest["images"]

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if args.id is not None:
        matches = [a for a in images if a["id"] == args.id]
        if not matches:
            raise SystemExit(f"no artwork with id {args.id} in manifest")
        artwork = matches[0]
    else:
        artwork = images[sum(ord(c) for c in today) % len(images)]

    with open("today.json", "w") as f:
        json.dump({"date": today, "artwork": artwork}, f, indent=2)
        f.write("\n")

    print(f"{today}: #{artwork['id']} — {artwork['title']} "
          f"by {artwork['artist']} ({artwork['year']})")


if __name__ == "__main__":
    main()
