"""Render the profile header as Geist Mono outlines (SVG in <img> can't load web fonts).

usage: python scripts/build-header.py <GeistMono font dir>
"""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT_DIR = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent.parent / "assets"
X = 1  # left inset so the first stem isn't clipped

THEMES = {
    "dark": {"title": "#fafafa", "text": "#a3a3a3", "accent": "#22d3ee"},
    "light": {"title": "#0a0a0a", "text": "#525252", "accent": "#0891b2"},
}

LINES = [  # (text, weight, size, baseline, role)
    ("VesselWave", "Medium", 28, 30, "title"),
    ("Vlad Vasko", "Regular", 15, 58, "text"),
    ("websites and automations", "Regular", 15, 90, "text"),
    ("for small businesses", "Regular", 15, 112, "text"),
    ("Austin, TX", "Regular", 15, 134, "text"),
]
HEIGHT = 142

fonts = {w: TTFont(FONT_DIR / f"GeistMono-{w}.ttf") for w in ("Regular", "Medium")}


def outline(text, weight, size, baseline):
    font = fonts[weight]
    upm = font["head"].unitsPerEm
    glyphs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font["hmtx"]
    s = size / upm
    pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    x = 0
    for ch in text:
        name = cmap[ord(ch)]
        glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, X + x * s, baseline)))
        x += hmtx[name][0]
    return pen.getCommands(), X + x * s


def build(theme):
    c = THEMES[theme]
    paths, widths = [], []
    for text, weight, size, baseline, role in LINES:
        d, end = outline(text, weight, size, baseline)
        paths.append(f'<path fill="{c[role]}" d="{d}"/>')
        widths.append(end)
    title_end = widths[0]
    cursor_x = title_end + 5
    width = round(max(widths[1:] + [cursor_x + 12]) + 2)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{HEIGHT}" viewBox="0 0 {width} {HEIGHT}" role="img" aria-label="VesselWave. Vlad Vasko. Websites and automations for small businesses, Austin, TX.">
<style>
.cursor{{animation:blink 1.2s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.cursor{{animation:none}}}}
</style>
{chr(10).join(paths)}
<rect class="cursor" x="{cursor_x:.2f}" y="10" width="11" height="21" fill="{c["accent"]}"/>
</svg>
'''
    (OUT / f"header-{theme}.svg").write_text(svg)
    print(theme, width, "x", HEIGHT)


for t in THEMES:
    build(t)
