from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QListWidget,
    QPushButton, QDialogButtonBox, QHBoxLayout, QLabel,
    QMessageBox
)
from editors.base import ReferenceLineEdit, ReferenceValidator


class StarChallengeModuleDialog(QDialog):
    """Dialog for editing StarChallengeModuleProperties."""

    ALLOWED_CLASSES = [
        "MoldColonyChallengeProps",
        "ZombiePotionModuleProperties",
        "ProtectThePlantChallengeProperties",
        "StarChallengeBeatTheLevelProps",
        "StarChallengeKillZombiesInTimeProps",
        "StarChallengePlantsLostProps",
        "StarChallengeSimultaneousPlantsProps",
        "StarChallengeSunProducedProps",
        "StarChallengeZombieDistanceProps",
        "StarChallengeSunUsedProps"
    ]

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit StarChallengeModuleProperties")
        self.resize(700, 500)

        data = existing_data or {}

        layout = QVBoxLayout()
        form = QFormLayout()

        # --- Challenges list ---
        self.challenges_list = QListWidget()
        for group in data.get("Challenges", []):
            joined = ", ".join(group)
            self.challenges_list.addItem(joined)

        btn_add = QPushButton("➕ Add Challenge Group")
        btn_edit = QPushButton("✏️ Edit Selected Group")
        btn_remove = QPushButton("🗑 Remove Selected")

        btn_add.clicked.connect(self.add_group)
        btn_edit.clicked.connect(self.edit_group)
        btn_remove.clicked.connect(self.remove_group)

        btns = QHBoxLayout()
        btns.addWidget(btn_add)
        btns.addWidget(btn_edit)
        btns.addWidget(btn_remove)

        layout.addWidget(QLabel("Challenge Groups (each group = array of RTIDs):"))
        layout.addWidget(self.challenges_list)
        layout.addLayout(btns)

        # --- Boolean toggle ---
        from PyQt6.QtWidgets import QCheckBox
        self.always_available = QCheckBox("Challenges Always Available")
        if str(data.get("ChallengesAlwaysAvailable", "")).lower() == "true":
            self.always_available.setChecked(True)
        layout.addWidget(self.always_available)

        # --- OK / Cancel ---
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.object_list_ref = getattr(parent, "objects", [])

    # =========================================================
    def add_group(self):
        dlg = ChallengeGroupDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            arr = dlg.get_data()
            self.challenges_list.addItem(", ".join(arr))

    def edit_group(self):
        idx = self.challenges_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select Group", "Please select a group to edit.")
            return

        current = [s.strip() for s in self.challenges_list.item(idx).text().split(",") if s.strip()]
        dlg = ChallengeGroupDialog(self, current)
        if dlg.exec() == dlg.DialogCode.Accepted:
            arr = dlg.get_data()
            self.challenges_list.item(idx).setText(", ".join(arr))

    def remove_group(self):
        for item in self.challenges_list.selectedItems():
            self.challenges_list.takeItem(self.challenges_list.row(item))

    # =========================================================
    def get_data(self):
        """Return JSON-ready object data."""
        challenges = []
        all_refs = []
        for i in range(self.challenges_list.count()):
            arr = [s.strip() for s in self.challenges_list.item(i).text().split(",") if s.strip()]
            challenges.append(arr)
            all_refs.extend(arr)

        # Validate references
        if self.object_list_ref:
            missing = ReferenceValidator.list_missing_references(all_refs, self.object_list_ref)
            if missing:
                QMessageBox.critical(
                    self, "Invalid References",
                    "The following referenced challenges do not exist:\n- " + "\n- ".join(missing)
                )
                raise Exception("Invalid challenge references")

        obj = {
            "Challenges": challenges
        }
        if self.always_available.isChecked():
            obj["ChallengesAlwaysAvailable"] = True

        return obj


class ChallengeGroupDialog(QDialog):
    """Dialog to edit a single Challenge Group (array of RTIDs)."""

    def __init__(self, parent=None, existing_group=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Challenge Group")
        self.resize(500, 400)
        self.group = existing_group or []

        layout = QVBoxLayout()
        self.list = QListWidget()
        for ch in self.group:
            self.list.addItem(ch)

        btn_add = QPushButton("➕ Add Challenge")
        btn_remove = QPushButton("🗑 Remove Selected")
        btn_add.clicked.connect(self.add_challenge)
        btn_remove.clicked.connect(self.remove_selected)

        btns = QHBoxLayout()
        btns.addWidget(btn_add)
        btns.addWidget(btn_remove)

        layout.addWidget(QLabel("Challenges in this group:"))
        layout.addWidget(self.list)
        layout.addLayout(btns)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def add_challenge(self):
        """Add RTID reference with autocomplete."""
        input_dialog = QDialog(self)
        input_dialog.setWindowTitle("Add Challenge Reference")
        input_dialog.resize(400, 120)

        layout = QVBoxLayout(input_dialog)
        ref_input = ReferenceLineEdit(
            object_list=getattr(self.parent(), "object_list_ref", []),
            allowed_classes=self.parent().ALLOWED_CLASSES
        )
        ref_input.setPlaceholderText("Type or select alias (e.g. BeatTheLevel)")
        layout.addWidget(QLabel("Select or type a challenge alias:"))
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