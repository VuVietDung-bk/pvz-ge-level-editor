from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox, QHBoxLayout,
    QListWidget, QPushButton, QSpinBox, QDoubleSpinBox, QLabel, QMessageBox
)
from editors.base import PlantLineEdit
import re


class ModifyConveyorDialog(QDialog):
    """Dialog for editing ModifyConveyorWaveActionProps."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit ModifyConveyorWaveActionProps")
        self.resize(720, 560)

        data = existing_data or {}
        layout = QVBoxLayout()

        # --------- ADD list ---------
        layout.addWidget(QLabel("Plants to Add:"))
        self.add_list = QListWidget()
        for p in data.get("Add", []):
            self.add_list.addItem(self.format_plant_entry(p))
        layout.addWidget(self.add_list)

        btn_add_add = QPushButton("➕ Add")
        btn_edit_add = QPushButton("✏️ Edit Selected")
        btn_remove_add = QPushButton("🗑 Remove Selected")
        btn_add_add.clicked.connect(lambda: self.add_plant(self.add_list))
        btn_edit_add.clicked.connect(lambda: self.edit_plant(self.add_list))
        btn_remove_add.clicked.connect(lambda: self.remove_selected(self.add_list))
        self.add_list.itemDoubleClicked.connect(lambda _: self.edit_plant(self.add_list))

        add_btns = QHBoxLayout()
        add_btns.addWidget(btn_add_add)
        add_btns.addWidget(btn_edit_add)
        add_btns.addWidget(btn_remove_add)
        layout.addLayout(add_btns)

        # --------- REMOVE list ---------
        layout.addWidget(QLabel("Plants to Remove:"))
        self.remove_list = QListWidget()
        for p in data.get("Remove", []):
            self.remove_list.addItem(self.format_plant_entry(p))
        layout.addWidget(self.remove_list)

        btn_add_remove = QPushButton("➕ Add")
        btn_edit_remove = QPushButton("✏️ Edit Selected")
        btn_remove_remove = QPushButton("🗑 Remove Selected")
        btn_add_remove.clicked.connect(lambda: self.add_plant(self.remove_list))
        btn_edit_remove.clicked.connect(lambda: self.edit_plant(self.remove_list))
        btn_remove_remove.clicked.connect(lambda: self.remove_selected(self.remove_list))
        self.remove_list.itemDoubleClicked.connect(lambda _: self.edit_plant(self.remove_list))

        remove_btns = QHBoxLayout()
        remove_btns.addWidget(btn_add_remove)
        remove_btns.addWidget(btn_edit_remove)
        remove_btns.addWidget(btn_remove_remove)
        layout.addLayout(remove_btns)

        # --------- OK/Cancel ----------
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    # ---------------- Utility: format display text ----------------
    def format_plant_entry(self, p):
        """Format plant entry into readable list text."""
        name = p.get("Type", "").replace("RTID(", "").replace("@PlantTypes)", "")
        info = [f"W={p.get('Weight', 0)}"]

        if p.get("MinCount"):
            info.append(f"Min={p['MinCount']}")
        if p.get("MaxCount"):
            info.append(f"Max={p['MaxCount']}")
        if p.get("MinCountCooldownSeconds"):
            info.append(f"MinCD={p['MinCountCooldownSeconds']}s")
        if p.get("MaxCountCooldownSeconds"):
            info.append(f"MaxCD={p['MaxCountCooldownSeconds']}s")
        if p.get("MinWeightFactor"):
            info.append(f"MinWF={p['MinWeightFactor']}")
        if p.get("MaxWeightFactor"):
            info.append(f"MaxWF={p['MaxWeightFactor']}")

        return f"{name} ({', '.join(info)})"

    # ---------------- Utility: parse entry back into data ----------------
    def parse_plant_entry(self, text):
        """Reverse of format_plant_entry — parse string into dict."""
        name = text.split(" (")[0].strip()
        inside = text[text.find("(") + 1:text.find(")")]
        parts = re.findall(r"(\w+)=([\w\.]+)", inside)

        d = {"Type": f"RTID({name}@PlantTypes)"}
        for key, val in parts:
            if key == "W":
                d["Weight"] = int(val)
            elif key == "Min":
                d["MinCount"] = int(val)
            elif key == "Max":
                d["MaxCount"] = int(val)
            elif key == "MinCD":
                d["MinCountCooldownSeconds"] = int(val.replace("s", ""))
            elif key == "MaxCD":
                d["MaxCountCooldownSeconds"] = int(val.replace("s", ""))
            elif key == "MinWF":
                d["MinWeightFactor"] = float(val)
            elif key == "MaxWF":
                d["MaxWeightFactor"] = float(val)
        return d

    # ------------------------------------------------
    def add_plant(self, list_widget):
        dlg = ModifyPlantDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            data = dlg.get_data()
            list_widget.addItem(self.format_plant_entry(data))

    def edit_plant(self, list_widget):
        idx = list_widget.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select Plant", "Please select an item to edit.")
            return

        text = list_widget.item(idx).text()
        existing = self.parse_plant_entry(text)

        dlg = ModifyPlantDialog(self, existing)
        if dlg.exec() == dlg.DialogCode.Accepted:
            data = dlg.get_data()
            list_widget.item(idx).setText(self.format_plant_entry(data))

    def remove_selected(self, list_widget):
        for item in list_widget.selectedItems():
            list_widget.takeItem(list_widget.row(item))

    # ------------------------------------------------
    def get_data(self):
        """Return final objdata for JSON export."""
        def parse_list(list_widget):
            result = []
            for i in range(list_widget.count()):
                text = list_widget.item(i).text()
                result.append(self.parse_plant_entry(text))
            return result

        return {
            "Add": parse_list(self.add_list),
            "Remove": parse_list(self.remove_list)
        }


# ---------------- Sub-dialog for each plant entry ----------------
class ModifyPlantDialog(QDialog):
    """Dialog for adding/editing one plant entry in ModifyConveyorWaveActionProps."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Conveyor Modification")
        self.resize(420, 400)
        form = QFormLayout()

        data = existing_data or {}

        self.plant_type = PlantLineEdit()
        self.plant_type.setText(
            data.get("Type", "").replace("RTID(", "").replace("@PlantTypes)", "")
        )
        self.weight = QSpinBox(); self.weight.setRange(0, 1000)
        self.weight.setValue(data.get("Weight", 0))

        # Counts & cooldowns
        self.max_count = QSpinBox(); self.max_count.setRange(0, 100)
        self.max_count.setValue(data.get("MaxCount", 0))
        self.max_count_cooldown = QSpinBox(); self.max_count_cooldown.setRange(0, 9999)
        self.max_count_cooldown.setValue(data.get("MaxCountCooldownSeconds", 0))

        self.min_count = QSpinBox(); self.min_count.setRange(0, 100)
        self.min_count.setValue(data.get("MinCount", 0))
        self.min_count_cooldown = QSpinBox(); self.min_count_cooldown.setRange(0, 9999)
        self.min_count_cooldown.setValue(data.get("MinCountCooldownSeconds", 0))

        # Weight factors
        self.max_weight_factor = QDoubleSpinBox(); self.max_weight_factor.setRange(0, 10)
        self.max_weight_factor.setValue(data.get("MaxWeightFactor", 0))
        self.min_weight_factor = QDoubleSpinBox(); self.min_weight_factor.setRange(0, 10)
        self.min_weight_factor.setValue(data.get("MinWeightFactor", 0))

        form.addRow("Plant Type:", self.plant_type)
        form.addRow("Weight:", self.weight)
        form.addRow("Max Count:", self.max_count)
        form.addRow("Max Count Cooldown (s):", self.max_count_cooldown)
        form.addRow("Min Count:", self.min_count)
        form.addRow("Min Count Cooldown (s):", self.min_count_cooldown)
        form.addRow("Max Weight Factor:", self.max_weight_factor)
        form.addRow("Min Weight Factor:", self.min_weight_factor)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)
        self.setLayout(form)

    def get_data(self):
        """Return structured dict, omitting 0 values."""
        d = {
            "Type": f"RTID({self.plant_type.text().strip()}@PlantTypes)",
            "Weight": self.weight.value()
        }
        if self.max_count.value() > 0:
            d["MaxCount"] = self.max_count.value()
        if self.max_count_cooldown.value() > 0:
            d["MaxCountCooldownSeconds"] = self.max_count_cooldown.value()
        if self.min_count.value() > 0:
            d["MinCount"] = self.min_count.value()
        if self.min_count_cooldown.value() > 0:
            d["MinCountCooldownSeconds"] = self.min_count_cooldown.value()
        if self.max_weight_factor.value() > 0:
            d["MaxWeightFactor"] = self.max_weight_factor.value()
        if self.min_weight_factor.value() > 0:
            d["MinWeightFactor"] = self.min_weight_factor.value()
        return d