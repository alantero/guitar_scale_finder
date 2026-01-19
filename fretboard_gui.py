# =========================
# File: fretboard_gui.py
# =========================




### TODO Add tuning option (Select tuning/Custom Tuning).

import sys

import matplotlib
matplotlib.use("QtAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QGroupBox,
        QLabel,
        QComboBox,
        QLineEdit,
        QPushButton,
        QStackedWidget,
        QCheckBox,
        QSpinBox,
        QStatusBar,
    )
except Exception:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QGroupBox,
        QLabel,
        QComboBox,
        QLineEdit,
        QPushButton,
        QStackedWidget,
        QCheckBox,
        QSpinBox,
        QStatusBar,
    )

from scales import SCALE_MODES
from fretboard_core import (
    FretboardRenderer,
    normalize_note,
    parse_notes_text,
    degrees_to_notes_text,
    generate_scale,
)

NOTE_CHOICES_SHARPS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTE_CHOICES_FLATS = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]


def app_stylesheet() -> str:
    return """
    QWidget { font-size: 20px; }
    QMainWindow { background: #101214; }

    QGroupBox {
        border: 1px solid #2B2F36;
        border-radius: 10px;
        margin-top: 10px;
        padding: 10px;
        background: #14181B;
        color: #E6E6E6;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px 0 6px;
        color: #E6E6E6;
    }
    QLabel { color: #E6E6E6; }

    QLineEdit, QComboBox, QSpinBox {
        background: #0F1215;
        border: 1px solid #2B2F36;
        border-radius: 8px;
        padding: 6px 10px;
        color: #EDEDED;
    }
    QComboBox::drop-down { border: 0px; width: 22px; }

    QPushButton {
        background: #2B6CB0;
        border: 0px;
        border-radius: 10px;
        padding: 10px 12px;
        color: white;
        font-weight: 600;
    }
    QPushButton:hover { background: #2C7BC9; }
    QPushButton:pressed { background: #245F99; }

    QCheckBox { color: #E6E6E6; padding: 6px 2px; }

    QStatusBar { background: #0E1012; color: #D0D0D0; }
    """


class FretboardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fretboard Plotter")
        self.setMinimumSize(1200, 720)

        self.renderer = FretboardRenderer(
            num_frets=24,
            wood_background=True,
            nut_color="#2B2B2B",
            scale_length=900.0,
            fontsize=14
        )

        root = QWidget()
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(12)

        # =========================
        # Top controls strip
        # =========================
        top = QWidget()
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(0, 0, 0, 0)
        top_l.setSpacing(12)

        # --- Input block
        gb_input = QGroupBox("Input")
        input_l = QVBoxLayout(gb_input)
        input_l.setContentsMargins(10, 14, 10, 10)
        input_l.setSpacing(10)

        row0 = QWidget()
        row0_l = QHBoxLayout(row0)
        row0_l.setContentsMargins(0, 0, 0, 0)
        row0_l.setSpacing(10)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Notes", "Degrees", "Scale"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)

        self.use_flats_cb = QCheckBox("Prefer flats")
        self.use_flats_cb.setChecked(False)
        self.use_flats_cb.stateChanged.connect(self._sync_root_choices)

        self.frets_spin = QSpinBox()
        self.frets_spin.setRange(1, 24)
        self.frets_spin.setValue(24)
        self.frets_spin.valueChanged.connect(self._on_frets_changed)

        row0_l.addWidget(QLabel("Mode"))
        row0_l.addWidget(self.mode_combo, 1)
        row0_l.addWidget(QLabel("Frets"))
        row0_l.addWidget(self.frets_spin, 0)
        row0_l.addWidget(self.use_flats_cb, 0)

        input_l.addWidget(row0)

        self.stack = QStackedWidget()

        # Notes page
        notes_page = QWidget()
        notes_l = QVBoxLayout(notes_page)
        notes_l.setContentsMargins(0, 0, 0, 0)
        notes_l.setSpacing(6)

        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Type note names separated by spaces (e.g. C E G Bb D)")
        notes_hint = QLabel("Examples:  C E G  |  C E G Bb D  |  C D Eb F Gb Ab Bb B")
        notes_hint.setStyleSheet("color: #B7BDC7;")
        notes_l.addWidget(self.notes_edit)
        notes_l.addWidget(notes_hint)

        # Degrees page
        deg_page = QWidget()
        deg_l = QVBoxLayout(deg_page)
        deg_l.setContentsMargins(0, 0, 0, 0)
        deg_l.setSpacing(6)

        self.deg_edit = QLineEdit()
        self.deg_edit.setPlaceholderText("Type degrees separated by spaces (e.g. 1 b3 5 or 1 2 3 #4 5 6 7)")
        deg_hint = QLabel("Accidentals: b, #, x. Examples: b2, #4, bb7, x4. Root aliases: R, root")
        deg_hint.setStyleSheet("color: #B7BDC7;")
        deg_l.addWidget(self.deg_edit)
        deg_l.addWidget(deg_hint)

        # Scale page
        scale_page = QWidget()
        scale_l = QVBoxLayout(scale_page)
        scale_l.setContentsMargins(0, 0, 0, 0)
        scale_l.setSpacing(6)

        #self.scale_combo = QComboBox()
        #self.scale_combo.addItems(sorted(SCALE_MODES.keys()))
        

        self.scale_combo = QComboBox()

        # display name -> internal key
        self.scale_display_to_key = {
            k.replace("_", " ").title(): k
            for k in SCALE_MODES.keys()
        }

        # show pretty names
        self.scale_combo.addItems(sorted(self.scale_display_to_key.keys()))


        scale_hint = QLabel("Select a scale.")
        scale_hint.setStyleSheet("color: #B7BDC7;")
        scale_l.addWidget(self.scale_combo)
        scale_l.addWidget(scale_hint)

        self.stack.addWidget(notes_page)
        self.stack.addWidget(deg_page)
        self.stack.addWidget(scale_page)

        input_l.addWidget(self.stack)

        # --- Root block
        gb_root = QGroupBox("Root")
        root_l = QVBoxLayout(gb_root)
        root_l.setContentsMargins(10, 14, 10, 10)
        root_l.setSpacing(10)

        self.root_combo = QComboBox()
        self.root_combo.setEditable(True)
        self._sync_root_choices()
        self.root_combo.setCurrentText("C")

        root_row = QWidget()
        root_row_l = QHBoxLayout(root_row)
        root_row_l.setContentsMargins(0, 0, 0, 0)
        root_row_l.setSpacing(10)
        root_row_l.addWidget(QLabel("Root note"))
        root_row_l.addWidget(self.root_combo, 1)

        root_l.addWidget(root_row)
        root_l.addStretch(1)

        # --- Actions block
        gb_actions = QGroupBox("Actions")
        actions_l = QVBoxLayout(gb_actions)
        actions_l.setContentsMargins(10, 14, 10, 10)
        actions_l.setSpacing(10)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.on_run)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setStyleSheet("background: #3A3F44;")
        self.clear_btn.clicked.connect(self.on_clear)

        actions_l.addWidget(self.run_btn)
        actions_l.addWidget(self.clear_btn)
        actions_l.addStretch(1)

        # compose top strip
        top_l.addWidget(gb_input, 3)
        top_l.addWidget(gb_root, 1)
        top_l.addWidget(gb_actions, 1)

        # =========================
        # Bottom plot area
        # =========================
        plot_wrap = QGroupBox("Fretboard")
        plot_l = QVBoxLayout(plot_wrap)
        plot_l.setContentsMargins(10, 14, 10, 10)

        self.fig = plt.Figure(figsize=(16, 5.2), dpi=120)
        self.fig.subplots_adjust(left=0.01, right=0.995, bottom=0.10, top=0.90)
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)


        gui_bg = "#101214"  # same as your QMainWindow background

        # Background outside the plot (figure area)
        self.fig.patch.set_facecolor(gui_bg)

        # Sometimes the Qt canvas widget itself shows white around the figure
        self.canvas.setStyleSheet(f"background-color: {gui_bg};")

        plot_l.addWidget(self.canvas)

        outer.addWidget(top, 0)
        outer.addWidget(plot_wrap, 3)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

        # initial empty fretboard
        self.renderer.draw(self.ax, scale_notes=[], root="C", use_flats=self.use_flats_cb.isChecked())
        self.canvas.draw_idle()

    def _sync_root_choices(self):
        use_flats = self.use_flats_cb.isChecked()
        choices = NOTE_CHOICES_FLATS if use_flats else NOTE_CHOICES_SHARPS

        current = self.root_combo.currentText().strip()
        self.root_combo.blockSignals(True)
        self.root_combo.clear()
        self.root_combo.addItems(choices)
        self.root_combo.setEditable(True)
        if current:
            self.root_combo.setCurrentText(current)
        self.root_combo.blockSignals(False)

    def _on_mode_changed(self, idx: int):
        self.stack.setCurrentIndex(idx)

    def _on_frets_changed(self, v: int):
        self.renderer.num_frets = int(v)
        self.on_clear()

    def _get_root(self) -> str:
        root = self.root_combo.currentText().strip()
        return root if root else "C"

    def _compute_notes(self):
        mode = self.mode_combo.currentText()
        use_flats = self.use_flats_cb.isChecked()
        root = self._get_root()

        if mode == "Notes":
            text = self.notes_edit.text().strip()
            notes = parse_notes_text(text, use_flats=use_flats) if text else []
            root_n = normalize_note(root, use_flats=use_flats)
            return notes, root_n

        if mode == "Degrees":
            text = self.deg_edit.text().strip()
            if not text:
                return [], normalize_note(root, use_flats=use_flats)
            notes = degrees_to_notes_text(text, root=root, use_flats=use_flats)
            root_n = normalize_note(root, use_flats=use_flats)
            return notes, root_n

        #scale_name = self.scale_combo.currentText()
        root_n = normalize_note(root, use_flats=use_flats)
        #notes = generate_scale(root=root_n, mode=scale_name, scale_modes=SCALE_MODES, use_flats=use_flats)

        scale_display = self.scale_combo.currentText()
        scale_key = self.scale_display_to_key[scale_display]

        notes = generate_scale(
            root=root_n,
            mode=scale_key,
            scale_modes=SCALE_MODES,
            use_flats=use_flats,
        )


        return notes, root_n

    def on_run(self):
        try:
            notes, root = self._compute_notes()
            self.renderer.draw(self.ax, scale_notes=notes, root=root, use_flats=self.use_flats_cb.isChecked())
            self.canvas.draw_idle()
            if notes:
                self.statusBar().showMessage(f"Plotted {len(notes)} notes. Root: {root}")
            else:
                self.statusBar().showMessage("No notes provided. Showing empty fretboard.")
        except Exception as e:
            self.statusBar().showMessage(f"Error: {e}")

    def on_clear(self):
        self.renderer.draw(self.ax, scale_notes=[], root="C", use_flats=self.use_flats_cb.isChecked())
        self.canvas.draw_idle()
        self.statusBar().showMessage("Cleared")


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(app_stylesheet())
    w = FretboardApp()
    #w.show()
    w.showMaximized()
    sys.exit(app.exec() if hasattr(app, "exec") else app.exec_())


if __name__ == "__main__":
    main()

