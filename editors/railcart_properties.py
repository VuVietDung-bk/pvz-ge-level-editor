from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QHBoxLayout, QDialogButtonBox, QFormLayout, QSpinBox, QComboBox
)

class RailcartPropertiesDialog(QDialog):
    """Dialog for editing RailcartProperties."""

    railcart_TYPES = [
        "railcart_cowboy", "railcart_tutorial", "railcart_egypt", "railcart_pirate", "railcart_cowboy", "railcart_kongfu",
        "railcart_future", "railcart_dark", "railcart_sky"
    ]

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit RailcartProperties")
        self.resize(600, 550)

        data = existing_data or {}

        layout = QVBoxLayout()

        # ========== RailcartType ==========
        layout.addWidget(QLabel("Railcart Type:"))
        self.combo_type = QComboBox()
        self.combo_type.addItems(self.railcart_TYPES)
        if data.get("RailcartType") in self.railcart_TYPES:
            self.combo_type.setCurrentText(data["RailcartType"])
        layout.addWidget(self.combo_type)

        # ========== Railcarts (list) ==========
        layout.addWidget(QLabel("Railcarts:"))
        self.list_railcarts = QListWidget()
        for rc in data.get("Railcarts", []):
            self.list_railcarts.addItem(f"Col {rc['Column']}, Row {rc['Row']}")
        layout.addWidget(self.list_railcarts)

        btn_add_rc = QPushButton("➕ Add Railcart")
        btn_edit_rc = QPushButton("✏️ Edit Selected")
        btn_rm_rc = QPushButton("🗑 Remove Selected")
        btn_add_rc.clicked.connect(self.add_railcart)
        btn_edit_rc.clicked.connect(self.edit_railcart)
        btn_rm_rc.clicked.connect(self.remove_railcart)

        rc_btns = QHBoxLayout()
        rc_btns.addWidget(btn_add_rc)
        rc_btns.addWidget(btn_edit_rc)
        rc_btns.addWidget(btn_rm_rc)
        layout.addLayout(rc_btns)

        # ========== Rails (list) ==========
        layout.addWidget(QLabel("Rails:"))
        self.list_rails = QListWidget()
        for r in data.get("Rails", []):
            self.list_rails.addItem(
                f"Column {r['Column']}: RowStart {r['RowStart']} → RowEnd {r['RowEnd']}"
            )
        layout.addWidget(self.list_rails)

        btn_add_r = QPushButton("➕ Add Rail")
        btn_edit_r = QPushButton("✏️ Edit Selected")
        btn_rm_r = QPushButton("🗑 Remove Selected")
        btn_add_r.clicked.connect(self.add_rail)
        btn_edit_r.clicked.connect(self.edit_rail)
        btn_rm_r.clicked.connect(self.remove_rail)

        r_btns = QHBoxLayout()
        r_btns.addWidget(btn_add_r)
        r_btns.addWidget(btn_edit_r)
        r_btns.addWidget(btn_rm_r)
        layout.addLayout(r_btns)

        # OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # ----------------------------------------------------------
    # Railcart (Column / Row)
    # ----------------------------------------------------------
    def add_railcart(self):
        dlg = RailcartEntryDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            d = dlg.get_data()
            self.list_railcarts.addItem(f"Col {d['Column']}, Row {d['Row']}")

    def edit_railcart(self):
        i = self.list_railcarts.currentRow()
        if i < 0:
            return
        text = self.list_railcarts.item(i).text()
        col = int(text.split("Col ")[1].split(",")[0])
        row = int(text.split("Row ")[1])
        dlg = RailcartEntryDialog(self, {"Column": col, "Row": row})
        if dlg.exec() == dlg.DialogCode.Accepted:
            d = dlg.get_data()
            self.list_railcarts.item(i).setText(f"Col {d['Column']}, Row {d['Row']}")

    def remove_railcart(self):
        for it in self.list_railcarts.selectedItems():
            self.list_railcarts.takeItem(self.list_railcarts.row(it))

    # ----------------------------------------------------------
    # Rails (Column / RowStart / RowEnd)
    # ----------------------------------------------------------
    def add_rail(self):
        dlg = RailEntryDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            d = dlg.get_data()
            self.list_rails.addItem(
                f"Column {d['Column']}: RowStart {d['RowStart']} → RowEnd {d['RowEnd']}"
            )

    def edit_rail(self):
        i = self.list_rails.currentRow()
        if i < 0:
            return
        text = self.list_rails.item(i).text()
        col = int(text.split("Column ")[1].split(":")[0])
        rest = text.split(":")[1].strip()
        row_start = int(rest.split("RowStart ")[1].split("→")[0])
        row_end = int(rest.split("RowEnd")[1].strip())

        dlg = RailEntryDialog(self, {
            "Column": col,
            "RowStart": row_start,
            "RowEnd": row_end
        })
        if dlg.exec() == dlg.DialogCode.Accepted:
            d = dlg.get_data()
            self.list_rails.item(i).setText(
                f"Column {d['Column']}: RowStart {d['RowStart']} → RowEnd {d['RowEnd']}"
            )

    def remove_rail(self):
        for it in self.list_rails.selectedItems():
            self.list_rails.takeItem(self.list_rails.row(it))

    # ----------------------------------------------------------
    def get_data(self):
        # Railcarts
        railcarts = []
        for i in range(self.list_railcarts.count()):
            text = self.list_railcarts.item(i).text()
            col = int(text.split("Col ")[1].split(",")[0])
            row = int(text.split("Row ")[1])
            railcarts.append({"Column": col, "Row": row})

        # Rails
        rails = []
        for i in range(self.list_rails.count()):
            text = self.list_rails.item(i).text()
            col = int(text.split("Column ")[1].split(":")[0])
            rest = text.split(":")[1].strip()
            row_start = int(rest.split("RowStart ")[1].split("→")[0])
            row_end = int(rest.split("RowEnd")[1].strip())
            rails.append({
                "Column": col,
                "RowStart": row_start,
                "RowEnd": row_end
            })

        return {
            "RailcartType": self.combo_type.currentText(),
            "Railcarts": railcarts,
            "Rails": rails
        }


# ===================================================================
# Entry dialogs
# ===================================================================

class RailcartEntryDialog(QDialog):
    """Add / edit railcart position (column / row)."""

    def __init__(self, parent=None, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Railcart Position")

        form = QFormLayout()

        self.col = QSpinBox()
        self.col.setRange(0, 8)
        self.row = QSpinBox()
        self.row.setRange(0, 4)

        if existing:
            self.col.setValue(existing.get("Column", 0))
            self.row.setValue(existing.get("Row", 0))

        form.addRow("Column:", self.col)
        form.addRow("Row:", self.row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)

        self.setLayout(form)

    def get_data(self):
        return {
            "Column": self.col.value(),
            "Row": self.row.value()
        }


class RailEntryDialog(QDialog):
    """Add / edit rail segment (column, rowstart → rowend)."""

    def __init__(self, parent=None, existing=None):
        super().__init__(parent)
        self.setWindowTitle("Rail Segment")

        form = QFormLayout()

        self.col = QSpinBox()
        self.col.setRange(0, 8)
        self.row_start = QSpinBox()
        self.row_start.setRange(0, 4)
        self.row_end = QSpinBox()
        self.row_end.setRange(0, 4)

        if existing:
            self.col.setValue(existing.get("Column", 0))
            self.row_start.setValue(existing.get("RowStart", 0))
            self.row_end.setValue(existing.get("RowEnd", 0))

        form.addRow("Column:", self.col)
        form.addRow("RowStart:", self.row_start)
        form.addRow("RowEnd:", self.row_end)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)

        self.setLayout(form)

    def get_data(self):
        return {
            "Column": self.col.value(),
            "RowStart": self.row_start.value(),
            "RowEnd": self.row_end.value()
        }