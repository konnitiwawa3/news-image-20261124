"""Original copperplate-style press marks for the international edition."""

from printing import noise


def circuit_engraving(press, x, y, colors):
    cream, ochre, brown, blue = colors

    def point(p):
        return p[0] + x, p[1] + y

    def line(a, b, color=brown, weight=1, alpha=215):
        press.stroke(point(a), point(b), color, weight, alpha)

    def shape(vertices, color, alpha=255):
        press.polygon([point(vertex) for vertex in vertices], color, alpha)

    def frame(vertices, color=brown, alpha=180):
        for a, b in zip(vertices, vertices[1:] + vertices[:1]):
            line(a, b, color, 1.25, alpha)

    press.rect(x, y, 452, 204, cream, 218)
    for py in range(3, 201):
        for px in range(3, 449):
            fleck = noise(px, py, 51)
            if fleck % 13 == 0:
                press.dot(x + px, y + py, brown, 10 + fleck % 24)

    frame([(3, 5), (446, 4), (448, 198), (5, 200)], ochre)
    for gy in range(27, 174, 23):
        end = 426 + noise(gy, 1, 5) % 7
        line((22, gy + 1), (end, gy), ochre, 0.8, 93)
    for gx in range(46, 423, 32):
        line((gx + 1, 16), (gx, 185), brown, 0.72, 65)

    for start in range(-35, 460, 6):
        left = max(start, 19)
        right = min(start + 43, 432)
        if left < right:
            line((left, 185 - (left - start) * 0.3),
                 (right, 185 - (right - start) * 0.3), ochre, 0.72, 86)

    trend = [(22, 155), (65, 147), (104, 166), (131, 132), (179, 139),
             (203, 104), (246, 115), (288, 80), (324, 94), (361, 64),
             (389, 72), (428, 28)]
    for a, b in zip(trend, trend[1:]):
        line((a[0], a[1] + 2), (b[0], b[1] + 2), ochre, 3.2, 133)
        line(a, b, blue, 2.6, 220)
    shape([(415, 25), (433, 22), (431, 42), (427, 31)], blue, 244)

    board = [(91, 131), (246, 55), (365, 104), (208, 178)]
    shape([(91, 138), (208, 185), (365, 110), (365, 104), (208, 174), (91, 131)], brown, 219)
    shape(board, cream)
    frame(board, brown, 250)
    inside = [(103, 130), (246, 60), (352, 104), (207, 173)]
    frame(inside, blue, 173)

    for n in range(15):
        drift = (noise(n, 9, 4) % 3 - 1) * 0.65
        a = (111 + n * 6, 132 + n * 2.48)
        b = (144 + n * 6, 116 + n * 2.48 + drift)
        c = (259 + n * 5, 72 + n * 2.02)
        d = (232 + n * 5, 85 + n * 2.02)
        line(a, b, blue, 1.15, 206)
        line(c, d, brown, 1.05, 179)
        shape([(a[0] - 1, a[1]), (a[0], a[1] - 1), (a[0] + 1, a[1]), (a[0], a[1] + 1)], brown)

    top = [(148, 105), (242, 60), (314, 90), (221, 135)]
    side = [(148, 105), (221, 135), (314, 90), (314, 105), (221, 150), (148, 120)]
    shape(side, brown, 252)
    for n in range(24):
        a = (150 + n * 3, 108 + n * 1.22)
        line(a, (a[0], a[1] + 10), cream, 0.7, 137)
        b = (223 + n * 3.76, 138 - n * 1.81)
        line(b, (b[0], b[1] + 10), ochre, 0.75, 183)
    shape(top, blue, 248)
    frame(top, brown, 249)

    inset = [(168, 104), (241, 69), (293, 91), (222, 125)]
    frame(inset, cream, 221)
    die = [(189, 103), (240, 78), (274, 92), (223, 117)]
    shape(die, cream, 229)
    frame(die, brown, 197)
    for n in range(8):
        line((199 + n * 4.6, 103 + n * 1.85), (244 + n * 3.5, 81 + n * 1.45), brown, 0.64, 180)
    for a, b in [(0, 1), (1, 2), (2, 3), (3, 0)]:
        p, q = inset[a], inset[b]
        for n in range(1, 8):
            t = n / 8
            u = p[0] + (q[0] - p[0]) * t
            v = p[1] + (q[1] - p[1]) * t
            press.dot(round(x + u), round(y + v), cream, 241)

    for px, py in [(22, 24), (25, 180), (425, 182), (428, 26)]:
        line((px - 4, py), (px + 5, py), brown, 0.9, 166)
        line((px, py - 4), (px, py + 5), brown, 0.9, 158)


def registration(press, x, y, dark, light):
    for index in range(8):
        jitter = noise(x + index, y, 30) % 3 - 1
        start = (x + index * 5, y + jitter)
        finish = (start[0] + 10, y - 9 + jitter)
        press.stroke(start, finish, dark if index % 3 else light, 1.35, 190)
