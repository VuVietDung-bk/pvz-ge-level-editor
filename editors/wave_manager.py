from math import ceil
from PyQt6.QtWidgets import *
from editors.base import ReferenceValidator, ReferenceLineEdit


class WaveManagerDialog(QDialog):
    """Dialog for editing WaveManagerProperties."""
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit WaveManagerProperties")
        self.resize(750, 520)

        data = existing_data or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # -------------------------------
        # Basic numeric fields
        self.flag_wave_interval = QSpinBox(); self.flag_wave_interval.setRange(1, 999)
        self.wave_count = QSpinBox(); self.wave_count.setRange(1, 999)
        self.flag_override = QLineEdit()

        self.flag_wave_interval.setValue(data.get("FlagWaveInterval", 1))
        self.wave_count.setValue(data.get("WaveCount", 1))
        self.flag_override.setText(
            ", ".join(map(str, data.get("FlagWaveVeteranOverrideTypes", [])))
        )

        form.addRow("Flag Wave Interval:", self.flag_wave_interval)
        form.addRow("Wave Count:", self.wave_count)
        form.addRow("FlagWaveVeteranOverrideTypes (comma separated):", self.flag_override)

        self.max_next_hp = QDoubleSpinBox(); self.max_next_hp.setRange(0.0, 1.0); self.max_next_hp.setSingleStep(0.05)
        self.min_next_hp = QDoubleSpinBox(); self.min_next_hp.setRange(0.0, 1.0); self.min_next_hp.setSingleStep(0.05)
        self.wave_points_inc = QSpinBox(); self.wave_points_inc.setRange(0, 99999)
        self.wave_points = QSpinBox(); self.wave_points.setRange(0, 99999)

        self.max_next_hp.setValue(data.get("MaxNextWaveHealthPercentage", 0.0))
        self.min_next_hp.setValue(data.get("MinNextWaveHealthPercentage", 0.0))
        self.wave_points_inc.setValue(data.get("WaveSpendingPointIncrement", 0))
        self.wave_points.setValue(data.get("WaveSpendingPoints", 0))

        form.addRow("Max Next Wave Health %:", self.max_next_hp)
        form.addRow("Min Next Wave Health %:", self.min_next_hp)
        form.addRow("Wave Spending Point Increment:", self.wave_points_inc)
        form.addRow("Wave Spending Points:", self.wave_points)

        layout.addLayout(form)

        # -------------------------------
        # Waves list
        layout.addWidget(QLabel("Waves (each wave is an array of RTIDs):"))

        self.waves_list = QListWidget()
        for idx, wave in enumerate(data.get("Waves", [])):
            joined = ", ".join(wave)
            self.waves_list.addItem(f"[Wave {idx+1}] {joined}")

        btn_add_wave = QPushButton("➕ Add Wave")
        btn_edit_wave = QPushButton("✏️ Edit Wave")
        btn_remove_wave = QPushButton("🗑 Remove Selected")

        btn_add_wave.clicked.connect(self.add_wave)
        btn_edit_wave.clicked.connect(self.edit_wave)
        btn_remove_wave.clicked.connect(self.remove_wave)

        wave_btns = QHBoxLayout()
        wave_btns.addWidget(btn_add_wave)
        wave_btns.addWidget(btn_edit_wave)
        wave_btns.addWidget(btn_remove_wave)

        layout.addWidget(self.waves_list)
        layout.addLayout(wave_btns)

        # -------------------------------
        # Events
        self.wave_count.valueChanged.connect(self.sync_wave_count)

        # OK / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.sync_wave_count()  # ensure list is up to date

    # =======================================================
    # --- Logic to maintain Wave Count
    # =======================================================
    def sync_wave_count(self):
        """Ensure the number of waves matches WaveCount."""
        count = self.wave_count.value()
        current = self.waves_list.count()

        # Add missing waves
        while current < count:
            self.waves_list.addItem(f"[Wave {current+1}] ")
            current += 1

        # Remove extra waves
        while current > count:
            self.waves_list.takeItem(current - 1)
            current -= 1

        # Update numbering
        for i in range(self.waves_list.count()):
            item = self.waves_list.item(i)
            text = item.text()
            # remove existing [Wave x]
            if "]" in text:
                _, rest = text.split("]", 1)
                item.setText(f"[Wave {i+1}]{rest}")
            else:
                item.setText(f"[Wave {i+1}] {text.strip()}")

    # =======================================================
    # --- Basic wave editing
    # =======================================================
    def add_wave(self):
        dlg = WaveArrayDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            arr = dlg.get_data()
            idx = self.waves_list.count() + 1
            self.waves_list.addItem(f"[Wave {idx}] {', '.join(arr)}")
            self.wave_count.setValue(idx)

    def edit_wave(self):
        idx = self.waves_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select Wave", "Please select a wave to edit.")
            return

        current_wave = self._extract_wave_items(self.waves_list.item(idx).text())
        dlg = WaveArrayDialog(self, current_wave)
        if dlg.exec() == dlg.DialogCode.Accepted:
            arr = dlg.get_data()
            self.waves_list.item(idx).setText(f"[Wave {idx+1}] {', '.join(arr)}")

    def remove_wave(self):
        idx = self.waves_list.currentRow()
        if idx >= 0:
            self.waves_list.takeItem(idx)
            self.sync_wave_count()
            self.wave_count.setValue(self.waves_list.count())

    # =======================================================
    def _extract_wave_items(self, text: str):
        """Extract RTIDs from '[Wave n] RTID(...)' lines."""
        if "]" in text:
            _, rest = text.split("]", 1)
            parts = [s.strip() for s in rest.split(",") if s.strip()]
            return parts
        return []

    # =======================================================
    def get_data(self):
        """Return JSON-compatible data with validation."""
        waves = []
        all_refs = []
        for i in range(self.waves_list.count()):
            wave_arr = self._extract_wave_items(self.waves_list.item(i).text())
            waves.append(wave_arr)
            all_refs.extend(wave_arr)

        # Reference validation
        parent = self.parent()
        object_list = getattr(self, "object_list_ref", None)
        if object_list:
            missing = ReferenceValidator.list_missing_references(all_refs, object_list)
            if missing:
                QMessageBox.critical(
                    self, "Invalid References",
                    "The following referenced waves do not exist:\n- " + "\n- ".join(missing)
                )
                raise Exception("Invalid references in Waves")

        # Parse overrides
        overrides = []
        for val in self.flag_override.text().split(","):
            val = val.strip()
            if val.isdigit():
                overrides.append(int(val))

        # Validate override length
        required = ceil(self.wave_count.value() / self.flag_wave_interval.value())
        if len(overrides) not in (0, required):
            QMessageBox.warning(
                self,
                "Invalid FlagWaveVeteranOverrideTypes",
                f"The number of override types must equal ceil(WaveCount / FlagWaveInterval).\n"
                f"Expected: {required}, got: {len(overrides)}\n\n"
                "Please correct the input before proceeding."
            )
            return None

        data = {
            "FlagWaveInterval": self.flag_wave_interval.value(),
            "WaveCount": self.wave_count.value(),
            "Waves": waves
        }
        if overrides:
            data["FlagWaveVeteranOverrideTypes"] = overrides

        # Optional values — chỉ thêm khi khác 0
        if self.max_next_hp.value() > 0:
            data["MaxNextWaveHealthPercentage"] = round(self.max_next_hp.value(), 3)
        if self.min_next_hp.value() > 0:
            data["MinNextWaveHealthPercentage"] = round(self.min_next_hp.value(), 3)
        if self.wave_points_inc.value() > 0:
            data["WaveSpendingPointIncrement"] = self.wave_points_inc.value()
        if self.wave_points.value() > 0:
            data["WaveSpendingPoints"] = self.wave_points.value()

        return data


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
        """Create temporary input with autocomplete."""
        input_dialog = QDialog(self)
        input_dialog.setWindowTitle("Add RTID")
        input_dialog.resize(400, 100)

        layout = QVBoxLayout(input_dialog)
        ref_input = ReferenceLineEdit(
            object_list=getattr(self.parent(), "object_list_ref", []),
            allowed_classes=["SpawnZombiesJitteredWaveActionProps", "ModifyConveyorWaveActionProps"]
        )
        ref_input.setPlaceholderText("Type or select alias (e.g. Wave1)")
        layout.addWidget(QLabel("Select or type a wave:"))
        layout.addWidget(ref_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(input_dialog.accept)
        buttons.rejected.connect(input_dialog.reject)

        if input_dialog.exec() == QDialog.DialogCode.Accepted:
            value = ref_input.get_rtid_value().strip()
            if value:
                self.list.addItem(value)

    def remove_selected(self):
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))

    def get_data(self):
        return [self.list.item(i).text() for i in range(self.list.count())]