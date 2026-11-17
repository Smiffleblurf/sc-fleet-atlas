#!/usr/bin/env python3
"""Render an overhead ship silhouette from an RSI Holoviewer OpenCTM mesh.

This developer-only tool processes a model supplied on disk. It never contacts
RSI or handles imported user hangar data. Mesh files are not distributed with
Fleet Atlas; use only models for which your intended use is permitted.

Dependencies: pip install numpy pillow openctm
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def silhouette(input_path: Path, size: int = 512, padding: int = 28,
               vertical_axis: int = 1, rotation: int = 180) -> Image.Image:
    import openctm

    with input_path.open('rb') as model_file:
        mesh = openctm.load_ctm(model_file)
    vertices = np.asarray(mesh['vertices'], dtype=np.float64)
    faces = np.asarray(mesh['faces'], dtype=np.int32)
    if vertices.ndim != 2 or vertices.shape[1] != 3 or not len(faces):
        raise ValueError('Expected a triangle mesh with XYZ vertices')
    if vertical_axis not in (0, 1, 2):
        raise ValueError('Vertical axis must be 0, 1, or 2')

    # RSI Holoviewer CTM assets observed to use Y-up; view X/Z from above.
    # Using normalized full-model extents retains the hull's true proportions.
    horizontal = [axis for axis in (0, 1, 2) if axis != vertical_axis]
    projected = vertices[:, horizontal]
    span = np.ptp(projected, axis=0)
    if min(span) <= 0:
        raise ValueError('Model has zero extent on a projection axis')
    scale = (size - 2 * padding) / float(max(span))
    pixels = (projected - (projected.min(0) + projected.max(0)) / 2) * scale
    pixels[:, 0] += size / 2
    pixels[:, 1] += size / 2
    pixels[:, 1] = size - pixels[:, 1]

    mask = Image.new('L', (size, size), 0)
    pen = ImageDraw.Draw(mask)
    # Orthographic union of projected mesh triangles. A low-quality or open
    # render mesh may leave tiny holes, handled conservatively below.
    for a, b, c in faces:
        pen.polygon((tuple(pixels[a]), tuple(pixels[b]), tuple(pixels[c])), fill=255)
    mask = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    result = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    result.putalpha(mask)
    return result.rotate(rotation) if rotation else result


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('model', type=Path, help='Locally available .ctm mesh')
    cli.add_argument('image', type=Path, help='Output transparent PNG')
    cli.add_argument('--size', type=int, default=512)
    cli.add_argument('--padding', type=int, default=28)
    cli.add_argument('--up-axis', type=int, default=1, choices=(0, 1, 2))
    cli.add_argument('--rotation', type=int, default=180, choices=(0, 90, 180, 270))
    args = cli.parse_args()
    if not 128 <= args.size <= 2048:
        cli.error('--size must be 128 to 2048')
    if not 0 <= args.padding < args.size / 3:
        cli.error('--padding must be nonnegative and less than one-third of size')
    img = silhouette(args.model, size=args.size, vertical_axis=args.up_axis,
                     rotation=args.rotation, padding=args.padding)
    img.save(args.image)
    print(f'Created {args.image} ({img.width}×{img.height}, transparent PNG)')


if __name__ == '__main__':
    main()
