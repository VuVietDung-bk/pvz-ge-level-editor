from PyQt6.QtWidgets import *
from editors.base import PlantLineEdit

class ProtectThePlantDialog(QDialog):
    """Dialog for editing ProtectThePlantChallengeProperties."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit ProtectThePlantChallengeProperties")
        self.resize(500, 400)

        self.existing_data = existing_data or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # MustProtectCount
        self.must_count = QSpinBox()
        self.must_count.setRange(0, 999)
        self.must_count.setValue(self.existing_data.get("MustProtectCount", 0))

        # Plant list
        self.plants_list = QListWidget()
        for p in self.existing_data.get("Plants", []):
            self.plants_list.addItem(
                f"({p['GridX']}, {p['GridY']}) - {p['PlantType']}"
            )

        # Buttons
        btn_add_plant = QPushButton("➕ Add Plant")
        btn_add_plant.clicked.connect(self.add_plant_popup)

        btn_edit_plant = QPushButton("✏ Edit Selected")
        btn_edit_plant.clicked.connect(self.edit_selected_plant)

        btn_remove_plant = QPushButton("🗑 Remove Selected")
        btn_remove_plant.clicked.connect(self.remove_selected_plant)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(btn_add_plant)
        btn_layout.addWidget(btn_edit_plant)
        btn_layout.addWidget(btn_remove_plant)

        form.addRow("Must Protect Count:", self.must_count)
        layout.addLayout(form)
        layout.addLayout(btn_layout)
        layout.addWidget(QLabel("Plants:"))
        layout.addWidget(self.plants_list)

        # OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # -----------------------------
    def add_plant_popup(self):
        """Popup for adding one plant."""
        dlg = PlantEditorDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            plant = dlg.get_data()
            self.plants_list.addItem(f"({plant['GridX']}, {plant['GridY']}) - {plant['PlantType']}")
            self.must_count.setValue(self.plants_list.count())

    def edit_selected_plant(self):
        """Edit selected endangered plant entry."""
        selected_items = self.plants_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Edit Plant", "Please select a plant to edit.")
            return

        item = selected_items[0]
        text = item.text()
        coords, plant_type = text.split(" - ")
        gridx, gridy = coords.strip("()").split(", ")
        plant_type_clean = plant_type.replace("RTID(", "").replace("@PlantTypes)", "")

        dlg = PlantEditorDialog(self)
        dlg.gridx.setValue(int(gridx))
        dlg.gridy.setValue(int(gridy))
        dlg.plant_type.setText(plant_type_clean)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_plant = dlg.get_data()
            item.setText(f"({new_plant['GridX']}, {new_plant['GridY']}) - {new_plant['PlantType']}")
            self.must_count.setValue(self.plants_list.count())

    def remove_selected_plant(self):
        """Remove selected plant(s) from list."""
        for item in self.plants_list.selectedItems():
            self.plants_list.takeItem(self.plants_list.row(item))
        self.must_count.setValue(self.plants_list.count())

    def get_data(self):
        """Return final objdata dict."""
        plants = []
        for i in range(self.plants_list.count()):
            text = self.plants_list.item(i).text()
            coords, plant_type = text.split(" - ")
            gridx, gridy = coords.strip("()").split(", ")
            plants.append({
                "GridX": int(gridx),
                "GridY": int(gridy),
                "PlantType": plant_type
            })

        return {
            "MustProtectCount": self.must_count.value(),
            "Plants": plants
        }


class PlantEditorDialog(QDialog):
    """Sub-dialog to add or edit one plant entry."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plant Editor")
        layout = QFormLayout(self)

        self.gridx = QSpinBox()
        self.gridx.setRange(0, 8)

        self.gridy = QSpinBox()
        self.gridy.setRange(0, 5)

        self.plant_type = PlantLineEdit()
        self.plant_type.setPlaceholderText("Enter plant alias (e.g. cabbagepult)")

        layout.addRow("GridX:", self.gridx)
        layout.addRow("GridY:", self.gridy)
        layout.addRow("PlantType:", self.plant_type)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        return {
            "GridX": self.gridx.value(),
            "GridY": self.gridy.value(),
            "PlantType": f"RTID({self.plant_type.text().strip()}@PlantTypes)"
        }