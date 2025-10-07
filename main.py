import struct
from itertools import accumulate
from pathlib import Path


def u16(x: int) -> bytes:
    return x.to_bytes(2, "big", signed=False)


def i16(x: int) -> bytes:
    return x.to_bytes(2, "big", signed=True)


def u32(x: int) -> bytes:
    return x.to_bytes(4, "big", signed=False)


def u64(x: int) -> bytes:
    return x.to_bytes(8, "big", signed=False)


ASCENT = 800
DESCENT = -200
ADV_WIDTH = 500
XMIN, YMIN, XMAX, YMAX = 0, 0, 500, 700


def build_head():
    return (
        u32(0x00010000)  # majorVersion | minorVersion
        + u32(0x00010000)  # fontRevision
        + u32(0)  # checkSumAdjustment
        + u32(0x5F0F3CF5)  # magicNumber
        + u16(0)  # flags
        + u16(1000)  # unitsPerEm
        + u64(0)  # created
        + u64(0)  # modified
        + i16(XMIN)  # xMin
        + i16(YMIN)  # yMin
        + i16(XMAX)  # xMax
        + i16(YMAX)  # yMax
        + u16(0)  # macStyle
        + u16(0)  # lowestRecPPEM
        + i16(0)  # fontDirectionHint
        + i16(1)  # indexToLocFormat
        + i16(0)  # glyphDataFormat
    )


def build_hhea():
    xMaxExtent = XMAX - XMIN
    return (
        u32(0x00010000)  # tableVersion
        + i16(ASCENT)  # ascender
        + i16(DESCENT)  # descender
        + i16(0)  # lineGap
        + u16(ADV_WIDTH)  # advanceWidthMax
        + i16(0)  # minLeftSideBearing
        + i16(0)  # minRightSideBearing
        + i16(xMaxExtent)  # xMaxExtent
        + i16(1)  # caretSlopeRise
        + i16(0)  # caretSlopeRun
        + i16(0)  # caretOffset
        + i16(0)  # reserved1
        + i16(0)  # reserved2
        + i16(0)  # reserved3
        + i16(0)  # reserved4
        + u16(0)  # metricDataFormat
        + u16(1)  # numberOfHMetrics
    )


def build_maxp():
    return (
        u32(0x00010000)  # tableVersion
        + u16(1)  # numGlyphs
        + u16(4)  # maxPoints
        + u16(1)  # maxContours
        + u16(0)  # maxCompositePoints
        + u16(0)  # maxCompositeContours
        + u16(0)  # maxZones
        + u16(0)  # maxTwilightPoints
        + u16(0)  # maxStorage
        + u16(0)  # maxFunctionDefs
        + u16(0)  # maxInstructionDefs
        + u16(0)  # maxStackElements
        + u16(0)  # maxSizeOfInstructions
        + u16(0)  # maxComponentElements
        + u16(0)  # maxComponentDepth
    )


def build_os2():
    return (
        u16(2)  # version
        + i16(0)  # xAvgCharWidth
        + u16(0)  # usWeightClass
        + u16(0)  # usWidthClass
        + u16(0)  # fsType
        + u16(0)  # ySubscriptXSize
        + u16(0)  # ySubscriptYSize
        + i16(0)  # ySubscriptXOffset
        + i16(0)  # ySubscriptYOffset
        + u16(0)  # ySuperscriptXSize
        + u16(0)  # ySuperscriptYSize
        + i16(0)  # ySuperscriptXOffset
        + i16(0)  # ySuperscriptYOffset
        + u16(0)  # yStrikeoutSize
        + i16(0)  # yStrikeoutPosition
        + i16(0)  # sFamilyClass
        + bytes(10)  # panose
        + u32(0)  # ulUnicodeRange1
        + u32(0)  # ulUnicodeRange2
        + u32(0)  # ulUnicodeRange3
        + u32(0)  # ulUnicodeRange4
        + b"NONE"  # achVendID
        + u16(0)  # fsSelection
        + u16(0)  # usFirstCharIndex
        + u16(0xFFFF)  # usLastCharIndex
        + i16(ASCENT)  # sTypoAscender
        + i16(DESCENT)  # sTypoDescender
        + i16(0)  # sTypoLineGap
        + u16(ASCENT)  # usWinAscent
        + u16(-DESCENT)  # usWinDescent
        + u32(0)  # ulCodePageRange1
        + u32(0)  # ulCodePageRange2
        + i16(0)  # sxHeight
        + i16(0)  # sCapHeight
        + u16(0)  # usDefaultChar
        + u16(0)  # usBreakChar
        + u16(0)  # usMaxContext
    )


def build_hmtx():
    return (
        u16(ADV_WIDTH)  # advanceWidth
        + i16(0)  # lsb (leftSideBearing)
    )


def build_cmap():
    sub13 = (
        u16(13)  # format
        + u16(0)  # reserved
        + u32(28)  # length
        + u32(0)  # language
        + u32(1)  # numGroups
        + u32(0x00000000)  # startCharCode
        + u32(0x0010FFFF)  # endCharCode
        + u32(0)  # startGlyphID
    )

    sub4 = (
        u16(4)  # format
        + u16(32)  # length
        + u16(0)  # language
        + u16(4)  # segCountX2
        + u16(4)  # searchRange
        + u16(1)  # entrySelector
        + u16(0)  # rangeShift
        + u16(0x0041)  # endCode[0]
        + u16(0xFFFF)  # endCode[1]
        + u16(0)  # reservedPad
        + u16(0x0041)  # startCode[0]
        + u16(0xFFFF)  # startCode[1]
        + u16((-0x0041) & 0xFFFF)  # idDelta[0]
        + u16(1)  # idDelta[1]
        + u16(0)  # idRangeOffset[0]
        + u16(0)  # idRangeOffset[1]
    )

    num = 2
    off0 = 4 + num * 8
    off1 = off0 + len(sub13)
    header = (
        u16(0)  # version
        + u16(num)  # numberSubtables
    )
    recs = struct.pack(">HHI", 3, 10, off0) + struct.pack(">HHI", 3, 1, off1)
    return header + recs + sub13 + sub4


def build_loca_and_glyf():
    pts = [(XMIN, YMIN), (XMAX, YMIN), (XMAX, YMAX), (XMIN, YMAX)]
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    x_d = [xs[0], xs[1] - xs[0], xs[2] - xs[1], xs[3] - xs[2]]
    y_d = [ys[0], ys[1] - ys[0], ys[2] - ys[1], ys[3] - ys[2]]

    notdef = (
        i16(1)  # numberOfContours
        + i16(XMIN)  # xMin
        + i16(YMIN)  # yMin
        + i16(XMAX)  # xMax
        + i16(YMAX)  # yMax
        + u16(3)  # endPtsOfContours
        + u16(0)  # instructionLength
        + bytes([0x01, 0x01, 0x01, 0x01])  # flags
        + b"".join(i16(v) for v in x_d)  # xCoordinates
        + b"".join(i16(v) for v in y_d)  # yCoordinates
    )

    glyf = notdef
    loca = u32(0) + u32(len(glyf))
    return loca, glyf


def build_name():
    items = [
        (1, "FontFromScratch"),
        (2, "Regular"),
        (3, "FontFromScratch 1.0"),
        (4, "FontFromScratch Regular"),
        (5, "Version 1.000"),
        (6, "FontFromScratch-Regular"),
    ]

    strings = [s.encode("utf-16-be") for _, s in items]
    lengths = [len(bs) for bs in strings]
    offsets = [sum(lengths[:i]) for i in range(len(lengths))]

    entries = [
        struct.pack(">HHHHHH", 3, 1, 0x0409, nid, ln, off)
        for (nid, _), ln, off in zip(items, lengths, offsets)
    ]

    count = len(entries)
    header = u16(0) + u16(count) + u16(6 + count * 12)

    return header + b"".join(entries) + b"".join(strings)


def build_post():
    return (
        u32(0x00030000)  # version
        + u32(0)  # italicAngle
        + i16(0)  # underlinePosition
        + i16(0)  # underlineThickness
        + u32(0)  # isFixedPitch
        + u32(0)  # minMemType42
        + u32(0)  # maxMemType42
        + u32(0)  # minMemType1
        + u32(0)  # maxMemType1
    )


def build_tables():
    loca, glyf = build_loca_and_glyf()
    return {
        b"head": build_head(),
        b"hhea": build_hhea(),
        b"maxp": build_maxp(),
        b"OS/2": build_os2(),
        b"hmtx": build_hmtx(),
        b"cmap": build_cmap(),
        b"loca": loca,
        b"glyf": glyf,
        b"name": build_name(),
        b"post": build_post(),
    }


def build_sfnt(tables):
    def pad4(b: bytes):
        return b + (b"\0" * ((-len(b)) & 3))

    def sfnt_checksum(data: bytes) -> int:
        d = pad4(data)
        return (
            sum(struct.unpack(">I", d[i : i + 4])[0] for i in range(0, len(d), 4))
            & 0xFFFFFFFF
        )

    def log2floor(n: int) -> int:
        return (n.bit_length() - 1) if n > 0 else 0

    tags = sorted(tables.keys())
    numTables = len(tags)
    p = 1 << log2floor(numTables)
    searchRange = p * 16
    entrySelector = log2floor(numTables)
    rangeShift = numTables * 16 - searchRange

    raws = [tables[t] for t in tags]
    lengths = [len(r) for r in raws]
    checksums = [
        sfnt_checksum(r if t != b"head" else r[:8] + b"\0\0\0\0" + r[12:])
        for t, r in zip(tags, raws)
    ]
    parts = [pad4(r) for r in raws]

    base = 12 + numTables * 16
    offsets_list = [base + o for o in accumulate([0] + [len(p) for p in parts])][:-1]
    offsets = {t: o for t, o in zip(tags, offsets_list)}

    entries = [
        t + u32(cs) + u32(off) + u32(length)
        for t, cs, off, length in zip(tags, checksums, offsets_list, lengths)
    ]
    header = (
        u32(0x00010000)
        + u16(numTables)
        + u16(searchRange)
        + u16(entrySelector)
        + u16(rangeShift)
    )
    directory = b"".join(entries)
    payload = b"".join(parts)

    font = bytearray(header + directory + payload)

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
