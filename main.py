import struct
from pathlib import Path


def u16(x):
    return struct.pack(">H", x & 0xFFFF)


def i16(x):
    return struct.pack(">h", ((x + 0x8000) & 0xFFFF) - 0x8000)


def u32(x):
    return struct.pack(">I", x & 0xFFFFFFFF)


def u64(x):
    return struct.pack(">Q", x & 0xFFFFFFFFFFFFFFFF)


UNITS_PER_EM = 1000
ASCENT = 800
DESCENT = -200
LINE_GAP = 0
ADV_WIDTH_0 = 500
ADV_WIDTH_1 = 500
XMIN, YMIN, XMAX, YMAX = 0, 0, 500, 700


def build_glyf_and_loca():
    def build_simple_glyph(contours, bbox):
        xMin, yMin, xMax, yMax = bbox
        endPts = []
        flags = []
        xs = []
        ys = []
        idx = 0
        for pts in contours:
            endPts.append(idx + len(pts) - 1)
            for x, y in pts:
                flags.append(0x01)
                xs.append(x)
                ys.append(y)
            idx += len(pts)
        x_d = [xs[0]] + [xs[i] - xs[i - 1] for i in range(1, len(xs))] if xs else []
        y_d = [ys[0]] + [ys[i] - ys[i - 1] for i in range(1, len(ys))] if ys else []
        return (
            i16(len(contours))
            + i16(xMin)
            + i16(yMin)
            + i16(xMax)
            + i16(yMax)
            + b"".join(u16(v) for v in endPts)
            + u16(0)
            + bytes(flags)
            + b"".join(i16(v) for v in x_d)
            + b"".join(i16(v) for v in y_d)
        )

    notdef_pts = [(0, 0), (500, 0), (500, 700), (0, 700)]
    notdef = build_simple_glyph([notdef_pts], (XMIN, YMIN, XMAX, YMAX))
    space = i16(0) + i16(0) + i16(0) + i16(0) + i16(0) + u16(0)
    glyf = notdef + space
    loca = u32(0) + u32(len(notdef)) + u32(len(glyf))
    return glyf, loca


def build_hmtx():
    return u16(ADV_WIDTH_0) + i16(0) + u16(ADV_WIDTH_1) + i16(0)


def build_hhea():
    advanceWidthMax = max(ADV_WIDTH_0, ADV_WIDTH_1)
    xMaxExtent = XMAX - XMIN
    return (
        u32(0x00010000)
        + i16(ASCENT)
        + i16(DESCENT)
        + i16(LINE_GAP)
        + u16(advanceWidthMax)
        + i16(0)
        + i16(0)
        + i16(xMaxExtent)
        + i16(1)
        + i16(0)
        + i16(0)
        + i16(0)
        + i16(0)
        + i16(0)
        + i16(0)
        + u16(0)
        + u16(2)
    )


def build_maxp():
    return (
        u32(0x00010000)
        + u16(2)
        + u16(4)
        + u16(1)
        + u16(0)
        + u16(0)
        + u16(2)
        + u16(0)
        + u16(0)
        + u16(0)
        + u16(0)
        + u16(0)
        + u16(0)
        + u16(0)
        + u16(0)
    )


def build_post():
    version = 0x00030000
    italicAngle = 0
    underlinePosition = -75
    underlineThickness = 50
    isFixedPitch = 0
    minMemType42 = 0
    maxMemType42 = 0
    minMemType1 = 0
    maxMemType1 = 0
    return (
        u32(version)
        + u32(italicAngle)
        + i16(underlinePosition)
        + i16(underlineThickness)
        + u32(isFixedPitch)
        + u32(minMemType42)
        + u32(maxMemType42)
        + u32(minMemType1)
        + u32(maxMemType1)
    )


def build_name():
    def enc16(s):
        return s.encode("utf-16-be")

    PLATFORM_MS = 3
    ENC_MS_UNICODE_BMP = 1
    LANG_EN_US = 0x0409
    NAME_FAMILY = 1
    NAME_SUBFAMILY = 2
    NAME_UNIQUE = 3
    NAME_FULL = 4
    NAME_VERSION = 5
    NAME_POSTSCRIPT = 6
    family = "FontFromScratch"
    style = "Regular"
    full = "FontFromScratch Regular"
    ps = "FontFromScratch-Regular"
    version = "Version 1.000"
    unique = family + " 1.0"
    recs = [
        (PLATFORM_MS, ENC_MS_UNICODE_BMP, LANG_EN_US, NAME_FAMILY, enc16(family)),
        (PLATFORM_MS, ENC_MS_UNICODE_BMP, LANG_EN_US, NAME_SUBFAMILY, enc16(style)),
        (PLATFORM_MS, ENC_MS_UNICODE_BMP, LANG_EN_US, NAME_UNIQUE, enc16(unique)),
        (PLATFORM_MS, ENC_MS_UNICODE_BMP, LANG_EN_US, NAME_FULL, enc16(full)),
        (PLATFORM_MS, ENC_MS_UNICODE_BMP, LANG_EN_US, NAME_VERSION, enc16(version)),
        (PLATFORM_MS, ENC_MS_UNICODE_BMP, LANG_EN_US, NAME_POSTSCRIPT, enc16(ps)),
    ]
    count = len(recs)
    stringOffset = 6 + count * 12
    header = u16(0) + u16(count) + u16(stringOffset)
    entries = []
    strings = []
    off = 0
    for pl, en, lang, nid, bs in recs:
        entries.append(struct.pack(">HHHHHH", pl, en, lang, nid, len(bs), off))
        strings.append(bs)
        off += len(bs)
    return header + b"".join(entries) + b"".join(strings)


def build_cmap():
    PLATFORM_MS = 3
    ENC_MS_UNICODE_BMP = 1

    def format4(mapping):
        def log2floor(n):
            p = 0
            while (1 << (p + 1)) <= n:
                p += 1
            return p

        endCodes = [0x0000, 0x0020, 0xFFFF]
        startCodes = [0x0000, 0x0020, 0xFFFF]
        idDeltas = [
            (mapping.get(0x0000, 0) - 0x0000) & 0xFFFF,
            (mapping.get(0x0020, 0) - 0x0020) & 0xFFFF,
            1,
        ]
        idRangeOffsets = [0, 0, 0]
        segCount = 3
        segCountX2 = segCount * 2
        entrySelector = log2floor(segCount)
        searchRange = 2 * (1 << entrySelector)
        rangeShift = segCountX2 - searchRange
        length = 14 + segCountX2 * 4 + 2
        return (
            u16(4)
            + u16(length)
            + u16(0)
            + u16(segCountX2)
            + u16(searchRange)
            + u16(entrySelector)
            + u16(rangeShift)
            + b"".join(u16(x) for x in endCodes)
            + u16(0)
            + b"".join(u16(x) for x in startCodes)
            + b"".join(u16(x) for x in idDeltas)
            + b"".join(u16(x) for x in idRangeOffsets)
        )

    sub = format4({0x0000: 0, 0x0020: 1})
    header = u16(0) + u16(1) + struct.pack(">HHI", PLATFORM_MS, ENC_MS_UNICODE_BMP, 12)
    return header + sub


def build_head():
    return (
        u32(0x00010000)
        + u32(0x00010000)
        + u32(0)
        + u32(0x5F0F3CF5)
        + u16(0)
        + u16(UNITS_PER_EM)
        + u64(0)
        + u64(0)
        + i16(XMIN)
        + i16(YMIN)
        + i16(XMAX)
        + i16(YMAX)
        + u16(0)
        + u16(8)
        + i16(2)
        + i16(1)
        + i16(0)
    )


def build_os2_v2():
    return (
        u16(2)
        + i16(500)
        + u16(400)
        + u16(5)
        + u16(0)
        + u16(650)
        + u16(699)
        + i16(0)
        + i16(140)
        + u16(650)
        + u16(699)
        + i16(0)
        + i16(479)
        + u16(50)
        + i16(300)
        + i16(0)
        + bytes(10)
        + u32(1)
        + u32(0)
        + u32(0)
        + u32(0)
        + b"NONE"
        + u16(0x0040)
        + u16(0x0000)
        + u16(0x0020)
        + i16(ASCENT)
        + i16(DESCENT)
        + i16(0)
        + u16(ASCENT)
        + u16(-DESCENT)
        + u32(1)
        + u32(0)
        + i16(500)
        + i16(700)
        + u16(0)
        + u16(32)
        + u16(1)
    )


def build_tables():
    glyf_raw, loca_raw = build_glyf_and_loca()
    return {
        b"OS/2": build_os2_v2(),
        b"cmap": build_cmap(),
        b"glyf": glyf_raw,
        b"head": build_head(),
        b"hhea": build_hhea(),
        b"hmtx": build_hmtx(),
        b"loca": loca_raw,
        b"maxp": build_maxp(),
        b"name": build_name(),
        b"post": build_post(),
    }


def build_sfnt(tables):
    def pad4(b: bytes):
        return b + (b"\0" * ((-len(b)) & 3))

    def sfnt_checksum(data: bytes) -> int:
        d = pad4(data)
        s = 0
        for i in range(0, len(d), 4):
            s = (s + struct.unpack(">I", d[i : i + 4])[0]) & 0xFFFFFFFF
        return s

    def log2floor(n: int) -> int:
        p = 0
        while (1 << (p + 1)) <= n:
            p += 1
        return p

    tags = sorted(tables.keys())
    numTables = len(tags)
    p = 1 << log2floor(numTables)
    searchRange = p * 16
    entrySelector = log2floor(numTables)
    rangeShift = numTables * 16 - searchRange

    offset = 12 + numTables * 16
    entries = []
    payload = []
    offsets = {}
    for t in tags:
        raw = tables[t]
        length = len(raw)
        cs = sfnt_checksum(raw if t != b"head" else raw[:8] + b"\0\0\0\0" + raw[12:])
        entries.append(t + u32(cs) + u32(offset) + u32(length))
        offsets[t] = offset
        part = pad4(raw)
        payload.append(part)
        offset += len(part)

    header = (
        u32(0x00010000)
        + u16(numTables)
        + u16(searchRange)
        + u16(entrySelector)
        + u16(rangeShift)
    )
    directory = b"".join(entries)
    font = bytearray(header + directory + b"".join(payload))

    head_off = offsets[b"head"]
    font[head_off + 8 : head_off + 12] = b"\0\0\0\0"
    adj = (0xB1B0AFBA - sfnt_checksum(bytes(font))) & 0xFFFFFFFF
    font[head_off + 8 : head_off + 12] = u32(adj)

    return bytes(font)


def main():
    font = build_sfnt(build_tables())
    Path("FontFromScratch.ttf").write_bytes(font)


if __name__ == "__main__":
    main()
