#!/usr/bin/env python3
"""Sampling is a vendor strategy, not a per-listing choice."""
import json, math, pathlib, sys
import plate
from plate import INK, INK2, MUTED, RULE, GRID, FAINT

W, H = 880, 620
ALLS, NONE, MIX = "#c08a3e", "#2f6f5e", "#b4472e"


def main():
    here = pathlib.Path(__file__).resolve()
    src = sys.argv[1] if len(sys.argv) > 1 else str(sorted((here.parents[1] / "public").glob("vendors-*.json"))[-1])
    V = json.load(open(src))
    alls = [v for v in V if v["sample_pct"] == 100]
    none = [v for v in V if v["sample_pct"] == 0]
    mix  = [v for v in V if 0 < v["sample_pct"] < 100]

    s = plate.open_svg(W, H,
        f"{100*(len(alls)+len(none))/len(V):.0f}% of vendors are all-sample or no-sample, never a mix",
        subtitle=f"One mark per vendor, n={len(V)}. Horizontal is how many listings it has; vertical is "
                 f"what share of them are trial samples.")
    f, y = plate.frame(W, 88,
        who="Anyone treating a marketplace listing count as a count of available products",
        decide="Whether to read sampling as a per-product choice or a vendor's whole posture",
        wrong="Vendors spread across the middle — then sampling is chosen product by product")
    s += f

    x0, x1 = 84, W - 210
    top, bot = y + 34, H - 160
    def px(n): return x0 + (x1-x0) * math.log10(max(n,1)) / math.log10(300)
    def py(p): return bot - (bot-top) * p / 100
    for p in (0, 25, 50, 75, 100):
        gy = py(p)
        s.append(f'<line x1="{x0}" y1="{gy:.1f}" x2="{x1}" y2="{gy:.1f}" stroke="{GRID}"/>')
        s.append(plate.txt(x0-9, gy+3.5, f"{p}", size=10.5, fill=MUTED, anchor="end"))
    for n in (1, 10, 100):
        gx = px(n)
        s.append(f'<line x1="{gx:.1f}" y1="{top}" x2="{gx:.1f}" y2="{bot}" stroke="{GRID}"/>')
        s.append(f'<text x="{gx:.1f}" y="{bot+18}" font-size="10.5" fill="{MUTED}" text-anchor="middle" '
                 f'style="font-variant-numeric: tabular-nums">10<tspan dy="-5" font-size="7.5">'
                 f'{int(math.log10(n))}</tspan></text>')
    # Left-anchored at x0: an end-anchored two-line label ran off the canvas.
    s.append(plate.txt(x0, top-16, "% of a vendor's listings that are samples", size=10, fill=MUTED))
    s.append(plate.txt((x0+x1)/2, bot+38, "listings held by that vendor", size=10.5, fill=MUTED, anchor="middle"))

    # Deterministic jitter: 219 of 226 vendors sit on exactly two y values, so
    # unjittered they stack into two invisible lines. Seeded by index, never RNG,
    # so the plate rebuilds identically.
    for i, v in enumerate(V):
        col = ALLS if v["sample_pct"] == 100 else (NONE if v["sample_pct"] == 0 else MIX)
        jx = ((i * 37) % 11 - 5) * 0.9
        jy = ((i * 53) % 11 - 5) * 1.1
        s.append(f'<circle cx="{px(v["n"])+jx:.1f}" cy="{py(v["sample_pct"])+jy:.1f}" r="4" '
                 f'fill="{col}" fill-opacity="0.55" stroke="{plate.SURFACE}" stroke-width="0.9"/>')

    lx = x1 + 26
    s.append(plate.txt(lx, top+2, "VENDOR POSTURE", size=9, fill=MUTED, weight="700", spacing="0.9"))
    for i,(lab,grp,col) in enumerate((("all samples",alls,ALLS),("no samples",none,NONE),("a mix",mix,MIX))):
        yy = top + 26 + i*62
        s.append(f'<rect x="{lx}" y="{yy-10:.1f}" width="12" height="12" rx="2" fill="{col}"/>')
        s += plate.halo(lx+19, yy, f"{len(grp)}", size=15, fill=INK)
        s.append(plate.txt(lx, yy+16, lab, size=10.5, fill=INK2))
        s.append(plate.txt(lx, yy+29, f"{sum(v['n'] for v in grp):,} listings", size=10, fill=MUTED))

    s += plate.halo(x0, bot+62,
        f"Only {len(mix)} vendors of {len(V)} sit anywhere in between.", size=12.5, fill=INK)
    s += plate.wrap(x0, bot+80,
        "All-sample vendors carry more listings each (median 9 against 2), so the trial half of this "
        "marketplace is built by fewer firms listing more.",
        size=10.5, fill=MUTED, chars=104, leading=13)

    s.append(f'<line x1="28" y1="{H-64:.1f}" x2="{W-28}" y2="{H-64:.1f}" stroke="{RULE}"/>')
    s += plate.wrap(28, H-48,
        "Databricks Marketplace sitemap, first capture 2026-09-25. Vendor is the segment before the "
        "first underscore in the URL name. Marks carry a small deterministic jitter because 219 of 226 "
        "vendors sit on exactly two values and would otherwise stack into two flat lines.",
        size=10, fill=MUTED, chars=132, leading=13)
    s.append("</svg>")
    out = here.parent / "charts" / "vendor-strategy.svg"
    out.write_text("\n".join(s), encoding="utf-8")
    print(f"  wrote {out.name}  {len(alls)} all / {len(none)} none / {len(mix)} mixed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
