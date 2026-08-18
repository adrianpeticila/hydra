#!/usr/bin/env python3
"""
cadmus.py - Cadmus: Content ROI on Behavior CLI (v1)

Evaluates content assets on high-intent actions (saves, shares, inquiries)
rather than vanity metrics. Emits actionable quadrant classifications.

Run:
    python3 cadmus.py --views 4000 --saves 120 --shares 30
    python3 cadmus.py --file posts.json --json
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List


def classify_post(title: str, views: int, saves: int, shares: int, inquiries: int) -> Dict[str, Any]:
    save_rate = (saves / views * 1000) if views > 0 else 0.0
    
    if save_rate >= 25 and views >= 2000:
        quad = "Core Asset"
        recommendation = "Evergreen Anchor: Repurpose into long-form and link sitewide."
    elif save_rate >= 25 and views < 2000:
        quad = "Quiet Goldmine"
        recommendation = "High substance, low distribution: Rewrite the hook via Tyche."
    elif save_rate < 10 and views >= 3000:
        quad = "Viral Bubble"
        recommendation = "Ephemeral reach: Zero buyer conviction. Do not boost or replicate."
    else:
        quad = "Dead Weight"
        recommendation = "Archive or fundamentally rethink premise from scratch."

    return {
        "title": title,
        "views": views,
        "saves": saves,
        "shares": shares,
        "inquiries": inquiries,
        "save_rate_per_1k": round(save_rate, 1),
        "quadrant": quad,
        "action": recommendation
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Cadmus: Content ROI on Behavior")
    parser.add_argument("--title", default="Untitled Post", help="Post title")
    parser.add_argument("--views", type=int, default=0, help="Total views/impressions")
    parser.add_argument("--saves", type=int, default=0, help="Saves / Bookmarks")
    parser.add_argument("--shares", type=int, default=0, help="Shares / Reposts")
    parser.add_argument("--inquiries", type=int, default=0, help="Qualified inquiries")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    res = classify_post(args.title, args.views, args.saves, args.shares, args.inquiries)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("\nCADMUS : CONTENT BEHAVIOR AUDIT\n")
        print(f"Title: {res['title']}")
        print(f"Views: {res['views']:,}  |  Saves: {res['saves']:,}  |  Save Rate: {res['save_rate_per_1k']}/1k")
        print(f"Quadrant: {res['quadrant']}")
        print(f"Action:   {res['action']}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
