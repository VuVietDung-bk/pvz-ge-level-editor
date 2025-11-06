from PyQt6.QtWidgets import *
from editors.base import ReferenceLineEdit, ReferenceValidator, ObjectEditorFactory

class WaveManagerModuleDialog(QDialog):
    """Dialog for editing WaveManagerModuleProperties."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit WaveManagerModuleProperties")
        self.resize(700, 500)

        self.existing_data = existing_data or {}

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # WaveManagerProps reference
        from PyQt6.QtWidgets import QLineEdit
        self.wave_manager_ref = ReferenceLineEdit(
            object_list=getattr(parent, "object_list_ref", []),
            allowed_classes=["WaveManagerProperties"]
        )
        self.wave_manager_ref.setText(self.existing_data.get("WaveManagerProps", "RTID(WaveManagerProps@CurrentLevel)"))
        form_layout.addRow("WaveManagerProps Reference:", self.wave_manager_ref)

        # DynamicZombies list
        self.zombie_set_list = QListWidget()
        for i, dz in enumerate(self.existing_data.get("DynamicZombies", [])):
            self.zombie_set_list.addItem(f"DynamicZombie[{i}] - {len(dz.get('ZombiePool', []))} zombies")

        btn_add_set = QPushButton("➕ Edit Dynamic Zombies (7 Sets)")
        btn_add_set.clicked.connect(self.open_dynamic_sets)

        layout.addLayout(form_layout)
        layout.addWidget(btn_add_set)
        layout.addWidget(QLabel("Dynamic Zombies:"))
        layout.addWidget(self.zombie_set_list)

        # OK / Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        # Ensure default 7 sets
        if not self.existing_data.get("DynamicZombies"):
            self.dynamic_sets = [self._default_dynamic_zombie() for _ in range(7)]
        else:
            self.dynamic_sets = self.existing_data["DynamicZombies"]

    def _default_dynamic_zombie(self):
        return {
            "PointIncrementPerWave": 0,
            "StartingPoints": 0,
            "StartingWave": 0,
            "ZombiePool": []
        }

    def open_dynamic_sets(self):
        """Open an editor dialog to configure the 7 DynamicZombie entries."""
        dlg = DynamicZombiesDialog(self, self.dynamic_sets)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.dynamic_sets = dlg.get_data()
            self.zombie_set_list.clear()
            for i, dz in enumerate(self.dynamic_sets):
                self.zombie_set_list.addItem(f"DynamicZombie[{i}] - {len(dz.get('ZombiePool', []))} zombies")

    def get_data(self):
        ref = self.wave_manager_ref.get_rtid_value()
        object_list = getattr(self, "object_list_ref", [])

        if not ReferenceValidator.is_reference_valid(ref, object_list):
            QMessageBox.critical(self, "Invalid Reference",
                f"The reference '{ref}' does not match any existing object alias.\n\n"
                "Please ensure the referenced object exists in Added Objects.")
            raise Exception("Invalid reference")

        return {
            "DynamicZombies": self.dynamic_sets,
            "WaveManagerProps": ref
        }

    
class DynamicZombiesDialog(QDialog):
    """Dialog to edit all 7 DynamicZombie sets."""
    def __init__(self, parent=None, existing_sets=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Dynamic Zombies")
        self.resize(600, 400)

        self.sets = existing_sets or []

        layout = QVBoxLayout()
        self.list = QListWidget()
        for i, dz in enumerate(self.sets):
            self.list.addItem(f"Set {i+1} - {len(dz.get('ZombiePool', []))} zombies")

        btn_edit = QPushButton("✏️ Edit Selected Set")
        btn_edit.clicked.connect(self.edit_set)

        layout.addWidget(self.list)
        layout.addWidget(btn_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def edit_set(self):
        sel = self.list.currentRow()
        if sel < 0:
            QMessageBox.warning(self, "Select a Set", "Please select a DynamicZombie set to edit.")
            return

        dz = self.sets[sel]
        dlg = OneDynamicZombieDialog(self, dz)
        if dlg.exec() == dlg.DialogCode.Accepted:
            self.sets[sel] = dlg.get_data()
            self.list.item(sel).setText(f"Set {sel+1} - {len(dz.get('ZombiePool', []))} zombies")

    def get_data(self):
        return self.sets

class OneDynamicZombieDialog(QDialog):
    """Dialog to edit a single DynamicZombie entry."""
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit DynamicZombie")
        self.resize(400, 300)

        data = existing_data or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        self.point_inc = QSpinBox(); self.point_inc.setRange(0, 9999)
        self.start_points = QSpinBox(); self.start_points.setRange(0, 9999)
        self.start_wave = QSpinBox(); self.start_wave.setRange(0, 50)

        self.point_inc.setValue(data.get("PointIncrementPerWave", 0))
        self.start_points.setValue(data.get("StartingPoints", 0))
        self.start_wave.setValue(data.get("StartingWave", 0))

        form.addRow("Point Increment / Wave:", self.point_inc)
        form.addRow("Starting Points:", self.start_points)
        form.addRow("Starting Wave:", self.start_wave)

        self.zombie_list = QListWidget()
        for z in data.get("ZombiePool", []):
            self.zombie_list.addItem(z)

        btn_add_z = QPushButton("➕ Add Zombie")
        btn_add_z.clicked.connect(self.add_zombie)
        btn_del_z = QPushButton("🗑 Remove Selected")
        btn_del_z.clicked.connect(self.remove_zombie)

        z_btns = QHBoxLayout()
        z_btns.addWidget(btn_add_z)
        z_btns.addWidget(btn_del_z)

        layout.addLayout(form)
        layout.addWidget(QLabel("Zombie Pool:"))
        layout.addWidget(self.zombie_list)
        layout.addLayout(z_btns)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def add_zombie(self):
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Add Zombie", "Enter ZombieType (e.g., tutorial_armor1):")
        if ok and text.strip():
            self.zombie_list.addItem(f"RTID({text.strip()}@ZombieTypes)")

    def remove_zombie(self):
        for item in self.zombie_list.selectedItems():
            self.zombie_list.takeItem(self.zombie_list.row(item))

    def get_data(self):
        zombies = [self.zombie_list.item(i).text() for i in range(self.zombie_list.count())]
        return {
            "PointIncrementPerWave": self.point_inc.value(),
            "StartingPoints": self.start_points.value(),
            "StartingWave": self.start_wave.value(),
            "ZombiePool": zombies
        }
