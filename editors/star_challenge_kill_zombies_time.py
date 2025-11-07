from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox,
    QDialogButtonBox, QCheckBox
)


class StarChallengeKillZombiesInTimeDialog(QDialog):
    """Dialog for editing StarChallengeKillZombiesInTimeProps."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit StarChallengeKillZombiesInTimeProps")
        self.resize(400, 220)

        data = existing_data or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # --- Numeric fields ---
        self.time_limit = QSpinBox()
        self.time_limit.setRange(1, 9999)
        self.time_limit.setValue(data.get("Time", 1))

        self.zombies_to_kill = QSpinBox()
        self.zombies_to_kill.setRange(1, 9999)
        self.zombies_to_kill.setValue(data.get("ZombiesToKill", 1))

        form.addRow("Time Limit:", self.time_limit)
        form.addRow("Zombies To Kill:", self.zombies_to_kill)

        layout.addLayout(form)

        # --- OK / Cancel ---
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        """Return structured objdata for JSON export."""
        obj = {
            "Time": self.time_limit.value(),
            "ZombiesToKill": self.zombies_to_kill.value()
        }
        return obj