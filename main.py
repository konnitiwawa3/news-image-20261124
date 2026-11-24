"""Render the November 24 international edition as a deterministic RGB PNG."""

from pathlib import Path
import struct
import sys
import zlib

ASSET_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ASSET_DIR))

from illustrations import circuit_engraving, registration
from news import COLUMNS, FEATURES, LEAD
from printing import Font, Press

WIDTH = HEIGHT = 1024
MAX_BYTES = 1_048_576
PAPER = (255, 252, 247)
CREAM = (237, 228, 212)
INK = (28, 22, 16)
BROWN = (74, 53, 32)
OCHRE = (184, 136, 89)
RUST = (140, 58, 58)
BLUE = (58, 94, 140)
LEFT = 31
RIGHT = 993
COLUMN_STEP = 246
COLUMN_WIDTH = 224
ROW_HEIGHT = 57


def fit(font, value, width, size, max_lines, tracking=0):
    words = value.split()
    for point_size in range(size, size - 4, -1):
        if font.width(value, point_size, tracking) <= width:
            return (value,), point_size
        if max_lines != 2:
            continue
        candidates = []
        for cut in range(1, len(words)):
            lines = (' '.join(words[:cut]), ' '.join(words[cut:]))
            sizes = [font.width(line, point_size, tracking) for line in lines]
            if max(sizes) <= width:
                imbalance = abs(sizes[0] - sizes[1])
                candidates.append((imbalance + (point_size if cut == len(words) - 1 else 0), lines))
        if candidates:
            return min(candidates)[1], point_size
    raise ValueError(f'Text is too wide for its column: {value}')


class Edition:
    def __init__(self):
        self.press = Press(WIDTH, HEIGHT, PAPER)
        self.serif = Font(ASSET_DIR / 'fonts/newsreader.ttf')
        self.sans = Font(ASSET_DIR / 'fonts/plex-sans.ttf')

    def centered(self, font, text, y, size, color, tracking=0, bold=False, x=512):
        start = x - font.width(text, size, tracking) / 2
        font.print(self.press, text, start, y, size, color, tracking, bold)

    def right(self, font, text, y, size, color, tracking=0, x=RIGHT):
        start = x - font.width(text, size, tracking)
        font.print(self.press, text, start, y, size, color, tracking)

    def label(self, value, x, y, color=RUST, size=12, tracking=0.9):
        self.sans.print(self.press, value, x, y, size, color, tracking)

    def block(self, font, value, x, y, width, size, leading, color, tracking=0, bold=False):
        lines, point_size = fit(font, value, width, size, 2, tracking)
        for index, line in enumerate(lines):
            font.print(self.press, line, x, y + leading * index, point_size, color, tracking, bold)

    def masthead(self):
        self.press.rule(LEFT, 26, RIGHT - LEFT, BROWN, 2)
        registration(self.press, LEFT + 4, 51, BROWN, OCHRE)
        registration(self.press, RIGHT - 50, 51, BROWN, OCHRE)
        self.centered(self.serif, 'The World Ledger', 80, 71, INK, -1.5, True)
        self.press.rule(LEFT, 99, RIGHT - LEFT, BROWN)
        self.label('INTERNATIONAL EDITION', LEFT, 113, BROWN, 12, 1.25)
        self.centered(self.sans, 'TUESDAY, NOVEMBER 24, 2026', 114, 14, INK, 1.4)
        self.right(self.sans, 'ASIA MORNING EDITION', 113, 12, BROWN, 1.1)
        self.press.rule(LEFT, 122, RIGHT - LEFT, BROWN, 2)

    def hero(self):
        self.label('MARKETS  /  ASIA', LEFT + 2, 149, RUST, 13, 1.55)
        self.block(self.serif, LEAD.headline, LEFT, 210, 499, 69, 63, INK, -1, True)
        self.press.rule(LEFT + 3, 280, 78, OCHRE, 2)
        self.block(self.serif, LEAD.deck, LEFT + 3, 311, 450, 22, 25, BROWN)
        circuit_engraving(self.press, 541, 139, (CREAM, OCHRE, BROWN, BLUE))
        self.label('SEOUL  /  KOSPI OPENS NEARLY 6% HIGHER', 542, 361, BROWN, 12, 0.79)
        self.press.rule(LEFT, 373, RIGHT - LEFT, BROWN, 2)

    def features(self):
        for index, story in enumerate(FEATURES):
            x = LEFT + index * COLUMN_STEP
            self.label(story.place.upper(), x, 393, RUST, 13, 0.9)
            self.block(self.serif, story.headline, x, 420, COLUMN_WIDTH, 26, 24, INK, -0.25, True)
            self.block(self.sans, story.deck, x, 464, COLUMN_WIDTH, 14, 16, BROWN)
        self.press.rule(LEFT, 489, RIGHT - LEFT, BROWN)

    def briefs(self):
        for column, (subject, articles) in enumerate(COLUMNS):
            x = LEFT + column * COLUMN_STEP
            self.press.rect(x, 495, COLUMN_WIDTH, 21, CREAM, 204)
            self.press.rule(x, 495, COLUMN_WIDTH, OCHRE)
            self.label(subject, x + 6, 510, BROWN, 12, 0.74)
            if column:
                self.press.rect(x - 12, 388, 1, 585, OCHRE, 132)
            for row, story in enumerate(articles):
                y = 519 + ROW_HEIGHT * row
                self.label(story.place.upper(), x, y + 13, RUST, 11, 0.75)
                self.block(self.serif, story.headline, x, y + 32, COLUMN_WIDTH, 20, 18, INK, -0.12)
                if row < len(articles) - 1:
                    self.press.rect(x, y + ROW_HEIGHT - 1, COLUMN_WIDTH, 1, OCHRE, 155)

    def footer(self):
        self.press.rule(LEFT, 979, RIGHT - LEFT, BROWN, 2)
        stories = (LEAD,) + FEATURES + tuple(story for _, group in COLUMNS for story in group)
        regions = len({story.region for story in stories})
        self.label(f'{len(stories)} REPORTS FROM {regions} REGIONS', LEFT, 999, BROWN, 11, 1.1)
        self.right(self.sans, '24 NOV 2026  /  FRONT PAGE', 999, 11, BROWN, 1.1)

    def render(self):
        self.press.paper(OCHRE)
        self.masthead()
        self.hero()
        self.features()
        self.briefs()
        self.footer()
        return self.press.pixels


def png_chunk(kind, data):
    payload = kind + data
    return struct.pack('>I', len(data)) + payload + struct.pack('>I', zlib.crc32(payload))


def encode_png(pixels):
    stride = WIDTH * 3
    scanlines = bytearray()
    for offset in range(0, len(pixels), stride):
        row = pixels[offset:offset + stride]
        scanlines.append(1)
        scanlines.extend(row[:3])
        scanlines.extend((row[index] - row[index - 3]) & 255 for index in range(3, stride))
    header = struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    return b''.join((
        b'\x89PNG\r\n\x1a\n',
        png_chunk(b'IHDR', header),
        png_chunk(b'IDAT', zlib.compress(scanlines, 9)),
        png_chunk(b'IEND', b''),
    ))


def main():
    picture = encode_png(Edition().render())
    if len(picture) > MAX_BYTES:
        raise ValueError('The newspaper exceeds the PNG size limit')
    output = Path('/output/entry.png')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(picture)


if __name__ == '__main__':
    main()
