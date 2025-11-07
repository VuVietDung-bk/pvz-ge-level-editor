from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QLabel,
    QDialogButtonBox, QHBoxLayout
)


class PiratePlankDialog(QDialog):
    """Dialog for editing PiratePlankProperties."""
    ROWS = 5  # 0–4

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit PiratePlankProperties")
        self.resize(400, 250)

        data = existing_data or {}
        plank_rows = set(data.get("PlankRows", []))

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select the rows (0–4) where Pirate Planks appear:"))

        self.row_boxes = []
        box_layout = QHBoxLayout()
        for i in range(self.ROWS):
            cb = QCheckBox(f"Row {i}")
            cb.setChecked(i in plank_rows)
            self.row_boxes.append(cb)
            box_layout.addWidget(cb)

        layout.addLayout(box_layout)

        # OK / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        """Return selected rows in JSON-ready format."""
        selected = [i for i, cb in enumerate(self.row_boxes) if cb.isChecked()]
        return {"PlankRows": selected}