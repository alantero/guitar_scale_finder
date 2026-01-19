# Guitar Scale Finder (Fretboard GUI)

A small Python app that renders a **guitar fretboard** and highlights notes based on what you select in a **PyQt (Qt) GUI**.  
It is useful for visualizing **chords, scales, and custom degree formulas** across the neck (up to 24 frets).

![GUI Screenshot](docs/gui.png)

---

## Features

### Interactive Fretboard
- 6-string guitar fretboard (default tuning: **E A D G B E**).
- Up to **24 frets**.
- **Wood background** enabled by default for a more realistic look.
- Root notes are highlighted with an extra ring.

### Input Modes
The GUI supports three ways to define what gets plotted:

1) **Notes**
- Type note names separated by spaces (e.g. `C E G Bb D`)
- The app will plot those pitch classes everywhere on the fretboard.

2) **Degrees**
- Type scale degrees relative to a chosen root (e.g. `1 b3 5` or `1 2 3 #4 5 6 7`)
- Supported accidentals:
  - `b` = -1 semitone
  - `#` = +1 semitone
  - `x` = +2 semitones
- Examples:
  - `b2`, `#4`, `bb7`, `x4`
- Root aliases:
  - `R`, `root` are treated as `1`

3) **Scale**
- Choose a scale from a dropdown list (loaded from `scales.py`)
- The app generates the note set using the interval steps of that scale.

### Root Selection
- Choose a **root note** from a dropdown (sharps or flats).
- The root field is also **editable** (you can type directly).
- A checkbox lets you **prefer flats** (Db, Eb, Gb, Ab, Bb) instead of sharps.

### Controls
- **Frets**: select 1–24 frets.
- **Run**: renders the selected notes on the fretboard.
- **Clear**: removes notes and shows an empty fretboard.
- A **status bar** shows messages and errors (invalid note tokens, invalid degrees, etc.).

---

## Project Structure

- `fretboard_gui.py`  
  The Qt GUI: input widgets + embedded Matplotlib canvas + Run/Clear logic.

- `fretboard_core.py`  
  Rendering engine + note parsing + degrees conversion + fretboard drawing on a Matplotlib Axes.

- `scales.py`  
  Scale dictionary (`SCALE_MODES`) with interval steps (semitones) that sum to 12.

---

## Requirements

- Python 3.9+ recommended
- Dependencies:
  - `numpy`
  - `matplotlib`
  - `PyQt6` (recommended) **or** `PyQt5`

Install (PyQt6):
```bash
pip install numpy matplotlib pyqt6
````

Or (PyQt5):

```bash
pip install numpy matplotlib pyqt5
```

---

## Run

From the repository folder:

```bash
python fretboard_gui.py
```

If you are on Linux and your system uses a different Qt setup, you may need to ensure that Matplotlib is using a Qt backend (the code sets `QtAgg`).

---

## Notes / Tips

* If you see an empty fretboard: choose a mode, enter data (or select a scale), then press **Run**.
* If you type something invalid (e.g. an unsupported note name), the error will appear in the **status bar**.
* Flats/sharps preference affects displayed note names (pitch classes are the same).

---

## License

Add your preferred license here (MIT, Apache-2.0, etc.).

```
::contentReference[oaicite:0]{index=0}
```
