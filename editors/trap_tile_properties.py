from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QListWidget, QComboBox,
    QDoubleSpinBox
)

# Hardcoded list of trap tile groups (expandable later)
TRAP_GROUPS = [
    "flame",
    "boulder_forward",
]


class TrapTilePropertiesEditor(QDialog):
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)

        self.setWindowTitle("TrapTileProperties Editor")
        self.setModal(True)
        self.resize(500, 450)

        self.existing_data = existing_data or {"TrapTiles": []}
        self.placements = self.existing_data.get("TrapTiles", [])

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Trap Tiles:"))

        # List of traps
        self.list_widget = QListWidget()
        for t in self.placements:
            self.list_widget.addItem(self._tile_to_text(t))

        layout.addWidget(self.list_widget)

        # Buttons add/remove
        btn_row = QHBoxLayout()
        btn_add = QPushButton("Add Trap Tile")
        btn_remove = QPushButton("Remove Selected")

        btn_add.clicked.connect(self.add_tile)
        btn_remove.clicked.connect(self.remove_tile)

        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_remove)
        layout.addLayout(btn_row)

        # OK / Cancel
        bottom_row = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")

        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        bottom_row.addWidget(btn_ok)
        bottom_row.addWidget(btn_cancel)
        layout.addLayout(bottom_row)

        self.setLayout(layout)

    # -------------------------------------------------------------

    def _tile_to_text(self, t):
        group = t.get("Group", "")
        loc = t.get("Location", {})
        x = loc.get("mX", "")
        y = loc.get("mY", "")
        delay = t.get("RecoverDelay", 0)
        return f"{group} @ ({x},{y}) delay={delay}"

    # -------------------------------------------------------------

    def add_tile(self):
        dlg = TrapTileEntryDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            data = dlg.get_data()
            self.placements.append(data)
            self.list_widget.addItem(self._tile_to_text(data))

    def remove_tile(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        self.list_widget.takeItem(row)
        self.placements.pop(row)

    # -------------------------------------------------------------

    def get_data(self):
        return {"TrapTiles": self.placements}

class TrapTileEntryDialog(QDialog):
    def __init__(self, parent=None, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Trap Tile")
        self.setModal(True)
        self.resize(360, 240)

        data = existing or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # Group selector (no autocomplete)
        self.input_group = QComboBox()
        self.input_group.addItems(TRAP_GROUPS)
        if data.get("Group") in TRAP_GROUPS:
            self.input_group.setCurrentText(data["Group"])

        # mX 0–8
        self.input_mX = QComboBox()
        self.input_mX.addItems([str(i) for i in range(0, 9)])
        self.input_mX.setCurrentText(str(data.get("Location", {}).get("mX", 0)))

        # mY 0–4
        self.input_mY = QComboBox()
        self.input_mY.addItems([str(i) for i in range(0, 5)])
        self.input_mY.setCurrentText(str(data.get("Location", {}).get("mY", 0)))

        # RecoverDelay float
        self.input_delay = QDoubleSpinBox()
        self.input_delay.setRange(0.0, 999.0)
        self.input_delay.setSingleStep(0.5)
        self.input_delay.setValue(float(data.get("RecoverDelay", 0.0)))

        form.addRow("Group:", self.input_group)
        form.addRow("mX:", self.input_mX)
        form.addRow("mY:", self.input_mY)
        form.addRow("Recover Delay:", self.input_delay)

        layout.addLayout(form)

        # OK / Cancel
        row = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        row.addWidget(btn_ok)
        row.addWidget(btn_cancel)
        layout.addLayout(row)

        self.setLayout(layout)

    # -------------------------------------------------

    def get_data(self):
        return {
            "Group": self.input_group.currentText(),
            "Location": {
                "mX": int(self.input_mX.currentText()),
                "mY": int(self.input_mY.currentText())
            },
            "RecoverDelay": float(self.input_delay.value())
        }