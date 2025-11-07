from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QSpinBox, QDoubleSpinBox,
    QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from editors.base import PlantLineEdit


class ConveyorSeedBankDialog(QDialog):
    """Dialog for editing ConveyorSeedBankProperties."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit ConveyorSeedBankProperties")
        self.resize(700, 550)

        data = existing_data or {}
        layout = QVBoxLayout()

        # ---------- Drop Delay Conditions ----------
        layout.addWidget(QLabel("Drop Delay Conditions:"))
        self.drop_list = QListWidget()
        for cond in data.get("DropDelayConditions", []):
            self.drop_list.addItem(f"Delay={cond['Delay']}s, MaxPackets={cond['MaxPackets']}")
        layout.addWidget(self.drop_list)

        btn_add_drop = QPushButton("➕ Add Drop Condition")
        btn_edit_drop = QPushButton("✏️ Edit Selected")
        btn_remove_drop = QPushButton("🗑 Remove Selected")
        btn_add_drop.clicked.connect(self.add_drop_condition)
        btn_edit_drop.clicked.connect(self.edit_drop_condition)
        btn_remove_drop.clicked.connect(self.remove_selected_drop)
        drop_btns = QHBoxLayout()
        drop_btns.addWidget(btn_add_drop)
        drop_btns.addWidget(btn_edit_drop)
        drop_btns.addWidget(btn_remove_drop)
        layout.addLayout(drop_btns)

        # ---------- Initial Plant List ----------
        layout.addWidget(QLabel("Initial Plant List:"))
        self.plant_list = QListWidget()
        for p in data.get("InitialPlantList", []):
            if p.get("Weight", 0) <= 0:
                continue
            item = QListWidgetItem(self._format_plant_entry(p))
            item.setData(Qt.ItemDataRole.UserRole, p.copy())
            self.plant_list.addItem(item)
        layout.addWidget(self.plant_list)

        btn_add_plant = QPushButton("➕ Add Plant")
        btn_edit_plant = QPushButton("✏️ Edit Selected")
        btn_remove_plant = QPushButton("🗑 Remove Selected")
        btn_add_plant.clicked.connect(self.add_plant)
        btn_edit_plant.clicked.connect(self.edit_selected_plant)
        btn_remove_plant.clicked.connect(self.remove_selected_plant)
        # double-click to edit
        self.plant_list.itemDoubleClicked.connect(lambda _: self.edit_selected_plant())
        plant_btns = QHBoxLayout()
        plant_btns.addWidget(btn_add_plant)
        plant_btns.addWidget(btn_edit_plant)
        plant_btns.addWidget(btn_remove_plant)
        layout.addLayout(plant_btns)

        # ---------- Speed Conditions ----------
        layout.addWidget(QLabel("Speed Conditions:"))
        self.speed_list = QListWidget()
        for cond in data.get("SpeedConditions", []):
            self.speed_list.addItem(f"MaxPackets={cond['MaxPackets']}, Speed={cond['Speed']}")
        layout.addWidget(self.speed_list)

        btn_add_speed = QPushButton("➕ Add Speed Condition")
        btn_edit_speed = QPushButton("✏️ Edit Selected")
        btn_remove_speed = QPushButton("🗑 Remove Selected")
        btn_add_speed.clicked.connect(self.add_speed_condition)
        btn_edit_speed.clicked.connect(self.edit_selected_speed)
        btn_remove_speed.clicked.connect(self.remove_selected_speed)
        speed_btns = QHBoxLayout()
        speed_btns.addWidget(btn_add_speed)
        speed_btns.addWidget(btn_edit_speed)
        speed_btns.addWidget(btn_remove_speed)
        layout.addLayout(speed_btns)

        # ---------- OK / Cancel ----------
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    # ================== DROP DELAY CONDITIONS ==================
    def add_drop_condition(self):
        dlg = DropConditionDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            cond = dlg.get_data()
            self.drop_list.addItem(f"Delay={cond['Delay']}s, MaxPackets={cond['MaxPackets']}")

    def edit_drop_condition(self):
        idx = self.drop_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select Condition", "Please select a condition to edit.")
            return
        text = self.drop_list.item(idx).text()
        parts = text.replace("Delay=", "").replace("s,", "").replace("MaxPackets=", "").split()
        existing = {"Delay": int(parts[0]), "MaxPackets": int(parts[-1])}
        dlg = DropConditionDialog(self, existing)
        if dlg.exec() == dlg.DialogCode.Accepted:
            cond = dlg.get_data()
            self.drop_list.item(idx).setText(f"Delay={cond['Delay']}s, MaxPackets={cond['MaxPackets']}")

    def remove_selected_drop(self):
        for item in self.drop_list.selectedItems():
            self.drop_list.takeItem(self.drop_list.row(item))

    # ================== INITIAL PLANTS ==================
    def _format_plant_entry(self, p: dict) -> str:
        """Readable single-line summary of a plant entry (only non-zero extras)."""
        # PlantType in this dialog is plain code, not RTID
        name = p.get("PlantType", "").strip()
        info = [f"W={p.get('Weight', 0)}"]
        if p.get("MinCount"): info.append(f"Min={p['MinCount']}")
        if p.get("MaxCount"): info.append(f"Max={p['MaxCount']}")
        if p.get("MinCountCooldownSeconds"): info.append(f"MinCD={p['MinCountCooldownSeconds']}s")
        if p.get("MaxCountCooldownSeconds"): info.append(f"MaxCD={p['MaxCountCooldownSeconds']}s")
        if p.get("MinWeightFactor"): info.append(f"MinWF={p['MinWeightFactor']}")
        if p.get("MaxWeightFactor"): info.append(f"MaxWF={p['MaxWeightFactor']}")
        return f"{name} ({', '.join(info)})"

    def add_plant(self):
        dlg = ConveyorPlantDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            plant = dlg.get_data()
            if plant["Weight"] > 0:
                item = QListWidgetItem(self._format_plant_entry(plant))
                item.setData(Qt.ItemDataRole.UserRole, plant)
                self.plant_list.addItem(item)

    def edit_selected_plant(self):
        idx = self.plant_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select Plant", "Please select a plant to edit.")
            return
        item = self.plant_list.item(idx)
        existing = item.data(Qt.ItemDataRole.UserRole) or {}
        dlg = ConveyorPlantDialog(self, existing)
        if dlg.exec() == dlg.DialogCode.Accepted:
            plant = dlg.get_data()
            if plant["Weight"] > 0:
                item.setText(self._format_plant_entry(plant))
                item.setData(Qt.ItemDataRole.UserRole, plant)
            else:
                # weight == 0 => remove
                self.plant_list.takeItem(idx)

    def remove_selected_plant(self):
        for item in self.plant_list.selectedItems():
            self.plant_list.takeItem(self.plant_list.row(item))

    # ================== SPEED CONDITIONS ==================
    def add_speed_condition(self):
        dlg = SpeedConditionDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            cond = dlg.get_data()
            self.speed_list.addItem(f"MaxPackets={cond['MaxPackets']}, Speed={cond['Speed']}")

    def edit_selected_speed(self):
        idx = self.speed_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select Speed", "Please select a condition to edit.")
            return
        text = self.speed_list.item(idx).text()
        parts = text.replace("MaxPackets=", "").replace("Speed=", "").split(",")
        existing = {"MaxPackets": int(parts[0]), "Speed": int(parts[1])}
        dlg = SpeedConditionDialog(self, existing)
        if dlg.exec() == dlg.DialogCode.Accepted:
            cond = dlg.get_data()
            self.speed_list.item(idx).setText(f"MaxPackets={cond['MaxPackets']}, Speed={cond['Speed']}")

    def remove_selected_speed(self):
        for item in self.speed_list.selectedItems():
            self.speed_list.takeItem(self.speed_list.row(item))

    # ================== EXPORT ==================
    def get_data(self):
        """Return final objdata for JSON export."""
        drop_conditions, plants, speeds = [], [], []

        # DropDelayConditions
        for i in range(self.drop_list.count()):
            text = self.drop_list.item(i).text()
            parts = text.replace("Delay=", "").replace("s,", "").replace("MaxPackets=", "").split()
            delay = int(parts[0])
            maxpack = int(parts[-1])
            drop_conditions.append({"Delay": delay, "MaxPackets": maxpack})

        # InitialPlantList (use stored dicts; omit zero fields)
        for i in range(self.plant_list.count()):
            item = self.plant_list.item(i)
            p = dict(item.data(Qt.ItemDataRole.UserRole) or {})
            if p.get("Weight", 0) <= 0:
                continue

            out = {"PlantType": p.get("PlantType", "").strip(), "Weight": int(p.get("Weight", 0))}
            # optional ints
            for k in ("MaxCount", "MinCount",
                      "MinCountCooldownSeconds", "MaxCountCooldownSeconds"):
                v = int(p.get(k, 0)) if p.get(k) is not None else 0
                if v > 0: out[k] = v
            # optional floats
            for k in ("MaxWeightFactor", "MinWeightFactor"):
                v = float(p.get(k, 0.0)) if p.get(k) is not None else 0.0
                if v > 0.0: out[k] = v

            plants.append(out)

        # SpeedConditions
        for i in range(self.speed_list.count()):
            text = self.speed_list.item(i).text()
            parts = text.replace("MaxPackets=", "").replace("Speed=", "").split(",")
            speeds.append({"MaxPackets": int(parts[0]), "Speed": int(parts[1])})

        return {
            "DropDelayConditions": drop_conditions,
            "InitialPlantList": plants,
            "SpeedConditions": speeds
        }


# ---------------- Sub-dialogs ----------------
class DropConditionDialog(QDialog):
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Drop Delay Condition")
        self.resize(300, 150)
        form = QFormLayout()

        self.delay = QSpinBox(); self.delay.setRange(1, 999)
        self.max_packets = QSpinBox(); self.max_packets.setRange(0, 99)

        if existing_data:
            self.delay.setValue(existing_data.get("Delay", 1))
            self.max_packets.setValue(existing_data.get("MaxPackets", 0))

        form.addRow("Delay (sec):", self.delay)
        form.addRow("Max Packets:", self.max_packets)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)
        self.setLayout(form)

    def get_data(self):
        return {"Delay": self.delay.value(), "MaxPackets": self.max_packets.value()}


class ConveyorPlantDialog(QDialog):
    """Editor for one plant entry in InitialPlantList (stores plain PlantType)."""
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Plant")
        self.resize(420, 320)
        form = QFormLayout()

        self.plant_type = PlantLineEdit()
        self.weight = QSpinBox(); self.weight.setRange(0, 1000)

        # counts
        self.max_count = QSpinBox(); self.max_count.setRange(0, 100)
        self.min_count = QSpinBox(); self.min_count.setRange(0, 100)

        # cooldowns
        self.min_count_cd = QSpinBox(); self.min_count_cd.setRange(0, 9999)
        self.max_count_cd = QSpinBox(); self.max_count_cd.setRange(0, 9999)

        # weight factors
        self.max_weight_factor = QDoubleSpinBox(); self.max_weight_factor.setRange(0, 10); self.max_weight_factor.setSingleStep(0.1)
        self.min_weight_factor = QDoubleSpinBox(); self.min_weight_factor.setRange(0, 10); self.min_weight_factor.setSingleStep(0.1)

        if existing_data:
            self.plant_type.setText(existing_data.get("PlantType", ""))
            self.weight.setValue(int(existing_data.get("Weight", 0)))
            self.max_count.setValue(int(existing_data.get("MaxCount", 0)))
            self.min_count.setValue(int(existing_data.get("MinCount", 0)))
            self.min_count_cd.setValue(int(existing_data.get("MinCountCooldownSeconds", 0)))
            self.max_count_cd.setValue(int(existing_data.get("MaxCountCooldownSeconds", 0)))
            self.max_weight_factor.setValue(float(existing_data.get("MaxWeightFactor", 0)))
            self.min_weight_factor.setValue(float(existing_data.get("MinWeightFactor", 0)))

        form.addRow("Plant Type:", self.plant_type)
        form.addRow("Weight:", self.weight)
        form.addRow("Max Count:", self.max_count)
        form.addRow("Min Count:", self.min_count)
        form.addRow("Min Count Cooldown (s):", self.min_count_cd)
        form.addRow("Max Count Cooldown (s):", self.max_count_cd)
        form.addRow("Max Weight Factor:", self.max_weight_factor)
        form.addRow("Min Weight Factor:", self.min_weight_factor)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)
        self.setLayout(form)

    def get_data(self):
        data = {
            "PlantType": self.plant_type.text().strip(),
            "Weight": self.weight.value()
        }
        # optional ints
        if self.max_count.value() > 0: data["MaxCount"] = self.max_count.value()
        if self.min_count.value() > 0: data["MinCount"] = self.min_count.value()
        if self.min_count_cd.value() > 0: data["MinCountCooldownSeconds"] = self.min_count_cd.value()
        if self.max_count_cd.value() > 0: data["MaxCountCooldownSeconds"] = self.max_count_cd.value()
        # optional floats
        if self.max_weight_factor.value() > 0: data["MaxWeightFactor"] = self.max_weight_factor.value()
        if self.min_weight_factor.value() > 0: data["MinWeightFactor"] = self.min_weight_factor.value()
        return data


class SpeedConditionDialog(QDialog):
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Speed Condition")
        self.resize(300, 150)
        form = QFormLayout()

        self.max_packets = QSpinBox(); self.max_packets.setRange(0, 99)
        self.speed = QSpinBox(); self.speed.setRange(0, 999)

        if existing_data:
            self.max_packets.setValue(existing_data.get("MaxPackets", 0))
            self.speed.setValue(existing_data.get("Speed", 0))

        form.addRow("Max Packets:", self.max_packets)
        form.addRow("Speed:", self.speed)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)
        self.setLayout(form)

    def get_data(self):
        return {"MaxPackets": self.max_packets.value(), "Speed": self.speed.value()}