from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QSpinBox, QDialogButtonBox
)


class StarChallengeSunUsedPropsDialog(QDialog):
    """Dialog for editing StarChallengeSunUsedProps."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit StarChallengeSunUsedProps")
        self.resize(300, 150)

        data = existing_data or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # MaximumSun
        self.max_sun = QSpinBox()
        self.max_sun.setRange(0, 99999)
        self.max_sun.setValue(data.get("MaximumSun", 0))

        form.addRow("Maximum Sun:", self.max_sun)
        layout.addLayout(form)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    # --------------------------
    def get_data(self):
        """Return JSON objdata."""
        return {
            "MaximumSun": self.max_sun.value()
        }