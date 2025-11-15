from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QListWidget,
    QSpinBox
)

from editors.base import ZombieLineEdit, ConditionLineEdit


class InitialZombiePropertiesEditor(QDialog):
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)

        self.setWindowTitle("Edit InitialZombieProperties")
        self.setModal(True)
        self.resize(500, 420)

        self.existing_data = existing_data or {"InitialZombiePlacements": []}
        self.placements = self.existing_data.get("InitialZombiePlacements", [])

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Initial Zombie Placements:"))

        # List widget displaying all placements
        self.list_widget = QListWidget()
        for p in self.placements:
            self.list_widget.addItem(self._placement_to_text(p))

        layout.addWidget(self.list_widget)

        # Buttons under the list
        btn_row = QHBoxLayout()
        btn_add = QPushButton("Add Placement")
        btn_remove = QPushButton("Remove Selected")

        btn_add.clicked.connect(self.add_placement)
        btn_remove.clicked.connect(self.remove_placement)

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

    # ---------------------------------------------------

    def _placement_to_text(self, p):
        c = p.get("Condition", "")
        x = p.get("GridX", "")
        y = p.get("GridY", "")
        t = p.get("TypeName", "")
        return f"{t} @ ({x},{y}) [{c}]"

    # ---------------------------------------------------

    def add_placement(self):
        dlg = ZombiePlacementEditorDialog(parent=self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            data = dlg.get_data()
            if data:
                self.placements.append(data)
                self.list_widget.addItem(self._placement_to_text(data))

    def remove_placement(self):
        row = self.list_widget.currentRow()
        if row < 0:
            return
        self.list_widget.takeItem(row)
        self.placements.pop(row)

    # ---------------------------------------------------

    def get_data(self):
        return {"InitialZombiePlacements": self.placements}

class ZombiePlacementEditorDialog(QDialog):
    def __init__(self, parent=None, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Zombie Placement")
        self.setModal(True)

        data = existing or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # Condition autocomplete
        self.input_condition = ConditionLineEdit()
        self.input_condition.setText(data.get("Condition", ""))

        # Zombie autocomplete
        self.input_typename = ZombieLineEdit()
        self.input_typename.setText(data.get("TypeName", ""))

        # GridX 0–8
        self.input_gridx = QSpinBox()
        self.input_gridx.setRange(0, 8)
        self.input_gridx.setValue(data.get("GridX", 0))

        # GridY 0–4
        self.input_gridy = QSpinBox()
        self.input_gridy.setRange(0, 4)
        self.input_gridy.setValue(data.get("GridY", 0))

        form.addRow("Condition:", self.input_condition)
        form.addRow("TypeName:", self.input_typename)
        form.addRow("Column (0-8):", self.input_gridx)
        form.addRow("Row (0-4):", self.input_gridy)

        layout.addLayout(form)

        # OK / Cancel
        btn_row = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    # ---------------------------------------------------

    def get_data(self):
        data = {
            "TypeName": self.input_typename.text().strip(),
            "GridX": int(self.input_gridx.value()),
            "GridY": int(self.input_gridy.value()),
        }

        cond = self.input_condition.text().strip()
        if cond:
            data["Condition"] = cond

        return data
