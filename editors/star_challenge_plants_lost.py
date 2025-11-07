from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox,
    QDialogButtonBox
)


class StarChallengePlantsLostDialog(QDialog):
    """Dialog for editing StarChallengePlantsLostProps."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit StarChallengePlantsLostProps")
        self.resize(350, 180)

        data = existing_data or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # --- Field: MaximumPlantsLost ---
        self.max_lost = QSpinBox()
        self.max_lost.setRange(0, 999)
        self.max_lost.setValue(data.get("MaximumPlantsLost", 0))
        form.addRow("Maximum Plants Lost:", self.max_lost)

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
            "MaximumPlantsLost": self.max_lost.value()
        }