# =========================
# File: fretboard_core.py
# =========================
import numpy as np

CHROMATIC_SHARPS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CHROMATIC_FLATS  = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

SHARP_TO_FLAT = {"C#": "Db", "D#": "Eb", "F#": "Gb", "G#": "Ab", "A#": "Bb"}
FLAT_TO_SHARP = {"Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#", "Ab": "G#", "Bb": "A#", "Cb": "B"}
ENHARMONIC = {"B#": "C", "E#": "F"}

NOTE_TO_INDEX_SHARPS = {n: i for i, n in enumerate(CHROMATIC_SHARPS)}
NOTE_TO_INDEX_FLATS  = {n: i for i, n in enumerate(CHROMATIC_FLATS)}

DEFAULT_TUNING = ["E", "A", "D", "G", "B", "E"]  # low to high
DEGREE_BASE_OFFSETS = {1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11}


def normalize_note(note: str, use_flats: bool = False) -> str:
    n = note.strip().upper().replace(" ", "")
    if not n:
        raise ValueError("Empty note")

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


def parse_notes_text(text: str, use_flats: bool) -> list[str]:
    raw = [x for x in text.replace(",", " ").split() if x.strip()]
    return [normalize_note(x, use_flats) for x in raw]


def unique_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for x in items:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def parse_degree_token(token: str) -> tuple[int, int]:
    t = token.strip()
    if not t:
        raise ValueError("Empty degree token")

    t = t.replace("♭", "b").replace("♯", "#")

    if t.lower() in ["r", "root"]:
        return 1, 0

    def is_acc(ch: str) -> bool:
        return ch in ["b", "#", "x"]

    i = 0
    n = len(t)

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


def degrees_to_notes_text(text: str, root: str, use_flats: bool) -> list[str]:
    raw = [x for x in text.replace(",", " ").split() if x.strip()]
    if not raw:
        raise ValueError("No degree tokens provided")

    chromatic = CHROMATIC_FLATS if use_flats else CHROMATIC_SHARPS
    note_to_index = NOTE_TO_INDEX_FLATS if use_flats else NOTE_TO_INDEX_SHARPS

    root_n = normalize_note(root, use_flats=use_flats)
    root_idx = note_to_index[root_n]

    notes = []
    for tok in raw:
        deg, shift = parse_degree_token(tok)
        deg_base = ((deg - 1) % 7) + 1
        base_offset = DEGREE_BASE_OFFSETS[deg_base]
        offset = (base_offset + shift) % 12
        notes.append(chromatic[(root_idx + offset) % 12])

    return unique_preserve_order(notes)


def generate_scale(root: str, mode: str, scale_modes: dict[str, list[int]], use_flats: bool) -> list[str]:
    if mode not in scale_modes:
        raise ValueError(f"Unsupported mode: {mode}")

    root_n = normalize_note(root, use_flats=False)
    root_idx = NOTE_TO_INDEX_SHARPS[root_n]
    steps = scale_modes[mode]

    notes = [root_n]
    idx = root_idx
    for step in steps:
        idx = (idx + step) % 12
        notes.append(CHROMATIC_SHARPS[idx])

    # remove octave duplicate for typical scales
    if len(steps) in (5, 6, 7, 8, 12):
        notes = notes[:-1]

    if use_flats:
        notes = [SHARP_TO_FLAT.get(n, n) for n in notes]
    return unique_preserve_order(notes)


def fret_positions_equal_temperament(num_frets: int, scale_length: float) -> np.ndarray:
    frets = np.arange(0, num_frets + 1, dtype=float)
    xs = scale_length * (1.0 - (2.0 ** (-frets / 12.0)))
    xs[0] = 0.0
    return xs


def get_inlay_frets(num_frets: int) -> list[int]:
    base = [3, 5, 7, 9, 12, 15, 17, 19, 21, 24]
    return [f for f in base if f <= num_frets]


class FretboardRenderer:
    def __init__(
        self,
        num_frets: int = 24,
        tuning: list[str] | None = None,
        scale_length: float = 650.0,
        wood_background: bool = True,
        nut_color: str = "#2B2B2B",
        inlay_color: str = "#B0B0B0",
        note_color: str = "#FFD24A",
        fontsize: int = 10,
    ):
        self.num_frets = int(max(1, min(num_frets, 24)))
        self.tuning = tuning[:] if tuning else DEFAULT_TUNING[:]
        self.scale_length = float(scale_length)
        self.wood_background = bool(wood_background)
        self.nut_color = str(nut_color)
        self.inlay_color = str(inlay_color)
        self.note_color = str(note_color)
        self.fontsize = int(fontsize)

    def draw(self, ax, scale_notes: list[str] | None, root: str | None, use_flats: bool):
        
        ui_text = "#E6E6E6"

        ax.clear()

        ax.set_facecolor("#101214")

        scale_notes = scale_notes or []
        root = root or (scale_notes[0] if scale_notes else "C")

        chromatic = CHROMATIC_FLATS if use_flats else CHROMATIC_SHARPS
        note_to_index = NOTE_TO_INDEX_FLATS if use_flats else NOTE_TO_INDEX_SHARPS

        tuning = [normalize_note(x, use_flats) for x in self.tuning]
        scale_set = set(scale_notes)

        xs = fret_positions_equal_temperament(self.num_frets, self.scale_length)
        open_x = xs[0] - 0.60 * (xs[1] - xs[0])

        num_strings = len(tuning)
        ys = np.arange(num_strings, dtype=float)
        y_scale = 1.0

        if self.wood_background:
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
                    open_x - 0.10 * self.scale_length,
                    xs[-1] + 0.02 * self.scale_length,
                    -1.35,
                    (num_strings - 1) * y_scale + 1.05,
                ],
                cmap="YlOrBr",
                alpha=0.28,
                aspect="auto",
                zorder=0,
            )

        # strings
        for si, y in enumerate(ys):
            lw = 2.8 - 0.35 * si
            ax.plot([open_x, xs[-1]], [y * y_scale, y * y_scale], linewidth=lw, color="silver", zorder=1)

        # frets
        for f, x in enumerate(xs):
            if f == 0:
                ax.plot(
                    [x, x],
                    [-0.65, (num_strings - 1) * y_scale + 0.65],
                    linewidth=7.0,
                    color=self.nut_color,
                    zorder=2,
                )
            else:
                ax.plot(
                    [x, x],
                    [-0.55, (num_strings - 1) * y_scale + 0.55],
                    linewidth=1.8,
                    color="black",
                    zorder=2,
                )

        # inlays
        for f in get_inlay_frets(self.num_frets):
            if f == 0:
                continue
            x_mid = 0.5 * (xs[f - 1] + xs[f])
            y_mid = 0.5 * ((ys[0] + ys[-1]) * y_scale)

            if f in [12, 24]:
                ax.scatter(
                    [x_mid, x_mid],
                    [y_mid - 0.45, y_mid + 0.45],
                    s=140,
                    marker="o",
                    c=self.inlay_color,
                    edgecolors="none",
                    zorder=3,
                )
            else:
                ax.scatter(
                    [x_mid],
                    [y_mid],
                    s=140,
                    marker="o",
                    c=self.inlay_color,
                    edgecolors="none",
                    zorder=3,
                )

        # labels
        label_x = open_x - 0.07 * self.scale_length
        for si, open_note in enumerate(tuning):
            ax.text(label_x, float(ys[si] * y_scale), open_note, ha="right", va="center", fontsize=self.fontsize, color=ui_text)

        for f in range(1, self.num_frets + 1):
            x = float(0.5 * (xs[f - 1] + xs[f]))
            ax.text(x, -0.95, str(f), ha="center", va="center", fontsize=max(7, self.fontsize - 1), color=ui_text)

        # note markers (if any)
        if scale_notes:
            mids = np.empty(self.num_frets + 1, dtype=float)
            mids[0] = open_x
            if self.num_frets >= 1:
                mids[1:] = 0.5 * (xs[:-1] + xs[1:])

            x_root, y_root, t_root = [], [], []
            x_norm, y_norm, t_norm = [], [], []

            frets = np.arange(0, self.num_frets + 1, dtype=int)
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
                    facecolors=self.note_color,
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
                    facecolors=self.note_color,
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
                ax.text(x, y, n, ha="center", va="center", fontsize=max(7, self.fontsize - 1), color="black", zorder=8)
            for x, y, n in zip(x_root, y_root, t_root):
                ax.text(x, y, n, ha="center", va="center", fontsize=self.fontsize, fontweight="bold", color="black", zorder=9)

            scale_str = " ".join(scale_notes)
            ax.set_title(f"Notes: {scale_str}   |   Root: {root}", fontsize=self.fontsize + 2, color=ui_text)
        else:
            ax.set_title(f"Fretboard ({self.num_frets} frets) - press Run to plot notes", fontsize=self.fontsize + 2, color=ui_text)

        ax.set_ylim(-1.35, (num_strings - 1) * y_scale + 1.05)
        ax.set_xlim(open_x - 0.10 * self.scale_length, xs[-1] + 0.02 * self.scale_length)
        ax.axis("off")
