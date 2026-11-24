"""Set and print the 24 November 2026 issue of The World Ledger."""

from math import isqrt
from pathlib import Path
from random import Random
import struct
import sys
import zlib


ASSET_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ASSET_DIR))

from illustrations import conference_plate
from stories import DESKS, ISSUE_DATE, LEAD
from typeface import measure, print_type


SIZE = 1024
EDGE = 33
RIGHT = SIZE - EDGE
INK = (40, 32, 26)
BODY = (58, 46, 36)
MUTED = (92, 71, 51)
RUST = (125, 53, 37)
RULE = (125, 95, 67)
PAPER = (241, 228, 199)


class Page:
    def __init__(self):
        self.pixels = bytearray(bytes(PAPER) * SIZE * SIZE)

    def box(self, x, y, width, height, color):
        left, right = max(0, x), min(SIZE, x + width)
        top, bottom = max(0, y), min(SIZE, y + height)
        if left >= right or top >= bottom:
            return
        stripe = bytes(color) * (right - left)
        for row in range(top, bottom):
            start = 3 * (row * SIZE + left)
            self.pixels[start:start + len(stripe)] = stripe

    def ink(self, x, y, color, opacity):
        if not (0 <= x < SIZE and 0 <= y < SIZE):
            return
        index = 3 * (y * SIZE + x)
        for channel, value in enumerate(color):
            old = self.pixels[index + channel]
            self.pixels[index + channel] = (old * (255 - opacity) + value * opacity) // 255

    def line(self, x1, y1, x2, y2, color, width=1):
        dx, dy = abs(x2 - x1), -abs(y2 - y1)
        step_x = 1 if x1 < x2 else -1
        step_y = 1 if y1 < y2 else -1
        error = dx + dy
        while True:
            self.box(x1, y1, width, width, color)
            if x1 == x2 and y1 == y2:
                break
            change = 2 * error
            if change >= dy:
                error += dy
                x1 += step_x
            if change <= dx:
                error += dx
                y1 += step_y

    def ellipse(self, x, y, rx, ry, color):
        for row in range(-ry, ry + 1):
            half = isqrt(rx * rx * (ry * ry - row * row)) // ry
            self.box(x - half, y + row, half * 2 + 1, 1, color)

    def polygon(self, points, color):
        edges = tuple(zip(points, points[1:] + points[:1]))
        for y in range(min(y for _, y in points), max(y for _, y in points) + 1):
            changes = []
            for (x1, y1), (x2, y2) in edges:
                if min(y1, y2) <= y < max(y1, y2):
                    changes.append(x1 + (y - y1) * (x2 - x1) // (y2 - y1))
            changes.sort()
            for left, right in zip(changes[::2], changes[1::2]):
                self.box(left, y, right - left + 1, 1, color)

    def png(self):
        stride = 3 * SIZE
        scanlines = bytearray()
        for offset in range(0, len(self.pixels), stride):
            row = self.pixels[offset:offset + stride]
            scanlines.append(1)
            scanlines.extend(row[:3])
            scanlines.extend(
                (channel - row[index]) & 255
                for index, channel in enumerate(row[3:])
            )

        def chunk(tag, data):
            return (
                struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', zlib.crc32(tag + data))
            )

        return b'\x89PNG\r\n\x1a\n' + b''.join((
            chunk(b'IHDR', struct.pack('>IIBBBBB', SIZE, SIZE, 8, 2, 0, 0, 0)),
            chunk(b'IDAT', zlib.compress(scanlines, 9)),
            chunk(b'IEND', b''),
        ))


def aged_paper(page):
    rng = Random(20261124)
    for y in range(0, SIZE, 8):
        for x in range(0, SIZE, 8):
            edge = min(x, SIZE - x - 8, y, SIZE - y - 8)
            corner = (x + 14) ** 2 + (y - 962) ** 2
            cloud = (x - 902) ** 2 + (y + 153) ** 2
            age = (6 if corner < 340 ** 2 else 0) + (4 if cloud < 370 ** 2 else 0)
            shade = age + max(0, 15 - edge) // 3 + rng.choice((0, 0, 1, 2, 3))
            tone = tuple(channel - shade for channel in PAPER)
            page.box(x, y, 8, 8, tone)
    for _ in range(9700):
        x = rng.randrange(SIZE)
        y = rng.randrange(SIZE)
        grain = rng.choice(((231, 214, 184), (226, 207, 173), (245, 232, 207)))
        page.box(x, y, rng.choice((1, 1, 1, 2)), 1, grain)
    for x, y in ((4, 366), (1013, 217), (13, 938), (996, 1018), (181, 4)):
        for _ in range(54):
            dx = rng.randrange(-15, 16)
            dy = rng.randrange(-9, 10)
            if 3 * abs(dx) + 5 * abs(dy) < 61:
                page.ink(x + dx, y + dy, RULE, rng.randrange(22, 100))
    for x, y in ((5, 24), (13, 1019), (1007, 1005)):
        page.line(x, y, x + 12, y - 7, (224, 202, 167))
        page.line(x + 2, y + 1, x + 12, y - 4, (232, 216, 185))


def press_rule(page, start, end, y, color=RULE, weight=1):
    x = start
    while x < end:
        span = min(26 + (x * 11 + y) % 30, end - x)
        shift = int((x + y * 3) % 11 == 0)
        page.box(x, y + shift, span, weight, color)
        x += span + int((x ^ y) % 7 == 0)


def centered(page, text, y, size, color, strong=False, width_scale=0.8):
    width = measure(text, size, width_scale)
    print_type(page, (SIZE - width) // 2, y, text, size, color,
               strong=strong, width_scale=width_scale)


def masthead(page):
    press_rule(page, EDGE, RIGHT, 20, INK, 2)
    print_type(page, EDGE, 28, ISSUE_DATE.upper(), 14, INK, strong=True)
    edition = 'WORLD EDITION'
    edition_x = RIGHT - measure(edition, 14)
    print_type(page, edition_x, 28, edition, 14, RUST, strong=True)
    press_rule(page, EDGE, RIGHT, 48)
    centered(page, 'THE WORLD LEDGER', 57, 62, INK, strong=True, width_scale=0.88)
    press_rule(page, EDGE, RIGHT, 126, INK, 3)
    press_rule(page, EDGE, RIGHT, 132)


def front_story(page):
    first, second, deck, _ = LEAD
    print_type(page, EDGE + 2, 149, 'CLIMATE & DIPLOMACY', 15, RUST, strong=True)
    print_type(page, EDGE, 173, first, 54, INK, strong=True, limit=600)
    print_type(page, EDGE, 234, second, 54, INK, strong=True, limit=600)
    for y, row in zip((308, 332, 356), deck):
        print_type(page, EDGE + 2, y, row, 19, BODY, limit=600)
    conference_plate(page, 665, 145)
    press_rule(page, EDGE, RIGHT, 388, INK, 3)
    press_rule(page, EDGE, RIGHT, 393)


def world_pages(page):
    column_width = 302
    column_pitch = 326
    row_pitch = 195
    grid_top = 402
    for index, (region, articles) in enumerate(DESKS):
        column, row = index % 3, index // 3
        left = EDGE + column * column_pitch
        top = grid_top + row * row_pitch
        print_type(page, left, top + 2, region.upper(), 17, RUST,
                   strong=True, limit=column_width)
        press_rule(page, left, left + column_width, top + 23)
        for article, (headline, deck, _) in enumerate(articles):
            y = top + 31 + article * 39
            print_type(page, left, y, headline, 16, INK,
                       strong=True, limit=column_width)
            print_type(page, left, y + 21, deck, 12, BODY, limit=column_width)
            if article < len(articles) - 1:
                press_rule(page, left, left + column_width, y + 37, (165, 136, 106))
        if row < 2:
            press_rule(page, left, left + column_width, top + 185, RULE, 2)
    for x in (347, 673):
        page.line(x, grid_top, x + 1, 985, RULE)


def make_page():
    page = Page()
    aged_paper(page)
    masthead(page)
    front_story(page)
    world_pages(page)
    press_rule(page, EDGE, RIGHT, 987, INK, 2)
    press_rule(page, EDGE, RIGHT, 994, RULE)
    return page


if __name__ == '__main__':
    output = Path(sys.argv[1] if len(sys.argv) > 1 else '/output/entry.png')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(make_page().png())
