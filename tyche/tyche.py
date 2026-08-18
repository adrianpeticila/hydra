#!/usr/bin/env python3
"""
tyche.py - Tyche: B2B Executive Hook Bank and Scoring CLI (v1)

Deterministic scoring and generation of opening hooks based on
proven operator frameworks. Zero ML, zero dependencies, pure Python.

Run:
    python3 tyche.py "Most founders treat churn as a product bug..."
    python3 tyche.py --topic "B2B Pricing" --metric "40k EUR" --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Dict, List

FRAMEWORKS = [
    {
        "id": "contrarian-diagnostic",
        "name": "The Contrarian Diagnostic",
        "structure": "Most [Role/Industry] believe [Common Myth]. The reality is [Hard Truth with Data].",
        "example": "Most founders treat churn as a product bug. In 85% of B2B cases, churn is an onboarding failure that happened in the first 14 minutes.",
        "why": "Forces immediate cognitive dissonance by dismantling comfortable assumptions."
    },
    {
        "id": "expensive-mistake",
        "name": "The Expensive Mistake",
        "structure": "How [Target Audience] burns [Metric/Dollars/Hours] on [Tactical Distraction] without realizing it.",
        "example": "How Series A companies burn 40k EUR a month on outbound spam while their core landing page converts at 0.4%.",
        "why": "Loss framing combined with tangible resource drain. High emotional resonance for operators."
    },
    {
        "id": "concrete-arithmetic",
        "name": "Concrete Arithmetic",
        "structure": "[Exact Number] [Timeframe/Asset]. Zero [Fluff/Excuses]. Here is the breakdown.",
        "example": "29 brands built, 6 years running lean, 0 sales calls booked. The exact system behind zero-waste distribution.",
        "why": "Proof-of-work up front. Removes abstract hype and replaces it with quantifiable results."
    },
    {
        "id": "uncomfortable-audit",
        "name": "The Uncomfortable Audit",
        "structure": "If your [Asset/Team/Strategy] does [Tell/Symptom], you do not have [Goal]. You have [Uncomfortable Reality].",
        "example": "If your marketing requires a 12-page PDF to explain your value proposition, you don't have a positioning problem: you have no product conviction.",
        "why": "Binary diagnostic. The reader is forced to self-assess immediately."
    },
    {
        "id": "behind-the-curtain",
        "name": "Behind the Curtain",
        "structure": "Inside the [Exact System/Pipeline] we use to [Outcome] without [Standard Industry Headache].",
        "example": "Inside the deterministic pre-merge gate we use to prevent AI slop from reaching production across 7 brand repos.",
        "why": "Appeals to craftsmanship and curiosity. Offers a concrete operational look rather than general advice."
    }
]


def score_hook(text: str) -> Dict[str, Any]:
    words = text.strip().split()
    length = len(words)

    # 1. Specificity & Arithmetic
    nums = re.findall(r"\b\d+(?:[\.,]\d+)?%?|\$\d+|\€\d+|EUR|USD|hours?|days?|months?|k\b", text, re.I)
    if len(nums) >= 2:
        score_spec = 25
    elif len(nums) == 1:
        score_spec = 18
    else:
        score_spec = 8

    # 2. Cognitive Tension
    tension_words = ["most", "reality", "instead", "mistake", "burn", "zero", "stop", "fail", "without", "truth", "myth", "lie", "waste", "hidden", "broken", "vs", "versus"]
    tension_hits = [w for w in tension_words if re.search(r"\b" + w + r"\b", text, re.I)]
    if len(tension_hits) >= 2:
        score_tension = 25
    elif len(tension_hits) == 1:
        score_tension = 18
    else:
        score_tension = 10

    # 3. Voice & Brevity
    slop_words = ["leverage", "unleash", "delve", "game-changer", "supercharge", "elevate", "seamless", "synergy", "journey"]
    has_slop = any(re.search(r"\b" + w + r"\b", text, re.I) for w in slop_words)
    if has_slop:
        score_voice = 5
    elif 10 <= length <= 30:
        score_voice = 25
    elif length < 10:
        score_voice = 15
    else:
        score_voice = 12

    # 4. Qualified Relevancy
    b2b_markers = ["founder", "cmo", "ceo", "b2b", "pipeline", "churn", "pricing", "retention", "landing page", "revenue", "system", "brand", "client", "customer", "audit", "margin"]
    rel_hits = [w for w in b2b_markers if re.search(r"\b" + w + r"\b", text, re.I)]
    if len(rel_hits) >= 2:
        score_rel = 25
    elif len(rel_hits) == 1:
        score_rel = 19
    else:
        score_rel = 12

    total = score_spec + score_tension + score_voice + score_rel

    return {
        "text": text,
        "total_score": total,
        "word_count": length,
        "dimensions": {
            "specificity": score_spec,
            "tension": score_tension,
            "voice": score_voice,
            "relevancy": score_rel,
        },
        "metrics_found": nums,
        "tension_cues": tension_hits,
        "has_slop": has_slop,
    }


def generate_for_topic(topic: str, metric: str, villain: str, truth: str) -> List[Dict[str, str]]:
    return [
        {
            "framework": "The Contrarian Diagnostic",
            "hook": f"Most teams approach {topic} by {villain}. In reality, {metric} are lost because nobody took the time for {truth}.",
        },
        {
            "framework": "The Expensive Mistake",
            "hook": f"How companies lose {metric} trying to solve {topic} through {villain}.",
        },
        {
            "framework": "Concrete Arithmetic",
            "hook": f"{metric} impacted, 0 vanity metrics. The exact arithmetic behind {topic} through {truth}.",
        },
        {
            "framework": "The Uncomfortable Audit",
            "hook": f"If your {topic} relies on {villain}, you don't have a distribution strategy: you have a high-cost distraction.",
        },
        {
            "framework": "Behind the Curtain",
            "hook": f"Inside the exact operational framework we use to master {topic} through {truth} (without {villain}).",
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Tyche: Executive Hook Bank & Scorer")
    parser.add_argument("hook", nargs="?", help="Hook text to evaluate")
    parser.add_argument("--topic", help="Topic for generating hooks")
    parser.add_argument("--metric", default="24%", help="Metric for generated hooks")
    parser.add_argument("--villain", default="chasing feature parity", help="Villain / mistake")
    parser.add_argument("--truth", default="owning one clear claim", help="Core truth / fix")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    if args.topic:
        gen = generate_for_topic(args.topic, args.metric, args.villain, args.truth)
        if args.json:
            print(json.dumps({"topic": args.topic, "generated": gen}, indent=2))
        else:
            print(f"\nTYCHE : GENERATED HOOKS FOR '{args.topic}':\n")
            for item in gen:
                print(f"[{item['framework']}]")
                print(f"  \"{item['hook']}\"\n")
        return 0

    if args.hook:
        res = score_hook(args.hook)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"\nTYCHE QUALITY SCORE : {res['total_score']}/100")
            print(f"  Length: {res['word_count']} words")
            print(f"  Specificity: {res['dimensions']['specificity']}/25")
            print(f"  Tension:     {res['dimensions']['tension']}/25")
            print(f"  Voice:       {res['dimensions']['voice']}/25")
            print(f"  Relevancy:   {res['dimensions']['relevancy']}/25")
            if res['has_slop']:
                print("  [WARN] Blacklisted buzzword detected!")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
