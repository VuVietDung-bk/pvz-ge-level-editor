from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QComboBox, QLabel, QListWidget, QListWidgetItem
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

        # --- Modules selection ---
        self.modules_list = QListWidget()
        self.modules_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        modules = GameData.get_flat_list("Modules")

        for m in modules:
            item = QListWidgetItem(f"RTID({m}@LevelModules)")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.modules_list.addItem(item)

        # Auto-check specific default modules
        default_auto_check = {
            "ZombiesDeadWinCon",
            "DefaultZombieWinCondition",
            "StandardIntro",
            "DefaultSunDropper",
        }

        for i in range(self.modules_list.count()):
            item = self.modules_list.item(i)
            # extract module code from text "RTID(X@LevelModules)"
            text = item.text()
            match = re.match(r"RTID\(([^@]+)@LevelModules\)", text)
            if match and match.group(1) in default_auto_check:
                item.setCheckState(Qt.CheckState.Checked)

        # Layout setup
        form.addRow("Description:", self.description)
        form.addRow("Level Number:", self.level_number)
        form.addRow("Level Name:", self.name)
        form.addRow("Written By:", self.written_by)
        form.addRow("Music Type:", self.music_type)
        form.addRow("Stage:", self.stage_module)
        form.addRow("Mower:", self.mower_module)

        self.layout.addLayout(form)
        self.layout.addWidget(QLabel("Modules:"))
        self.layout.addWidget(self.modules_list)
        self.layout.addWidget(QLabel("Fixed Loot/Present tables will be auto-filled."))

        self.setLayout(self.layout)

    # --------------------------------------------------------
    def build_level_definition(self, alias_modules):
        """Return the JSON object for LevelDefinition."""
        modules = []
        for i in range(self.modules_list.count()):
            item = self.modules_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                modules.append(item.text())

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

        # Restore module check states
        for i in range(self.modules_list.count()):
            item = self.modules_list.item(i)
            if item.text() in data.get("Modules", []):
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)