from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QSpinBox, 
    QDialogButtonBox, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QCheckBox
)
from PyQt6.QtCore import Qt


class ZombiePotionModuleDialog(QDialog):
    """Dialog for editing ZombiePotionModuleProperties."""
    POTION_TYPES = {
        "Potion (Speed)": "zombiepotion_speed",
        "Potion (Toughness)": "zombiepotion_toughness",
        "Potion (Invisibility)": "zombiepotion_invisibility",
    }

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit ZombiePotionModuleProperties")
        self.resize(450, 400)

        data = existing_data or {}
        form = QFormLayout()

        # Numeric properties
        self.initial_count = QSpinBox()
        self.initial_count.setRange(0, 45)
        self.initial_count.setValue(data.get("InitialPotionCount", 0))

        self.max_count = QSpinBox()
        self.max_count.setRange(0, 45)
        self.max_count.setValue(data.get("MaxPotionCount", 0))

        # Timer fields (float)
        timer_data = data.get("PotionSpawnTimer", {"Min": 0.0, "Max": 0.0})
        self.timer_min = QDoubleSpinBox(); self.timer_min.setRange(0.0, 999.0)
        self.timer_min.setDecimals(2)
        self.timer_min.setSingleStep(0.1)
        self.timer_min.setValue(float(timer_data.get("Min", 0.0)))

        self.timer_max = QDoubleSpinBox(); self.timer_max.setRange(0.0, 999.0)
        self.timer_max.setDecimals(2)
        self.timer_max.setSingleStep(0.1)
        self.timer_max.setValue(float(timer_data.get("Max", 0.0)))

        timer_box = QHBoxLayout()
        timer_box.addWidget(QLabel("Min:")); timer_box.addWidget(self.timer_min)
        timer_box.addWidget(QLabel("Max:")); timer_box.addWidget(self.timer_max)

        # --- PotionTypes checkboxes ---
        self.potion_list = QListWidget()
        self.potion_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.potion_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        

        existing_types = data.get("PotionTypes", [])
        for name, value in self.POTION_TYPES.items():
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if value in existing_types else Qt.CheckState.Unchecked)
            self.potion_list.addItem(item)
        
        self.suppress_tip = QCheckBox("Suppress Objective Tip")
        if str(data.get("SuppressObjectiveTip", "")).lower() == "true":
            self.suppress_tip.setChecked(True)

        form.addRow("Initial Potion Count:", self.initial_count)
        form.addRow("Max Potion Count:", self.max_count)
        form.addRow("Potion Spawn Timer:", timer_box)
        form.addRow(QLabel("Potion Types:"))
        form.addRow(self.potion_list)
        form.addRow(self.suppress_tip)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    # ---------------------------------------------------
    def get_data(self):
        selected_potions = []
        for i in range(self.potion_list.count()):
            item = self.potion_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_potions.append(self.POTION_TYPES[item.text()])
        
        obj = {
            "InitialPotionCount": self.initial_count.value(),
            "MaxPotionCount": self.max_count.value(),
            "PotionSpawnTimer": {
                "Min": round(self.timer_min.value(), 2),
                "Max": round(self.timer_max.value(), 2)
            },
            "PotionTypes": selected_potions
        }

        if self.suppress_tip.isChecked():
            obj["SuppressObjectiveTip"] = True

        return obj