````markdown
# Fretboard Plotter

A small CLI tool that renders a guitar fretboard diagram and highlights a set of pitch classes (scales, chords, or any custom note collection). It supports:

- Note-name input (e.g., "C E G Bb D")
- Scale-degree input (e.g., "1 2 3 #4 5 6 7") converted to notes from a given root
- Up to 24 frets
- Standard tuning by default (custom tuning supported)
- Optional left-handed view
- Optional wood-like background
- High-resolution raster output (PNG, etc.) and vector output (SVG/PDF)

---

## Files

- fretboard_plot_degrees.py (the current script version with both note-name and degree input)

---

## Requirements

- Python 3.8+
- numpy
- matplotlib

Install dependencies:

```bash
pip install numpy matplotlib
````

---

## Basic Usage (Note Names)

Pass the notes you want to highlight directly:

```bash
python fretboard_plot_degrees.py "C E G Bb D" --root C --frets 24 --dpi 450 --wood_background --out fretboard_C9.png
```

Notes can be separated by spaces or commas.

### Flats vs Sharps display

To display flats (Db, Eb, Gb, Ab, Bb) instead of sharps (C#, D#, F#, G#, A#):

```bash
python fretboard_plot_degrees.py "C Db E Gb Ab Bb B" --use_flats --root C --frets 24 --dpi 450 --wood_background --out enigmatic_C.png
```

---

## Degree Input Mode

Enable --degrees to interpret the positional argument as scale degrees relative to --root.

### Degree token notation

* Plain degrees: 1 2 3 4 5 6 7
* Accidentals:

  * b = -1 semitone (flat)
  * # = +1 semitone (sharp)
  * x = +2 semitones (double-sharp)
* Accidentals can be prefix or suffix:

  * b2 or 2b
  * #4 or 4#
  * bb7, ##4, x4
* Root aliases:

  * R or root is treated as 1

Degrees higher than 7 wrap by scale degree class (e.g., 9 -> 2, 11 -> 4, 13 -> 6), affecting pitch class only.

### Example: Lydian degrees

Lydian is: 1 2 3 #4 5 6 7

Root F gives: F G A B C D E

```bash
python fretboard_plot_degrees.py "1 2 3 #4 5 6 7" --degrees --root F --frets 24 --dpi 450 --wood_background --out lydian_F.png
```

Root C gives: C D E F# G A B

```bash
python fretboard_plot_degrees.py "1 2 3 #4 5 6 7" --degrees --root C --frets 24 --dpi 450 --wood_background --out lydian_C.png
```

### Example: Locrian degrees in B

Locrian is: 1 b2 b3 4 b5 b6 b7

```bash
python fretboard_plot_degrees.py "1 b2 b3 4 b5 b6 b7" --degrees --root B --frets 24 --dpi 450 --wood_background --out locrian_B.png
```

---

## Scale Mode Generation (Optional)

If you do not pass scale_input, you can generate a built-in scale with --mode and --root:

```bash
python fretboard_plot_degrees.py --root C --mode major --frets 24 --dpi 450 --wood_background --out C_major.png
```

Available modes depend on what is defined in SCALE_MODES in the script (e.g., major, minor, etc.).

---

## Tuning

Default tuning is standard guitar:

E A D G B E

Provide custom tuning (low-to-high):

```bash
python fretboard_plot_degrees.py "C D E F G A B" --root C --tuning "D G C F A D" --frets 24 --dpi 450 --out custom_tuning.png
```

---

## Left-Handed View

```bash
python fretboard_plot_degrees.py "C E G" --root C --frets 24 --left_handed --dpi 450 --out C_triad_left.png
```

---

## Output Quality

For sharp, readable output (especially at 24 frets), increase DPI:

```bash
python fretboard_plot_degrees.py "C E G Bb D" --root C --frets 24 --dpi 450 --wood_background --out high_res.png
```

### Vector output (recommended for infinite zoom)

```bash
python fretboard_plot_degrees.py "C E G Bb D" --root C --frets 24 --wood_background --format svg --out fretboard.svg
```

or

```bash
python fretboard_plot_degrees.py "C E G Bb D" --root C --frets 24 --wood_background --format pdf --out fretboard.pdf
```

---

## Command Line Options (Summary)

* scale_input (positional): notes or degrees depending on --degrees
* --degrees: interpret scale_input as degrees instead of note names
* --root: root note (required for --degrees, and for --mode)
* --mode: generate a built-in scale mode (if scale_input is omitted)
* --frets: number of frets (max 24)
* --tuning: tuning low-to-high
* --use_flats: display flats instead of sharps where applicable
* --dpi: output DPI for raster images
* --format: force output format (png, svg, pdf, ...)
* --out: output file path
* --wood_background: enable wood-like background
* --left_handed: flip the fretboard view
* --fig_w, --fig_h: override figure size (inches)
* --fontsize: base font size

---

## Notes / Limitations

* The tool highlights pitch classes (note names modulo octave), not specific positions/fingerings.
* Degree-to-note conversion is based on major-scale degree reference (1..7) with accidentals shifting semitones.
* Enharmonic spelling is simplified; --use_flats switches display preference for common sharp notes.

---

## License

Do whatever you want with it.

```
::contentReference[oaicite:0]{index=0}
```
