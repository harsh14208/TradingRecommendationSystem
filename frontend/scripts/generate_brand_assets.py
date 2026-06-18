"""Generate all static brand assets from the canonical BrandMark.

SINGLE SOURCE OF TRUTH: the mark paths + stroke live in `frontend/src/cin.ui.jsx`
(`BRAND_MARK_PATHS` / `BRAND_MARK_STROKE`). This script parses them, derives the
centering/scale geometry from the actual mark bounding box (via headless
chromium), and (re)writes:

    public/favicon.svg          mark on a dark rounded square
    public/logo-full.svg        horizontal lockup (mark + SIGNAL.TRADE wordmark)
    public/favicon.png (128)    rasterized icon
    public/logo-icon.png (256)
    public/logo-icon-192.png
    public/logo-icon-512.png
    public/apple-touch-icon.png (256)
    public/logo-full.png (400x266, transparent)

Run after editing the mark in cin.ui.jsx:
    backend/venv/bin/python frontend/scripts/generate_brand_assets.py

Requires playwright + chromium (already installed in backend/venv).
"""

import pathlib
import re

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "frontend/src/cin.ui.jsx"
PUB = ROOT / "frontend/public"

ACCENT = "#22d3ee"  # --bull / --up
TEXT = "#eef2f9"  # wordmark fill (near-white, for dark backgrounds)
BG = "#0D1322"  # icon background (--bg-1)

ICON_FILL_FRAC = 22 / 32  # how much of the square the mark's bbox spans
LOCKUP_MARK_H = 70  # mark visual height (px) inside the 400x266 lockup
LOCKUP_GAP = 18  # gap between mark and wordmark


def parse_mark() -> tuple[float, list[str]]:
    src = SRC.read_text()
    stroke = float(re.search(r"BRAND_MARK_STROKE\s*=\s*([\d.]+)", src).group(1))
    block = re.search(r"BRAND_MARK_PATHS\s*=\s*\[(.*?)\]", src, re.S).group(1)
    paths = re.findall(r'"([^"]+)"', block)
    if not paths:
        raise SystemExit("generate_brand_assets: no BRAND_MARK_PATHS parsed from cin.ui.jsx")
    return stroke, paths


def mark_group(stroke: float, paths: list[str], transform: str) -> str:
    inner = "\n    ".join(f'<path d="{d}"/>' for d in paths)
    return (
        f'<g transform="{transform}" fill="none" stroke="{ACCENT}" stroke-width="{stroke}" '
        f'stroke-linecap="round" stroke-linejoin="round">\n    {inner}\n  </g>'
    )


def main() -> None:
    stroke, paths = parse_mark()
    raw_paths = "".join(f'<path d="{d}"/>' for d in paths)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # 1. Measure the mark's geometric bbox (stroke excluded by getBBox).
        page = browser.new_page()
        page.set_content(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            f'<g id="m" fill="none" stroke-width="{stroke}">{raw_paths}</g></svg>'
        )
        bb = page.eval_on_selector("#m", "e=>{const b=e.getBBox();return{x:b.x,y:b.y,w:b.width,h:b.height}}")
        page.close()

        cx, cy = bb["x"] + bb["w"] / 2, bb["y"] + bb["h"] / 2
        vw, vh = bb["w"] + stroke, bb["h"] + stroke  # visual extents (add stroke)

        # 2. Icon transform: scale the mark's bbox to ICON_FILL_FRAC of 32, centered.
        s_i = (ICON_FILL_FRAC * 32) / max(vw, vh)
        tx_i, ty_i = 16 - s_i * cx, 16 - s_i * cy
        icon_tf = f"translate({tx_i:.3f} {ty_i:.3f}) scale({s_i:.4f})"

        # 3. Lockup transform: fixed visual height, left-aligned, vertically centered.
        s_l = LOCKUP_MARK_H / vh
        tx_l = 24 - s_l * bb["x"] + s_l * stroke / 2  # visual left edge → x=24
        ty_l = 133 - s_l * cy  # vertical center of the 266-tall canvas
        lockup_tf = f"translate({tx_l:.3f} {ty_l:.3f}) scale({s_l:.4f})"
        wordmark_x = 24 + s_l * (bb["w"] + stroke) + LOCKUP_GAP

        favicon_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">\n'
            f'  <rect width="32" height="32" rx="7" fill="{BG}"/>\n'
            f"  {mark_group(stroke, paths, icon_tf)}\n</svg>\n"
        )
        lockup_svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 266" fill="none" '
            'role="img" aria-label="SIGNAL.TRADE">\n'
            f"  {mark_group(stroke, paths, lockup_tf)}\n"
            f'  <text x="{wordmark_x:.1f}" y="134" dominant-baseline="central" text-anchor="start"\n'
            "        font-family=\"'JetBrains Mono','SFMono-Regular',ui-monospace,Menlo,Consolas,monospace\"\n"
            '        font-size="34" font-weight="700" letter-spacing="1">\n'
            f'    <tspan fill="{TEXT}">SIGNAL</tspan><tspan fill="{ACCENT}">.</tspan>'
            f'<tspan fill="{TEXT}">TRADE</tspan>\n  </text>\n</svg>\n'
        )
        (PUB / "favicon.svg").write_text(favicon_svg)
        (PUB / "logo-full.svg").write_text(lockup_svg)
        print("wrote favicon.svg, logo-full.svg")

        # 4. Rasterize PNGs from the freshly written SVGs.
        jobs = [
            (favicon_svg, 128, 128, "favicon.png", False),
            (favicon_svg, 256, 256, "logo-icon.png", False),
            (favicon_svg, 192, 192, "logo-icon-192.png", False),
            (favicon_svg, 512, 512, "logo-icon-512.png", False),
            (favicon_svg, 256, 256, "apple-touch-icon.png", False),
            (lockup_svg, 400, 266, "logo-full.png", True),
        ]
        for svg, w, h, out, transp in jobs:
            bg = "transparent" if transp else BG
            page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            page.set_content(
                f"<!doctype html><html><head><meta charset=utf-8><style>"
                f"html,body{{margin:0;padding:0;background:{bg}}}"
                f"svg{{display:block;width:{w}px;height:{h}px}}</style></head><body>{svg}</body></html>",
                wait_until="networkidle",
            )
            page.screenshot(
                path=str(PUB / out),
                omit_background=transp,
                clip={"x": 0, "y": 0, "width": w, "height": h},
            )
            page.close()
            print(f"wrote {out} ({w}x{h})")

        browser.close()
    print("done — brand assets regenerated from cin.ui.jsx")


if __name__ == "__main__":
    main()
