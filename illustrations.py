"""Spot illustrations in the edition's 100-by-60 drawing coordinates."""

from random import Random


class Scene:
    def __init__(self, canvas, left, top, width, height):
        self.canvas = canvas
        self.left, self.top = left, top
        self.width, self.height = width, height

    def point(self, x, y):
        return self.left + x * self.width / 100, self.top + y * self.height / 60

    def rect(self, ink, x, y, width, height):
        left, top = self.point(x, y)
        self.canvas.box(left, top, width * self.width / 100, height * self.height / 60, ink)

    def ellipse(self, ink, x, y, width, height):
        left, top = self.point(x, y)
        self.canvas.oval(left, top, width * self.width / 100, height * self.height / 60, ink)

    def fill(self, ink, *coordinates):
        points = iter(coordinates)
        self.canvas.polygon([self.point(x, y) for x, y in zip(points, points, strict=True)], ink)

    def stroke(self, ink, weight, *coordinates):
        points = iter(coordinates)
        self.canvas.line([self.point(x, y) for x, y in zip(points, points, strict=True)], ink, weight)

    def horizon(self, edge, above, below):
        self.rect(above, 0, 0, 100, 60)
        self.rect(below, 0, edge, 100, 60 - edge)

    def stipple(self, ink, seed, count, band, longest=3):
        random = Random(seed)
        for _ in range(count):
            x = random.uniform(1, 97)
            y = random.uniform(*band)
            end = min(99, x + random.uniform(.6, longest))
            self.stroke(ink, .46, x, y, end, y - .3)


def tanker(view, x, y, width, height):
    def point(horizontal, vertical):
        return x + horizontal * width, y + vertical * height

    def hull(ink, *coords):
        pairs = iter(coords)
        view.fill(ink, *(coordinate for a, b in zip(pairs, pairs, strict=True)
                         for coordinate in point(a, b)))

    hull("dark_water", 0, .56, .13, .42, .89, .34, 1, .46, .93, .85, .12, 1)
    hull("rust", .01, .57, .12, .76, .94, .61, .93, .85, .12, 1)
    hull("coal", 0, .55, .13, .38, .89, .28, 1, .45, .91, .61, .11, .76)
    hull("stone", .09, .54, .17, .43, .89, .34, .96, .45, .17, .69)
    hull("steel", .22, .47, .85, .39, .88, .48, .22, .61)
    for fraction in (.30, .43, .56, .69, .82):
        a, b = point(fraction, .46 - fraction * .08)
        c, d = point(fraction, .60 - fraction * .13)
        view.stroke("coal", .7, a, b, c, d)
    hull("mist", .16, .54, .16, .13, .28, .09, .33, .20, .33, .52)
    hull("silver", .28, .09, .33, .20, .33, .52, .28, .56)
    a, b = point(.18, .22)
    c, d = point(.27, .19)
    view.stroke("dark_water", 1.05, a, b, c, d)
    a, b = point(.24, .09)
    c, d = point(.24, -.20)
    view.stroke("coal", .75, a, b, c, d)


def hormuz(view):
    view.horizon(25, "sky", "water")
    view.ellipse("cream", 72, 3, 10, 29)
    view.fill("cloud", 0, 7, 15, 8, 25, 13, 46, 13, 63, 17, 0, 17)
    view.fill("mist", 0, 16, 30, 16, 52, 21, 85, 16, 100, 16, 100, 25, 0, 27)
    view.fill("ridge", 0, 26, 11, 16, 20, 17, 24, 14, 36, 25, 42, 27, 0, 34)
    view.fill("sand", 0, 27, 9, 18, 14, 19, 23, 21, 30, 26, 36, 29, 26, 32, 0, 38)
    view.fill("stone", 0, 31, 9, 27, 15, 26, 26, 31, 20, 35, 0, 40)
    view.fill("ridge", 76, 28, 88, 19, 94, 18, 100, 12, 100, 34)
    view.fill("sand", 79, 28, 88, 25, 95, 26, 100, 23, 100, 33)
    view.fill("dark_water", 0, 44, 19, 39, 53, 45, 100, 40, 100, 60, 0, 60)
    view.fill("water", 0, 50, 40, 48, 76, 55, 100, 45, 100, 60, 0, 60)
    view.stipple("wave", 501, 280, (34, 59), 4)
    view.stipple("pale_water", 85, 133, (30, 57), 3)

    # Schematic vessel positions express the reported scale, without claiming locations.
    for x, y, w, h in ((72, 32, 15, 5), (52, 34, 18, 7)):
        tanker(view, x, y, w, h)
    for px, py, w, h, ink in (
        (54, 39, 8, 10, "smoke"), (56, 33, 8, 12, "smoke"),
        (59, 27, 10, 13, "smoke"), (63, 21, 13, 14, "smoke"),
        (67, 17, 13, 13, "cloud"), (72, 14, 17, 13, "cloud"),
        (78, 13, 15, 9, "cloud"), (53, 43, 6, 7, "rust"),
    ):
        view.ellipse(ink, px, py, w, h)
    view.fill("amber", 54, 50, 56, 43, 57, 47, 59, 44, 60, 51)
    view.stroke("pale_water", 1.2, 8, 56, 18, 55, 34, 54, 54, 50, 67, 48)
    tanker(view, 16, 37, 52, 16)
    view.stroke("pale_water", .7, 9, 55, 16, 55, 23, 54)
    view.stroke("mist", .8, 19, 56, 31, 55, 43, 54)


def maritime_skyline(view):
    view.horizon(48, "sky", "water")
    view.ellipse("cream", 69, 8, 15, 23)
    for x, width, height in ((2, 8, 22), (13, 8, 31), (25, 6, 20), (50, 7, 24),
                              (69, 9, 19), (83, 7, 30), (92, 6, 23)):
        view.rect("steel", x, 48 - height, width, height)
        view.stroke("light_blue", .6, x + 2, 50 - height, x + 2, 46)
    for x, top in ((34, 26), (40, 23), (46, 27)):
        view.fill("dark_water", x, 48, x + 1.5, top, x + 5, top, x + 4.5, 48)
    view.fill("cream", 30, 24, 38, 20, 55, 22, 53, 26, 33, 28)
    view.stroke("dark_water", 1, 31, 26, 46, 25, 54, 22)
    view.stipple("pale_water", 71, 73, (49, 58), 5)


def briefing(view):
    view.horizon(34, "mist", "slate")
    for x in range(4, 100, 13):
        view.rect("sky", x, 1, 11, 31)
        view.stroke("ridge", .55, x + 1, 2, x + 1, 33)
    view.fill("stone", 0, 43, 33, 28, 69, 28, 100, 43, 82, 60, 18, 60)
    view.fill("sand", 6, 45, 33, 31, 67, 31, 93, 45, 81, 57, 19, 57)
    for x, y in ((25, 22), (41, 18), (59, 18), (75, 22), (20, 40), (80, 40)):
        view.ellipse("coal", x - 4, y - 5, 8, 12)
        view.ellipse("navy", x - 7, y + 5, 14, 10)
    for x in (32, 49, 67):
        view.fill("cream", x, 42, x + 5, 40, x + 9, 45, x + 4, 48)


def airspace(view):
    view.horizon(41, "light_blue", "steel")
    view.fill("pine", 0, 42, 12, 27, 22, 31, 29, 27, 36, 40, 53, 43, 0, 52)
    view.stipple("pale_water", 14, 72, (44, 60))
    view.stroke("mist", 1.0, 2, 39, 24, 35, 39, 28, 69, 18)
    view.fill("navy", 38, 29, 58, 25, 70, 19, 77, 18, 82, 20, 72, 23,
              65, 28, 68, 33, 64, 35, 54, 30, 45, 33)
    view.stroke("mist", .7, 54, 28, 73, 21, 79, 20)


def rainfall(view):
    view.horizon(35, "cloud", "pine")
    view.fill("leaf", 0, 42, 18, 27, 34, 37, 53, 23, 67, 34, 84, 25, 100, 39, 100, 60, 0, 60)
    view.fill("pine", 0, 54, 27, 39, 50, 53, 76, 40, 100, 46, 100, 60, 0, 60)
    view.fill("pale_water", 74, 40, 81, 44, 67, 49, 67, 52, 82, 57, 78, 60, 56, 54, 57, 49)
    for x in range(2, 100, 5):
        height = 9 + (x * 5) % 20
        view.stroke("mist", .6, x, height, x - 2, height + 12)


def supplies(view):
    view.horizon(34, "mist", "ridge")
    view.rect("stone", 1, 6, 98, 20)
    view.rect("light_blue", 32, 7, 36, 17)
    for x, y, w, h in ((8, 36, 24, 17), (30, 29, 27, 23), (54, 39, 36, 14)):
        view.rect("sand", x, y, w, h)
        view.fill("cream", x, y, x + w, y, x + w - 4, y - 4, x + 3, y - 4)
        view.rect("ridge", x + w * .44, y, w * .19, h)
    view.stroke("rust", 2, 49, 12, 49, 20)
    view.stroke("rust", 2, 44, 16, 54, 16)


def parliament(view):
    view.horizon(46, "light_blue", "stone")
    view.fill("cream", 8, 25, 50, 7, 92, 25)
    view.rect("sand", 11, 25, 78, 22)
    view.rect("ridge", 16, 28, 68, 18)
    for x in (19, 31, 43, 55, 67, 79):
        view.rect("mist", x, 26, 4, 20)
    for y in (45, 49, 53):
        view.rect("cream", 12 - (y - 45) / 2, y, 76 + (y - 45), 1)


SCENES = {
    "hormuz": hormuz,
    "singapore": maritime_skyline,
    "briefing": briefing,
    "airspace": airspace,
    "rain": rainfall,
    "supplies": supplies,
    "parliament": parliament,
}
