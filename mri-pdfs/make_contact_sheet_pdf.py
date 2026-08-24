#!/usr/bin/env python3
"""Combine MRI JPEGs into a 9-per-page PDF with zero re-encoding.

Original JPEG bytes are embedded verbatim as /DCTDecode image XObjects, so
pixel data is bit-identical to the source files.
"""
import os
import re
import sys
from PIL import Image
import pikepdf
from pikepdf import Name, Dictionary, Array, String

# A4 portrait, points
PW, PH = 595.276, 841.890
MARGIN = 11.0
GUTTER = 4.0
LABEL_H = 9.0
LABEL_SIZE = 6.0
COLS, ROWS = 3, 3
PER_PAGE = COLS * ROWS


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
        cs, bpc = Name.DeviceGray, 8
    elif mode == 'CMYK':
        cs, bpc = Name.DeviceCMYK, 8
    else:
        cs, bpc = Name.DeviceRGB, 8
    xobj = pikepdf.Stream(pdf, raw)
    xobj.Type = Name.XObject
    xobj.Subtype = Name.Image
    xobj.Width = w
    xobj.Height = h
    xobj.ColorSpace = cs
    xobj.BitsPerComponent = bpc
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

    usable_w = PW - 2 * MARGIN
    usable_h = PH - 2 * MARGIN
    cell_w = (usable_w - (COLS - 1) * GUTTER) / COLS
    cell_h = (usable_h - (ROWS - 1) * GUTTER) / ROWS
    slot_h = cell_h - (LABEL_H if label else 0)

    for start in range(0, len(files), PER_PAGE):
        chunk = files[start:start + PER_PAGE]
        placed = []          # (xobj_name, xobj, draw_w, draw_h, caption)
        resources = Dictionary()
        for idx, path in enumerate(chunk):
            xobj, w, h = make_xobject(pdf, path)
            scale = min(cell_w / w, slot_h / h)
            resources[f'/Im{idx}'] = pdf.make_indirect(xobj)
            placed.append((f'/Im{idx}', w * scale, h * scale,
                           os.path.splitext(os.path.basename(path))[0]))

        # row heights from the tallest drawn image in each row -> tight grid
        row_h = []
        for r in range(ROWS):
            row = placed[r * COLS:(r + 1) * COLS]
            if not row:
                break
            row_h.append(max(p[2] for p in row) + (LABEL_H if label else 0))
        block_h = sum(row_h) + (len(row_h) - 1) * GUTTER
        top_y = MARGIN + usable_h - (usable_h - block_h) / 2

        ops = []
        y_cursor = top_y
        for r, rh in enumerate(row_h):
            row = placed[r * COLS:(r + 1) * COLS]
            for c, (nm, dw, dh, cap) in enumerate(row):
                cell_x = MARGIN + c * (cell_w + GUTTER)
                x = cell_x + (cell_w - dw) / 2
                y = y_cursor - (LABEL_H if label else 0) - dh
                ops.append(f'q {dw:.3f} 0 0 {dh:.3f} {x:.3f} {y:.3f} cm {nm} Do Q')
                if label:
                    ty = y - LABEL_H + 2.0
                    tw = len(cap) * LABEL_SIZE * 0.5   # Helvetica avg width
                    tx = cell_x + max(0.0, (cell_w - tw) / 2)
                    ops.append(
                        f'q BT /F1 {LABEL_SIZE} Tf 0.35 0.35 0.35 rg '
                        f'{tx:.3f} {ty:.3f} Td ({esc(cap)}) Tj ET Q')
            y_cursor -= rh + GUTTER

        content = pikepdf.Stream(pdf, '\n'.join(ops).encode('ascii'))
        page_dict = Dictionary(
            Type=Name.Page,
            MediaBox=Array([0, 0, PW, PH]),
            Resources=Dictionary(XObject=resources,
                                 Font=Dictionary(F1=font)),
            Contents=pdf.make_indirect(content))
        pdf.pages.append(pikepdf.Page(pdf.make_indirect(page_dict)))

    with pdf.open_metadata() as meta:
        meta['dc:title'] = os.path.splitext(os.path.basename(out_path))[0]
    pdf.save(out_path, linearize=False)
    return len(files), len(pdf.pages)


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    n_img, n_pg = build(src, dst)
    print(f'{dst}: {n_img} images -> {n_pg} pages')
