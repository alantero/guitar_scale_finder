# Fretboard Plotter

A small CLI tool that renders a guitar fretboard diagram and highlights a set of pitch classes (scales, chords, or any custom note collection). It supports:

- **Note-name input** (e.g., `C E G Bb D`)
- **Scale-degree input** (e.g., `1 2 3 #4 5 6 7`) converted to notes from a given root
- Up to **24 frets**
- Standard tuning by default (custom tuning supported)
- Optional **left-handed** view
- Optional **wood-like** background
- High-resolution raster output (PNG, etc.) and vector output (SVG/PDF)

---

## Files

- `fretboard_plot.py` (the current script version with both note-name and degree input)

---

## Requirements

- Python 3.8+
- `numpy`
- `matplotlib`

Install dependencies:

```bash
pip install numpy matplotlib
