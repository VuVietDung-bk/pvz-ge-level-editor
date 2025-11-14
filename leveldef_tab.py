from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QLabel, QListWidget, QListWidgetItem,
    QCheckBox, QScrollArea, QWidget as QW, QGridLayout
)
from PyQt6.QtCore import Qt
from data_loader import GameData
import re

class LevelDefinitionTab(QWidget):
    """Tab for customizing the LevelDefinition core object."""
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        form = QFormLayout()

        # Editable fields
        self.description = QLineEdit("Description")
        self.level_number = QLineEdit("1")
        self.name = QLineEdit("Unnamed Level")
        self.written_by = QLineEdit("unnamed")
        self.starting_sun = QLineEdit("50")

        # Fixed internal fields (not user editable)
        self.loot = "RTID(DefaultLoot@LevelModules)"
        self.normal_table = "egypt_normal_01"
        self.shiny_table = "egypt_shiny_01"

        # MusicType selection
        self.music_type = QComboBox()
        self.music_type.addItem("None")
        self.music_type.addItems(GameData.get_flat_list("Music Types"))

        # Stage module selection
        self.stage_module = QComboBox()
        self.stage_module.addItems(GameData.get_flat_list("Stages"))

        # Mower module selection
        self.mower_module = QComboBox()
        self.mower_module.addItem("None")
        self.mower_module.addItems(GameData.get_flat_list("Lawn Mowers"))

        # -------- Modules selection (3 columns, show plain names) --------
        self.modules_area = QScrollArea()
        self.modules_area.setWidgetResizable(True)
        self.modules_host = QW()
        self.modules_grid = QGridLayout(self.modules_host)
        self.modules_grid.setContentsMargins(0, 0, 0, 0)
        self.modules_grid.setHorizontalSpacing(16)
        self.modules_grid.setVerticalSpacing(8)

        # danh sách checkbox: [(name, QCheckBox)]
        self.module_checkboxes = []
        modules = GameData.get_flat_list("Modules")  # list các tên (X), không phải RTID

        # Auto-check specific default modules
        default_auto_check = {
            "ZombiesDeadWinCon",
            "DefaultZombieWinCondition",
            "StandardIntro",
            "DefaultSunDropper",
        }

        # tạo checkbox theo lưới 3 cột
        cols = 3
        for idx, name in enumerate(modules):
            cb = QCheckBox(name)
            if name in default_auto_check:
                cb.setCheckState(Qt.CheckState.Checked)
            self.module_checkboxes.append((name, cb))
            r = idx // cols
            c = idx % cols
            self.modules_grid.addWidget(cb, r, c)

        self.modules_area.setWidget(self.modules_host)

        # Layout setup
        form.addRow("Description:", self.description)
        form.addRow("Level Number:", self.level_number)
        form.addRow("Level Name:", self.name)
        form.addRow("Written By:", self.written_by)
        form.addRow("Starting Sun:", self.starting_sun)
        form.addRow("Music Type:", self.music_type)
        form.addRow("Stage:", self.stage_module)
        form.addRow("Mower:", self.mower_module)

        self.layout.addLayout(form)
        self.layout.addWidget(QLabel("Modules:"))
        self.layout.addWidget(self.modules_area)
        self.layout.addWidget(QLabel("Fixed Loot/Present tables will be auto-filled."))

        self.setLayout(self.layout)

    # --------------------------------------------------------
    def build_level_definition(self, alias_modules):
        """Return the JSON object for LevelDefinition."""
        # Thu thập modules đã check, và bọc lại thành RTID(X@LevelModules)
        modules = []
        for name, cb in self.module_checkboxes:
            if cb.checkState() == Qt.CheckState.Checked:
                modules.append(f"RTID({name}@LevelModules)")

        # Add mower module if not None
        if self.mower_module.currentText() != "None":
            mower_ref = f"RTID({self.mower_module.currentText()}@LevelModules)"
            if mower_ref not in modules:
                modules.append(mower_ref)

        # Add CurrentLevel modules based on aliases (auto)
        for alias in alias_modules:
            modules.append(f"RTID({alias}@CurrentLevel)")

        # Remove duplicates while preserving order
        seen = set()
        modules = [m for m in modules if not (m in seen or seen.add(m))]

        objdata = {
            "Description": self.description.text(),
            "LevelNumber": int(self.level_number.text() or 1),
            "Loot": self.loot,
            "Modules": modules,
            "Name": self.name.text(),
            "WritenBy": self.written_by.text(),
            "NormalPresentTable": self.normal_table,
            "ShinyPresentTable": self.shiny_table,
            "StageModule": f"RTID({self.stage_module.currentText()}@LevelModules)"
        }

        # Handle MusicType: omit if "None"
        if self.music_type.currentText() != "None":
            objdata["MusicType"] = self.music_type.currentText()

        # Handle Starting Sun
        if self.starting_sun.text() != "50":
            objdata["StartingSun"] = self.starting_sun.text() 

        return {
            "objclass": "LevelDefinition",
            "objdata": objdata
        }

    # --------------------------------------------------------
    def load_from_json(self, data):
        """Restore UI from JSON data."""
        self.description.setText(data.get("Description", ""))
        self.level_number.setText(str(data.get("LevelNumber", 1)))
        self.name.setText(data.get("Name", ""))
        self.written_by.setText(data.get("WritenBy", ""))
        self.starting_sun.setText(data.get("Starting", "50"))

        # Stage module
        stage = data.get("StageModule", "")
        if "@LevelModules" in stage:
            name = stage.replace("RTID(", "").replace("@LevelModules)", "")
            if name in [self.stage_module.itemText(i) for i in range(self.stage_module.count())]:
                self.stage_module.setCurrentText(name)

        # Music type
        music = data.get("MusicType", "None")
        if music in ["MiniGame_A", "MiniGame_B"]:
            self.music_type.setCurrentText(music)
        else:
            self.music_type.setCurrentText("None")

        # Detect mower module from existing Modules
        mower_found = None
        for m in data.get("Modules", []):
            if "mower" in m.lower():  # check substring
                mower_name = m.replace("RTID(", "").replace("@LevelModules)", "")
                mower_found = mower_name
                break

        if mower_found and mower_found in [self.mower_module.itemText(i) for i in range(self.mower_module.count())]:
            self.mower_module.setCurrentText(mower_found)
        else:
            self.mower_module.setCurrentText("None")

        # Restore module check states (parse RTID(X@LevelModules) -> name)
        checked_names = set()
        for m in data.get("Modules", []):
            if m.startswith("RTID(") and "@LevelModules)" in m:
                name = m[len("RTID("):m.index("@LevelModules)")]
                checked_names.add(name)

        for name, cb in self.module_checkboxes:
            cb.setCheckState(Qt.CheckState.Checked if name in checked_names else Qt.CheckState.Unchecked)