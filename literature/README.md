# Literature

| File | What it is |
|---|---|
| [G14_Literature_Matrix.csv](G14_Literature_Matrix.csv) | The literature matrix: 18 papers × authors, title, venue, theme, problem, method, dataset, key result, limitation/gap, year, DOI. Shows as a table on GitHub. |
| [G14_Literature_Matrix.xlsx](G14_Literature_Matrix.xlsx) | The same matrix in Excel, plus a **Themes & Gap** sheet: requirement check (18 papers, 72% from 2021 or later), the three themes and the research gap. |
| [G14_references.bib](G14_references.bib) | All 24 references of the paper in BibTeX, numbered [1]–[24] in the `note` field. Import into Zotero (File → Import) or use in Overleaf. |

**Themes:** vectorised CPU execution & SIMD (8 papers) · GPU & new hardware (6) · columnar formats, Arrow & dataframes (4).

**Research gap:** few studies separate how much of an embedded engine's speed-up over Pandas comes from its execution model (vectorisation/SIMD) and how much from extra CPU cores, on ordinary hardware. Our study measures both by running DuckDB on 1 thread and on all threads.
