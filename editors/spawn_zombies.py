from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QHBoxLayout,
    QPushButton, QDialogButtonBox, QMessageBox, QFormLayout,
    QLabel, QSpinBox, QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt
from editors.base import ZombieLineEdit
from data_loader import GameData


class SpawnZombiesJitteredDialog(QDialog):
    """Dialog for editing SpawnZombiesJitteredWaveActionProps."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit SpawnZombiesJitteredWaveActionProps")
        self.resize(600, 500)

        data = existing_data or {}
        layout = QVBoxLayout()

        # ========== Zombies List ==========
        layout.addWidget(QLabel("<b>Zombie Spawn List</b>"))
        self.zombie_list = QListWidget()
        for z in data.get("Zombies", []):
            t = z.get("Type", "")
            row = z.get("Row", 0)
            col = z.get("Column", 0)
            desc = t
            if row != 0:
                desc += f" → Row {row}"
            if col != 0:
                desc += f", Col {col}"
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

        # ========== DynamicPlantfood ==========
        layout.addWidget(QLabel("<b>Dynamic Plantfood</b>"))
        self.dynamic_pf = []
        grid = QGridLayout()
        labels = ["Diff Null", "Diff Null", "Diff Null", "Diff D", "Diff C", "Diff B", "Diff A"]
        defaults = data.get("DynamicPlantfood", [0] * 7)
        for i in range(7):
            sp = QSpinBox()
            sp.setRange(0, 1)
            sp.setValue(defaults[i] if i < len(defaults) else 0)
            grid.addWidget(QLabel(labels[i]), i, 0)
            grid.addWidget(sp, i, 1)
            self.dynamic_pf.append(sp)
        layout.addLayout(grid)

        # ========== AdditionalPlantfood ==========
        layout.addWidget(QLabel("<b>Additional Plantfood</b>"))
        self.additional_pf = QSpinBox()
        self.additional_pf.setRange(0, 10)
        self.additional_pf.setValue(data.get("AdditionalPlantfood", 0))
        layout.addWidget(self.additional_pf)

        # ========== NotificationEvents ==========
        layout.addWidget(QLabel("<b>Notification Event (Neon Jam)</b>"))
        self.event_combo = QComboBox()
        available_events = GameData.get_flat_list("Neon Jams")
        self.event_combo.addItem("None")
        self.event_combo.addItems(available_events)

        chosen_events = data.get("NotificationEvents", [])
        if chosen_events:
            ev = chosen_events[0]
            if ev in available_events:
                self.event_combo.setCurrentText(ev)
        else:
            self.event_combo.setCurrentText("None")

        layout.addWidget(self.event_combo)

        # OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # ========================================================
    def add_zombie(self):
        dlg = OneZombieDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            z = dlg.get_data()
            desc = z["Type"]
            if z.get("Row", 0) != 0:
                desc += f" → Row {z['Row']}"
            if z.get("Column", 0) != 0:
                desc += f", Col {z['Column']}"
            self.zombie_list.addItem(desc)

    def edit_zombie(self):
        idx = self.zombie_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select", "Please select a zombie to edit.")
            return

        text = self.zombie_list.item(idx).text()
        parts = text.split("→ Row")
        ztype = parts[0].strip()
        row = 0
        col = 0
        if len(parts) > 1:
            rest = parts[1].strip()
            if ", Col" in rest:
                row_part, col_part = rest.split(", Col")
                row = int(row_part.strip())
                col = int(col_part.strip())
            else:
                row = int(rest.strip())

        dlg = OneZombieDialog(self, {"Type": ztype, "Row": row, "Column": col})
        if dlg.exec() == dlg.DialogCode.Accepted:
            z = dlg.get_data()
            desc = z["Type"]
            if z.get("Row", 0) != 0:
                desc += f" → Row {z['Row']}"
            if z.get("Column", 0) != 0:
                desc += f", Col {z['Column']}"
            self.zombie_list.item(idx).setText(desc)

    def remove_zombie(self):
        for item in self.zombie_list.selectedItems():
            self.zombie_list.takeItem(self.zombie_list.row(item))

    # ========================================================
    def get_data(self):
        zombies = []
        for i in range(self.zombie_list.count()):
            text = self.zombie_list.item(i).text()
            t = text.split("→")[0].strip()
            row = 0
            col = 0
            if "Row" in text:
                match = text.split("Row")[-1].strip()
                if ", Col" in match:
                    parts = match.split(", Col")
                    row = int(parts[0].strip())
                    col = int(parts[1].strip())
                else:
                    row = int(match.strip())

            z_entry = {"Type": t}
            if row != 0:
                z_entry["Row"] = row
            if col != 0:
                z_entry["Column"] = col
            zombies.append(z_entry)

        dyn_pf = [sp.value() for sp in self.dynamic_pf]
        selected_event = self.event_combo.currentText()
        event_value = selected_event if selected_event != "None" else None

        result = {
            "Zombies": zombies,
            "DynamicPlantfood": dyn_pf,
            "AdditionalPlantfood": self.additional_pf.value(),
        }

        if event_value:
            result["NotificationEvents"] = [event_value]

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
        self.ztype.setText(data.get("Type", "").replace("RTID(", "").replace("@ZombieTypes)", ""))

        self.row = QSpinBox(); self.row.setRange(0, 5)
        self.row.setValue(data.get("Row", 0))
        self.col = QSpinBox(); self.col.setRange(0, 9)
        self.col.setValue(data.get("Column", 0))

        form.addRow("Zombie Type:", self.ztype)
        form.addRow("Row (0–5):", self.row)
        form.addRow("Column (0–9):", self.col)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)

        self.setLayout(form)

    def get_data(self):
        ztype = f"RTID({self.ztype.text().strip()}@ZombieTypes)"
        row = self.row.value()
        col = self.col.value()

        z_entry = {"Type": ztype}
        if row != 0:
            z_entry["Row"] = row
        if col != 0:
            z_entry["Column"] = col
        return z_entry