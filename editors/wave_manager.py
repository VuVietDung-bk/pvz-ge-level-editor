from PyQt6.QtWidgets import *
from editors.base import ReferenceValidator, ReferenceLineEdit

class WaveManagerDialog(QDialog):
    """Dialog for editing WaveManagerProperties."""
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit WaveManagerProperties")
        self.resize(700, 500)

        data = existing_data or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # Basic numeric fields
        self.flag_wave_interval = QSpinBox(); self.flag_wave_interval.setRange(1, 100)
        self.wave_count = QSpinBox(); self.wave_count.setRange(1, 200)
        self.flag_override = QLineEdit()

        self.flag_wave_interval.setValue(data.get("FlagWaveInterval", 6))
        self.wave_count.setValue(data.get("WaveCount", 18))
        self.flag_override.setText(
            ", ".join(map(str, data.get("FlagWaveVeteranOverrideTypes", [0, 1, 1])))
        )

        form.addRow("Flag Wave Interval:", self.flag_wave_interval)
        form.addRow("Wave Count:", self.wave_count)
        form.addRow("FlagWaveVeteranOverrideTypes (comma separated):", self.flag_override)

        layout.addLayout(form)

        # Waves list
        layout.addWidget(QLabel("Waves (each wave is an array of RTIDs):"))
        self.waves_list = QListWidget()
        for wave in data.get("Waves", []):
            joined = ", ".join(wave)
            self.waves_list.addItem(joined)

        btn_add_wave = QPushButton("➕ Add Wave")
        btn_edit_wave = QPushButton("✏️ Edit Wave")
        btn_remove_wave = QPushButton("🗑 Remove Wave")

        btn_add_wave.clicked.connect(self.add_wave)
        btn_edit_wave.clicked.connect(self.edit_wave)
        btn_remove_wave.clicked.connect(self.remove_wave)

        wave_btns = QHBoxLayout()
        wave_btns.addWidget(btn_add_wave)
        wave_btns.addWidget(btn_edit_wave)
        wave_btns.addWidget(btn_remove_wave)

        layout.addWidget(self.waves_list)
        layout.addLayout(wave_btns)

        # OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # ----------------------------
    def add_wave(self):
        dlg = WaveArrayDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            arr = dlg.get_data()
            self.waves_list.addItem(", ".join(arr))

    def edit_wave(self):
        idx = self.waves_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select Wave", "Please select a wave to edit.")
            return

        current_wave = [
            t.strip() for t in self.waves_list.item(idx).text().split(",") if t.strip()
        ]
        dlg = WaveArrayDialog(self, current_wave)
        if dlg.exec() == dlg.DialogCode.Accepted:
            arr = dlg.get_data()
            self.waves_list.item(idx).setText(", ".join(arr))

    def remove_wave(self):
        for item in self.waves_list.selectedItems():
            self.waves_list.takeItem(self.waves_list.row(item))

    def get_data(self):
        """Return JSON-compatible data with reference validation."""
        waves = []
        all_refs = []
        for i in range(self.waves_list.count()):
            wave_arr = [s.strip() for s in self.waves_list.item(i).text().split(",") if s.strip()]
            waves.append(wave_arr)
            all_refs.extend(wave_arr)

        # Kiểm tra missing references
        parent = self.parent()
        object_list = getattr(self, "object_list_ref", None)
        if object_list:
            missing = ReferenceValidator.list_missing_references(all_refs, object_list)
            if missing:
                QMessageBox.critical(self, "Invalid References",
                    "The following referenced waves do not exist:\n- " + "\n- ".join(missing))
                raise Exception("Invalid references in Waves")

        overrides = []
        for val in self.flag_override.text().split(","):
            val = val.strip()
            if val.isdigit():
                overrides.append(int(val))

        return {
            "FlagWaveInterval": self.flag_wave_interval.value(),
            "WaveCount": self.wave_count.value(),
            "FlagWaveVeteranOverrideTypes": overrides,
            "Waves": waves
        }


class WaveArrayDialog(QDialog):
    """Dialog for editing one wave (list of RTIDs)."""
    def __init__(self, parent=None, existing_wave=None):
        super().__init__(parent)
        self.setWindowTitle("Edit One Wave")
        self.resize(500, 400)

        self.wave = existing_wave or []

        layout = QVBoxLayout()
        self.list = QListWidget()
        for w in self.wave:
            self.list.addItem(w)

        btn_add = QPushButton("➕ Add RTID")
        btn_remove = QPushButton("🗑 Remove Selected")
        btn_add.clicked.connect(self.add_rtid)
        btn_remove.clicked.connect(self.remove_selected)

        btns = QHBoxLayout()
        btns.addWidget(btn_add)
        btns.addWidget(btn_remove)

        layout.addWidget(self.list)
        layout.addLayout(btns)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def add_rtid(self):
        # Create temporary input with autocomplete
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel
        input_dialog = QDialog(self)
        input_dialog.setWindowTitle("Add RTID")
        input_dialog.resize(400, 100)

        layout = QVBoxLayout(input_dialog)
        ref_input = ReferenceLineEdit(
            object_list=getattr(self.parent(), "object_list_ref", []),
            allowed_classes=["SpawnZombiesJitteredWaveActionProps"]
        )
        ref_input.setPlaceholderText("Type or select alias (e.g. Wave1)")
        layout.addWidget(QLabel("Select or type a wave:"))
        layout.addWidget(ref_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(input_dialog.accept)
        buttons.rejected.connect(input_dialog.reject)

        # >>> Quan trọng: chạy dialog và lấy dữ liệu
        if input_dialog.exec() == QDialog.DialogCode.Accepted:
            text = ref_input.text().strip()
            if text:
                self.list.addItem(text)

    def remove_selected(self):
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))

    def get_data(self):
        return [self.list.item(i).text() for i in range(self.list.count())]