import json
import json5
import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTextEdit, QPushButton,
    QFileDialog, QVBoxLayout, QHBoxLayout, QMessageBox,
    QLabel, QTabWidget
)
from PyQt6.QtGui import QFont

from info_tab import InfoTab
from objects_tab import ObjectsTab
from leveldef_tab import LevelDefinitionTab


class EditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌱 PvZ GE Level Editor")
        self.resize(1150, 800)

        # Main elements
        self.tabs = QTabWidget()
        self.json_editor = QTextEdit()
        self.json_editor.setFont(QFont("Consolas", 11))
        self.json_editor.setPlaceholderText("Paste or type your level JSON here...")

        # Initialize tabs
        self.info_tab = InfoTab(self.json_editor)
        self.leveldef_tab = LevelDefinitionTab()
        self.objects_tab = ObjectsTab(self.json_editor)

        # Add tabs
        self.tabs.addTab(self.info_tab, "Level Information")
        self.tabs.addTab(self.leveldef_tab, "Level Definition")
        self.tabs.addTab(self.objects_tab, "Objects")
        self.tabs.addTab(self.create_json_tab(), "JSON Editor")

        # Generate full JSON button
        self.btn_generate_all = QPushButton("🌍 Generate Full JSON")
        self.btn_generate_all.clicked.connect(self.generate_full_json)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.btn_generate_all)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        tutorial_path = "tutorial_level.json"
        if os.path.exists(tutorial_path):
            try:
                self.load_json_from_path(tutorial_path)
            except Exception as e:
                a = 1

    # ---------------------------------------------------
    def generate_full_json(self):
        """Combine all sections into one final JSON structure."""
        # Get Information
        info = self.info_tab
        info_data = {
            "Information": {
                "Author": info.author.text() or "Unknown",
                "Introduction": info.introduction.toPlainText() or "",
                "Version": info.version.text(),
                "CreatedAt": info.created_at.text(),
                "UpdatedAt": info.updated_at.text(),
                "Difficulty": info.difficulty.currentText(),
                "Category": info.category.currentText()
            }
        }

        # Collect aliases from all root objects
        alias_modules = self.objects_tab.get_root_aliases()

        # Build LevelDefinition object
        level_def = self.leveldef_tab.build_level_definition(alias_modules)

        # Combine all into final structure
        final_json = info_data.copy()
        final_json["objects"] = [level_def] + self.objects_tab.objects
        final_json["version"] = 1

        # Update editor + tree
        self.json_editor.setText(json.dumps(final_json, indent=2, ensure_ascii=False))
        QMessageBox.information(self, "JSON Generated", "Full level JSON has been built successfully!")

    # ---------------------------------------------------
    def create_json_tab(self):
        """Creates the JSON editor tab."""
        page = QWidget()
        layout = QVBoxLayout()

        btn_open = QPushButton("📂 Open JSON")
        btn_open.clicked.connect(self.load_json)

        btn_save = QPushButton("💾 Save JSON")
        btn_save.clicked.connect(self.save_json)

        btn_validate = QPushButton("✅ Validate JSON")
        btn_validate.clicked.connect(self.validate_json)

        button_layout = QHBoxLayout()
        button_layout.addWidget(btn_open)
        button_layout.addWidget(btn_save)
        button_layout.addWidget(btn_validate)

        layout.addLayout(button_layout)
        layout.addWidget(QLabel("JSON Content:"))
        layout.addWidget(self.json_editor)

        page.setLayout(layout)
        return page

    # ---------------------------------------------------
    def load_json(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open JSON or JSON5 File", "", "JSON Files (*.json *.json5)"
        )
        if not file_name:
            return

        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json5.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read file:\n{e}")
            return

        # Cập nhật text editor
        self.json_editor.setText(json.dumps(data, indent=2, ensure_ascii=False))

        # --- Cập nhật các tab ---
        if "Information" in data:
            self.info_tab.load_from_json(data["Information"])

        # Lấy LevelDefinition từ danh sách objects
        level_def = next(
            (obj for obj in data.get("objects", []) if obj.get("objclass") == "LevelDefinition"), None
        )
        if level_def:
            self.leveldef_tab.load_from_json(level_def["objdata"])

        # Các object khác (ngoại trừ LevelDefinition)
        other_objs = [
            o for o in data.get("objects", [])
            if o.get("objclass") != "LevelDefinition"
        ]
        self.objects_tab.load_from_json(other_objs)

        QMessageBox.information(self, "Loaded", "File loaded and state updated successfully!")

    def load_json_from_path(self, file_name):
        """Load JSON from a direct file path without dialog."""
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json5.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read file:\n{e}")
            return

        # Cập nhật text editor
        self.json_editor.setText(json.dumps(data, indent=2, ensure_ascii=False))

        # --- Cập nhật các tab ---
        if "Information" in data:
            self.info_tab.load_from_json(data["Information"])

        level_def = next(
            (obj for obj in data.get("objects", []) if obj.get("objclass") == "LevelDefinition"), None
        )
        if level_def:
            self.leveldef_tab.load_from_json(level_def["objdata"])

        other_objs = [
            o for o in data.get("objects", [])
            if o.get("objclass") != "LevelDefinition"
        ]
        self.objects_tab.load_from_json(other_objs)

    def save_json(self):
        try:
            data = json.loads(self.json_editor.toPlainText())
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"Syntax error:\n{e}")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json *.json5)")
        if not file_name:
            return

        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        QMessageBox.information(self, "Saved", "JSON file has been saved successfully!")

    def validate_json(self):
        try:
            json.loads(self.json_editor.toPlainText())
            QMessageBox.information(self, "Valid", "✅ JSON structure is valid!")
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid", f"❌ JSON syntax error:\n{e}")