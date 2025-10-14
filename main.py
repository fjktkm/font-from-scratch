import struct
from pathlib import Path

ASCENT = 800
DESCENT = -200
ADV_WIDTH = 500
XMIN, YMIN, XMAX, YMAX = 0, 0, 500, 700


def build_head() -> bytes:
    return struct.pack(
        ">IIIIHHQQhhhhHHhhh",
        0,  # tableVersion
        0,  # tableVersion
        0,  # checkSumAdjustment
        0x5F0F3CF5,  # magicNumber
        0,  # flags
        1000,  # unitsPerEm
        0,  # created
        0,  # modified
        XMIN,  # xMin
        YMIN,  # yMin
        XMAX,  # xMax
        YMAX,  # yMax
        0,  # macStyle
        0,  # lowestRecPPEM
        0,  # fontDirectionHint
        1,  # indexToLocFormat
        0,  # glyphDataFormat
    )


def build_hhea() -> bytes:
    xMaxExtent = XMAX - XMIN
    return struct.pack(
        ">IhhhHhhhhhhhhhhHH",
        0,  # tableVersion
        ASCENT,  # ascender
        DESCENT,  # descender
        0,  # lineGap
        ADV_WIDTH,  # advanceWidthMax
        0,  # minLeftSideBearing
        0,  # minRightSideBearing
        xMaxExtent,  # xMaxExtent
        1,  # caretSlopeRise
        0,  # caretSlopeRun
        0,  # caretOffset
        0,  # reserved1
        0,  # reserved2
        0,  # reserved3
        0,  # reserved4
        0,  # metricDataFormat
        1,  # numberOfHMetrics
    )


def build_maxp() -> bytes:
    return struct.pack(
        ">IHHHHHHHHHHHHHH",
        0,  # tableVersion
        1,  # numGlyphs
        4,  # maxPoints
        1,  # maxContours
        0,  # maxCompositePoints
        0,  # maxCompositeContours
        0,  # maxZones
        0,  # maxTwilightPoints
        0,  # maxStorage
        0,  # maxFunctionDefs
        0,  # maxInstructionDefs
        0,  # maxStackElements
        0,  # maxSizeOfInstructions
        0,  # maxComponentElements
        0,  # maxComponentDepth
    )


def build_os2() -> bytes:
    return struct.pack(
        ">HhHHHHHhhHHhhHhh10sIIII4sHHHhhhHHIIhhHHH",
        2,  # version
        ADV_WIDTH,  # xAvgCharWidth
        400,  # usWeightClass
        5,  # usWidthClass
        0,  # fsType
        0,  # ySubscriptXSize
        0,  # ySubscriptYSize
        0,  # ySubscriptXOffset
        0,  # ySubscriptYOffset
        0,  # ySuperscriptXSize
        0,  # ySuperscriptYSize
        0,  # ySuperscriptXOffset
        0,  # ySuperscriptYOffset
        0,  # yStrikeoutSize
        0,  # yStrikeoutPosition
        0,  # sFamilyClass
        bytes(10),  # panose
        0,  # ulUnicodeRange1
        0,  # ulUnicodeRange2
        0,  # ulUnicodeRange3
        0,  # ulUnicodeRange4
        b"NONE",  # achVendID
        0x0040,  # fsSelection
        0x0000,  # usFirstCharIndex
        0xFFFF,  # usLastCharIndex
        ASCENT,  # sTypoAscender
        DESCENT,  # sTypoDescender
        0,  # sTypoLineGap
        ASCENT,  # usWinAscent
        -DESCENT,  # usWinDescent
        0,  # ulCodePageRange1
        0,  # ulCodePageRange2
        0,  # sxHeight
        0,  # sCapHeight
        0,  # usDefaultChar
        0,  # usBreakChar
        0,  # usMaxContext
    )


def build_hmtx() -> bytes:
    return struct.pack(
        ">Hh",
        ADV_WIDTH,  # advanceWidth
        0,  # lsb
    )


def build_cmap() -> bytes:
    sub13 = struct.pack(
        ">HHIIIIII",
        13,  # format
        0,  # reserved
        28,  # length
        0,  # language
        1,  # numGroups
        0x00000000,  # startCharCode
        0x0010FFFF,  # endCharCode
        0,  # startGlyphID
    )

    sub4 = struct.pack(
        ">HHHHHHHHHHHH",
        4,  # format
        24,  # length
        0,  # language
        2,  # segCountX2
        2,  # searchRange
        1,  # entrySelector
        0,  # rangeShift
        0xFFFF,  # endCode[0]
        0,  # reservedPad
        0xFFFF,  # startCode[0]
        1,  # idDelta[0]
        0,  # idRangeOffset[0]
    )
    num = 2
    off0 = 4 + num * 8
    off1 = off0 + len(sub13)
    header = struct.pack(
        ">HH",
        0,  # version
        num,  # numberSubtables
    )

    recs = struct.pack(">HHI", 3, 10, off0) + struct.pack(">HHI", 3, 1, off1)

    return header + recs + sub13 + sub4


def build_loca_and_glyf() -> tuple[bytes, bytes]:
    glyf = (
        struct.pack(
            ">hhhhhHH",
            1,  # numberOfContours
            XMIN,  # xMin
            YMIN,  # yMin
            XMAX,  # xMax
            YMAX,  # yMax
            3,  # endPtsOfContours
            0,  # instructionLength
        )
        + bytes([0x01, 0x01, 0x01, 0x01])  # flags
        + struct.pack(">hhhh", 0, 500, 0, -500)  # xCoordinates
        + struct.pack(">hhhh", 0, 0, 700, 0)  # yCoordinates
    )

    loca = struct.pack(
        ">II",
        0,  # offset[0]
        len(glyf),  # offset[1]
    )

    return loca, glyf


def build_name() -> bytes:
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
        struct.pack(
            ">HHHHHH",
            3,  # platformID (Windows)
            1,  # encodingID (Unicode BMP)
            0x0409,  # languageID (English - United States)
            nid,  # nameID
            ln,  # length
            off,  # offset
        )
        for (nid, _), ln, off in zip(items, lengths, offsets)
    ]

    count = len(entries)
    header = struct.pack(
        ">HHH",
        0,  # format
        count,  # count
        6 + count * 12,  # stringOffset
    )

    return header + b"".join(entries) + b"".join(strings)


def build_post() -> bytes:
    return struct.pack(
        ">IIhhIIIII",
        0x00030000,  # version
        0,  # italicAngle
        -75,  # underlinePosition
        50,  # underlineThickness
        0,  # isFixedPitch
        0,  # minMemType42
        0,  # maxMemType42
        0,  # minMemType1
        0,  # maxMemType1
    )


def build_tables() -> dict[bytes, bytes]:
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


def build_sfnt(tables: dict[bytes, bytes]) -> bytes:
    def pad4(b: bytes) -> bytes:
        return b + (b"\0" * ((-len(b)) & 3))

    def sfnt_checksum(data: bytes) -> int:
        data = pad4(data)
        return (
            sum(int.from_bytes(data[i : i + 4], "big") for i in range(0, len(data), 4))
            & 0xFFFFFFFF
        )

    def log2floor(n: int) -> int:
        return (n.bit_length() - 1) if n > 0 else 0

    tags = tuple(sorted(tables.keys()))
    num_tables = len(tags)
    e = log2floor(num_tables)
    search_range = (1 << e) * 16
    entry_selector = e
    range_shift = num_tables * 16 - search_range

    raws = [tables[t] for t in tags]
    parts = [pad4(r) for r in raws]
    lengths = [len(r) for r in raws]
    checksums = [sfnt_checksum(r) for r in raws]

    base_offset = 12 + num_tables * 16
    sizes = [len(p) for p in parts]
    offsets = [base_offset + sum(sizes[:i]) for i in range(len(sizes))]

    entries = [
        struct.pack(">4sIII", t, cs, off, length)
        for t, cs, off, length in zip(tags, checksums, offsets, lengths)
    ]

    header = struct.pack(
        ">IHHHH",
        0x00010000,
        num_tables,
        search_range,
        entry_selector,
        range_shift,
    )

    font = bytearray(header + b"".join(entries) + b"".join(parts))

    head_index = tags.index(b"head")
    head_offset = base_offset + sum(sizes[:head_index])
    adjustment = (0xB1B0AFBA - sfnt_checksum(bytes(font))) & 0xFFFFFFFF
    font[head_offset + 8 : head_offset + 12] = struct.pack(">I", adjustment)

    return bytes(font)


def main() -> None:
    font = build_sfnt(build_tables())
    Path("FontFromScratch.ttf").write_bytes(font)


if __name__ == "__main__":
    main()
