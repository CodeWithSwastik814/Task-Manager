import sys, math, time
import task_manager as tm

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QLineEdit,
    QPushButton, QRadioButton, QButtonGroup, QScrollArea,
    QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QMessageBox,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore  import Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui   import (
    QPainter, QColor, QRadialGradient, QBrush, QPen,
    QFont, QFontDatabase, QPalette, QLinearGradient,
)

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = "#0a0a0f"
PANEL    = "#12121a"
PANEL2   = "#1a1a26"
GLASS    = "#1e1e2e"
BORDER   = "#2a2a3e"
ACCENT   = "#7c6dfa"
ACCENT2  = "#a78bfa"
TEXT_PRI = "#f0f0f8"
TEXT_SEC = "#8888aa"
TEXT_DIM = "#44445a"
HIGH_COL = "#f87171"
MED_COL  = "#fbbf24"
LOW_COL  = "#34d399"
DONE_COL = "#4ade80"

PRIO_COLORS = {"high": HIGH_COL, "medium": MED_COL, "low": LOW_COL}
PRIO_LABELS = {"high": "HIGH",   "medium": "MED",   "low": "LOW"}

ORBS = [
    {"x": 0.12, "y": 0.18, "r": 110, "r_col": "#2a1a8a", "g_col": "#1a1060", "dx": 0.15, "dy": 0.08},
    {"x": 0.80, "y": 0.12, "r":  75, "r_col": "#1e1270", "g_col": "#0d0d40", "dx":-0.10, "dy": 0.12},
    {"x": 0.65, "y": 0.75, "r": 130, "r_col": "#251580", "g_col": "#120c50", "dx": 0.08, "dy":-0.09},
    {"x": 0.20, "y": 0.80, "r":  60, "r_col": "#200e60", "g_col": "#1a0a3a", "dx":-0.12, "dy":-0.07},
    {"x": 0.90, "y": 0.55, "r":  85, "r_col": "#150e50", "g_col": "#0a0a30", "dx":-0.08, "dy": 0.10},
]

# ── Global font helper ─────────────────────────────────────────────────────────
def font(size=12, bold=False, mono=False):
    family = "Courier New" if mono else "Segoe UI"
    f = QFont(family, size)
    if bold:
        f.setWeight(QFont.Weight.Bold)
    return f


# ══════════════════════════════════════════════════════════════════════════════
class OrbWidget(QWidget):
    """Animated floating-orb background rendered via QPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._orbs = [dict(o) for o in ORBS]
        self._t0   = time.time()
        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(40)          # ~25 fps

    def paintEvent(self, _):
        p   = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(BG))

        t = time.time() - self._t0
        W, H = self.width(), self.height()

        for o in self._orbs:
            ox = o["x"] + math.sin(t * o["dx"] + o["r"] * 0.1) * 0.06
            oy = o["y"] + math.cos(t * o["dy"] + o["r"] * 0.1) * 0.05
            cx = ox * W
            cy = oy * H
            r  = o["r"]

            # outer glow layers
            for mult, alpha in [(3.2, 18), (2.2, 32), (1.5, 55)]:
                lr = r * mult
                grad = QRadialGradient(cx, cy, lr)
                base = QColor(o["g_col"])
                base.setAlpha(alpha)
                grad.setColorAt(0.0, base)
                grad.setColorAt(1.0, QColor(0, 0, 0, 0))
                p.setBrush(QBrush(grad))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(QRectF(cx - lr, cy - lr, lr*2, lr*2))

            # bright core
            grad2 = QRadialGradient(cx, cy, r)
            grad2.setColorAt(0.0, QColor(o["r_col"]))
            grad2.setColorAt(0.6, QColor(o["g_col"]))
            grad2.setColorAt(1.0, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(grad2))
            p.drawEllipse(QRectF(cx - r, cy - r, r*2, r*2))

        p.end()


# ══════════════════════════════════════════════════════════════════════════════
def _glass_frame(radius=12) -> QFrame:
    f = QFrame()
    f.setStyleSheet(f"""
        QFrame {{
            background: rgba(30,30,46,210);
            border: 1px solid {BORDER};
            border-radius: {radius}px;
        }}
    """)
    return f


def _label(text, size=12, bold=False, color=TEXT_PRI) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(font(size, bold))
    lbl.setStyleSheet(f"color:{color}; background:transparent; border:none;")
    return lbl


def _entry(placeholder="") -> QLineEdit:
    e = QLineEdit()
    e.setPlaceholderText(placeholder)
    e.setFont(font(12))
    e.setStyleSheet(f"""
        QLineEdit {{
            background: {PANEL2};
            color: {TEXT_PRI};
            border: 1px solid {BORDER};
            border-radius: 6px;
            padding: 7px 10px;
        }}
        QLineEdit:focus {{
            border: 1px solid {ACCENT};
        }}
    """)
    return e


def _radio(text, color=ACCENT2) -> QRadioButton:
    r = QRadioButton(text)
    r.setFont(font(10, bold=True))
    r.setStyleSheet(f"""
        QRadioButton {{
            color: {color};
            background: transparent;
            spacing: 6px;
        }}
        QRadioButton::indicator {{
            width: 13px; height: 13px;
            border-radius: 7px;
            border: 2px solid {color};
            background: transparent;
        }}
        QRadioButton::indicator:checked {{
            background: {color};
        }}
    """)
    return r


def _accent_button(text) -> QPushButton:
    b = QPushButton(text)
    b.setFont(font(12, bold=True))
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background: {ACCENT};
            color: #0a0a0f;
            border: none;
            border-radius: 8px;
            padding: 10px 0;
        }}
        QPushButton:hover {{
            background: {ACCENT2};
        }}
        QPushButton:pressed {{
            background: #6050d0;
        }}
    """)
    return b


def _tab_radio(text) -> QRadioButton:
    r = QRadioButton(text)
    r.setFont(font(12, bold=True))
    r.setStyleSheet(f"""
        QRadioButton {{
            color: {TEXT_SEC};
            background: transparent;
            padding: 6px 14px;
            border-radius: 6px;
        }}
        QRadioButton:hover {{
            color: {ACCENT2};
        }}
        QRadioButton::indicator {{ width:0; height:0; }}
        QRadioButton:checked {{
            color: {ACCENT2};
            background: rgba(124,109,250,0.15);
        }}
    """)
    return r


# ══════════════════════════════════════════════════════════════════════════════
class PriorityBadge(QLabel):
    def __init__(self, priority, parent=None):
        col  = PRIO_COLORS.get(priority, MED_COL)
        text = PRIO_LABELS.get(priority, "MED")
        super().__init__(text, parent)
        self.setFont(font(9, bold=True))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(46, 22)
        self.setStyleSheet(f"""
            QLabel {{
                color: {col};
                border: 1px solid {col};
                border-radius: 4px;
                background: rgba(0,0,0,0.35);
            }}
        """)


# ══════════════════════════════════════════════════════════════════════════════
class TaskRow(QWidget):
    """Single task row with priority badge / done marker + action buttons."""

    def __init__(self, task, index, on_complete=None, on_delete=None, done=False):
        super().__init__()
        self._task        = task
        self._index       = index
        self._on_complete = on_complete
        self._on_delete   = on_delete
        self._done        = done
        self.setFixedHeight(46)
        self.setStyleSheet("background: transparent;")
        self._build()

    def _build(self):
        row = QHBoxLayout(self)
        row.setContentsMargins(10, 0, 10, 0)
        row.setSpacing(10)

        # index
        num_col = DONE_COL if self._done else ACCENT2
        num = _label(f"{self._index:02d}", size=10, color=num_col)
        num.setFixedWidth(28)
        row.addWidget(num)

        # badge / checkmark
        if self._done:
            chk = _label("✓", size=11, bold=True, color=DONE_COL)
            chk.setFixedWidth(36)
            row.addWidget(chk)
        else:
            row.addWidget(PriorityBadge(self._task.get("priority", "medium")))

        # task name
        name_col = TEXT_SEC if self._done else TEXT_PRI
        name = _label(self._task["name"], size=12, color=name_col)
        name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        if self._done:
            name.setStyleSheet(f"color:{TEXT_SEC}; text-decoration:line-through; background:transparent; border:none;")
        row.addWidget(name)

        # action buttons
        if not self._done:
            for sym, col, cb in [("✓", DONE_COL, self._complete), ("✕", HIGH_COL, self._delete)]:
                b = QPushButton(sym)
                b.setFont(font(12, bold=True))
                b.setFixedSize(32, 28)
                b.setCursor(Qt.CursorShape.PointingHandCursor)
                b.setStyleSheet(f"""
                    QPushButton {{
                        color: {col}; background: transparent;
                        border: 1px solid {col}; border-radius: 6px;
                    }}
                    QPushButton:hover {{ background: {col}; color: #0a0a0f; }}
                """)
                b.clicked.connect(cb)
                row.addWidget(b)

    def _complete(self):
        if self._on_complete:
            self._on_complete(self._index - 1)

    def _delete(self):
        if self._on_delete:
            self._on_delete(self._index - 1)


# ══════════════════════════════════════════════════════════════════════════════
class TaskManagerWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.resize(1060, 700)
        self.setMinimumSize(800, 560)
        tm.load_tasks()
        self._build_ui()
        self._refresh()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Orb canvas as central background
        self._orb = OrbWidget(self)
        self._orb.setGeometry(self.rect())

        # Transparent central overlay
        central = QWidget(self)
        central.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setContentsMargins(28, 22, 28, 22)
        outer.setSpacing(0)

        self._build_header(outer)

        body = QHBoxLayout()
        body.setSpacing(16)
        outer.addLayout(body, stretch=1)

        self._build_sidebar(body)
        self._build_task_panel(body)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._orb.setGeometry(self.rect())

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self, parent_layout):
        hdr = QHBoxLayout()
        hdr.setContentsMargins(0, 0, 0, 0)

        title = _label("TASK MANAGER", size=22, bold=True)
        hdr.addWidget(title)
        hdr.addStretch()

        self._lbl_incomplete = _label("0", size=30, bold=True, color=ACCENT2)
        self._lbl_complete   = _label("0", size=30, bold=True, color=DONE_COL)

        for val_lbl, text, col in [
            (self._lbl_incomplete, "incomplete", ACCENT2),
            (self._lbl_complete,   "completed",  DONE_COL),
        ]:
            sf = QVBoxLayout()
            sf.setSpacing(0)
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub = _label(text, size=9, color=TEXT_SEC)
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sf.addWidget(val_lbl)
            sf.addWidget(sub)
            hdr.addLayout(sf)
            hdr.addSpacing(18)

        parent_layout.addLayout(hdr)

        # divider
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background:{BORDER}; border:none;")
        parent_layout.addSpacing(10)
        parent_layout.addWidget(line)
        parent_layout.addSpacing(14)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self, body_layout):
        side = _glass_frame()
        side.setFixedWidth(240)
        side.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        vbox = QVBoxLayout(side)
        vbox.setContentsMargins(18, 18, 18, 18)
        vbox.setSpacing(8)

        # ── Add Task ──
        vbox.addWidget(_label("Add Task", size=13, bold=True))

        vbox.addWidget(_label("Task name", size=10, color=TEXT_SEC))
        self._name_entry = _entry("Enter task name…")
        self._name_entry.returnPressed.connect(self._add_task)
        vbox.addWidget(self._name_entry)

        vbox.addSpacing(4)
        vbox.addWidget(_label("Priority", size=10, color=TEXT_SEC))

        pf = QHBoxLayout()
        pf.setSpacing(8)
        self._prio_group = QButtonGroup(self)
        self._prio_radios = {}
        for val, label, col in [("high","HIGH",HIGH_COL),("medium","MED",MED_COL),("low","LOW",LOW_COL)]:
            rb = _radio(label, col)
            self._prio_group.addButton(rb)
            self._prio_radios[val] = rb
            pf.addWidget(rb)
        self._prio_radios["medium"].setChecked(True)
        vbox.addLayout(pf)

        vbox.addSpacing(8)
        add_btn = _accent_button("+ Add Task")
        add_btn.clicked.connect(self._add_task)
        vbox.addWidget(add_btn)

        # divider
        div = QFrame(); div.setFixedHeight(1)
        div.setStyleSheet(f"background:{BORDER}; border:none;")
        vbox.addSpacing(8); vbox.addWidget(div); vbox.addSpacing(8)

        # ── Search ──
        vbox.addWidget(_label("Search", size=10, color=TEXT_SEC))
        self._search_entry = _entry("Search tasks…")
        self._search_entry.textChanged.connect(lambda _: self._refresh())
        vbox.addWidget(self._search_entry)

        vbox.addSpacing(8)
        vbox.addWidget(_label("Filter by priority", size=10, color=TEXT_SEC))

        ff = QHBoxLayout(); ff.setSpacing(4)
        self._filter_group = QButtonGroup(self)
        self._filter_radios = {}
        for val, label, col in [("all","ALL",ACCENT2),("high","HIGH",HIGH_COL),
                                  ("medium","MED",MED_COL),("low","LOW",LOW_COL)]:
            rb = _radio(label, col)
            rb.setFont(font(9, bold=True))
            self._filter_group.addButton(rb)
            self._filter_radios[val] = rb
            ff.addWidget(rb)
        self._filter_radios["all"].setChecked(True)
        self._filter_group.buttonClicked.connect(lambda _: self._refresh())
        vbox.addLayout(ff)

        vbox.addStretch()
        body_layout.addWidget(side)

    # ── Task Panel ────────────────────────────────────────────────────────────

    def _build_task_panel(self, body_layout):
        panel = _glass_frame()
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(16, 12, 16, 12)
        vbox.setSpacing(0)

        # tabs
        tabs = QHBoxLayout()
        tabs.setSpacing(4)
        self._tab_group = QButtonGroup(self)
        self._tab_radios = {}
        for val, label in [("incomplete","Incomplete"),("complete","Completed"),("all","All")]:
            rb = _tab_radio(label)
            self._tab_group.addButton(rb)
            self._tab_radios[val] = rb
            tabs.addWidget(rb)
        tabs.addStretch()
        self._tab_radios["incomplete"].setChecked(True)
        self._tab_group.buttonClicked.connect(lambda _: self._refresh())
        vbox.addLayout(tabs)

        # divider
        div = QFrame(); div.setFixedHeight(1)
        div.setStyleSheet(f"background:{BORDER}; border:none;")
        vbox.addSpacing(6); vbox.addWidget(div); vbox.addSpacing(8)

        # scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: #1a1a26; width: 6px; border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #3a3a5e; border-radius: 3px;
            }
        """)

        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 8, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_widget)
        vbox.addWidget(scroll, stretch=1)

        body_layout.addWidget(panel, stretch=1)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _selected_priority(self):
        for val, rb in self._prio_radios.items():
            if rb.isChecked():
                return val
        return "medium"

    def _selected_filter(self):
        for val, rb in self._filter_radios.items():
            if rb.isChecked():
                return val
        return "all"

    def _selected_tab(self):
        for val, rb in self._tab_radios.items():
            if rb.isChecked():
                return val
        return "incomplete"

    def _add_task(self):
        name = self._name_entry.text().strip()
        if not name:
            return
        tm.incomplete_tasks.append({"name": name, "priority": self._selected_priority()})
        tm.save_tasks()
        self._name_entry.clear()
        self._refresh()

    def _complete_task(self, index):
        if 0 <= index < len(tm.incomplete_tasks):
            done = tm.incomplete_tasks.pop(index)
            tm.complete_tasks.append(done)
            tm.save_tasks()
            self._refresh()

    def _delete_task(self, index):
        if 0 <= index < len(tm.incomplete_tasks):
            name = tm.incomplete_tasks[index]["name"]
            reply = QMessageBox.question(self, "Delete Task",
                f'Delete "{name}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                tm.incomplete_tasks.pop(index)
                tm.save_tasks()
                self._refresh()

    # ── Refresh ───────────────────────────────────────────────────────────────

    def _clear_list(self):
        while self._list_layout.count() > 1:   # keep the trailing stretch
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _sep(self):
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background:{BORDER}; border:none; margin: 0 4px;")
        self._list_layout.insertWidget(self._list_layout.count() - 1, line)

    def _refresh(self):
        self._lbl_incomplete.setText(str(len(tm.incomplete_tasks)))
        self._lbl_complete.setText(str(len(tm.complete_tasks)))

        self._clear_list()

        kw   = self._search_entry.text().strip().lower()
        prio = self._selected_filter()
        tab  = self._selected_tab()

        def matches(task):
            if kw   and kw not in task["name"].lower():          return False
            if prio != "all" and task.get("priority") != prio:   return False
            return True

        shown = 0
        insert_at = 0   # index before the trailing stretch

        def add_row(widget):
            nonlocal insert_at
            self._list_layout.insertWidget(insert_at, widget)
            insert_at += 1

        def add_section_label(text):
            lbl = _label(text, size=9, color=TEXT_DIM)
            lbl.setContentsMargins(4, 8, 0, 4)
            add_row(lbl)

        def add_sep():
            line = QFrame()
            line.setFixedHeight(1)
            line.setStyleSheet(f"background:{BORDER}; border:none;")
            add_row(line)

        if tab in ("incomplete", "all"):
            items = [t for t in tm.incomplete_tasks if matches(t)]
            if tab == "all" and items:
                add_section_label("Incomplete")
            for i, task in enumerate(items):
                row = TaskRow(task, i + 1,
                              on_complete=self._complete_task,
                              on_delete=self._delete_task)
                add_row(row)
                add_sep()
                shown += 1

        if tab in ("complete", "all"):
            items = [t for t in tm.complete_tasks if matches(t)]
            if tab == "all" and items:
                add_section_label("Completed")
            for i, task in enumerate(items):
                row = TaskRow(task, i + 1, done=True)
                add_row(row)
                add_sep()
                shown += 1

        if shown == 0:
            msg = "No tasks found." if (kw or prio != "all") else "Nothing here yet."
            lbl = _label(msg, size=12, color=TEXT_DIM)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setContentsMargins(0, 30, 0, 0)
            add_row(lbl)

    def closeEvent(self, e):
        tm.save_tasks()
        e.accept()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # dark fusion palette as base
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(BG))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(TEXT_PRI))
    palette.setColor(QPalette.ColorRole.Base,            QColor(PANEL2))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(PANEL))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor(GLASS))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor(TEXT_PRI))
    palette.setColor(QPalette.ColorRole.Text,            QColor(TEXT_PRI))
    palette.setColor(QPalette.ColorRole.Button,          QColor(PANEL))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(TEXT_PRI))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    win = TaskManagerWindow()
    win.show()
    sys.exit(app.exec())