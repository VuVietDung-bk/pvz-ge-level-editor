from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QFormLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt


class PowerTileDialog(QDialog):
    """Dialog for editing PowerTileProperties."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit PowerTileProperties")
        self.resize(650, 500)

        data = existing_data or {}
        layout = QVBoxLayout()

        # --- Linked Tiles list ---
        layout.addWidget(QLabel("Linked Tiles:"))
        self.list = QListWidget()

        for tile in data.get("LinkedTiles", []):
            # normalize & set defaults to avoid KeyError when loading old files
            norm = {
                "Group": tile.get("Group", "alpha"),
                "Location": {
                    "mX": tile.get("Location", {}).get("mX", 0),
                    "mY": tile.get("Location", {}).get("mY", 0),
                },
                "PropagationDelay": float(tile.get("PropagationDelay", 0.0))
            }
            # only include InitialDelay if present and non-zero
            init_delay = float(tile.get("PropagationInitialDelay", 0.0))
            if init_delay != 0.0:
                norm["PropagationInitialDelay"] = init_delay

            item = QListWidgetItem(self.format_entry(norm))
            item.setData(Qt.ItemDataRole.UserRole, norm)
            self.list.addItem(item)

        layout.addWidget(self.list)

        # --- Buttons for managing linked tiles ---
        btn_add = QPushButton("➕ Add Linked Tile")
        btn_edit = QPushButton("✏️ Edit Selected")
        btn_remove = QPushButton("🗑 Remove Selected")

        btn_add.clicked.connect(self.add_link)
        btn_edit.clicked.connect(self.edit_link)
        btn_remove.clicked.connect(self.remove_link)
        self.list.itemDoubleClicked.connect(lambda _: self.edit_link())

        btns = QHBoxLayout()
        btns.addWidget(btn_add)
        btns.addWidget(btn_edit)
        btns.addWidget(btn_remove)
        layout.addLayout(btns)

        # --- OK/Cancel buttons ---
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # ========================== Handlers ==========================

    def add_link(self):
        dlg = PowerTileLinkDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            data = dlg.get_data()
            item = QListWidgetItem(self.format_entry(data))
            item.setData(Qt.ItemDataRole.UserRole, data)
            self.list.addItem(item)

    def edit_link(self):
        idx = self.list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select", "Please select an entry to edit.")
            return
        item = self.list.item(idx)
        existing = item.data(Qt.ItemDataRole.UserRole) or {}
        dlg = PowerTileLinkDialog(self, existing)
        if dlg.exec() == dlg.DialogCode.Accepted:
            data = dlg.get_data()
            item.setText(self.format_entry(data))
            item.setData(Qt.ItemDataRole.UserRole, data)

    def remove_link(self):
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))

    def format_entry(self, data: dict) -> str:
        group = data.get("Group", "alpha")
        loc = data.get("Location", {"mX": 0, "mY": 0})
        delay = float(data.get("PropagationDelay", 0.0))
        init_delay = float(data.get("PropagationInitialDelay", 0.0))
        base = f"{group} → ({loc.get('mX',0)},{loc.get('mY',0)}) | Delay={delay}"
        if init_delay != 0.0:
            base += f" | InitDelay={init_delay}"
        return base

    def get_data(self):
        tiles = []
        for i in range(self.list.count()):
            item = self.list.item(i)
            data = dict(item.data(Qt.ItemDataRole.UserRole) or {})
            # ensure numeric types are correct on export
            data["PropagationDelay"] = float(data.get("PropagationDelay", 0.0))
            if float(data.get("PropagationInitialDelay", 0.0)) == 0.0 and "PropagationInitialDelay" in data:
                # drop zero initial delay to keep JSON clean
                data.pop("PropagationInitialDelay", None)
            tiles.append(data)
        return {"LinkedTiles": tiles}


class PowerTileLinkDialog(QDialog):
    """Sub-dialog for one linked tile entry."""
    GROUPS = ["alpha", "beta", "gamma", "delta", "epsilon"]

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Linked Tile")
        self.resize(400, 300)

        data = existing_data or {}
        layout = QFormLayout()

        self.group = QComboBox()
        self.group.addItems(self.GROUPS)
        if data.get("Group") in self.GROUPS:
            self.group.setCurrentText(data["Group"])

        self.mx = QSpinBox(); self.mx.setRange(0, 8)
        self.my = QSpinBox(); self.my.setRange(0, 5)
        loc = data.get("Location", {})
        self.mx.setValue(int(loc.get("mX", 0)))
        self.my.setValue(int(loc.get("mY", 0)))

        self.propagation_delay = QDoubleSpinBox()
        self.propagation_delay.setRange(0, 100)
        self.propagation_delay.setSingleStep(0.1)
        self.propagation_delay.setValue(float(data.get("PropagationDelay", 0.0)))

        self.propagation_init_delay = QDoubleSpinBox()
        self.propagation_init_delay.setRange(0, 100)
        self.propagation_init_delay.setSingleStep(0.1)
        self.propagation_init_delay.setValue(float(data.get("PropagationInitialDelay", 0.0)))

        layout.addRow("Group:", self.group)
        layout.addRow("Grid X:", self.mx)
        layout.addRow("Grid Y:", self.my)
        layout.addRow("Propagation Delay:", self.propagation_delay)
        layout.addRow("Initial Delay:", self.propagation_init_delay)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self):
        data = {
            "Group": self.group.currentText(),
            "Location": {"mX": self.mx.value(), "mY": self.my.value()},
            "PropagationDelay": self.propagation_delay.value()
        }
        # chỉ thêm khi khác 0 để tránh rác JSON
        if self.propagation_init_delay.value() != 0:
            data["PropagationInitialDelay"] = self.propagation_init_delay.value()
        return data