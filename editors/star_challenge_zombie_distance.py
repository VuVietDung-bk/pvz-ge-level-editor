from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox,
    QDialogButtonBox
)


class StarChallengeZombieDistanceDialog(QDialog):
    """Dialog for editing StarChallengeZombieDistanceProps."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit StarChallengeZombieDistanceProps")
        self.resize(350, 180)

        data = existing_data or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # --- Field: TargetDistance ---
        self.target_distance = QDoubleSpinBox()
        self.target_distance.setRange(0.1, 99.0)
        self.target_distance.setDecimals(2)
        self.target_distance.setSingleStep(0.1)
        self.target_distance.setValue(float(data.get("TargetDistance", 0.1)))

        form.addRow("Target Distance:", self.target_distance)
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
            "TargetDistance": round(self.target_distance.value(), 2)
        }