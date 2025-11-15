from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QListWidget,
    QPushButton, QDialogButtonBox, QHBoxLayout, QLabel,
    QSpinBox, QMessageBox
)
from editors.base import GridItemLineEdit


class InitialGridItemDialog(QDialog):
    """Dialog for editing InitialGridItemProperties."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit InitialGridItemProperties")
        self.resize(500, 400)

        data = existing_data or {}
        layout = QVBoxLayout()

        layout.addWidget(QLabel("<b>Initial Grid Item Placements</b>"))

        # List
        self.items_list = QListWidget()
        for it in data.get("InitialGridItemPlacements", []):
            gx = it.get("GridX", 0)
            gy = it.get("GridY", 0)
            t = it.get("TypeName", "")
            self.items_list.addItem(f"({gx},{gy}) - {t}")

        layout.addWidget(self.items_list)

        # buttons add / edit / remove
        btn_add = QPushButton("➕ Add")
        btn_edit = QPushButton("✏️ Edit Selected")
        btn_remove = QPushButton("🗑 Remove")

        btn_add.clicked.connect(self.add_item)
        btn_edit.clicked.connect(self.edit_item)
        btn_remove.clicked.connect(self.remove_item)

        b = QHBoxLayout()
        b.addWidget(btn_add)
        b.addWidget(btn_edit)
        b.addWidget(btn_remove)
        layout.addLayout(b)

        # OK Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # --------------------------------------------------------
    def add_item(self):
        dlg = OneGridItemDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            data = dlg.get_data()
            gx, gy = data["GridX"], data["GridY"]
            t = data["TypeName"]
            self.items_list.addItem(f"({gx},{gy}) - {t}")

    def edit_item(self):
        row = self.items_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select", "Select an entry to edit.")
            return

        text = self.items_list.item(row).text()
        coords, t = text.split(" - ")
        gx, gy = coords.strip("()").split(",")

        dlg = OneGridItemDialog(
            self,
            existing_data={
                "GridX": int(gx),
                "GridY": int(gy),
                "TypeName": t,
            }
        )

        if dlg.exec() == dlg.DialogCode.Accepted:
            data = dlg.get_data()
            gx, gy, t = data["GridX"], data["GridY"], data["TypeName"]
            self.items_list.item(row).setText(f"({gx},{gy}) - {t}")

    def remove_item(self):
        for it in self.items_list.selectedItems():
            self.items_list.takeItem(self.items_list.row(it))

    # --------------------------------------------------------
    def get_data(self):
        placements = []
        for i in range(self.items_list.count()):
            text = self.items_list.item(i).text()
            coords, t = text.split(" - ")
            gx, gy = coords.strip("()").split(",")
            placements.append({
                "GridX": int(gx),
                "GridY": int(gy),
                "TypeName": t.strip()
            })

        return {"InitialGridItemPlacements": placements}


# ============================================================
# Subdialog for one entry
# ============================================================
class OneGridItemDialog(QDialog):
    """Popup for adding 1 grid item."""
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Grid Item")
        self.resize(300, 200)

        data = existing_data or {}

        form = QFormLayout()

        self.gridx = QSpinBox()
        self.gridx.setRange(0, 8)
        self.gridx.setValue(data.get("GridX", 0))

        self.gridy = QSpinBox()
        self.gridy.setRange(0, 4)
        self.gridy.setValue(data.get("GridY", 0))

        # GridItemLineEdit for TypeName
        self.typename = GridItemLineEdit()
        self.typename.setText(data.get("TypeName", ""))
        self.typename.setPlaceholderText("grid item id (slider_up, slider_down, lava, ... )")

        form.addRow("Column (0-8):", self.gridx)
        form.addRow("Row (0-4):", self.gridy)
        form.addRow("TypeName:", self.typename)

        # OK Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)

        self.setLayout(form)

    def get_data(self):
        return {
            "GridX": self.gridx.value(),
            "GridY": self.gridy.value(),
            "TypeName": self.typename.text().strip()
        }