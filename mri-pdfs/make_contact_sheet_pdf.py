#!/usr/bin/env python3
"""Combine MRI JPEGs into a 9-per-page PDF with zero re-encoding.

Original JPEG bytes are embedded verbatim as /DCTDecode image XObjects, so
pixel data is bit-identical to the source files.

Page width is A3 (297 mm); page height is cropped to the image grid so no
white margin is left over. Images are scaled to fill their cell.
"""
import os
import re
import sys
from PIL import Image
import pikepdf
from pikepdf import Name, Dictionary, Array

MM = 72.0 / 25.4
PW = 297.0 * MM          # A3 width (841.89 pt); height is derived from content
MARGIN = 4.0
GUTTER = 3.0
LABEL_H = 9.0
LABEL_SIZE = 6.0
COLS, ROWS = 3, 3
PER_PAGE = COLS * ROWS

# Square cells: the studies are dominated by square images, so a square cell
# gives the tightest crop while still fitting portrait slices without distortion.
CELL_W = (PW - 2 * MARGIN - (COLS - 1) * GUTTER) / COLS
CELL_H = CELL_W
ROW_H = CELL_H + LABEL_H
PH = 2 * MARGIN + ROWS * ROW_H + (ROWS - 1) * GUTTER


def natural_key(path):
    name = os.path.basename(path)
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', name)]


def collect(folder):
    files = []
    for dirpath, _, names in os.walk(folder):
        for n in names:
            if n.lower().endswith(('.jpg', '.jpeg')):
                files.append(os.path.join(dirpath, n))
    files.sort(key=lambda p: (os.path.dirname(p).lower(), natural_key(p)))
    return files


def make_xobject(pdf, path):
    with open(path, 'rb') as fh:
        raw = fh.read()
    with Image.open(path) as im:
        w, h = im.size
        mode = im.mode
    if mode in ('L', '1'):
        cs = Name.DeviceGray
    elif mode == 'CMYK':
        cs = Name.DeviceCMYK
    else:
        cs = Name.DeviceRGB
    xobj = pikepdf.Stream(pdf, raw)
    xobj.Type = Name.XObject
    xobj.Subtype = Name.Image
    xobj.Width = w
    xobj.Height = h
    xobj.ColorSpace = cs
    xobj.BitsPerComponent = 8
    xobj.Filter = Name.DCTDecode
    return xobj, w, h


def esc(text):
    return text.replace('\\', r'\\').replace('(', r'\(').replace(')', r'\)')


def build(folder, out_path, label=True):
    files = collect(folder)
    if not files:
        raise SystemExit(f'no images found in {folder}')

    pdf = pikepdf.new()
    font = pdf.make_indirect(Dictionary(
        Type=Name.Font, Subtype=Name.Type1,
        BaseFont=Name.Helvetica, Encoding=Name.WinAnsiEncoding))

    for start in range(0, len(files), PER_PAGE):
        chunk = files[start:start + PER_PAGE]
        resources = Dictionary()
        ops = []
        for idx, path in enumerate(chunk):
            xobj, w, h = make_xobject(pdf, path)
            resources[f'/Im{idx}'] = pdf.make_indirect(xobj)

            scale = min(CELL_W / w, CELL_H / h)
            dw, dh = w * scale, h * scale

            r, c = divmod(idx, COLS)
            cell_x = MARGIN + c * (CELL_W + GUTTER)
            cell_top = PH - MARGIN - r * (ROW_H + GUTTER)
            x = cell_x + (CELL_W - dw) / 2
            y = cell_top - CELL_H + (CELL_H - dh) / 2
            ops.append(f'q {dw:.3f} 0 0 {dh:.3f} {x:.3f} {y:.3f} cm /Im{idx} Do Q')

            if label:
                cap = os.path.splitext(os.path.basename(path))[0]
                tw = len(cap) * LABEL_SIZE * 0.5      # Helvetica average width
                tx = cell_x + max(0.0, (CELL_W - tw) / 2)
                ty = cell_top - CELL_H - LABEL_H + 2.5
                ops.append(
                    f'q BT /F1 {LABEL_SIZE} Tf 0.35 0.35 0.35 rg '
                    f'{tx:.3f} {ty:.3f} Td ({esc(cap)}) Tj ET Q')

        content = pikepdf.Stream(pdf, '\n'.join(ops).encode('ascii'))
        page_dict = Dictionary(
            Type=Name.Page,
            MediaBox=Array([0, 0, PW, PH]),
            Resources=Dictionary(XObject=resources, Font=Dictionary(F1=font)),
            Contents=pdf.make_indirect(content))
        pdf.pages.append(pikepdf.Page(pdf.make_indirect(page_dict)))

    with pdf.open_metadata() as meta:
        meta['dc:title'] = os.path.splitext(os.path.basename(out_path))[0]
    pdf.save(out_path, linearize=False)
    return len(files), len(pdf.pages)


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    n_img, n_pg = build(src, dst)
    print(f'{dst}: {n_img} images -> {n_pg} pages, page {PW:.1f} x {PH:.1f} pt, '
          f'cell {CELL_W:.1f} pt')
