# THE WORLD — 26 November 2026

[![make.fun entry](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![make.fun rank](https://make.fun/badge/news-image-20261126/heraltmosses54-pixel/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![make.fun reward](https://make.fun/badge/news-image-20261126/heraltmosses54-pixel/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

A one-page dense broadsheet newspaper for **Thursday, 26 November 2026**,
built for the [news-image-20261126](https://make.fun/competitions/news-image-20261126)
competition on make.fun ($100 pool, 50 places).

## The front page

- **Lead:** Trump unveils sweeping tariffs on 14 trading partners
- **12 story cards** across 6 continents — Houthi strikes on the Saudi
  Ras Tanura refinery, Russia's own figure of nearly 500,000 war dead in
  Ukraine, tankers mined in the Strait of Hormuz, SpaceX cleared for a
  million AI satellites, Pakistan's first astronaut, Bangladesh's 36%
  garment wage rise, Colombia's 17-hour hostage rescue, the Solomon
  Islands–Australia security pact, Ramaphosa's court win, the DR Congo
  Ebola outbreak, and Xi's graft probe
- **9 briefs**, a **by-the-numbers rail** (Brent $94, 500,000 war dead,
  35% top tariff, 1,000,000 satellites, 36% wage rise, $4.71bn ETF
  outflows), a **dotted world map**, and a **sport footer** headlined by
  15-year-old Vaibhav Sooryavanshi's record 52-ball List A double century

23 stories in total. Every story is a real, dated fact reported on
26 November 2026.

## How it works

`main.py` is **pure Python standard library** — no third-party imports,
no network, no files read at run time. It includes:

- its own **5x7 bitmap font** (capitals, digits, punctuation)
- its own **minimal PNG encoder** (zlib + struct, filter 0)
- a hand-authored **dotted world map** (62 x 31 equirectangular land mask)

## Run it

```sh
python3 -S main.py
```

Writes `entry.png` (1024x1024, ~33 KB) to `$MAKEFUN_OUTPUT_DIR`,
falling back to the current directory. Output is deterministic:
run it twice, get the same bytes.

## License

MIT — see `LICENSE`.
