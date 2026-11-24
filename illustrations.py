"""An engraved conference table for the lead story."""

from math import isqrt
from random import Random


FRAME = (137, 104, 72)
PLATE = (220, 194, 151)
INK = (79, 59, 41)
SHADE = (157, 120, 83)
ACCENT = (148, 66, 46)
LIGHT = (237, 215, 173)
LAND = (170, 120, 79)


def conference_plate(page, left, top):
    width, height = 326, 223
    rng = Random(241126)

    def box(x, y, w, h, color):
        page.box(left + x, top + y, w, h, color)

    def line(x1, y1, x2, y2, color, weight=1):
        page.line(left + x1, top + y1, left + x2, top + y2, color, weight)

    def ellipse(x, y, rx, ry, color):
        page.ellipse(left + x, top + y, rx, ry, color)

    def polygon(points, color):
        page.polygon([(left + x, top + y) for x, y in points], color)

    box(0, 0, width, height, FRAME)
    box(2, 2, width - 4, height - 4, PLATE)

    # Worn edges and short hatch marks give the plate a printed margin.
    for _ in range(1350):
        x = rng.randrange(5, width - 5)
        y = rng.randrange(5, height - 5)
        distance = min(x, y, width - x, height - y)
        if distance < 28 or rng.randrange(6) == 0:
            span = rng.choice((1, 1, 2))
            box(x, y, span, 1, rng.choice((LIGHT, SHADE, PLATE)))
    for y in range(22, 145, 7):
        line(10, y, 65 + (y % 15), y - 3, LIGHT)
        line(257 - (y % 11), y + 2, 314, y, LIGHT)

    # Chair backs and the rims of an empty negotiating table.
    for x, y in ((45, 144), (86, 124), (251, 124), (285, 144)):
        ellipse(x, y, 15, 19, INK)
        ellipse(x, y - 2, 12, 16, SHADE)
        for offset in range(-7, 9, 4):
            line(x + offset, y - 10, x + offset + 1, y + 11, INK)
    ellipse(164, 169, 144, 37, INK)
    ellipse(164, 164, 144, 36, SHADE)
    ellipse(164, 161, 143, 31, INK)
    ellipse(164, 158, 139, 29, PLATE)
    for x in range(35, 298, 6):
        span = isqrt(max(0, 139 * 139 - (x - 164) ** 2))
        low = 161 + span * 27 // 139
        line(x, low, x - 1, low + 11, INK)

    # Globe, with graticule and two hemispheres in the engraving.
    ellipse(164, 143, 34, 6, INK)
    box(158, 107, 12, 35, INK)
    ellipse(164, 70, 56, 57, INK)
    ellipse(164, 70, 53, 54, LIGHT)
    polygon(((121, 42), (130, 31), (142, 32), (154, 39), (152, 47),
             (142, 49), (137, 58), (142, 66), (150, 72), (145, 74),
             (134, 69), (127, 56), (121, 53)), LAND)
    polygon(((146, 74), (159, 77), (166, 85), (160, 98), (155, 103),
             (153, 114), (149, 114), (148, 100), (142, 88)), LAND)
    polygon(((180, 37), (190, 36), (201, 44), (208, 53), (211, 64),
             (201, 62), (195, 57), (189, 59), (184, 55), (175, 56),
             (169, 50)), LAND)
    polygon(((173, 61), (182, 60), (194, 68), (188, 83), (181, 93),
             (177, 88), (176, 81), (169, 73)), LAND)
    polygon(((202, 93), (209, 91), (209, 101), (202, 106), (195, 103)), LAND)
    for y in range(23, 119):
        span = isqrt(max(0, 53 * 53 - (y - 70) ** 2))
        for factor in (-72, -35, 29, 69):
            x = 164 + span * factor // 100
            if (x + y) % 5:
                box(x, y, 1, 1, SHADE)
        if y in (44, 58, 72, 86, 100):
            for x in range(166 - span, 164 + span, 2):
                box(x, y + (x - 164) ** 2 // 1800, 1, 1, SHADE)
    for _ in range(235):
        x = rng.randrange(113, 215)
        y = rng.randrange(20, 121)
        if (x - 164) ** 2 + (y - 70) ** 2 < 51 ** 2:
            box(x, y, 1, 1, SHADE)

    # The interrupted manuscript is set on the near edge of the table.
    polygon(((122, 151), (189, 148), (212, 174), (138, 180)), LIGHT)
    line(126, 156, 190, 153, ACCENT, 2)
    for y in (161, 165, 169, 173):
        line(137, y + 3, 158, y + 2, SHADE)
        line(170, y, 195 + (y % 4), y - 2, SHADE)
    line(159, 150, 170, 158, INK, 2)
    line(170, 158, 163, 163, INK, 2)
    line(163, 163, 178, 175, INK, 2)
    for x in (68, 98, 234, 261):
        line(x - 1, 144, x + 8, 160, SHADE)
        line(x, 144, x + 10, 144, INK)
