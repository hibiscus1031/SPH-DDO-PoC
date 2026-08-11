# DDO-01E Python figure QA

## Contract and backend

- Backend: Python only (`matplotlib` with the non-interactive Agg backend).
- Archetype: quantitative grid.
- Final width: approximately 183 mm (double column).
- Exports per figure: editable SVG, PDF, 600-dpi TIFF, and PNG visual-QA preview.
- Source: `data/identifiability/ddo01e_figure_source_data.csv`.

## Visual review

All five PNG previews were inspected at original resolution. Panel labels,
titles, axes, tick labels, legends, cell annotations, and frozen gate lines are
readable without overlap. The heatmap outlines denote a single point threshold
only and are explicitly not presented as complete H3 PASS cells. Long-tail
metrics remain on their natural scale so adverse strata are not visually
suppressed.

## Export audit

- Every SVG contains editable `<text>` nodes (34 to 166 per file).
- Python PDF inspection found embedded Type0 Arial/Arial-Bold fonts in every
  PDF. The host did not provide the external `pdffonts` utility, so the audit
  used `pypdf` instead.
- Every TIFF is RGB, LZW-compressed, and records 600 x 600 dpi.
- TIFF dimensions range from 4,391 to 4,392 pixels wide and 1,659 to 2,769
  pixels high.
- PNG files are QA previews only; SVG is the editable primary output.

No raster microscopy, manual retouching, selective image adjustment, or visual
post-processing outside Python was used.

