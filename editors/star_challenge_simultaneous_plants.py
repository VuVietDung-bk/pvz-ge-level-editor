from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox,
    QDialogButtonBox
)


class StarChallengeSimultaneousPlantsDialog(QDialog):
    """Dialog for editing StarChallengeSimultaneousPlantsProps."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit StarChallengeSimultaneousPlantsProps")
        self.resize(350, 180)

        data = existing_data or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # --- Field: MaximumPlants ---
        self.max_plants = QSpinBox()
        self.max_plants.setRange(1, 999)
        self.max_plants.setValue(data.get("MaximumPlants", 1))
        form.addRow("Maximum Simultaneous Plants:", self.max_plants)

        layout.addLayout(form)

        # --- OK / Cancel ---
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        """Return structured objdata for JSON export."""
        return {
            "MaximumPlants": self.max_plants.value()
        }