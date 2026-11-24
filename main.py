"""Render the 24 November front page as a reproducible RGB PNG."""

from collections import Counter
from functools import lru_cache
from itertools import pairwise
import json
from math import cos, sin, tau
from os import environ
from pathlib import Path
from random import Random
from struct import pack
import sys
from zlib import compress, crc32, decompress

ASSET_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ASSET_DIR))
from illustrations import SCENES, Scene

SIDE = 1024
SUPERSAMPLE = 3
STRIDE = SIDE * SUPERSAMPLE
LEFT = 24
RIGHT = SIDE - LEFT
CONTENT = RIGHT - LEFT
REGION_INK = {
    "N. America": "purple",
    "Latin America": "ochre",
    "Europe": "blue",
    "Africa": "umber",
    "Middle East": "red",
    "South Asia": "plum",
    "East Asia": "green",
    "SE Asia": "teal",
    "Oceania": "slate",
}

# Editorial inks use Astryx Stone Light stops. Scene inks form a print palette.
SWATCHES = {
    "ink": "25252a", "muted": "5f5f64", "navy": "17263a", "rule": "848489",
    "hairline": "d4d3dd", "panel": "f0f0f7", "white": "ffffff",
    "blue": "344861", "red": "603c37", "umber": "5e3f27", "green": "2c4f44",
    "teal": "264d57", "purple": "4c405b", "ochre": "524818", "plum": "643c53",
    "slate": "394e60", "silver": "9aadb2", "water": "304c58", "wave": "6e868a",
    "pale_water": "a5b7b6", "mist": "e3ded0", "cloud": "bac1bd", "sky": "cdd0c2",
    "sand": "c7aa7f", "ridge": "9f866d", "stone": "8b8176", "coral": "a45e4d",
    "rust": "76443e", "coal": "37393b", "smoke": "6b6965", "cream": "f3ead7",
    "amber": "dba66d", "pine": "466257", "leaf": "81967e", "steel": "607479",
    "light_blue": "bccdd8", "clay": "976853", "dark_water": "263d4a",
}
INK_INDEX = {name: index for index, name in enumerate(SWATCHES, start=1)}
RGB = [(250, 248, 241)] + [tuple(bytes.fromhex(code)) for code in SWATCHES.values()]
GLYPH_ALIASES = str.maketrans("·−\u00a0", "|- ")
UNIT_CIRCLE = [(cos(i * tau / 32), sin(i * tau / 32)) for i in range(32)]
PAPER_TONES = tuple(tuple(channel + shift for channel in RGB[0]) for shift in (-1, 0, 1))


class Canvas:
    def __init__(self, fonts):
        self.pixels = bytearray(STRIDE * STRIDE)
        self.fonts = fonts

    def _span(self, y, left, right, paint):
        left = max(left, 0)
        right = min(right, STRIDE)
        if left < right:
            offset = y * STRIDE
            self.pixels[offset + left:offset + right] = paint * (right - left)

    def box(self, x, y, w, h, color):
        x0, x1 = round(x * SUPERSAMPLE), round((x + w) * SUPERSAMPLE)
        y0, y1 = round(y * SUPERSAMPLE), round((y + h) * SUPERSAMPLE)
        paint = bytes([INK_INDEX[color]])
        for sample_y in range(max(y0, 0), min(y1, STRIDE)):
            self._span(sample_y, x0, x1, paint)

    def line(self, points, color, weight=1):
        half = weight / 2
        for (x0, y0), (x1, y1) in pairwise(points):
            dx, dy = x1 - x0, y1 - y0
            segments = max(1, round(max(abs(dx), abs(dy)) * SUPERSAMPLE))
            for step in range(segments + 1):
                t = step / segments
                self.box(x0 + dx * t - half, y0 + dy * t - half, weight, weight, color)

    def polygon(self, points, color):
        vertices = [(x * SUPERSAMPLE, y * SUPERSAMPLE) for x, y in points]
        edges = tuple(pairwise([*vertices, vertices[0]]))
        first = max(0, int(min(point[1] for point in vertices)))
        last = min(STRIDE, round(max(point[1] for point in vertices)))
        paint = bytes([INK_INDEX[color]])
        for row in range(first, last):
            level = row + .5
            intersections = []
            for (x0, y0), (x1, y1) in edges:
                if min(y0, y1) <= level < max(y0, y1):
                    intersections.append(x0 + (x1 - x0) * (level - y0) / (y1 - y0))
            crossings = iter(sorted(intersections))
            for left, right in zip(crossings, crossings, strict=True):
                self._span(row, round(left), round(right), paint)

    def oval(self, x, y, w, h, color):
        self.polygon([(x + w / 2 * (1 + cx), y + h / 2 * (1 + cy))
                      for cx, cy in UNIT_CIRCLE], color)

    def rule(self, x, y, width, color="hairline", thickness=.8):
        self.box(x, y, width, thickness, color)

    def frame(self, x, y, width, height):
        for edge in (y, y + height):
            self.rule(x, edge, width, "rule")
        for edge in (x, x + width - .8):
            self.box(edge, y, .8, height, "rule")

    @lru_cache(maxsize=3600)
    def _mask(self, face, letter, size):
        _, dx, dy, width, height, encoded = self.fonts[face][letter]
        if not width or not height:
            return ()
        stride = (width + 7) // 8
        data = bytes.fromhex(encoded)
        offset_x, offset_y = round(dx * size), round(dy * size)
        columns = [min(width - 1, int(x / size)) for x in range(round(width * size))]
        dots = []
        for y in range(round(height * size)):
            row = min(height - 1, int(y / size)) * stride
            for x, source_x in enumerate(columns):
                if data[row + source_x // 8] & (0x80 >> (source_x % 8)):
                    dots.append((offset_x + x, offset_y + y))
        return tuple(dots)

    def measure(self, value, face, size):
        alphabet = self.fonts[face]
        advances = (round(alphabet[letter][0] * size) for letter in value.translate(GLYPH_ALIASES))
        return sum(advances) / SUPERSAMPLE

    def text(self, value, x, y, *, face="sans11", size=1, color="ink", align=0, width=None):
        value = value.translate(GLYPH_ALIASES)
        if width is not None:
            while self.measure(value, face, size) > width:
                size -= .01
                if size < .5:
                    raise ValueError(f"Cannot fit text into {width}px: {value}")
        pen = round((x - align * self.measure(value, face, size)) * SUPERSAMPLE)
        baseline = round(y * SUPERSAMPLE)
        paint = INK_INDEX[color]
        for letter in value:
            for dx, dy in self._mask(face, letter, size):
                px, py = pen + dx, baseline + dy
                if 0 <= px < STRIDE and 0 <= py < STRIDE:
                    self.pixels[py * STRIDE + px] = paint
            pen += round(self.fonts[face][letter][0] * size)

    def _wrap(self, value, width, face, size):
        first, *rest = value.split()
        lines = [first]
        for word in rest:
            trial = " ".join((lines[-1], word))
            if self.measure(trial, face, size) > width:
                lines.append(word)
            else:
                lines[-1] = trial
        return lines

    def paragraph(self, value, x, y, width, *, face, size, leading, rows, color="muted"):
        lines = self._wrap(value, width, face, size)
        while len(lines) > rows and size > .65:
            size -= .02
            lines = self._wrap(value, width, face, size)
        if len(lines) > rows:
            raise ValueError(f"Cannot fit text into {rows} lines: {value}")
        for index, line in enumerate(lines):
            self.text(line, x, y + index * leading, face=face, size=size, color=color, width=width)


def flag(canvas, issue):
    canvas.rule(LEFT, 18, CONTENT, "navy", 2)
    canvas.text("THE WORLD DISPATCH", LEFT, 60, face="display55", size=.84, color="navy")
    canvas.text(issue["date"], RIGHT, 48, align=1, face="display27", size=1.01, color="navy")
    edition_line = f"TUESDAY  /  WORLD NEWS  /  THROUGH {issue['cutoff']}"
    canvas.text(edition_line, RIGHT, 66, align=1, size=1.08, color="muted")
    totals = Counter(article["region"] for article in issue["stories"])
    slot = CONTENT / len(REGION_INK)
    for index, (region, ink) in enumerate(REGION_INK.items()):
        left = LEFT + index * slot
        canvas.rule(left, 81, slot - 8, ink, 2)
        canvas.text(f"{region.upper()} {totals[region]:02}", left, 98,
                    width=slot - 9, color=ink, size=1.08)


def credit(article):
    return f"{article['place']}  /  {article['source']}"


def image(canvas, article, left, top, width, height):
    scene = Scene(canvas, left, top, width, height)
    SCENES[article["scene"]](scene)


def opening_moves(canvas, article, left, top, width):
    canvas.box(left, top, width, 56, "panel")
    canvas.text("INDEX MOVES AT THE OPEN", left + 8, top + 14, color="muted", size=.91)
    slot = width / len(article["opening_moves"])
    for index, (label, change, _) in enumerate(article["opening_moves"]):
        x = left + index * slot + 8
        canvas.text(label, x, top + 29, color="teal", size=.90)
        canvas.text(f"+{change:.1f}%", x, top + 48, face="display22", size=.89, color="navy")
        if index:
            canvas.box(x - 8, top + 22, .65, 29, "hairline")


def lead_story(canvas, article):
    width = 648
    ink = REGION_INK[article["region"]]
    canvas.text(article["place"], LEFT, 129, color=ink, size=1.42)
    canvas.text(article["source"], LEFT + width, 129, align=1, color=ink, size=1.14)
    for baseline, line in zip((185, 240), article["lines"], strict=True):
        canvas.text(line, LEFT, baseline, face="display55", size=1.10,
                    width=width, color="navy")
    image(canvas, article, LEFT, 253, width, 164)
    canvas.box(LEFT, 397, width, 20, "dark_water")
    canvas.text(article["caption"], LEFT + 8, 412, color="white", size=1.02)
    canvas.paragraph(article["detail"], LEFT, 438, width, face="sans13",
                     size=1.29, leading=18, rows=2, color="ink")


def secondary_stories(canvas, articles):
    left, width = 692, RIGHT - 692
    canvas.box(left - 12, 113, .85, 345, "hairline")
    for top, article in zip((118, 290), articles, strict=True):
        ink = REGION_INK[article["region"]]
        canvas.text(credit(article), left, top + 10, color=ink, size=1.00, width=width)
        canvas.paragraph(article["title"], left, top + 36, width, face="display27",
                         size=1.01, leading=24, rows=2, color="navy")
        if "opening_moves" in article:
            opening_moves(canvas, article, left, top + 67, width)
        else:
            image(canvas, article, left, top + 67, width, 56)
        canvas.paragraph(article["detail"], left, top + 140, width, face="sans13",
                         size=.97, leading=14, rows=2, color="ink")
        if top < 200:
            canvas.rule(left, top + 164, width, "hairline")


def section_label(canvas, top, label, legend):
    canvas.rule(LEFT, top, CONTENT, "navy", 1.4)
    canvas.text(label, LEFT, top + 18, color="navy", size=1.22)
    canvas.text(legend, RIGHT, top + 18, align=1, color="muted", size=.92)


def dispatches(canvas, articles):
    section_label(canvas, 470, "WORLD REPORT", "24 NOVEMBER  /  EARLY EDITION")
    gap = 12
    width = (CONTENT - 3 * gap) / 4
    for index, article in enumerate(articles):
        row, column = divmod(index, 4)
        left, top = LEFT + column * (width + gap), 493 + row * 93
        ink = REGION_INK[article["region"]]
        if column:
            canvas.box(left - 6, top + 1, .6, 83, "hairline")
        if row:
            canvas.rule(left, top - 4, width, "hairline")
        canvas.text(credit(article), left, top + 10, color=ink, width=width, size=.95)
        canvas.paragraph(article["title"], left, top + 30, width, face="display22",
                         size=.93, leading=18, rows=2, color="navy")
        if "scene" in article:
            image(canvas, article, left + width - 64, top + 47, 64, 36)
            width_for_detail = width - 72
        else:
            width_for_detail = width
        canvas.paragraph(article["detail"], left, top + 60, width_for_detail,
                         face="sans13", size=.86, leading=12, rows=3, color="ink")


def briefs(canvas, articles):
    section_label(canvas, 680, "IN BRIEF", "TODAY MARKS SCHEDULED ITEMS")
    gap, columns, rows = 16, 3, 9
    width = (CONTENT - (columns - 1) * gap) / columns
    if len(articles) > columns * rows:
        raise ValueError("The brief section can hold up to 27 reports.")
    for index, article in enumerate(articles):
        column, row = divmod(index, rows)
        left, top = LEFT + column * (width + gap), 705 + row * 32
        ink = REGION_INK[article["region"]]
        canvas.box(left, top + 3, 2, 22, ink)
        state = "  /  TODAY" if article.get("agenda") else ""
        canvas.text(credit(article) + state, left + 7, top + 10,
                    color=ink, size=.94, width=width - 8)
        canvas.text(article["title"], left + 7, top + 24, face="sans13",
                    size=1.06, color="ink", width=width - 9)
        if row < rows - 1:
            canvas.rule(left, top + 30, width, "hairline", .55)


def typeset(issue, fonts):
    canvas = Canvas(fonts)
    stories = issue["stories"]
    if len(stories) < 35 or set(REGION_INK) != {article["region"] for article in stories}:
        raise ValueError("The front page requires at least 35 stories across all nine regions.")
    flag(canvas, issue)
    lead_story(canvas, stories[0])
    secondary_stories(canvas, stories[1:3])
    dispatches(canvas, stories[3:11])
    briefs(canvas, stories[11:])
    canvas.rule(LEFT, 997, CONTENT, "navy", 1.4)
    scheduled = sum(bool(article.get("agenda")) for article in stories)
    total = f"{len(stories) - scheduled} REPORTS  /  {scheduled} ON THE AGENDA  /  {len(REGION_INK)} REGIONS"
    canvas.text(total, LEFT, 1011,
                color="navy", size=.93)
    canvas.text("THE WORLD DISPATCH  /  24 NOV 2026", RIGHT, 1011, align=1,
                color="muted", size=.93)
    return canvas.pixels


def encode_rows(samples):
    grain = iter(Random(24112026).randbytes(SIDE * SIDE))
    scanlines = bytearray()
    for row in range(SIDE):
        top = row * SUPERSAMPLE * STRIDE
        previous = (0, 0, 0)
        scanlines.append(1)  # PNG Sub filter.
        for offset in range(top, top + STRIDE, SUPERSAMPLE):
            middle, bottom = offset + STRIDE, offset + 2 * STRIDE
            block = samples[offset:offset + 3] + samples[middle:middle + 3] + samples[bottom:bottom + 3]
            texture = next(grain) % 3
            ink = block[0]
            if block.count(ink) == len(block):
                color = RGB[ink] if ink else PAPER_TONES[texture]
            else:
                shift = texture - 1 if 0 in block else 0
                components = zip(*(RGB[index] for index in block))
                color = tuple(max(0, min(255, sum(values) // 9 + shift)) for values in components)
            scanlines.extend((channel - prior) & 255 for channel, prior in zip(color, previous))
            previous = color
    return scanlines


def png_chunk(tag, payload):
    body = tag + payload
    return pack(">I", len(payload)) + body + pack(">I", crc32(body))


def main():
    issue = json.loads((ASSET_DIR / "edition.json").read_text(encoding="utf-8"))
    fonts = json.loads(decompress((ASSET_DIR / "materials" / "glyphs.json.z").read_bytes()))
    header = pack(">IIBBBBB", SIDE, SIDE, 8, 2, 0, 0, 0)
    scanlines = encode_rows(typeset(issue, fonts))
    png = b"\x89PNG\r\n\x1a\n" + b"".join((
        png_chunk(b"IHDR", header),
        png_chunk(b"IDAT", compress(scanlines, 9)),
        png_chunk(b"IEND", b""),
    ))
    if len(png) > 1024 * 1024:
        raise ValueError("The finished page exceeds the 1 MiB output limit.")
    folder = Path(environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "entry.png").write_bytes(png)


if __name__ == "__main__":
    main()
