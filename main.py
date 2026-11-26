#!/usr/bin/env python3
"""THE WORLD - a one-page dense broadsheet for 26 November 2026.

Pure Python standard library only. No third-party imports, no network,
no files read at run time. Renders a 1024x1024 newspaper front page with
its own 5x7 bitmap font and its own minimal PNG encoder (zlib + struct).

Writes entry.png to $MAKEFUN_OUTPUT_DIR (falls back to the current
working directory). Output is deterministic: same code, same bytes.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
NAVY = (20, 33, 61)
RED = (178, 34, 34)
INK = (30, 30, 30)
GREY = (110, 108, 100)
WHITE = (255, 255, 255)
LIGHT = (232, 227, 216)

W = 1024
H = 1024

# ------------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows of 5 cells ('#' = on, '.' = off).
# Only capitals, digits and common punctuation are defined; the renderer
# upper-cases everything and maps unknown characters to a space.
FONT = {
    'A': ('.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'),
    'B': ('####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'),
    'C': ('.####', '#....', '#....', '#....', '#....', '#....', '.####'),
    'D': ('####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'),
    'E': ('#####', '#....', '#....', '####.', '#....', '#....', '#####'),
    'F': ('#####', '#....', '#....', '####.', '#....', '#....', '#....'),
    'G': ('.####', '#....', '#....', '#..##', '#...#', '#...#', '.###.'),
    'H': ('#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'),
    'I': ('#####', '..#..', '..#..', '..#..', '..#..', '..#..', '#####'),
    'J': ('..###', '...#.', '...#.', '...#.', '...#.', '#..#.', '.##..'),
    'K': ('#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'),
    'L': ('#....', '#....', '#....', '#....', '#....', '#....', '#####'),
    'M': ('#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'),
    'N': ('#...#', '##..#', '##..#', '#.#.#', '#..##', '#..##', '#...#'),
    'O': ('.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'),
    'P': ('####.', '#...#', '#...#', '####.', '#....', '#....', '#....'),
    'Q': ('.###.', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#'),
    'R': ('####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'),
    'S': ('.####', '#....', '#....', '.###.', '....#', '....#', '####.'),
    'T': ('#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'),
    'U': ('#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'),
    'V': ('#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '..#..'),
    'W': ('#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'),
    'X': ('#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'),
    'Y': ('#...#', '#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'),
    'Z': ('#####', '....#', '...#.', '..#..', '.#...', '#....', '#####'),
}

FONT.update({
    '0': ('.###.', '#..##', '#.#.#', '##..#', '#...#', '#...#', '.###.'),
    '1': ('..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '.###.'),
    '2': ('.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'),
    '3': ('####.', '....#', '....#', '.###.', '....#', '....#', '####.'),
    '4': ('...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'),
    '5': ('#####', '#....', '####.', '....#', '....#', '#...#', '.###.'),
    '6': ('.###.', '#....', '#....', '####.', '#...#', '#...#', '.###.'),
    '7': ('#####', '....#', '...#.', '..#..', '..#..', '..#..', '..#..'),
    '8': ('.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'),
    '9': ('.###.', '#...#', '#...#', '.####', '....#', '....#', '.###.'),
    '.': ('.....', '.....', '.....', '.....', '.....', '.##..', '.##..'),
    ',': ('.....', '.....', '.....', '.....', '.....', '.##..', '.#...'),
    ':': ('.....', '.##..', '.##..', '.....', '.##..', '.##..', '.....'),
    ';': ('.....', '.##..', '.##..', '.....', '.##..', '.##..', '.#...'),
    '!': ('..#..', '..#..', '..#..', '..#..', '..#..', '.....', '..#..'),
    '?': ('.###.', '#...#', '....#', '...#.', '..#..', '.....', '..#..'),
    "'": ('..#..', '..#..', '.#...', '.....', '.....', '.....', '.....'),
    '"': ('.#.#.', '.#.#.', '.#.#.', '.....', '.....', '.....', '.....'),
    '-': ('.....', '.....', '.....', '.###.', '.....', '.....', '.....'),
    chr(8212): ('.....', '.....', '.....', '#####', '.....', '.....', '.....'),
    '(': ('...##', '..#..', '.#...', '.#...', '.#...', '..#..', '...##'),
    ')': ('##...', '..#..', '...#.', '...#.', '...#.', '..#..', '##...'),
    '/': ('....#', '....#', '...#.', '..#..', '.#...', '#....', '#....'),
    '%': ('##..#', '##.#.', '...#.', '..#..', '.#...', '#.##.', '#..##'),
    '$': ('..#..', '.####', '#.#..', '.###.', '..#.#', '####.', '..#..'),
    '&': ('.##..', '#..#.', '#..#.', '.#...', '#.#.#', '#..#.', '.##.#'),
    '+': ('.....', '..#..', '..#..', '#####', '..#..', '..#..', '.....'),
    '=': ('.....', '.....', '#####', '.....', '#####', '.....', '.....'),
    '*': ('.....', '.#.#.', '..#..', '#####', '..#..', '.#.#.', '.....'),
    '#': ('.#.#.', '.#.#.', '#####', '.#.#.', '#####', '.#.#.', '.#.#.'),
    '@': ('.###.', '#...#', '#.###', '#.#.#', '#.###', '#....', '.###.'),
    chr(8226): ('.....', '.....', '..#..', '.###.', '.###.', '..#..', '.....'),
    ' ': ('.....', '.....', '.....', '.....', '.....', '.....', '.....'),
})

BLANK = ('.....',) * 7


def glyph(ch):
    return FONT.get(ch, BLANK)


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, color):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(color)

    def fill(self, color):
        r, g, b = color
        self.px[:] = bytes((r, g, b)) * (self.w * self.h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        r, g, b = color
        row = bytes((r, g, b)) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x0, x1, y, color, thick=1):
        self.rect(x0, y, x1, y + thick, color)

    def vline(self, x, y0, y1, color, thick=1):
        self.rect(x, y0, x + thick, y1, color)

    def disc(self, cx, cy, rad, color):
        for dy in range(-rad, rad + 1):
            half = int((rad * rad - dy * dy) ** 0.5)
            for dx in range(-half, half + 1):
                self.set(cx + dx, cy + dy, color)

    def text(self, x, y, s, scale, color):
        """Draw one line, upper-cased. Returns the pixel width drawn."""
        s = s.upper()
        cx = x
        for ch in s:
            rows = glyph(ch)
            for ry in range(7):
                row = rows[ry]
                for rx in range(5):
                    if row[rx] == '#':
                        self.rect(cx + rx * scale, y + ry * scale,
                                  cx + (rx + 1) * scale,
                                  y + (ry + 1) * scale, color)
            cx += 6 * scale
        return cx - x

    def text_width(self, s, scale):
        return len(s.upper()) * 6 * scale

    def text_centred(self, cx, y, s, scale, color):
        w = self.text_width(s, scale)
        return self.text(cx - w // 2, y, s, scale, color)


def wrap(s, max_chars):
    """Greedy word wrap to a list of lines, each at most max_chars long."""
    words = s.split()
    lines = []
    cur = ''
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur = cur + ' ' + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, scale, color, max_width, max_lines=None):
    """Draw a wrapped paragraph. Returns the y just below the last line."""
    max_chars = max(1, max_width // (6 * scale))
    lines = wrap(s, max_chars)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        cv.text(x, y, line, scale, color)
        y += 9 * scale
    return y

# ------------------------------------------------------------- PNG encoder
def _chunk(tag, data):
    out = struct.pack('>I', len(data)) + tag + data
    return out + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)


def encode_png(w, h, pixels):
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += pixels[y * w * 3:(y + 1) * w * 3]
    return (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', ihdr) +
            _chunk(b'IDAT', zlib.compress(bytes(raw), 9)) +
            _chunk(b'IEND', b''))


# ------------------------------------------------------------ dotted world
# Hand-authored coarse equirectangular land mask, 62 columns x 31 rows.
# Each entry: (row, [(x0, x1), ...]) with inclusive column ranges of land.
# Row 0 is the far north (about 90N), row 30 the far south.
MAP_ROWS = [
    (0, [(24, 25)]),
    (1, [(4, 6), (23, 27)]),
    (2, [(3, 8), (22, 28), (31, 34), (36, 58)]),
    (3, [(2, 9), (21, 28), (30, 35), (36, 59)]),
    (4, [(3, 12), (21, 27), (29, 35), (36, 58)]),
    (5, [(4, 14), (29, 35), (36, 57)]),
    (6, [(5, 16), (29, 35), (36, 56)]),
    (7, [(6, 17), (29, 34), (36, 55), (54, 56)]),
    (8, [(7, 17), (29, 34), (36, 54)]),
    (9, [(8, 17), (30, 34), (37, 53)]),
    (10, [(8, 15), (27, 38), (42, 52)]),
    (11, [(9, 14), (27, 38), (43, 52)]),
    (12, [(12, 15), (27, 38), (44, 52)]),
    (13, [(14, 16), (27, 37), (46, 53)]),
    (14, [(17, 24), (27, 37), (47, 54)]),
    (15, [(18, 25), (28, 37), (48, 55)]),
    (16, [(18, 25), (29, 36)]),
    (17, [(19, 24), (30, 36), (51, 57)]),
    (18, [(19, 24), (30, 35), (51, 58)]),
    (19, [(20, 23), (31, 35), (51, 58)]),
    (20, [(20, 23), (31, 34), (52, 57)]),
    (21, [(21, 22), (32, 34), (52, 56), (59, 60)]),
    (22, [(21, 22), (53, 55), (59, 60)]),
    (23, [(21, 21), (59, 59)]),
    (24, [(21, 21)]),
    (27, [(8, 12), (30, 36), (50, 55)]),
]

MAP_COLS = 62
MAP_X0 = 34
MAP_Y0 = 234
MAP_DX = 10
MAP_DY = 5


def draw_map(cv):
    cv.text(MAP_X0, 222, 'THE WORLD IN DOTS', 1, NAVY)
    for row, spans in MAP_ROWS:
        cy = MAP_Y0 + row * MAP_DY
        for x0, x1 in spans:
            for col in range(x0, x1 + 1):
                cv.disc(MAP_X0 + col * MAP_DX, cy, 2, NAVY)


# ------------------------------------------------------------------ stories
# Real news reported on Thursday 26 November 2026 (and the days just
# before it). Lead + 12 cards + 9 briefs + the sport footer = 23 stories.

LEAD = {
    'kicker': 'TARIFFS — WASHINGTON',
    'headline': 'TRUMP UNVEILS SWEEPING TARIFFS ON 14 PARTNERS',
    'deck': ('President announces new duties on China, the EU, Japan and 11 '
             'other economies from January, in a Thanksgiving-eve broadside '
             'that rattled markets and drew swift warnings of retaliation.'),
    'body': ('The US Trade Representative said the measures follow a probe '
             'into structural overcapacity, with proposed rates of up to 35%. '
             'Taiwan faces 15%, in the lowest tier alongside Japan, South '
             'Korea and the EU. Exporters braced for the January start as '
             'markets slid and partners weighed their response.'),
}

CARDS = [
    ('MIDDLE EAST', 'HOUTHIS HIT SAUDI REFINERY; OIL TOPS $94',
     "Yemen's Houthis claimed strikes on Saudi Arabia's Ras Tanura refinery "
     'and Riyadh\'s financial district, sending Brent crude above $94 and '
     'raising fears of disruption to Gulf energy supplies.'),
    ('EUROPE', "MOSCOW'S OWN FIGURES: NEARLY 500,000 WAR DEAD",
     'Russian figures show nearly half a million military deaths in the '
     "Ukraine war, a rare official glimpse of the conflict's human cost as "
     'Kyiv strikes Russian refineries and Moscow vows retaliation.'),
    ('MIDDLE EAST', 'TWO TANKERS HIT MINES IN STRAIT OF HORMUZ',
     'Two oil tankers struck naval mines in the Strait of Hormuz, the '
     "world's most important oil chokepoint, heightening fears for shipping "
     'as regional tensions climb.'),
    ('MIDDLE EAST', 'ISRAEL STRIKES HAMAS OFFICIAL; CEASEFIRE STRAINS',
     'An Israeli strike killed a Hamas official in Gaza, putting the '
     'fragile ceasefire under fresh strain as mediators raced to keep the '
     'truce from unravelling.'),
    ('SPACE', 'SPACEX CLEARED FOR A MILLION AI SATELLITES',
     "The US regulator approved SpaceX's plan to deploy one million "
     'satellites for orbital AI data centres, the largest constellation '
     'ever authorised, in a bet on computing in space.'),
    ('ASIA', "PAKISTAN'S FIRST ASTRONAUT JOINS CHINA'S STATION",
     "Muhammad Zeeshan Ali became the first foreign astronaut chosen for "
     "China's Tiangong station, flying aboard the Shenzhou-24 mission in a "
     "milestone for Pakistan's space programme."),
    ('ASIA', 'BANGLADESH GARMENT WORKERS WIN 36% PAY RISE',
     'Bangladesh raised the minimum wage for entry-level garment workers by '
     "36%, a big win for millions of factory staff in the world's "
     'second-largest clothing exporter.'),
    ('SOUTH AMERICA', 'COLOMBIA FREES 20 AFTER 17-HOUR SUPERMARKET SIEGE',
     'Colombian police stormed a supermarket to free 20 people held hostage '
     'for 17 hours, ending a siege that gripped the country and tested the '
     'security forces.'),
    ('OCEANIA', 'SOLOMON ISLANDS AND AUSTRALIA SIGN SECURITY PACT',
     'The Solomon Islands and Australia signed a historic security treaty, '
     'deepening defence ties in the Pacific as regional powers compete for '
     'influence across the island nations.'),
    ('AFRICA', 'RAMAPHOSA WINS COURT BATTLE OVER PHALA PHALA',
     "South Africa's High Court set aside a 2022 panel report that found "
     'President Cyril Ramaphosa may have had a case to answer over $580,000 '
     'stolen from his Phala Phala farm.'),
    ('AFRICA', 'EBOLA OUTBREAK WORSENS AS FIGHTING HAMPERS AID',
     'Health officials warn heavy fighting in eastern DR Congo is hampering '
     'the Ebola response, with more than 1,000 infected and about 650 dead '
     'around Beni.'),
    ('ASIA', "XI'S GRAFT PROBE SHAKES CHINA'S POWER LADDER",
     'A corruption probe into a rising Shanghai star has upended the '
     'traditional path to power in China, in the most closely watched purge '
     'of a senior figure this year.'),
]

BRIEFS = [
    'NORTH KOREA ORDERS SWISS TO SHUT PYONGYANG OFFICE',
    'NEPAL: 5.6-MAGNITUDE QUAKE HITS KOSHI PROVINCE',
    'INDIA MARKS 18 YEARS SINCE 26/11 MUMBAI ATTACKS',
    'BITCOIN ETFS SEE RECORD $4.71BN NOVEMBER OUTFLOWS',
    'HERA TO REVEAL CLOSE-UPS OF ASTEROID IN EARTH TEST',
    'UKRAINE LEGALISES CRYPTO MARKET FROM JULY 2027',
    'US UNVEILS F-15EX FIGHTERS AT OKINAWA BASE',
    'NOLLYWOOD STAR PETE EDOCHIE DIES AGED 79',
    'DOJ LAUNCHES BIGGEST SCAM CRACKDOWN: 800+ CHARGED',
]

NUMBERS = [
    ('$94', 'BRENT CRUDE AFTER THE HOUTHI REFINERY ATTACK'),
    ('500,000', "RUSSIAN WAR DEAD, PER MOSCOW'S OWN FIGURES"),
    ('35%', 'TOP TARIFF RATE PROPOSED BY THE USTR'),
    ('1,000,000', 'SATELLITES SPACEX MAY LAUNCH FOR AI DATA'),
    ('36%', 'BANGLADESH GARMENT WAGE RISE'),
    ('$4.71BN', 'RECORD NOVEMBER OUTFLOWS FROM BITCOIN ETFS'),
]

SPORT_1 = 'SPORT  •  SOORYAVANSHI, 15, HITS RECORD 52-BALL DOUBLE TON'
SPORT_2 = ('GUKESH v SINDAROV, GAME 3 OF WORLD TITLE MATCH  •  SENEGAL '
           'REINSTATED AS AFCON 2025 CHAMPIONS  •  IPL AUCTION DRAWS '
           '1,220 PLAYERS')

# ------------------------------------------------------------------ layout
COL_X = (24, 354, 684)
COL_W = 314
CARD_ROWS = (424, 534, 644, 754)
CARD_H = 104


def draw_masthead(cv):
    cv.rect(0, 0, W, 78, NAVY)
    cv.text_centred(W // 2, 14, 'THE WORLD', 6, WHITE)
    cv.text_centred(W // 2, 62, 'THE NEWSPAPER OF RECORD FOR ONE DAY ONLY',
                    1, LIGHT)
    cv.hline(0, W, 78, RED, 3)
    cv.text(24, 86, 'THURSDAY, 26 NOVEMBER 2026', 1, INK)
    right = 'EDITION NO. 330 — PRICE: ONE DOLLAR'
    cv.text(W - 24 - cv.text_width(right, 1), 86, right, 1, INK)
    cv.hline(24, W - 24, 100, NAVY, 1)


def draw_lead(cv):
    cv.text(24, 108, LEAD['kicker'], 1, RED)
    cv.text(24, 124, LEAD['headline'], 3, NAVY)
    draw_para(cv, 24, 154, LEAD['deck'], 1, INK, 976, max_lines=2)
    draw_para(cv, 24, 176, LEAD['body'], 1, INK, 976, max_lines=3)
    cv.hline(24, W - 24, 212, NAVY, 1)


def draw_numbers_rail(cv):
    x = 700
    cv.text(x, 222, 'BY THE NUMBERS', 2, RED)
    y = 246
    for num, label in NUMBERS:
        cv.text(x, y, num, 3, NAVY)
        draw_para(cv, x + 155, y + 2, label, 1, INK, 145, max_lines=2)
        y += 27


def draw_card(cv, x, y, kicker, headline, body):
    cv.text(x, y + 2, kicker, 1, RED)
    draw_para(cv, x, y + 14, headline, 2, NAVY, COL_W, max_lines=2)
    draw_para(cv, x, y + 56, body, 1, INK, COL_W, max_lines=4)


def draw_cards(cv):
    for i, (kicker, headline, body) in enumerate(CARDS):
        col = i % 3
        row = i // 3
        draw_card(cv, COL_X[col], CARD_ROWS[row], kicker, headline, body)


def draw_briefs(cv):
    cv.hline(24, W - 24, 868, NAVY, 1)
    cv.text(24, 876, 'IN BRIEF', 2, RED)
    for i, brief in enumerate(BRIEFS):
        col = i % 3
        row = i // 3
        text = brief if len(brief) <= 50 else brief[:47] + '...'
        cv.text(COL_X[col], 900 + row * 18, text, 1, INK)


def draw_sport(cv):
    cv.rect(0, 966, W, H, RED)
    cv.text_centred(W // 2, 974, SPORT_1, 2, WHITE)
    cv.text_centred(W // 2, 996, SPORT_2, 1, WHITE)


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_lead(cv)
    draw_map(cv)
    draw_numbers_rail(cv)
    cv.hline(24, W - 24, 416, NAVY, 1)
    draw_cards(cv)
    draw_briefs(cv)
    draw_sport(cv)
    return encode_png(W, H, cv.px)


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    data = build()
    path = os.path.join(out_dir, 'entry.png')
    with open(path, 'wb') as f:
        f.write(data)
    print('WROTE %s %d bytes' % (path, len(data)))


if __name__ == '__main__':
    main()
