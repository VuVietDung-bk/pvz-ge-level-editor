from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QDialogButtonBox, QHBoxLayout, QLineEdit, QFormLayout, QMessageBox
)


class StarChallengeBeatTheLevelDialog(QDialog):
    """Dialog for editing StarChallengeBeatTheLevelProps."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit StarChallengeBeatTheLevelProps")
        self.resize(600, 500)

        data = existing_data or {}
        self.descriptions = data.get("Descriptions", [])
        self.descriptions_multi = data.get("DescriptionsMultiLanguage", [])

        layout = QVBoxLayout()

        # --- Descriptions list ---
        layout.addWidget(QLabel("<b>Descriptions</b>"))
        self.desc_list = QListWidget()
        for d in self.descriptions:
            self.desc_list.addItem(d)
        layout.addWidget(self.desc_list)

        btn_add_desc = QPushButton("➕ Add")
        btn_edit_desc = QPushButton("✏️ Edit")
        btn_remove_desc = QPushButton("🗑 Remove")
        btn_add_desc.clicked.connect(self.add_desc)
        btn_edit_desc.clicked.connect(self.edit_desc)
        btn_remove_desc.clicked.connect(self.remove_desc)

        desc_btns = QHBoxLayout()
        desc_btns.addWidget(btn_add_desc)
        desc_btns.addWidget(btn_edit_desc)
        desc_btns.addWidget(btn_remove_desc)
        layout.addLayout(desc_btns)

        # --- DescriptionsMultiLanguage list ---
        layout.addWidget(QLabel("<b>Descriptions Multi-Language</b>"))
        self.multi_list = QListWidget()
        for item in self.descriptions_multi:
            text = ", ".join(f"{k}: {v}" for k, v in item.items())
            self.multi_list.addItem(text)
        layout.addWidget(self.multi_list)

        btn_add_multi = QPushButton("➕ Add Lang Entry")
        btn_edit_multi = QPushButton("✏️ Edit Selected")
        btn_remove_multi = QPushButton("🗑 Remove Selected")

        btn_add_multi.clicked.connect(self.add_multi)
        btn_edit_multi.clicked.connect(self.edit_multi)
        btn_remove_multi.clicked.connect(self.remove_multi)

        multi_btns = QHBoxLayout()
        multi_btns.addWidget(btn_add_multi)
        multi_btns.addWidget(btn_edit_multi)
        multi_btns.addWidget(btn_remove_multi)
        layout.addLayout(multi_btns)

        # --- OK / Cancel ---
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    # ========== Descriptions ==========
    def add_desc(self):
        text, ok = self._get_text_input("Add Description", "")
        if ok and text:
            self.desc_list.addItem(text)

    def edit_desc(self):
        idx = self.desc_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select", "Please select a description to edit.")
            return
        old_text = self.desc_list.item(idx).text()
        text, ok = self._get_text_input("Edit Description", old_text)
        if ok and text:
            self.desc_list.item(idx).setText(text)

    def remove_desc(self):
        for item in self.desc_list.selectedItems():
            self.desc_list.takeItem(self.desc_list.row(item))

    # ========== Multi-Language ==========
    def add_multi(self):
        dlg = LanguageEntryDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted:
            d = dlg.get_data()
            text = ", ".join(f"{k}: {v}" for k, v in d.items())
            self.multi_list.addItem(text)

    def edit_multi(self):
        idx = self.multi_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Select", "Please select an entry to edit.")
            return
        text = self.multi_list.item(idx).text()
        pairs = dict(pair.split(": ", 1) for pair in text.split(", "))
        dlg = LanguageEntryDialog(self, pairs)
        if dlg.exec() == dlg.DialogCode.Accepted:
            d = dlg.get_data()
            new_text = ", ".join(f"{k}: {v}" for k, v in d.items())
            self.multi_list.item(idx).setText(new_text)

    def remove_multi(self):
        for item in self.multi_list.selectedItems():
            self.multi_list.takeItem(self.multi_list.row(item))

    # ========== Utils ==========
    def _get_text_input(self, title, default=""):
        from PyQt6.QtWidgets import QInputDialog
        return QInputDialog.getText(self, title, "Enter text:", text=default)

    def get_data(self):
        descs = [self.desc_list.item(i).text() for i in range(self.desc_list.count())]
        multi = []
        for i in range(self.multi_list.count()):
            txt = self.multi_list.item(i).text()
            pairs = dict(pair.split(": ", 1) for pair in txt.split(", "))
            multi.append(pairs)
        return {"Descriptions": descs, "DescriptionsMultiLanguage": multi}


class LanguageEntryDialog(QDialog):
    """Dialog for editing one DescriptionsMultiLanguage entry (en, zh, etc.)."""

    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Multi-Language Entry")
        self.resize(400, 250)

        data = existing_data or {}
        layout = QFormLayout()

        self.en = QLineEdit(data.get("en", ""))
        self.zh = QLineEdit(data.get("zh", ""))

        layout.addRow("English (en):", self.en)
        layout.addRow("Chinese (zh):", self.zh)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_data(self):
        d = {}
        if self.en.text().strip():
            d["en"] = self.en.text().strip()
        if self.zh.text().strip():
            d["zh"] = self.zh.text().strip()
        return d
