# MRI contact-sheet PDFs

Each source image folder was combined into one PDF, 9 images per A4 page.

| PDF | Source folder | Images | Pages |
| --- | --- | --- | --- |
| `MNWAA_FAIAD_SALEEM_EL_ANZY_195142.pdf` | `MNWAA_FAIAD_SALEEM_EL_ANZY 195142/2026-07-29 221706` | 204 | 23 |
| `Naif_2.pdf` | `Naif 2/ALANAZI_MUNWAH_FAYADH 2265245/2026-03-03 234950` | 190 | 22 |

## No quality loss

The original JPEG streams are embedded verbatim as `/DCTDecode` image XObjects —
the files are never decoded, resampled, or re-encoded. Every embedded stream was
verified byte-identical (SHA-256) to its source `.jpg`, so the PDFs carry the
images at full original resolution; on-page size only affects display scale.

## Layout

- Page is 841.9 x 868.9 pt: A3 width (297 mm) with the height cropped to the
  image grid, so there is no white margin around or between the rows.
- 3 x 3 grid, images ordered by series then instance number
  (`IMG-<series>-<instance>`).
- Each cell is 276 pt (9.7 cm) square. Aspect ratio is preserved per image and
  never cropped, so portrait slices are height-limited within their cell.
- Each image is captioned with its source filename for cross-reference.
- Printed on A3 paper at "fit to page", the images come out at their maximum
  possible size for a 9-up sheet.

## Regenerating

```
pip install pillow pikepdf
python make_contact_sheet_pdf.py "<image folder>" "<output.pdf>"
```

Grid, page size and margins are constants at the top of the script.
