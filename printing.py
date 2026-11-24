"""A small raster press and an outline reader for the two newspaper typefaces."""

from functools import lru_cache
from math import ceil, floor
import struct


def u16(data, offset):
    return struct.unpack_from('>H', data, offset)[0]


def i16(data, offset):
    return struct.unpack_from('>h', data, offset)[0]


def u32(data, offset):
    return struct.unpack_from('>I', data, offset)[0]


def noise(x, y, salt=0):
    value = ((x * 374761393) ^ (y * 668265263) ^ (salt * 2246822519)) & 0xFFFFFFFF
    value = ((value ^ (value >> 13)) * 1274126177) & 0xFFFFFFFF
    return value ^ (value >> 16)


class Press:
    def __init__(self, width, height, paper):
        self.width = width
        self.height = height
        self.pixels = bytearray(bytes(paper) * (width * height))

    def dot(self, x, y, color, alpha=255):
        if not (0 <= x < self.width and 0 <= y < self.height) or alpha == 0:
            return
        offset = 3 * (self.width * y + x)
        if alpha == 255:
            self.pixels[offset:offset + 3] = bytes(color)
            return
        for channel in range(3):
            base = self.pixels[offset + channel]
            self.pixels[offset + channel] = base + ((color[channel] - base) * alpha + 127) // 255

    def rect(self, x, y, width, height, color, alpha=255):
        left, right = max(0, x), min(self.width, x + width)
        top, bottom = max(0, y), min(self.height, y + height)
        if right <= left or bottom <= top:
            return
        if alpha == 255:
            row = bytes(color) * (right - left)
            for py in range(top, bottom):
                start = (py * self.width + left) * 3
                self.pixels[start:start + len(row)] = row
        else:
            for py in range(top, bottom):
                for px in range(left, right):
                    self.dot(px, py, color, alpha)

    def polygon(self, points, color, alpha=255):
        edges = list(zip(points, points[1:] + points[:1]))
        low = max(0, floor(min(y for _, y in points)))
        high = min(self.height, ceil(max(y for _, y in points)))
        for y in range(low, high):
            spans = crossings(edges, y + 0.5)
            for left, right in zip(spans[::2], spans[1::2]):
                start, stop = floor(left), ceil(right)
                for x in range(start, stop):
                    coverage = min(x + 1, right) - max(x, left)
                    self.dot(x, y, color, round(alpha * coverage))

    def stroke(self, a, b, color, weight=1, alpha=255):
        x, y = a
        u, v = b
        distance = max(1, ((u - x) ** 2 + (v - y) ** 2) ** 0.5)
        dx = (y - v) * weight / (2 * distance)
        dy = (u - x) * weight / (2 * distance)
        self.polygon([(x + dx, y + dy), (u + dx, v + dy),
                      (u - dx, v - dy), (x - dx, y - dy)], color, alpha)

    def paper(self, margin_ink):
        for y in range(self.height):
            for x in range(self.width):
                offset = (y * self.width + x) * 3
                fine = noise(x, y, 7)
                edge = min(x, y, self.width - x - 1, self.height - y - 1)
                fold = abs(y - 571 + (x - 512) // 117)
                wash = ((x - 344) ** 2 + (y - 380) ** 2) // 135000
                warmth = max(0, 10 - edge // 3) + wash
                if fold < 5:
                    warmth += (5 - fold) // 2
                grain = (fine % 3) - 1
                if fine % 91 == 0:
                    grain -= 5
                for channel in range(3):
                    shade = grain - warmth * (channel + 1) // 3
                    self.pixels[offset + channel] = max(0, min(255, self.pixels[offset + channel] + shade))
                if edge < 16 and fine % 17 == 0:
                    self.dot(x, y, margin_ink, 14 + fine % 17)

    def rule(self, x, y, width, color, depth=1):
        self.rect(x, y, width, depth, color, 210)
        for px in range(x, x + width):
            grain = noise(px, y, 19)
            if grain % 14 == 0:
                self.dot(px, y - 1, color, 30 + grain % 27)
            if grain % 17 == 0:
                self.dot(px, y + depth, color, 28 + grain % 26)


def crossings(edges, height):
    row = []
    for (x0, y0), (x1, y1) in edges:
        if min(y0, y1) <= height < max(y0, y1):
            row.append(x0 + (height - y0) * (x1 - x0) / (y1 - y0))
    return sorted(row)


def coordinate_values(data, offset, flags, short_bit, same_bit):
    values = []
    total = 0
    for flag in flags:
        if flag & short_bit:
            delta = data[offset]
            total += delta if flag & same_bit else -delta
            offset += 1
        elif not flag & same_bit:
            total += i16(data, offset)
            offset += 2
        values.append(total)
    return values, offset


def midpoint(first, second):
    return ((first[0] + second[0]) / 2, (first[1] + second[1]) / 2, True)


def flatten(points, scale):
    first, last = points[0], points[-1]
    if first[2]:
        start, rest = first, points[1:]
    elif last[2]:
        start, rest = last, points[:-1]
    else:
        start, rest = midpoint(first, last), points
    queue = rest + [start]
    x, y, _ = start
    outline = [(x * scale, -y * scale)]
    index = 0
    while index < len(queue):
        u, v, on_curve = queue[index]
        if on_curve:
            outline.append((u * scale, -v * scale))
            x, y = u, v
            index += 1
            continue
        following = queue[index + 1]
        end_x, end_y, _ = following if following[2] else midpoint(queue[index], following)
        steps = min(18, max(4, ceil(scale * (abs(u - x) + abs(v - y) + abs(end_x - u) + abs(end_y - v)) / 3)))
        for step in range(1, steps + 1):
            t = step / steps
            inverse = 1 - t
            px = inverse * inverse * x + 2 * inverse * t * u + t * t * end_x
            py = inverse * inverse * y + 2 * inverse * t * v + t * t * end_y
            outline.append((px * scale, -py * scale))
        x, y = end_x, end_y
        index += 2 if following[2] else 1
    return list(zip(outline, outline[1:]))


class Font:
    def __init__(self, filename):
        data = filename.read_bytes()
        self.tables = {}
        for index in range(u16(data, 4)):
            offset = 12 + 16 * index
            name, _, start, length = struct.unpack_from('>4sIII', data, offset)
            self.tables[name] = data[start:start + length]
        head = self.tables[b'head']
        self.units = u16(head, 18)
        self.long_offsets = bool(i16(head, 50))
        self.metrics = u16(self.tables[b'hhea'], 34)
        self.cmap = self._character_map()

    def _character_map(self):
        table = self.tables[b'cmap']
        for index in range(u16(table, 2)):
            platform, encoding, offset = struct.unpack_from('>HHI', table, 4 + 8 * index)
            if platform == 3 and encoding == 1 and u16(table, offset) == 4:
                return table[offset:]
        raise ValueError('Type face does not contain a Windows Unicode format 4 character map')

    @lru_cache(maxsize=128)
    def index(self, character):
        code = ord(character)
        count = u16(self.cmap, 6) // 2
        for index in range(count):
            end = u16(self.cmap, 14 + 2 * index)
            if code > end:
                continue
            start = u16(self.cmap, 16 + 2 * (count + index))
            if code < start:
                break
            delta = i16(self.cmap, 16 + 2 * (2 * count + index))
            range_index = 16 + 2 * (3 * count + index)
            relative = u16(self.cmap, range_index)
            if relative == 0:
                return (code + delta) & 65535
            encoded = u16(self.cmap, range_index + relative + 2 * (code - start))
            return (encoded + delta) & 65535 if encoded else 0
        raise ValueError(f'No glyph for U+{code:04X}')

    def contours(self, character):
        return self._glyph(self.index(character))

    @lru_cache(maxsize=128)
    def _glyph(self, glyph):
        loca = self.tables[b'loca']
        if self.long_offsets:
            start, end = struct.unpack_from('>II', loca, 4 * glyph)
        else:
            start, end = (2 * value for value in struct.unpack_from('>HH', loca, 2 * glyph))
        if start == end:
            return []
        data = self.tables[b'glyf'][start:end]
        count = i16(data, 0)
        if count < 0:
            return self._composite(data)
        if count == 0:
            return []
        ends = struct.unpack_from('>' + 'H' * count, data, 10)
        offset = 10 + 2 * count
        offset += 2 + u16(data, offset)
        flags = []
        while len(flags) <= ends[-1]:
            flag = data[offset]
            flags.append(flag)
            offset += 1
            if flag & 8:
                flags.extend([flag] * data[offset])
                offset += 1
        xs, offset = coordinate_values(data, offset, flags, 2, 16)
        ys, _ = coordinate_values(data, offset, flags, 4, 32)
        points = list(zip(xs, ys, (bool(flag & 1) for flag in flags)))
        return [points[begin:end + 1] for begin, end in zip((0,) + tuple(e + 1 for e in ends), ends)]

    def _composite(self, data):
        offset = 10
        result = []
        while True:
            flags, component = struct.unpack_from('>HH', data, offset)
            offset += 4
            whole_words, use_translation = bool(flags & 1), bool(flags & 2)
            if whole_words:
                args = struct.unpack_from('>hh' if use_translation else '>HH', data, offset)
                offset += 4
            else:
                args = struct.unpack_from('>bb' if use_translation else '>BB', data, offset)
                offset += 2

            xx = yy = 1.0
            xy = yx = 0.0
            if flags & 8:
                xx = yy = i16(data, offset) / 16384
                offset += 2
            elif flags & 64:
                xx, yy = (number / 16384 for number in struct.unpack_from('>hh', data, offset))
                offset += 4
            elif flags & 128:
                xx, xy, yx, yy = (number / 16384 for number in struct.unpack_from('>hhhh', data, offset))
                offset += 8

            def project(x, y):
                return xx * x + yx * y, xy * x + yy * y

            outlines = [[(*project(x, y), on_curve) for x, y, on_curve in path]
                        for path in self._glyph(component)]
            if use_translation:
                dx, dy = project(*args) if flags & 2048 else args
            else:
                parent_points = [point for path in result for point in path]
                component_points = [point for path in outlines for point in path]
                x0, y0, _ = parent_points[args[0]]
                x1, y1, _ = component_points[args[1]]
                dx, dy = x0 - x1, y0 - y1
            result.extend([(x + dx, y + dy, on_curve) for x, y, on_curve in path] for path in outlines)
            if not flags & 32:
                return result

    def advance(self, character, size):
        glyph = self.index(character)
        width = u16(self.tables[b'hmtx'], 4 * min(glyph, self.metrics - 1))
        return width * size / self.units

    def placement(self, value, size, tracking):
        pen = 0.0
        previous = ''
        for character in value:
            if previous + character in ('AV', 'VA', 'Wa', 'We', 'Ta', 'Te', 'To', 'Yo', 'LT'):
                pen -= size * 0.035
            width = self.advance(character, size)
            yield character, pen, width
            pen += width + tracking
            previous = character

    def width(self, value, size, tracking=0):
        return max((pen + width for _, pen, width in self.placement(value, size, tracking)), default=0)

    @lru_cache(maxsize=680)
    def mask(self, character, size):
        outlines = self.contours(character)
        if not outlines:
            return ()
        scale = size / self.units
        edges = [edge for outline in outlines for edge in flatten(outline, scale)]
        top = floor(min(y for edge in edges for _, y in edge))
        bottom = ceil(max(y for edge in edges for _, y in edge))
        mask = []
        samples = (0.125, 0.375, 0.625, 0.875)
        for y in range(top, bottom):
            coverage = {}
            for fractional_y in samples:
                spans = crossings(edges, y + fractional_y)
                for left, right in zip(spans[::2], spans[1::2]):
                    for x in range(floor(left), ceil(right)):
                        covered = min(x + 1, right) - max(x, left)
                        coverage[x] = coverage.get(x, 0) + covered
            mask.extend((x, y, round(value * 63.75)) for x, value in coverage.items())
        return tuple(mask)

    def print(self, press, value, x, baseline, size, ink, tracking=0, bold=False):
        for character, pen, _ in self.placement(value, size, tracking):
            left = round(x + pen)
            variation = noise(left, baseline, ord(character))
            bob = (variation % 3 - 1) if size >= 35 else 0
            pressure = 247 + (variation >> 5) % 9
            for dx, dy, coverage in self.mask(character, size):
                px, py = left + dx, baseline + bob + dy
                if bold or (size >= 35 and variation % 4 == 0):
                    press.dot(px + 1, py, ink, coverage * (135 if bold else 44) // 255)
                if size >= 30 and (variation + dx * 5 + dy) % 13 == 0:
                    press.dot(px, py + 1, ink, coverage // 7)
                press.dot(px, py, ink, coverage * pressure // 255)
