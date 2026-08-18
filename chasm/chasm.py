#!/usr/bin/env python3
"""
chasm.py - Chasm: editorial gate AS CODE (v1) - deterministic prose gate.

Product name: Chasm (codename editorial-gate).
Deterministic, no AI opinion, no upload, zero dependencies, MIT.

A draft either PASSES the gate or it does not. No editorial deliberation
at ship time: the machine blocks. You tune the rules, not the judgement.

Run:
    python3 chasm.py draft.txt
    python3 chasm.py draft.txt --strict --json
    echo "..." | python3 chasm.py --stdin

Exit codes: 0 = PASS, 2 = FAIL (hard rules), 3 = WARN (only soft findings)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# RULESET v1 - deterministic, keyword/heuristic based.
# ---------------------------------------------------------------------------

# A) HARD-kill vocabulary: AI-isms / corporate slop / cliches. A hit => gate FAILS.
HARD_WORDS: List[str] = [
    "leverage", "harness", "unlock", "elevate", "streamline", "ecosystem",
    "paradigm", "groundbreaking", "innovative", "cutting-edge", "state-of-the-art",
    "robust", "holistic", "seamless", "synergy", "delve", "navigate", "landscape",
    "revolutionize", "game-changer", "game changing", "best-in-class",
    "world-class", "next-level", "empower", "supercharge", "low-hanging fruit",
    "dive deep", "deep-dive", "fast-paced", "gameplan", "mission-critical",
    "thought-leader", "influencer-grade", "unprecedented", "disrupt", "pivot",
]

# B) SOFT flags: weak / filler openers & vague phrases. A hit => WARN (config-fail with --strict).
SOFT_PHRASES: List[str] = [
    "it's important to note", "it is important to note", "it's worth mentioning",
    "it is worth mentioning", "at the end of the day", "let's dive into",
    "in conclusion", "to sum up", "when it comes to", "keep in mind",
    "as we all know", "in today's", "in today,s", "remember that",
    "it's been a journey", "a lot of", "kind of", "sort of", "stuff like",
    "things like", "trust me", "just saying", "long story short",
]

# C) Rhythm / structure heuristics.
EM_DASH = "\u2014"
EN_DASH = "\u2013"

# Legit all-caps acronyms that must never be flagged as "shouting".
ACRONYM_ALLOW = {
    "CMO", "CEO", "CTO", "CFO", "COO", "CRO", "VC", "AI", "SEO", "MCP", "HTTP",
    "HTTPS", "URL", "B2B", "B2C", "B2G", "ROI", "KPI", "CRM", "SaaS", "LLM",
    "RO", "EN", "HTML", "CSS", "JS", "GH", "WWW", "CTA", "GMT", "UTC", "ROAS",
    "RSS", "XML", "JSON", "SVG", "API", "AWS", "CF", "MRR", "ARR",
}

_sent_split = re.compile(r"(?<=[.!?])\s+")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lines(text: str) -> List[str]:
    return text.replace("\r\n", "\n").split("\n")


def hard_hits(text: str) -> List[Dict[str, Any]]:
    low = text.lower()
    out: List[Dict[str, Any]] = []
    for word in HARD_WORDS:
        n = low.count(word)
        if n:
            out.append({"rule": "A:hard-kill-word", "term": word, "count": n})
    return out


def soft_hits(text: str) -> List[Dict[str, Any]]:
    low = text.lower()
    out: List[Dict[str, Any]] = []
    for phrase in SOFT_PHRASES:
        n = low.count(phrase)
        if n:
            out.append({"rule": "B:filler-phrase", "term": phrase, "count": n})
    return out


def structure_hits(text: str, strict_emdash: bool) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    # em-dash overuse (optional: stays warn unless --strict-emdash)
    em = text.count(EM_DASH)
    if em:
        out.append({"rule": "C:emdash-count", "term": "em dash", "count": em,
                    "severity": "warn"})

    # fragment stacking: >=3 consecutive sentences of <=5 words
    lines = [l.strip() for l in _lines(text) if l.strip()]
    joined = " ".join(lines)
    sents = [s.strip() for s in _sent_split.split(joined) if s.strip()]
    run = 0
    for s in sents:
        wc = len(s.split())
        run = run + 1 if wc <= 5 else 0
        if run >= 3:
            out.append({"rule": "C:fragment-stack",
                        "term": ">=3 short sentences in a row",
                        "count": run, "severity": "warn"})
            break

    # sentence over-length
    for s in sents:
        wc = len(s.split())
        if wc > 60:
            out.append({"rule": "C:sentence-overlong", "term": f"{wc} words",
                        "count": wc, "severity": "warn"})

    # all-caps shouting (exclude legitimate acronyms) / chatter punctuation
    caps_tokens = [t for t in re.findall(r"\b[A-Z]{3,}\b", text)
                   if t not in ACRONYM_ALLOW]
    if caps_tokens:
        out.append({"rule": "C:all-caps", "term": "shouting caps",
                    "count": len(set(caps_tokens)), "severity": "warn"})
    for p in ["!!!", "???", "!!?"]:
        if p in text:
            out.append({"rule": "C:chatter-punct", "term": p,
                        "count": text.count(p), "severity": "warn"})

    if strict_emdash:
        for h in out:
            if h["rule"] == "C:emdash-count":
                h["severity"] = "fail"
    return out


def score(findings: List[Dict[str, Any]]) -> float:
    hard = [f for f in findings if f.get("severity", "fail") == "fail"]
    warn = [f for f in findings if f.get("severity") == "warn"]
    penalty = len(hard) * 40 + len(warn) * 8
    return max(0.0, min(100.0, 100 - penalty))


def run_gate(text: str, strict_emdash: bool) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    for h in hard_hits(text):
        h.setdefault("severity", "fail")
        findings.append(h)
    for s in soft_hits(text):
        s["severity"] = "warn"
        findings.append(s)
    findings.extend(structure_hits(text, strict_emdash))

    hard = [f for f in findings if f.get("severity", "fail") == "fail"]
    warn = [f for f in findings if f.get("severity") == "warn"]

    if hard:
        verdict = "FAIL"
    elif warn:
        verdict = "WARN"
    else:
        verdict = "PASS"

    return {
        "verdict": verdict,
        "score": round(score(findings), 1),
        "rules_run": len(HARD_WORDS) + len(SOFT_PHRASES) + 4,
        "hard_hits": len(hard),
        "warn_hits": len(warn),
        "findings": findings,
    }


def render(result: Dict[str, Any], strict: bool) -> str:
    v = result["verdict"]
    lines = [f"EDITORIAL GATE : verdict: {v}"]
    lines.append("")
    lines.append(f"  score: {result['score']}/100  |  "
                 f"rules_run: {result['rules_run']}  |  "
                 f"hard: {result['hard_hits']}  |  warn: {result['warn_hits']}"
                 + ("   [--strict: warns fail]" if strict else ""))
    lines.append("")
    for f in result["findings"]:
        severity = f["severity"].upper().ljust(4)
        lines.append(f"  [{severity}] {f['rule']:<22}  "
                     f"{f.get('term','')}  x{f['count']}")
    if not result["findings"]:
        lines.append("  (no findings) clean.")
    lines.append("")
    if v == "FAIL":
        lines.append("  Blocked. Resolve the hard-kill items above before shipping.")
    elif v == "WARN":
        lines.append("  Soft findings only. Hard rules passed.")
    else:
        lines.append("  Ship it.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic editorial gate (Phase 2 v1)")
    ap.add_argument("file", nargs="?", help="path to draft text file")
    ap.add_argument("--stdin", action="store_true", help="read draft from stdin")
    ap.add_argument("--strict", action="store_true",
                    help="promote soft findings to fail (block on warns)")
    ap.add_argument("--strict-emdash", action="store_true",
                    help="treat em-dash overuse as hard fail")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args()

    if args.stdin:
        text = sys.stdin.read()
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"editorial_gate: cannot read {args.file}: {e}", file=sys.stderr)
            return 1
    else:
        ap.print_help()
        return 1

    result = run_gate(text, args.strict_emdash)
    if args.strict and result["verdict"] == "WARN":
        result["verdict"] = "FAIL"
        result["hard_hits"] += result["warn_hits"]

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result, args.strict))

    return {"PASS": 0, "WARN": 3, "FAIL": 2}[result["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
