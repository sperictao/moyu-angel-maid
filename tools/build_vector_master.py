#!/usr/bin/env python3
"""Trace a Codex Pet v2 RGBA atlas into a two-layer SVG master.

The generated SVG contains a white silhouette layer and a black ink layer for
all populated 192x208 cells. It does not embed the source raster.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

CELL_W, CELL_H = 192, 208
ROWS = (6, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8)
PATH_RE = re.compile(r'<path\s+d="([^"]+)"')


def trace(mask: Image.Image, temp: Path, name: str) -> list[str]:
    pbm = temp / f"{name}.pbm"
    svg = temp / f"{name}.svg"
    mask.save(pbm)
    subprocess.run(["potrace", "-s", "-t", "2", "-a", "0.6", "--opttolerance", "0.2", str(pbm), "-o", str(svg)], check=True)
    return PATH_RE.findall(svg.read_text())


def cell_paths(cell: Image.Image, temp: Path, name: str) -> tuple[list[str], list[str]]:
    alpha = cell.getchannel("A")
    luminance = cell.convert("L")
    visible = alpha.point(lambda value: 0 if value > 24 else 255)
    ink = Image.new("1", cell.size, 255)
    ink_pixels = ink.load()
    alpha_pixels = alpha.load()
    lum_pixels = luminance.load()
    for y in range(CELL_H):
        for x in range(CELL_W):
            ink_pixels[x, y] = 0 if alpha_pixels[x, y] > 24 and lum_pixels[x, y] < 185 else 255
    return trace(visible, temp, name + "-silhouette"), trace(ink, temp, name + "-ink")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("atlas", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    atlas = Image.open(args.atlas).convert("RGBA")
    expected = (CELL_W * 8, CELL_H * 11)
    if atlas.size != expected:
        raise SystemExit(f"expected {expected}, got {atlas.size}")

    groups: list[str] = []
    with tempfile.TemporaryDirectory(prefix="moyu-vector-") as temp_dir:
        temp = Path(temp_dir)
        for row, frame_count in enumerate(ROWS):
            for frame in range(frame_count):
                x, y = frame * CELL_W, row * CELL_H
                cell = atlas.crop((x, y, x + CELL_W, y + CELL_H))
                silhouette, ink = cell_paths(cell, temp, f"r{row}-f{frame}")
                paths = [f'<path fill="#fff" fill-rule="evenodd" d="{escape(d)}"/>' for d in silhouette]
                paths += [f'<path fill="#000" fill-rule="evenodd" d="{escape(d)}"/>' for d in ink]
                paths = ['<g transform="translate(0 208) scale(0.1 -0.1)">' + ''.join(paths) + '</g>']
                groups.append(
                    f'<g id="row-{row}-frame-{frame}" transform="translate({x} {y})">'
                    + "".join(paths)
                    + "</g>"
                )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    svg = "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="2288" viewBox="0 0 1536 2288">',
        '<title>Moyu Angel Maid — traced vector master</title>',
        '<desc>Two-layer vector trace of the Codex Pet v2 atlas: white silhouette and black ink paths. Runtime package remains spritesheet.webp.</desc>',
        *groups,
        '</svg>',
        "",
    ])
    args.output.write_text(svg)
    print(f"wrote {args.output} ({len(groups)} populated cells)")


if __name__ == "__main__":
    main()
