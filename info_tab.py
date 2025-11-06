import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QPushButton, QLabel, QMessageBox
)


class InfoTab(QWidget):
    """Tab for entering level information and generating JSON."""
    def __init__(self, editor_reference):
        super().__init__()
        self.editor_reference = editor_reference  # Reference to main JSON editor (in other tab)

        # Layouts
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        # --- Fields ---
        self.author = QLineEdit()
        self.introduction = QTextEdit()
        self.version = QLineEdit("1.0")
        self.created_at = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.updated_at = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.difficulty = QComboBox()
        self.category = QComboBox()

        # Populate combo boxes
        self.difficulty.addItems(["Easy", "Normal", "Hard", "Extreme"])
        self.category.addItems(["Adventure", "Survival", "Challenge", "MiniGame"])

        # Add to form layout
        form_layout.addRow("Author:", self.author)
        form_layout.addRow("Introduction:", self.introduction)
        form_layout.addRow("Version:", self.version)
        form_layout.addRow("Created At:", self.created_at)
        form_layout.addRow("Updated At:", self.updated_at)
        form_layout.addRow("Difficulty:", self.difficulty)
        form_layout.addRow("Category:", self.category)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(QLabel("Click 'Generate Full JSON' to get the JSON file"))

        self.setLayout(main_layout)


    def load_from_json(self, info):
        self.author.setText(info.get("Author", ""))
        self.introduction.setPlainText(info.get("Introduction", ""))
        self.version.setText(info.get("Version", "1.0"))
        self.created_at.setText(info.get("CreatedAt", ""))
        self.updated_at.setText(info.get("UpdatedAt", ""))
        self.difficulty.setCurrentText(info.get("Difficulty", "Normal"))
        self.category.setCurrentText(info.get("Category", "Survival"))
