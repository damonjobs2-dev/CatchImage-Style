#!/usr/bin/env python3
"""Local palette sampling; Pillow is optional and never installed by this tool."""
import argparse
import json
import sys


def sample(path, colors=8):
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise RuntimeError('Pillow unavailable; use host image sampling or label colors as visual estimates.') from exc
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original).convert('RGBA')
        width, height = image.size
        image.thumbnail((320, 320))
        data = image.get_flattened_data() if hasattr(image, 'get_flattened_data') else image.getdata()
        pixels = [(r, g, b) for r, g, b, a in data if a >= 128]
    if not pixels:
        return {'width': width, 'height': height, 'sampledPixels': 0, 'swatches': [], 'note': 'No opaque pixels.'}
    strip = Image.new('RGB', (len(pixels), 1))
    strip.putdata(pixels)
    indexed = strip.quantize(colors=colors, method=Image.Quantize.MEDIANCUT)
    palette = indexed.getpalette()
    counts = sorted(indexed.getcolors(), reverse=True)
    return {'width': width, 'height': height, 'sampledPixels': len(pixels),
            'method': 'EXIF oriented, thumbnail <=320px, alpha>=128, median-cut',
            'swatches': [{'hex': '#%02X%02X%02X' % tuple(palette[i*3:i*3+3]),
                          'share': round(count / len(pixels), 6)} for count, i in counts]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image')
    parser.add_argument('--colors', type=int, default=8, choices=range(2, 17))
    args = parser.parse_args()
    try:
        print(json.dumps(sample(args.image, args.colors), ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
