from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox,
    QDialogButtonBox
)


class StarChallengeSunProducedDialog(QDialog):
    """Dialog for editing StarChallengeSunProducedProps."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit StarChallengeSunProducedProps")
        self.resize(350, 180)

        data = existing_data or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # --- Field: TargetSun ---
        self.target_sun = QSpinBox()
        self.target_sun.setRange(0, 1000000000000)
        self.target_sun.setValue(data.get("TargetSun", 0))
        form.addRow("Target Sun:", self.target_sun)

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
            "TargetSun": self.target_sun.value()
        }