#!/usr/bin/env python3
"""Publish today's artwork selection to today.json.

Run daily by the GitHub Action (or by hand). Every natureCube reads
today.json rather than choosing locally, so all devices worldwide show
the same piece on the same day.

    python3 pick_daily.py            # deterministic pick from UTC date
    python3 pick_daily.py --id 42    # curatorial override for today

Selection is a year-seeded permutation: the manifest order is shuffled
once per year (seed = the year) and indexed by day-of-year, so every
piece appears exactly once a year and consecutive days are unrelated.
(The old ASCII-sum formula walked the manifest nearly sequentially and
rewound ~8 places at every ten-day boundary — replaying pieces shown
the week before.) The natureCube server's offline fallback implements
the identical formula, so a device that can't reach today.json still
agrees with the fleet.
"""

import argparse
import json
import random
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
        now = datetime.now(timezone.utc)
        order = list(range(len(images)))
        random.Random(now.year).shuffle(order)
        artwork = images[order[(now.timetuple().tm_yday - 1)
                               % len(images)]]

    with open("today.json", "w") as f:
        json.dump({"date": today, "artwork": artwork}, f, indent=2)
        f.write("\n")

    print(f"{today}: #{artwork['id']} — {artwork['title']} "
          f"by {artwork['artist']} ({artwork['year']})")


if __name__ == "__main__":
    main()
