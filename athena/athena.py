#!/usr/bin/env python3
"""
athena.py - Athena: Deterministic OpenGraph & Brand Asset Generator CLI (v1)

Generates pure vector SVG OpenGraph cards directly from design tokens.
Zero external design software required at runtime.

Run:
    python3 athena.py --title "Brand Assets Without Design Tax" --kicker "HYDRA . 015" --out og.svg
    python3 athena.py --title "The Editorial Gate" --colorway dark --out cover.svg
"""
from __future__ import annotations

import argparse
import sys
from typing import Dict

COLORWAYS: Dict[str, Dict[str, str]] = {
    "light": {
        "bg": "#F5F4EF", "bg2": "#ECEAE4", "fg": "#060606",
        "mid": "#555550", "accent": "#D42020", "rule": "#D8D6D0"
    },
    "dark": {
        "bg": "#060606", "bg2": "#0F0F0F", "fg": "#F0EBE0",
        "mid": "#909088", "accent": "#D42020", "rule": "#1A1A1A"
    },
    "crimson": {
        "bg": "#D42020", "bg2": "#B01818", "fg": "#FFFFFF",
        "mid": "#FFD6D6", "accent": "#FFFFFF", "rule": "#E04040"
    },
    "slate": {
        "bg": "#181818", "bg2": "#222222", "fg": "#F5F4EF",
        "mid": "#909088", "accent": "#F5F4EF", "rule": "#333333"
    }
}


def build_svg(title: str, kicker: str, desc: str, stamp: str, cat: str, colorway: str) -> str:
    cw = COLORWAYS.get(colorway, COLORWAYS["light"])
    
    # Escape XML entities
    t_clean = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    k_clean = kicker.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    d_clean = desc.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s_clean = stamp.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    c_clean = cat.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&amp;family=DM+Mono:wght@400;500&amp;family=Unbounded:wght@900&amp;display=swap');
      .title {{ font-family: 'Unbounded', sans-serif; font-weight: 900; fill: {cw['accent']}; text-transform: lowercase; letter-spacing: -0.04em; }}
      .desc {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 500; fill: {cw['fg']}; }}
      .mono {{ font-family: 'DM Mono', monospace; font-size: 15px; letter-spacing: 0.12em; text-transform: uppercase; fill: {cw['mid']}; }}
      .tag {{ font-family: 'DM Mono', monospace; font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase; fill: {cw['accent']}; }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="{cw['bg']}"/>
  <rect x="30" y="30" width="1140" height="570" fill="none" stroke="{cw['rule']}" stroke-width="1.5"/>
  
  <!-- Corner Crosses -->
  <path d="M 22 30 L 38 30 M 30 22 L 30 38" stroke="{cw['accent']}" stroke-width="2"/>
  <path d="M 1162 30 L 1178 30 M 1170 22 L 1170 38" stroke="{cw['accent']}" stroke-width="2"/>
  <path d="M 22 600 L 38 600 M 30 592 L 30 608" stroke="{cw['accent']}" stroke-width="2"/>
  <path d="M 1162 600 L 1178 600 M 1170 592 L 1170 608" stroke="{cw['accent']}" stroke-width="2"/>

  <!-- Top Metadata Bar -->
  <text x="70" y="85" class="mono">{k_clean}</text>
  <rect x="1000" y="66" width="130" height="28" fill="{cw['bg2']}" stroke="{cw['rule']}"/>
  <text x="1065" y="85" text-anchor="middle" class="tag">{c_clean}</text>

  <line x1="70" y1="115" x2="1130" y2="115" stroke="{cw['rule']}" stroke-width="1"/>

  <!-- Main Headline -->
  <text x="70" y="240" font-size="52" class="title">{t_clean}</text>
  
  <!-- Subtitle -->
  <text x="70" y="360" font-size="24" class="desc" opacity="0.9">{d_clean}</text>

  <line x1="70" y1="515" x2="1130" y2="515" stroke="{cw['rule']}" stroke-width="1"/>

  <!-- Bottom Stamp -->
  <text x="70" y="555" class="mono">{s_clean}</text>
  <text x="1130" y="555" text-anchor="end" class="mono">VERIFIED OPERATOR ASSET</text>
</svg>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Athena: Brand Assets & OG Generator")
    parser.add_argument("--title", default="Brand Assets Without The Design Tax", help="Headline")
    parser.add_argument("--kicker", default="HYDRA · 015 · ATHENA", help="Kicker text")
    parser.add_argument("--desc", default="Deterministic vector card generator running entirely in pure code.", help="Subtitle")
    parser.add_argument("--stamp", default="ADRIAN M. PETICILA · PETICILA.RO", help="Footer stamp")
    parser.add_argument("--cat", default="OPERATING SYSTEM", help="Category tag")
    parser.add_argument("--colorway", choices=["light", "dark", "crimson", "slate"], default="light", help="Colorway palette")
    parser.add_argument("--out", default="og.svg", help="Output SVG path")
    args = parser.parse_args()

    svg_content = build_svg(args.title, args.kicker, args.desc, args.stamp, args.cat, args.colorway)

    try:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"Athena: Generated SVG written to {args.out}")
    except OSError as e:
        print(f"Athena error: cannot write to {args.out}: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
