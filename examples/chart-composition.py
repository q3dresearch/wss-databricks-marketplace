#!/usr/bin/env python3
"""What the Databricks Marketplace is actually made of."""
import json, pathlib, sys
import plate
from plate import INK, INK2, MUTED, RULE, GRID, FAINT

W = 880
REAL, SAMPLE = "#2f6f5e", "#c08a3e"


def main():
    here = pathlib.Path(__file__).resolve()
    src = sys.argv[1] if len(sys.argv) > 1 else str(sorted((here.parents[1] / "public").glob("composition-*.json"))[-1])
    d = json.load(open(src))
    n, ns, top = d["listings"], d["samples"], d["top"]
    real = n - ns
    H = 330 + len(top) * 26

    s = plate.open_svg(W, H,
        f"{100*ns/n:.0f}% of the Databricks Marketplace is sample data, not products",
        subtitle=f"{n:,} listings from {d['vendors']} vendors. A listing counts as a sample when "
                 f"SAMPLE appears in its name, which is how Databricks marks trial datasets.")
    f, y = plate.frame(W, 88,
        who="Anyone sizing this marketplace, or comparing it against another",
        decide="Which number to quote — the listing count, or the product count",
        wrong="Samples are spread evenly across vendors, making the split uninformative")
    s += f

    x0, x1 = 208, W - 210
    top_y = y + 30
    mx = max(t["n"] for t in top)
    for i, t in enumerate(top):
        ry = top_y + i * 26
        w = (x1 - x0) * t["n"] / mx
        sw = w * t["sample_pct"] / 100
        s.append(f'<rect x="{x0}" y="{ry:.1f}" width="{w:.1f}" height="17" rx="3" fill="{REAL}" fill-opacity="0.85"/>')
        if sw > 0.5:
            s.append(f'<rect x="{x0}" y="{ry:.1f}" width="{sw:.1f}" height="17" rx="3" fill="{SAMPLE}" fill-opacity="0.95"/>')
        s.append(plate.txt(x0 - 10, ry + 13, t["vendor"][:26], size=10.5, fill=INK2, anchor="end"))
        # Count only. The fill colour already says sample-or-not, and repeating
        # it in text ran the labels under the right-hand legend.
        s += plate.halo(x0 + w + 8, ry + 13, f'{t["n"]}', size=10.5, fill=MUTED)
    bot = top_y + len(top) * 26

    lx = x1 + 26
    s.append(plate.txt(lx, top_y + 2, "THE STORE", size=9, fill=MUTED, weight="700", spacing="0.9"))
    for i, (lab, v, col) in enumerate((("samples", ns, SAMPLE), ("real products", real, REAL))):
        yy = top_y + 26 + i * 46
        s.append(f'<rect x="{lx}" y="{yy-10:.1f}" width="12" height="12" rx="2" fill="{col}"/>')
        s += plate.halo(lx + 19, yy, f"{v:,}", size=15, fill=INK)
        s.append(plate.txt(lx, yy + 16, lab, size=10.5, fill=MUTED))

    s += plate.halo(x0 - 10, bot + 26,
        f"Quote {real:,}, not {n:,}.", size=13, fill=INK, anchor="end")
    s += plate.wrap(x0 - 10, bot + 44,
        f"The two largest vendors are opposites: Techsalerator's {top[0]['n']} listings are "
        f"{top[0]['sample_pct']:.0f}% samples, John-Snow-Labs' {top[1]['n']} are "
        f"{top[1]['sample_pct']:.0f}%. Together they are 22% of the store.",
        size=10.5, fill=MUTED, chars=74, leading=13)

    s.append(f'<line x1="28" y1="{H-74:.1f}" x2="{W-28}" y2="{H-74:.1f}" stroke="{RULE}"/>')
    s += plate.wrap(28, H - 58,
        f"Databricks Marketplace sitemap, first capture 2026-09-25. Vendor is the segment before the "
        f"first underscore in the URL name; splitting on the hyphen instead shreds hyphenated vendors "
        f"like john-snow-labs into useless tokens. The sample share is NOT a large-vendor habit: it is "
        f"{d['sample_big']:.0f}% among vendors with 20+ listings and {d['sample_small']:.0f}% among "
        f"smaller ones, so the split is store-wide rather than driven by the biggest sellers.",
        size=10, fill=MUTED, chars=132, leading=13)
    s.append("</svg>")
    out = here.parent / "charts" / "composition.svg"
    out.write_text("\n".join(s), encoding="utf-8")
    print(f"  wrote {out.name}  {100*ns/n:.0f}% samples, {d['vendors']} vendors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
