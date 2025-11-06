from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox,
    QDialogButtonBox, QPushButton, QListWidget, QLabel,
    QHBoxLayout, QMessageBox
)
from editors.base import GridItemLineEdit


class GravestonePropertiesDialog(QDialog):
    """Dialog for editing GravestoneProperties, including ForceSpawnData."""
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit GravestoneProperties")
        self.resize(500, 400)

        data = existing_data or {}

        form = QFormLayout()

        # Basic properties
        self.gravestone_count = QSpinBox()
        self.gravestone_count.setRange(0, 45)
        self.gravestone_count.setValue(data.get("GravestoneCount", 0))

        self.spawn_start = QSpinBox()
        self.spawn_start.setRange(1, 9)
        self.spawn_start.setValue(data.get("SpawnColumnStart", 0))

        self.spawn_end = QSpinBox()
        self.spawn_end.setRange(1, 9)
        self.spawn_end.setValue(data.get("SpawnColumnEnd", 0))

        # ForceSpawnData list
        self.force_list = QListWidget()
        for entry in data.get("ForceSpawnData", []):
            gx = entry.get("GridX", 0)
            gy = entry.get("GridY", 0)
            typ = entry.get("TypeName", "")
            self.force_list.addItem(f"({gx}, {gy}) - {typ}")

        btn_add = QPushButton("➕ Add Force Spawn")
        btn_add.clicked.connect(self.add_force_spawn)
        btn_remove = QPushButton("🗑 Remove Selected")
        btn_remove.clicked.connect(self.remove_selected)
        btns = QHBoxLayout()
        btns.addWidget(btn_add)
        btns.addWidget(btn_remove)

        form.addRow("Gravestone Count:", self.gravestone_count)
        form.addRow("Spawn Column Start:", self.spawn_start)
        form.addRow("Spawn Column End:", self.spawn_end)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(QLabel("Force Spawn Data:"))
        layout.addWidget(self.force_list)
        layout.addLayout(btns)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # --------------------------------
    def add_force_spawn(self):
        dlg = ForceSpawnEntryDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            gx, gy, t = d["GridX"], d["GridY"], d["TypeName"]
            self.force_list.addItem(f"({gx}, {gy}) - {t}")

    def remove_selected(self):
        for i in self.force_list.selectedItems():
            self.force_list.takeItem(self.force_list.row(i))

    def get_data(self):
        force_data = []
        for i in range(self.force_list.count()):
            txt = self.force_list.item(i).text()
            coords, name = txt.split(" - ")
            gx, gy = coords.strip("()").split(", ")
            force_data.append({
                "GridX": int(gx),
                "GridY": int(gy),
                "TypeName": name
            })

        data = {}
        if self.gravestone_count.value() > 0:
            data["GravestoneCount"] = self.gravestone_count.value()
        if self.spawn_start.value() > 0 or self.spawn_end.value() > 0:
            data["SpawnColumnStart"] = self.spawn_start.value()
            data["SpawnColumnEnd"] = self.spawn_end.value()
        if force_data:
            data["ForceSpawnData"] = force_data
        return data


class ForceSpawnEntryDialog(QDialog):
    """Dialog for adding one ForceSpawnData entry."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Force Spawn Entry")
        self.resize(300, 200)
        form = QFormLayout()

        self.gridx = QSpinBox(); self.gridx.setRange(0, 20)
        self.gridy = QSpinBox(); self.gridy.setRange(0, 5)
        self.type_name = GridItemLineEdit()

        form.addRow("GridX:", self.gridx)
        form.addRow("GridY:", self.gridy)
        form.addRow("TypeName:", self.type_name)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self):
        return {
            "GridX": self.gridx.value(),
            "GridY": self.gridy.value(),
            "TypeName": self.type_name.text().strip()
        }