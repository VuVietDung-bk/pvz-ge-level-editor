from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QCheckBox,
    QLabel, QPushButton, QDialogButtonBox
)
from PyQt6.QtCore import Qt


class MoldColonyChallengeDialog(QDialog):
    """Dialog for editing MoldColonyChallengeProps."""
    ROWS = 5
    COLS = 9

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit MoldColonyChallengeProps")
        self.resize(600, 420)

        data = existing_data or {}
        mold_matrix = data.get("MoldMatrix", ["0" * self.COLS for _ in range(self.ROWS)])

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tick cells to mark Mold Colonies:"))

        # --- Grid of checkboxes ---
        self.grid_layout = QGridLayout()
        self.checkboxes = []

        for row in range(self.ROWS):
            row_boxes = []
            for col in range(self.COLS):
                cb = QCheckBox()
                cb.setChecked(mold_matrix[row][col] == "1")
                self.grid_layout.addWidget(cb, row, col)
                row_boxes.append(cb)
            self.checkboxes.append(row_boxes)

        layout.addLayout(self.grid_layout)

        # --- Select All / Clear ---
        btn_all = QPushButton("✅ Select All")
        btn_clear = QPushButton("❌ Clear All")
        btn_all.clicked.connect(self.select_all)
        btn_clear.clicked.connect(self.clear_all)
        layout.addWidget(btn_all)
        layout.addWidget(btn_clear)

        # --- SuppressObjectiveTip ---
        self.suppress_tip = QCheckBox("Suppress Objective Tip")
        if str(data.get("SuppressObjectiveTip", "")).lower() == "true":
            self.suppress_tip.setChecked(True)
        layout.addWidget(self.suppress_tip)

        # --- OK / Cancel ---
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # ------------------------------------------------
    def select_all(self):
        for row in self.checkboxes:
            for cb in row:
                cb.setChecked(True)

    def clear_all(self):
        for row in self.checkboxes:
            for cb in row:
                cb.setChecked(False)

    # ------------------------------------------------
    def get_data(self):
        """Convert grid state into MoldMatrix format."""
        matrix = []
        for row in self.checkboxes:
            s = "".join("1" if cb.isChecked() else "0" for cb in row)
            matrix.append(s)

        obj = {"MoldMatrix": matrix}
        if self.suppress_tip.isChecked():
            obj["SuppressObjectiveTip"] = True

        return obj