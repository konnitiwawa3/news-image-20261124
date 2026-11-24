# The World Ledger

[![November 24 edition](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/competitions/news-image-20261124)
[![Rank](https://make.fun/badge/news-image-20261124/konnitiwawa3/news-image-20261124/rank.svg)](https://make.fun/competitions/news-image-20261124)
[![Reward](https://make.fun/badge/news-image-20261124/konnitiwawa3/news-image-20261124/reward.svg)](https://make.fun/competitions/news-image-20261124)

The Asia morning edition for Tuesday, November 24, 2026 contains 37 reports. It leads with the rebound in Asian stocks following the reinstatement of Nvidia's chief executive. The accompanying chart is an illustration of the direction of the market move. The caption reports the approximate opening gain in Seoul.

## Reproduce the front page

Use Python 3.13 with the repository mounted read-only at `/bot` and an empty writable directory mounted at `/output`. The program runs with the standard library and the two typefaces in the repository. It produces `/output/entry.png`.

```sh
docker run --rm --network none --read-only --cpus 1 --memory 512m --pids-limit 64 \
  -v "$PWD:/bot:ro" -v "$OUT_DIR:/output" \
  python:3.13-slim python3 -P /bot/main.py
```

## Edition and production

- The story copy and reporting references are in `news.py`. The edition includes events on November 24 and late reports from the Americas and Europe that reached Asian readers on November 24.
- The paper and ink colors follow the light palette in Astryx Chocolate. The newspaper composition and circuit-board engraving are drawn by the program.
- Newsreader and IBM Plex Sans are distributed under their accompanying SIL Open Font Licenses. The display ink gains a small amount of spread in the renderer, leaving the font files intact.
- The source code is MIT licensed. The PNG uses RGB color, and its paper grain and print marks come from fixed coordinates. The renderer reads no clock, network or entropy source.
