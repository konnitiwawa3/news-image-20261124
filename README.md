# The World Dispatch

Tuesday, 24 November 2026 · Early edition through 02:15 UTC

A one-page English newspaper with 35 reports and three scheduled items across nine regions. The lead is the report from Iran's Revolutionary Guard about fires aboard three oil tankers in the Strait of Hormuz. The scene is drawn for this edition. The page attributes the report and marks scheduled items with TODAY. Source links, timing, and coverage notes live in [edition.json](edition.json).

The palette uses Astryx Stone Light for editorial ink, labels, panels, and dividers. The layout uses its 4 px spacing scale for section and column gaps.

## Render

Run with Python 3.13 and the bundled glyph masks.

```sh
MAKEFUN_OUTPUT_DIR=./preview python3.13 -P -s main.py
```

The program writes a 1024 × 1024 RGB PNG named `entry.png` to `MAKEFUN_OUTPUT_DIR`, which defaults to `/output`. It uses only the Python standard library and files in the repository. The rasterizer and type assets are adapted from the preceding edition by The World Dispatch contributors. The font license notices are in `fonts/`.
