from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QHBoxLayout,
    QPushButton, QDialogButtonBox, QMessageBox, QFormLayout,
    QLabel, QSpinBox, QComboBox, QGridLayout, QCheckBox
)
from PyQt6.QtCore import Qt
from editors.base import ZombieLineEdit
from data_loader import GameData


class SpawnZombiesJitteredDialog(QDialog):
    """Dialog for editing SpawnZombiesJitteredWaveActionProps."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit SpawnZombiesJitteredWaveActionProps")
        self.resize(650, 650)

        data = existing_data or {}
        layout = QVBoxLayout()

        # =============================================
        # ZOMBIE LIST
        # =============================================
        layout.addWidget(QLabel("<b>Zombie Spawn List</b>"))
        self.zombie_list = QListWidget()

        for z in data.get("Zombies", []):
            t = z.get("Type", "")
            row = z.get("Row", 0)
            col = z.get("Column", 0)
            carry = z.get("CarrySun", 0)

            desc = t
            if row != 0:
                desc += f" → Row {row}"
            if col != 0:
                desc += f", Col {col}"
            if carry > 0:
                desc += f"  ☼{carry}"

            self.zombie_list.addItem(desc)

        btn_add = QPushButton("➕ Add Zombie")
        btn_edit = QPushButton("✏️ Edit Selected")
        btn_remove = QPushButton("🗑 Remove Selected")

        btn_add.clicked.connect(self.add_zombie)
        btn_edit.clicked.connect(self.edit_zombie)
        btn_remove.clicked.connect(self.remove_zombie)

        zbtns = QHBoxLayout()
        zbtns.addWidget(btn_add)
        zbtns.addWidget(btn_edit)
        zbtns.addWidget(btn_remove)

        layout.addWidget(self.zombie_list)
        layout.addLayout(zbtns)

        self.must_kill_all = QCheckBox("Must Kill All To Next Wave")
        if str(data.get("MustKillAllToNextWave", "")).lower() == "true":
            self.must_kill_all.setChecked(True)

        layout.addWidget(self.must_kill_all)

        layout.addWidget(QLabel("<b>Additional Plantfood</b>"))
        self.additional_pf = QSpinBox()
        self.additional_pf.setRange(0, 10)
        self.additional_pf.setValue(data.get("AdditionalPlantfood", 0))
        layout.addWidget(self.additional_pf)

        layout.addWidget(QLabel("<b>Dynamic Plantfood (independent)</b>"))

        self.dynamic_pf = []
        grid = QGridLayout()
        labels = ["Diff Null", "Diff Null", "Diff Null", "Diff D", "Diff C", "Diff B", "Diff A"]

        defaults = data.get("DynamicPlantfood", [0] * 7)

        for i in range(7):
            sp = QSpinBox()
            sp.setRange(0, 10)
            sp.setValue(defaults[i] if i < len(defaults) else 0)
            grid.addWidget(QLabel(labels[i]), i, 0)
            grid.addWidget(sp, i, 1)
            self.dynamic_pf.append(sp)

        layout.addLayout(grid)

        layout.addWidget(QLabel("<b>Notification Event (Neon Jam)</b>"))
        self.event_combo = QComboBox()
        available_events = GameData.get_flat_list("Neon Jams")
        self.event_combo.addItem("None")
        self.event_combo.addItems(available_events)

        chosen_events = data.get("NotificationEvents", [])
        if chosen_events:
            first = chosen_events[0]
            if first in available_events:
                self.event_combo.setCurrentText(first)
        else:
            self.event_combo.setCurrentText("None")

        layout.addWidget(self.event_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def add_zombie(self):
        dlg = OneZombieDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            z = dlg.get_data()
            desc = self.format_desc(z)
            self.zombie_list.addItem(desc)

    def edit_zombie(self):
        idx = self.zombie_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select", "Please select a zombie to edit.")
            return

        text = self.zombie_list.item(idx).text()
        z = self.parse_desc(text)

        dlg = OneZombieDialog(self, z)
        if dlg.exec() == dlg.DialogCode.Accepted:
            z2 = dlg.get_data()
            self.zombie_list.item(idx).setText(self.format_desc(z2))

    def remove_zombie(self):
        for item in self.zombie_list.selectedItems():
            self.zombie_list.takeItem(self.zombie_list.row(item))

    def format_desc(self, z):
        desc = z["Type"]
        if z.get("Row", 0) != 0:
            desc += f" → Row {z['Row']}"
        if z.get("Column", 0) != 0:
            desc += f", Col {z['Column']}"
        if z.get("CarrySun", 0) > 0:
            desc += f"  ☼{z['CarrySun']}"
        return desc

    def parse_desc(self, text):
        parts = text.split("→")
        ztype = parts[0].strip()
        row = 0
        col = 0
        carry = 0

        if len(parts) > 1:
            right = parts[1]

            if "☼" in right:
                right, carry_part = right.split("☼")
                carry = int(carry_part.strip())

            if "Col" in right:
                row_part, col_part = right.split("Col")
                row = int(row_part.replace("Row", "").strip().strip(","))
                col = int(col_part.strip())
            else:
                row = int(right.replace("Row", "").strip())

        return {"Type": ztype, "Row": row, "Column": col, "CarrySun": carry}

    # ========================================================
    def get_data(self):
        zombies = []

        for i in range(self.zombie_list.count()):
            z = self.parse_desc(self.zombie_list.item(i).text())
            z_entry = {"Type": z["Type"]}

            if z["Row"] != 0:
                z_entry["Row"] = z["Row"]
            if z["Column"] != 0:
                z_entry["Column"] = z["Column"]
            if z["CarrySun"] > 0:
                z_entry["CarrySun"] = z["CarrySun"]

            zombies.append(z_entry)

        result = {"Zombies": zombies}

        if self.additional_pf.value() > 0:
            result["AdditionalPlantfood"] = self.additional_pf.value()

        dyn = [sp.value() for sp in self.dynamic_pf]
        if any(val != 0 for val in dyn):
            result["DynamicPlantfood"] = dyn

        if self.must_kill_all.isChecked():
            result["MustKillAllToNextWave"] = True

        ev = self.event_combo.currentText()
        if ev != "None":
            result["NotificationEvents"] = [ev]

        return result

class OneZombieDialog(QDialog):
    """Dialog to create or edit one zombie entry."""
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Zombie Spawn Entry")
        self.resize(400, 250)

        data = existing_data or {}
        form = QFormLayout()

        self.ztype = ZombieLineEdit()
        cleaned = data.get("Type", "").replace("RTID(", "").replace("@ZombieTypes)", "")
        self.ztype.setText(cleaned)

        self.row = QSpinBox(); self.row.setRange(0, 5)
        self.row.setValue(data.get("Row", 0))

        self.col = QSpinBox(); self.col.setRange(0, 9)
        self.col.setValue(data.get("Column", 0))

        self.carry = QSpinBox(); self.carry.setRange(0, 999)
        self.carry.setValue(data.get("CarrySun", 0))

        form.addRow("Zombie Type:", self.ztype)
        form.addRow("Row (0–5):", self.row)
        form.addRow("Column (0–9):", self.col)
        form.addRow("Carry Sun:", self.carry)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)

        self.setLayout(form)

    def get_data(self):
        z = {
            "Type": f"RTID({self.ztype.text().strip()}@ZombieTypes)"
        }
        if self.row.value() != 0:
            z["Row"] = self.row.value()
        if self.col.value() != 0:
            z["Column"] = self.col.value()
        if self.carry.value() > 0:
            z["CarrySun"] = self.carry.value()
        return z