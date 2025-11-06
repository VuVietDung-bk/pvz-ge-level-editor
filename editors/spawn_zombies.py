from PyQt6.QtWidgets import *
from editors.base import ZombieLineEdit

class SpawnZombiesJitteredDialog(QDialog):
    """Dialog for editing SpawnZombiesJitteredWaveActionProps."""
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit SpawnZombiesJitteredWaveActionProps")
        self.resize(500, 400)

        data = existing_data or {}
        zombies = data.get("Zombies", [])

        layout = QVBoxLayout()
        self.list = QListWidget()
        for z in zombies:
            self.list.addItem(f"{z['Type']} → Row {z['Row']}")

        # Buttons
        btn_add = QPushButton("➕ Add Zombie")
        btn_edit = QPushButton("✏️ Edit Selected")
        btn_remove = QPushButton("🗑 Remove Selected")

        btn_add.clicked.connect(self.add_zombie)
        btn_edit.clicked.connect(self.edit_zombie)
        btn_remove.clicked.connect(self.remove_zombie)

        btns = QHBoxLayout()
        btns.addWidget(btn_add)
        btns.addWidget(btn_edit)
        btns.addWidget(btn_remove)

        layout.addWidget(QLabel("Zombie Spawn List:"))
        layout.addWidget(self.list)
        layout.addLayout(btns)

        # OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # ---------------------------------
    def add_zombie(self):
        dlg = OneZombieDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            z = dlg.get_data()
            self.list.addItem(f"{z['Type']} → Row {z['Row']}")

    def edit_zombie(self):
        idx = self.list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select", "Please select a zombie to edit.")
            return

        text = self.list.item(idx).text()
        type_part, row_part = text.split("→ Row")
        ztype = type_part.strip()
        row = int(row_part.strip())
        dlg = OneZombieDialog(self, {"Type": ztype, "Row": row})
        if dlg.exec() == dlg.DialogCode.Accepted:
            z = dlg.get_data()
            self.list.item(idx).setText(f"{z['Type']} → Row {z['Row']}")

    def remove_zombie(self):
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))

    def get_data(self):
        """Return structured JSON data."""
        zombies = []
        for i in range(self.list.count()):
            text = self.list.item(i).text()
            type_part, row_part = text.split("→ Row")
            ztype = type_part.strip()
            row = int(row_part.strip())
            zombies.append({"Type": ztype, "Row": row})
        return {"Zombies": zombies}
    
class OneZombieDialog(QDialog):
    """Dialog to create or edit one zombie entry."""
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Zombie Spawn Entry")
        self.resize(400, 250)

        data = existing_data or {}
        layout = QFormLayout()

        self.ztype = ZombieLineEdit()
        self.ztype.setText(data.get("Type", "").replace("RTID(", "").replace("@ZombieTypes)", ""))
        layout.addRow("Zombie Type:", self.ztype)
        self.row = QSpinBox(); self.row.setRange(0, 5)
        self.row.setValue(data.get("Row", 0))

        layout.addRow("Zombie Type:", self.ztype)
        layout.addRow("Row (0–5):", self.row)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        return {
            "Type": f"RTID({self.ztype.text().strip()}@ZombieTypes)",
            "Row": self.row.value()
        }