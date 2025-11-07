from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QSpinBox, QDialogButtonBox
)

class LastStandMinigameDialog(QDialog):
    """Dialog for editing LastStandMinigameProperties."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit LastStandMinigameProperties")
        self.resize(350, 180)

        data = existing_data or {}
        form = QFormLayout()

        # StartingPlantfood (default = 2)
        self.starting_plantfood = QSpinBox()
        self.starting_plantfood.setRange(0, 10)
        self.starting_plantfood.setValue(data.get("StartingPlantfood", 2))
        form.addRow("Starting Plantfood:", self.starting_plantfood)

        # StartingSun (default = 2000, step = 25)
        self.starting_sun = QSpinBox()
        self.starting_sun.setRange(0, 9999)
        self.starting_sun.setSingleStep(25)  # step size of 25
        self.starting_sun.setValue(data.get("StartingSun", 2000))
        form.addRow("Starting Sun:", self.starting_sun)

        # OK / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)

        self.setLayout(form)

    def get_data(self):
        """Return structured objdata for JSON export."""
        return {
            "StartingPlantfood": self.starting_plantfood.value(),
            "StartingSun": self.starting_sun.value()
        }