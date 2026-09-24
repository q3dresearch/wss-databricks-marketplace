#!/usr/bin/env python3
"""How deep each subject is, and how much of that depth is one vendor's shelf.

A buyer asking "can I get this somewhere else?" cannot read the answer off a
listing count. This plate puts catalogue depth on one axis and supplier
concentration on the other, because the two rank almost oppositely.
"""
import json, math, pathlib, sys
import plate
from plate import INK, INK2, MUTED, RULE, GRID, FAINT

W = 880
DEEP, CAPTIVE = "#2f6f5e", "#c08a3e"   # same pair the other plates use for real / sample
MAJORITY = 50.0                        # above this, one vendor IS the subject


def main():
    here = pathlib.Path(__file__).resolve()
    src = (sys.argv[1] if len(sys.argv) > 1
           else str(sorted((here.parents[1] / "public").glob("supplier-depth-*.json"))[-1]))
    d = json.load(open(src))
    cats = [c for c in d["depth"] if c["subject"] != "Unclassified"]
    unc = next(c for c in d["depth"] if c["subject"] == "Unclassified")

    PL, PR = 76, W - 34                # plot left / right
    PH = 400                           # plot height

    s = plate.open_svg(W, 10,
        "The deepest aisle in the store is one vendor's shelf.",
        subtitle=f"{d['real']:,} real products across {len(cats)} subjects. Horizontal: how many "
                 f"products the subject holds. Vertical: the share of them sold by its biggest vendor.")
    f, y = plate.frame(W, 88,
        who="A buyer who needs a second source, or any negotiating position at all",
        decide="Which subject to commit to, given that its largest vendor may raise price or leave",
        wrong="The biggest subjects are also the least concentrated — then catalogue size is a fair "
              "proxy for supplier choice and this plate is redundant")
    s += f

    top = y + 26
    bot = top + PH
    lo, hi = math.log10(2.4), math.log10(280)
    X = lambda v: PL + (PR - PL) * (math.log10(v) - lo) / (hi - lo)
    Y = lambda p: bot - PH * (p / 100.0)

    # grid: y every 20%, x decades labelled as powers of ten, minor decade steps unlabelled
    for p in range(0, 101, 20):
        s.append(f'<line x1="{PL}" y1="{Y(p):.1f}" x2="{PR}" y2="{Y(p):.1f}" stroke="{GRID}"/>')
        s.append(plate.txt(PL - 10, Y(p) + 3.5, p, size=10, fill=MUTED, anchor="end"))
    for v in (3, 5, 20, 30, 50, 200):
        s.append(f'<line x1="{X(v):.1f}" y1="{top}" x2="{X(v):.1f}" y2="{bot}" stroke="{GRID}"/>')
    for e in (1, 2):
        v = 10 ** e
        s.append(f'<line x1="{X(v):.1f}" y1="{top}" x2="{X(v):.1f}" y2="{bot+5:.1f}" stroke="{RULE}"/>')
        s.append(f'<text x="{X(v):.1f}" y="{bot+20:.1f}" font-size="10.5" fill="{MUTED}" '
                 f'text-anchor="middle" style="font-variant-numeric: tabular-nums">'
                 f'10<tspan dy="-4.5" font-size="7.5">{e}</tspan></text>')
    s.append(f'<line x1="{PL}" y1="{top}" x2="{PL}" y2="{bot}" stroke="{RULE}"/>')
    s.append(f'<line x1="{PL}" y1="{bot}" x2="{PR}" y2="{bot}" stroke="{RULE}"/>')

    # the majority line: above it, one vendor holds more than everyone else combined
    s.append(f'<line x1="{PL}" y1="{Y(MAJORITY):.1f}" x2="{PR}" y2="{Y(MAJORITY):.1f}" '
             f'stroke="{CAPTIVE}" stroke-width="1.4" stroke-dasharray="5 4" opacity="0.85"/>')
    # Annotated at the LEFT end: the right end of this line sits in the densest
    # part of the plot and the note landed on top of a subject's own sub-label.
    s += plate.halo(PL + 6, Y(MAJORITY) - 8, "above this line, one vendor holds the majority",
                    size=10, fill=CAPTIVE, anchor="start")

    s.append(plate.txt(PL - 10, top - 12, "%", size=10, fill=MUTED, anchor="end"))
    s.append(plate.txt(PL, top - 12, "SHARE HELD BY THE LARGEST VENDOR", size=8.5, fill=MUTED,
                       weight="700", spacing="0.9"))
    s.append(plate.txt(PR, bot + 34, "REAL PRODUCTS IN THE SUBJECT", size=8.5, fill=MUTED,
                       anchor="end", weight="700", spacing="0.9"))

    # marks: one per subject. Labels are PLACED, not offset by a rule of thumb.
    # A left/right flip on its own put "News & media" off the left edge, ran
    # "Consumer & identity" off the right, and stacked Retail & product on top
    # of Weather & environment. Each label now tries six positions and takes the
    # first that is inside the canvas and clear of every label already placed.
    CW_NAME, CW_SUB, LEFT_LIM, RIGHT_LIM = 6.05, 5.05, 30, W - 30

    def extent(lx, anchor, w):
        if anchor == "start":  return lx, lx + w
        if anchor == "end":    return lx - w, lx
        return lx - w / 2, lx + w / 2

    def hits(a, b):
        return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

    boxes, marks, leaders, labels = [], [], [], []
    for c in sorted(cats, key=lambda c: -c["real"]):
        cx, cy = X(c["real"]), Y(c["top1_pct"])
        col = CAPTIVE if c["top1_pct"] > MAJORITY else DEEP
        # The product count and the share are POSITIONS on the two axes; typing
        # them beside the mark is the axis written out twice and it was what made
        # the labels too wide to place. The sub-line carries only what is not
        # drawn anywhere: how many vendors, and which one is the largest.
        sub = f'{c["vendors"]} vendors · {c["top_vendor"]}'
        w = max(len(c["subject"]) * CW_NAME, len(sub) * CW_SUB)
        cands = []
        for dy in (3.5, -13, 20, -26, 33, -39, 46, -52, 59):
            cands += [("start", cx + 12, cy + dy), ("end", cx - 12, cy + dy)]
        cands += [("middle", cx, cy - 24), ("middle", cx, cy + 32)]
        for anchor, lx, ly in cands:
            x0, x1 = extent(lx, anchor, w)
            bx = (x0, ly - 10, x1, ly + 21)
            if x0 < LEFT_LIM or x1 > RIGHT_LIM:           continue
            if ly - 10 < top - 18 or ly + 21 > bot + 8:   continue
            if any(hits(bx, o) for o in boxes):           continue
            break
        else:
            raise SystemExit(f"no free position for {c['subject']} -- widen the plot")
        boxes.append(bx)
        marks.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="{col}" fill-opacity="0.9" '
                     f'stroke="{plate.SURFACE}" stroke-width="2"/>')
        # A label pushed off its own row needs a leader, or it reads as belonging
        # to whichever mark it drifted next to.
        if abs(ly - (cy + 3.5)) > 16:
            ax = lx - 5 if anchor == "start" else (lx + 5 if anchor == "end" else lx)
            leaders.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{ax:.1f}" y2="{ly-3:.1f}" '
                           f'stroke="{FAINT}" stroke-width="1"/>')
        labels += plate.halo(lx, ly, c["subject"], size=10.5, fill=INK2, anchor=anchor, weight="500")
        labels += plate.halo(lx, ly + 13, sub, size=9, fill=MUTED, anchor=anchor, weight="400")

    # Every leader goes down BEFORE any text. Emitted per-point, a later leader
    # drew straight across an earlier label and the halo could not mask it.
    s += marks + leaders + labels

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            assert not hits(boxes[i], boxes[j]), f"labels {i} and {j} overlap"

    # Ranks are READ, not typed: an earlier draft hard-coded "first and fifth"
    # and would have gone stale the first time a vendor was reclassified.
    ORD = {1:"first",2:"second",3:"third",4:"fourth",5:"fifth",6:"sixth",
           7:"seventh",8:"eighth",9:"ninth",10:"tenth",11:"eleventh",12:"twelfth"}
    by_prod = sorted(cats, key=lambda c: -c["real"])
    by_conc = sorted(cats, key=lambda c: c["top1_pct"])
    r_prod = lambda c: ORD[by_prod.index(c) + 1]
    r_conc = lambda c: ORD[by_conc.index(c) + 1]

    sy = bot + 58
    s += plate.halo(28, sy, "Health has the most to buy and the least choice about who to buy it from.",
                    size=12.5, fill=INK)
    hea = next(c for c in cats if c["subject"].startswith("Health"))
    biz = next(c for c in cats if c["subject"].startswith("Business"))
    s += plate.wrap(28, sy + 19,
        f"{hea['subject']} holds {hea['real']} real products, more than any other subject, and "
        f"{hea['top1_pct']:.0f}% of them are sold by {hea['top_vendor']}. {biz['subject']} holds only "
        f"{biz['real']}, spread over {biz['vendors']} vendors with the largest at {biz['top1_pct']:.0f}% "
        f"— the widest supplier choice on the platform. Ranked by products they sit {r_prod(hea)} and "
        f"{r_prod(biz)}; ranked by how much of the subject one firm controls, {r_conc(hea)} and "
        f"{r_conc(biz)}.",
        size=10.5, fill=MUTED, chars=126, leading=13)

    H = int(sy + 19 + 3 * 13 + 84)
    s.append(f'<line x1="28" y1="{H-70:.1f}" x2="{W-28}" y2="{H-70:.1f}" stroke="{RULE}"/>')
    s += plate.wrap(28, H - 54,
        f"Databricks Marketplace sitemap, captured 2026-09-24. Vendor is the slug segment before the "
        f"first underscore and subject is inferred from the product name — the publisher supplies "
        f"neither, so both are this repo's judgement and both are published alongside the counts. "
        f"Samples are excluded: only the {d['real']:,} real products are counted, because a trial "
        f"dataset is not a second source. Vendor COUNT is not drawn as a third channel — it "
        f"correlates with the horizontal axis at r=+0.75 and would be that axis drawn twice. "
        f"{unc['real']:,} real products match no subject rule and are omitted.",
        size=10, fill=MUTED, chars=134, leading=13)
    s.append("</svg>")
    # Both the <svg> tag AND the background rect carry the placeholder height.
    # Patching only the first leaves a 10px surface and a transparent plate.
    svg = ("\n".join(s).replace('height="10"', f'height="{H}"')
                        .replace(f'viewBox="0 0 {W} 10"', f'viewBox="0 0 {W} {H}"'))
    assert 'height="10"' not in svg, "placeholder height survived"
    out = here.parent / "charts" / "supplier-depth.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"  wrote {out.name}  {len(cats)} subjects, "
          f"{sum(1 for c in cats if c['top1_pct']>MAJORITY)} majority-held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
