from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox, QListWidget, 
    QPushButton, QDialogButtonBox, QHBoxLayout, QLabel, QCheckBox, 
    QComboBox, QMessageBox
)
from editors.base import PlantLineEdit


class SeedBankPropertiesDialog(QDialog):
    """Dialog for editing SeedBankProperties."""
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit SeedBankProperties")
        self.resize(600, 500)

        data = existing_data or {}
        layout = QVBoxLayout()
        form = QFormLayout()

        # --------------------------
        # ExcludeListSunProducers
        self.exclude_sun_producers = QCheckBox("Exclude Sun Producers")
        if str(data.get("ExcludeListSunProducers", "")).lower() == "true":
            self.exclude_sun_producers.setChecked(True)

        # --------------------------
        # Selection Method
        self.selection_method = QComboBox()
        self.selection_method.addItems(["chooser", "preset"])
        if data.get("SelectionMethod") in ["chooser", "preset"]:
            self.selection_method.setCurrentText(data["SelectionMethod"])

        # --------------------------
        # OverrideSeedSlotsCount
        self.override_slots = QSpinBox()
        self.override_slots.setRange(0, 8)  # cho phép 0 là giá trị mặc định
        self.override_slots.setValue(data.get("OverrideSeedSlotsCount", 0))

        # --------------------------
        # SuppressObjectiveTip
        self.suppress_tip = QCheckBox("Suppress Objective Tip")
        if str(data.get("SuppressObjectiveTip", "")).lower() == "true":
            self.suppress_tip.setChecked(True)

        # --------------------------
        # Plant Lists
        self.preset_list = EditablePlantList("Preset Plant List", data.get("PresetPlantList", []))
        self.exclude_list = EditablePlantList("Plant Exclude List", data.get("PlantExcludeList", []))
        self.include_list = EditablePlantList("Plant Include List", data.get("PlantIncludeList", []))

        # --------------------------
        form.addRow(self.exclude_sun_producers)
        form.addRow("Selection Method:", self.selection_method)
        form.addRow("Override Seed Slots Count:", self.override_slots)
        form.addRow(self.suppress_tip)

        layout.addLayout(form)
        layout.addWidget(self.preset_list)
        layout.addWidget(self.exclude_list)
        layout.addWidget(self.include_list)

        # --------------------------
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    # ============================================================
    def get_data(self):
        """Return objdata for SeedBankProperties."""
        obj = {}

        if self.exclude_sun_producers.isChecked():
            obj["ExcludeListSunProducers"] = "true"

        preset_plants = self.preset_list.get_values()
        exclude_plants = self.exclude_list.get_values()
        include_plants = self.include_list.get_values()

        if preset_plants:
            obj["PresetPlantList"] = preset_plants
        if exclude_plants:
            obj["PlantExcludeList"] = exclude_plants
        if include_plants:
            obj["PlantIncludeList"] = include_plants

        if self.selection_method.currentText():
            obj["SelectionMethod"] = self.selection_method.currentText()

        if self.suppress_tip.isChecked():
            obj["SuppressObjectiveTip"] = True

        if self.override_slots.value() > 0:
            obj["OverrideSeedSlotsCount"] = self.override_slots.value()

        return obj


# ============================================================
# Helper widget: Plant list with add/remove/autocomplete
# ============================================================
class EditablePlantList(QDialog):
    """Widget for editing a list of plants with autocomplete."""
    def __init__(self, title, values=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.values = values or []

        self.layout = QVBoxLayout()
        self.label = QLabel(title)
        self.list_widget = QListWidget()
        for v in self.values:
            self.list_widget.addItem(v)

        # Buttons
        btn_add = QPushButton("➕ Add")
        btn_add.clicked.connect(self.add_item)
        btn_remove = QPushButton("🗑 Remove Selected")
        btn_remove.clicked.connect(self.remove_selected)
        btns = QHBoxLayout()
        btns.addWidget(btn_add)
        btns.addWidget(btn_remove)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.list_widget)
        self.layout.addLayout(btns)
        self.setLayout(self.layout)

    # -----------------------------
    def add_item(self):
        dlg = PlantInputDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            val = dlg.get_value()
            if not val:
                QMessageBox.warning(self, "Empty", "Plant name cannot be empty.")
                return
            self.list_widget.addItem(val)

    def remove_selected(self):
        for i in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(i))

    def get_values(self):
        values = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        return values


class PlantInputDialog(QDialog):
    """Dialog for adding a single plant with autocomplete."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Plant")
        self.resize(300, 150)
        layout = QVBoxLayout()
        self.plant_input = PlantLineEdit()
        layout.addWidget(QLabel("Plant Type ID:"))
        layout.addWidget(self.plant_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_value(self):
        return self.plant_input.text().strip()