#!/usr/bin/env python3
"""What the marketplace is about, and which subjects are real products."""
import json, pathlib, sys
import plate
from plate import INK, INK2, MUTED, RULE, GRID, FAINT

W = 880
REAL, SAMPLE = "#2f6f5e", "#c08a3e"


def main():
    here = pathlib.Path(__file__).resolve()
    src = sys.argv[1] if len(sys.argv) > 1 else str(sorted((here.parents[1] / "public").glob("subjects-*.json"))[-1])
    d = json.load(open(src))
    cats = [c for c in d["categories"] if c["name"] != "Unclassified"]
    unc = next(c for c in d["categories"] if c["name"] == "Unclassified")
    cats.sort(key=lambda c: -c["real"])
    H = 340 + len(cats) * 28

    s = plate.open_svg(W, H,
        "The depth is in health data. The B2B listings are mostly teasers.",
        subtitle=f"{d['total']:,} listings by subject, split into real products and trial samples. "
                 f"Ordered by how many REAL products each subject holds.")
    f, y = plate.frame(W, 88,
        who="A buyer trying to work out what is actually for sale here",
        decide="Which subject to shop in, and whether a large listing count means depth",
        wrong="Sample share is similar across subjects — then the listing count is a fair guide")
    s += f

    x0, x1 = 214, W - 264
    top_y = y + 34
    mx = max(c["n"] for c in cats)
    for i, c in enumerate(cats):
        ry = top_y + i * 28
        w = (x1-x0) * c["n"] / mx
        rw = (x1-x0) * c["real"] / mx
        s.append(f'<rect x="{x0}" y="{ry:.1f}" width="{max(w,2):.1f}" height="18" rx="3" fill="{SAMPLE}" fill-opacity="0.85"/>')
        if rw > 0.5:
            s.append(f'<rect x="{x0}" y="{ry:.1f}" width="{rw:.1f}" height="18" rx="3" fill="{REAL}" fill-opacity="0.95"/>')
        s.append(plate.txt(x0-10, ry+14, c["name"], size=10.5, fill=INK2, anchor="end"))
        s += plate.halo(x0+max(w,2)+8, ry+14, f'{c["real"]:,} / {c["n"]:,}', size=10, fill=MUTED)
    bot = top_y + len(cats)*28

    lx = x1 + 30
    s.append(plate.txt(lx, top_y+2, "OF THE STORE", size=9, fill=MUTED, weight="700", spacing="0.9"))
    for i,(lab,v,col) in enumerate((("real products", d["real"], REAL),
                                    ("trial samples", d["total"]-d["real"], SAMPLE))):
        yy = top_y + 26 + i*48
        s.append(f'<rect x="{lx}" y="{yy-10:.1f}" width="12" height="12" rx="2" fill="{col}"/>')
        s += plate.halo(lx+19, yy, f"{v:,}", size=15, fill=INK)
        s.append(plate.txt(lx, yy+16, lab, size=10.5, fill=MUTED))

    s += plate.halo(28, bot+28,
        "Health is 11% of listings and 23% of real products.", size=12.5, fill=INK)
    # Read from the data: a typed "29" here disagreed with the bar's own label.
    biz = next(c for c in cats if c["name"].startswith("Business"))
    s += plate.wrap(28, bot+46,
        f"{biz['name']} is the largest subject by listing count and {biz['sample_pct']:.0f}% of it is "
        f"samples, leaving {biz['real']} real products. A buyer reading listing counts would shop in "
        f"exactly the wrong aisle.",
        size=10.5, fill=MUTED, chars=120, leading=13)

    s.append(f'<line x1="28" y1="{H-76:.1f}" x2="{W-28}" y2="{H-76:.1f}" stroke="{RULE}"/>')
    s += plate.wrap(28, H-60,
        f"Databricks Marketplace sitemap, first capture 2026-09-25. SUBJECT IS INFERRED FROM THE "
        f"PRODUCT NAME, because the publisher supplies no category anywhere -- not in the URL, not on "
        f"the page. The rules are regular expressions applied first-match in a fixed order, so a "
        f"listing naming two subjects lands in whichever comes first; both the patterns and that order "
        f"are a judgement, and they are published in public/subjects-2026-09-25.json. "
        f"{unc['n']:,} listings ({unc['share']:.0f}%) match no rule and are omitted from this chart.",
        size=10, fill=MUTED, chars=132, leading=13)
    s.append("</svg>")
    out = here.parent / "charts" / "subjects.svg"
    out.write_text("\n".join(s), encoding="utf-8")
    print(f"  wrote {out.name}  {len(cats)} subjects, {unc['share']:.0f}% unclassified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
