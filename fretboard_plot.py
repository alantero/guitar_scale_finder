#!/usr/bin/env python3
# fretboard_plot.py

import argparse
from typing import List, Set, Tuple, Dict

import numpy as np
import matplotlib.pyplot as plt


CHROMATIC_SHARPS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CHROMATIC_FLATS  = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

SHARP_TO_FLAT = {"C#": "Db", "D#": "Eb", "F#": "Gb", "G#": "Ab", "A#": "Bb"}
FLAT_TO_SHARP = {"Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#", "Ab": "G#", "Bb": "A#", "Cb": "B"}
ENHARMONIC = {"B#": "C", "E#": "F"}

NOTE_TO_INDEX_SHARPS: Dict[str, int] = {n: i for i, n in enumerate(CHROMATIC_SHARPS)}
NOTE_TO_INDEX_FLATS: Dict[str, int] = {n: i for i, n in enumerate(CHROMATIC_FLATS)}

SCALE_MODES = {
    "major": [2, 2, 1, 2, 2, 2, 1],
    "minor": [2, 1, 2, 2, 1, 2, 2],
    "pentatonic_major": [2, 2, 3, 2, 3],
    "pentatonic_minor": [3, 2, 2, 3, 2],
    "blues": [3, 2, 1, 1, 3, 2],
}

DEFAULT_TUNING = "E A D G B E"

# Major scale degree offsets as reference (1..7)
DEGREE_BASE_OFFSETS: Dict[int, int] = {1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11}


def normalize_note(note: str, use_flats: bool = False) -> str:
    n = note.strip().upper().replace(" ", "")
    if not n:
        raise ValueError("Empty note")

    # Support "b" / "B" as flat (e.g., "Bb" -> "BB" after upper)
    if len(n) >= 2 and n[1] in ["#", "B"]:
        if n[1] == "B":
            n = n[0] + "b"
        else:
            n = n[0] + "#"
    else:
        n = n[0]

    if n in FLAT_TO_SHARP:
        n = FLAT_TO_SHARP[n]
    if n in ENHARMONIC:
        n = ENHARMONIC[n]
    if n not in NOTE_TO_INDEX_SHARPS:
        raise ValueError(f"Unsupported note: {note}")

    if use_flats and n in SHARP_TO_FLAT:
        return SHARP_TO_FLAT[n]
    return n


def parse_notes(notes_str: str, use_flats: bool = False) -> List[str]:
    raw = [x for x in notes_str.replace(",", " ").split() if x.strip()]
    return [normalize_note(x, use_flats) for x in raw]


def unique_preserve_order(items: List[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for x in items:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def generate_scale(root: str, mode: str, use_flats: bool = False) -> List[str]:
    if mode not in SCALE_MODES:
        raise ValueError(f"Unsupported mode: {mode}. Available: {list(SCALE_MODES.keys())}")

    root_n = normalize_note(root, use_flats=False)
    root_idx = NOTE_TO_INDEX_SHARPS[root_n]
    intervals = SCALE_MODES[mode]

    notes = [root_n]
    idx = root_idx
    for step in intervals:
        idx = (idx + step) % 12
        notes.append(CHROMATIC_SHARPS[idx])

    if mode.startswith("pentatonic"):
        notes = notes[:-1]

    if use_flats:
        notes = [SHARP_TO_FLAT.get(n, n) for n in notes]
    return notes


def parse_degree_token(token: str) -> Tuple[int, int]:
    """
    Parse a degree token into (degree_number, accidental_shift_semitones).

    Supported examples:
      "1", "2", "7"
      "b3", "#4", "bb7", "##4", "x4"
      "3b", "4#", "7bb"
      "R" (root, same as 1)
    """
    t = token.strip()
    if not t:
        raise ValueError("Empty degree token")

    # Normalize common unicode accidentals to ascii
    t = t.replace("♭", "b").replace("♯", "#")

    if t.lower() in ["r", "root"]:
        return 1, 0

    # We allow accidentals both prefix and suffix: [acc]*[num]+[acc]*
    i = 0
    n = len(t)

    def is_acc(ch: str) -> bool:
        return ch in ["b", "#", "x"]

    prefix = ""
    while i < n and is_acc(t[i]):
        prefix += t[i]
        i += 1

    if i >= n or not t[i].isdigit():
        raise ValueError(f"Invalid degree token: {token}")

    j = i
    while j < n and t[j].isdigit():
        j += 1

    num_str = t[i:j]
    suffix = ""
    k = j
    while k < n and is_acc(t[k]):
        suffix += t[k]
        k += 1

    if k != n:
        raise ValueError(f"Invalid degree token: {token}")

    degree = int(num_str)
    acc = prefix + suffix

    shift = 0
    for ch in acc:
        if ch == "b":
            shift -= 1
        elif ch == "#":
            shift += 1
        elif ch == "x":
            shift += 2

    return degree, shift


def degrees_to_notes(degrees_str: str, root: str, use_flats: bool) -> List[str]:
    """
    Convert a list of degree tokens into note names given a root.

    Degree semantics:
      - Base degrees follow major-scale reference: 1,2,3,4,5,6,7
      - Accidentals shift semitones: b = -1, # = +1, x = +2
      - Degrees > 7 wrap by (degree-1) % 7 for pitch class purposes (9 -> 2, 11 -> 4, 13 -> 6).
    """
    raw = [x for x in degrees_str.replace(",", " ").split() if x.strip()]
    if not raw:
        raise ValueError("No degree tokens provided")

    chromatic = CHROMATIC_FLATS if use_flats else CHROMATIC_SHARPS
    note_to_index = NOTE_TO_INDEX_FLATS if use_flats else NOTE_TO_INDEX_SHARPS

    root_n = normalize_note(root, use_flats=use_flats)
    root_idx = note_to_index[root_n]

    notes: List[str] = []
    for tok in raw:
        deg, shift = parse_degree_token(tok)
        deg_base = ((deg - 1) % 7) + 1
        base_offset = DEGREE_BASE_OFFSETS[deg_base]
        offset = (base_offset + shift) % 12
        notes.append(chromatic[(root_idx + offset) % 12])

    return unique_preserve_order(notes)


def fret_positions_equal_temperament(num_frets: int, scale_length: float) -> np.ndarray:
    frets = np.arange(0, num_frets + 1, dtype=float)
    xs = scale_length * (1.0 - (2.0 ** (-frets / 12.0)))
    xs[0] = 0.0
    return xs


def get_inlay_frets(num_frets: int) -> List[int]:
    base = [3, 5, 7, 9, 12, 15, 17, 19, 21, 24]
    return [f for f in base if f <= num_frets]


def auto_figsize(num_frets: int, fig_w: float, fig_h: float) -> Tuple[float, float]:
    if fig_w <= 0.0:
        fig_w = 0.70 * num_frets + 4.0
    if fig_h <= 0.0:
        fig_h = 4.2 if num_frets > 12 else 3.6
    return fig_w, fig_h


def plot_fretboard(
    scale_notes: List[str],
    root: str,
    tuning: List[str],
    num_frets: int,
    out_path: str,
    scale_length: float,
    dpi: int,
    use_flats: bool,
    note_color: str,
    inlay_color: str,
    left_handed: bool,
    wood_background: bool,
    fig_w: float,
    fig_h: float,
    fmt: str,
    fontsize: int,
) -> None:
    scale_set: Set[str] = set(scale_notes)

    chromatic = CHROMATIC_FLATS if use_flats else CHROMATIC_SHARPS
    note_to_index = NOTE_TO_INDEX_FLATS if use_flats else NOTE_TO_INDEX_SHARPS

    xs = fret_positions_equal_temperament(num_frets, scale_length)
    open_x = xs[0] - 0.60 * (xs[1] - xs[0])

    num_strings = len(tuning)
    ys = np.arange(num_strings, dtype=float)

    if left_handed:
        ys = ys[::-1]
        tuning = list(reversed(tuning))

    y_scale = 1.0

    fig_w, fig_h = auto_figsize(num_frets, fig_w, fig_h)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    if wood_background:
        w = 1024
        h = 256
        base = np.linspace(0, 1, w, dtype=float)
        grain = np.sin(np.linspace(0, 20 * np.pi, w)) * 0.08
        noise = np.random.default_rng(0).normal(0, 0.02, size=w)
        row = np.clip(base + grain + noise, 0, 1)
        img = np.tile(row, (h, 1))
        ax.imshow(
            img,
            extent=[
                open_x - 0.10 * scale_length,
                xs[-1] + 0.02 * scale_length,
                -1.35,
                (num_strings - 1) * y_scale + 1.05,
            ],
            cmap="YlOrBr",
            alpha=0.28,
            aspect="auto",
            zorder=0,
        )

    for si, y in enumerate(ys):
        lw = 2.8 - 0.35 * si
        ax.plot([open_x, xs[-1]], [y * y_scale, y * y_scale], linewidth=lw, color="silver", zorder=1)

    for f, x in enumerate(xs):
        if f == 0:
            ax.plot([x, x], [-0.65, (num_strings - 1) * y_scale + 0.65], linewidth=7.0, color="ivory", zorder=2)
        else:
            ax.plot([x, x], [-0.55, (num_strings - 1) * y_scale + 0.55], linewidth=1.8, color="black", zorder=2)

    inlays = get_inlay_frets(num_frets)
    for f in inlays:
        if f == 0:
            continue
        x_mid = 0.5 * (xs[f - 1] + xs[f])
        y_mid = 0.5 * ((ys[0] + ys[-1]) * y_scale)

        if f in [12, 24]:
            ax.scatter([x_mid, x_mid], [y_mid - 0.45, y_mid + 0.45], s=140, marker="o", c=inlay_color, edgecolors="none", zorder=3)
        else:
            ax.scatter([x_mid], [y_mid], s=140, marker="o", c=inlay_color, edgecolors="none", zorder=3)

    mids = np.empty(num_frets + 1, dtype=float)
    mids[0] = open_x
    if num_frets >= 1:
        mids[1:] = 0.5 * (xs[:-1] + xs[1:])

    x_root, y_root, t_root = [], [], []
    x_norm, y_norm, t_norm = [], [], []

    frets = np.arange(0, num_frets + 1, dtype=int)
    for si, open_note in enumerate(tuning):
        y = float(ys[si] * y_scale)
        open_idx = note_to_index[open_note]

        idxs = (open_idx + frets) % 12
        names = [chromatic[i] for i in idxs]

        for f, name in zip(frets, names):
            if name not in scale_set:
                continue
            x = float(mids[f])
            if name == root:
                x_root.append(x); y_root.append(y); t_root.append(name)
            else:
                x_norm.append(x); y_norm.append(y); t_norm.append(name)

    if x_norm:
        ax.scatter(
            x_norm, y_norm,
            s=440,
            marker="o",
            facecolors=note_color,
            edgecolors="black",
            linewidths=2.0,
            zorder=5,
        )

    if x_root:
        s_main = 520
        ax.scatter(
            x_root, y_root,
            s=s_main,
            marker="o",
            facecolors=note_color,
            edgecolors="black",
            linewidths=3.0,
            zorder=6,
        )
        ax.scatter(
            x_root, y_root,
            s=s_main * 1.18,
            marker="o",
            facecolors="none",
            edgecolors="black",
            linewidths=2.2,
            zorder=7,
        )

    for x, y, n in zip(x_norm, y_norm, t_norm):
        ax.text(x, y, n, ha="center", va="center", fontsize=max(7, fontsize - 1), color="black", zorder=8)

    for x, y, n in zip(x_root, y_root, t_root):
        ax.text(x, y, n, ha="center", va="center", fontsize=fontsize, fontweight="bold", color="black", zorder=9)

    label_x = open_x - 0.07 * scale_length if not left_handed else xs[-1] + 0.07 * scale_length
    ha = "right" if not left_handed else "left"
    for si, open_note in enumerate(tuning):
        ax.text(label_x, float(ys[si] * y_scale), open_note, ha=ha, va="center", fontsize=fontsize)

    for f in range(1, num_frets + 1):
        x = float(0.5 * (xs[f - 1] + xs[f]))
        ax.text(x, -0.95, str(f), ha="center", va="center", fontsize=max(7, fontsize - 1))

    scale_str = " ".join(scale_notes)
    ax.set_title(
        f"Scale: {scale_str}   |   Root: {root}   |   Tuning: {' '.join(tuning)}",
        fontsize=fontsize + 2,
    )

    ax.set_ylim(-1.35, (num_strings - 1) * y_scale + 1.05)
    ax.set_xlim(open_x - 0.10 * scale_length, xs[-1] + 0.02 * scale_length)
    if left_handed:
        ax.invert_xaxis()
    ax.axis("off")

    plt.tight_layout()

    save_kwargs = dict(bbox_inches="tight")
    if fmt:
        save_kwargs["format"] = fmt
        if fmt.lower() in ["png", "jpg", "jpeg", "tif", "tiff", "webp"]:
            save_kwargs["dpi"] = dpi
    else:
        ext = out_path.split(".")[-1].lower()
        if ext in ["png", "jpg", "jpeg", "tif", "tiff", "webp"]:
            save_kwargs["dpi"] = dpi

    fig.savefig(out_path, **save_kwargs)
    plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser(description="Plot a guitar fretboard with scale notes.")
    p.add_argument(
        "scale_input",
        type=str,
        nargs="?",
        default="",
        help='Either note names (e.g. "C D E F G A B") or degrees (e.g. "1 2 3 #4 5 6 7") if --degrees is set.',
    )
    p.add_argument("--degrees", action="store_true", help="Interpret scale_input as scale degrees instead of note names.")
    p.add_argument("--root", type=str, default="", help='Root note, e.g. "C". Required for --degrees and for --mode.')
    p.add_argument("--mode", type=str, default="", choices=list(SCALE_MODES.keys()), help="Scale mode to generate.")
    p.add_argument("--frets", type=int, default=12, help="Number of frets to show (default: 12, max 24).")
    p.add_argument("--tuning", type=str, default=DEFAULT_TUNING, help='Tuning low-to-high, e.g. "E A D G B E".')
    p.add_argument("--out", type=str, default="fretboard.png", help="Output image path.")
    p.add_argument("--format", type=str, default="", help="Output format: png, svg, pdf. Default inferred from --out.")
    p.add_argument("--scale_length", type=float, default=650.0, help="Scale length in mm (default: 650).")
    p.add_argument("--dpi", type=int, default=350, help="Output DPI for raster formats (default: 350).")
    p.add_argument("--use_flats", action="store_true", help="Use flat notation instead of sharps.")
    p.add_argument("--note_color", type=str, default="#FFD24A", help="Color for note markers (hex).")
    p.add_argument("--inlay_color", type=str, default="#B0B0B0", help="Color for inlays (hex).")
    p.add_argument("--left_handed", action="store_true", help="Render for left-handed view.")
    p.add_argument("--wood_background", action="store_true", help="Add a simulated wood background.")
    p.add_argument("--fig_w", type=float, default=0.0, help="Figure width in inches (0 = auto).")
    p.add_argument("--fig_h", type=float, default=0.0, help="Figure height in inches (0 = auto).")
    p.add_argument("--fontsize", type=int, default=10, help="Base font size (default: 10).")

    args = p.parse_args()

    has_scale_input = bool(args.scale_input.strip())
    has_mode = bool(args.mode.strip())

    if not has_scale_input and (not args.root or not has_mode):
        p.error("Provide either scale_input, or both --root and --mode.")

    if args.degrees and not args.root.strip():
        p.error("--degrees requires --root.")

    if has_scale_input:
        if args.degrees:
            scale = degrees_to_notes(args.scale_input, args.root, args.use_flats)
        else:
            scale = parse_notes(args.scale_input, args.use_flats)
    else:
        scale = generate_scale(args.root, args.mode, args.use_flats)

    tuning = [normalize_note(x, args.use_flats) for x in args.tuning.split()]
    num_frets = max(1, min(int(args.frets), 24))

    if args.root.strip():
        root = normalize_note(args.root, args.use_flats)
    else:
        root = scale[0]

    plot_fretboard(
        scale_notes=scale,
        root=root,
        tuning=tuning,
        num_frets=num_frets,
        out_path=args.out,
        scale_length=float(args.scale_length),
        dpi=int(args.dpi),
        use_flats=bool(args.use_flats),
        note_color=str(args.note_color),
        inlay_color=str(args.inlay_color),
        left_handed=bool(args.left_handed),
        wood_background=bool(args.wood_background),
        fig_w=float(args.fig_w),
        fig_h=float(args.fig_h),
        fmt=str(args.format),
        fontsize=int(args.fontsize),
    )


if __name__ == "__main__":
    main()

