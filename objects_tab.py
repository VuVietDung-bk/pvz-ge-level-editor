import json
import re
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout,
    QComboBox, QLineEdit, QPushButton, QLabel,
    QListWidget, QMessageBox, QDialog
)
from editors.base import ObjectEditorFactory, ReferenceLineEdit
from data_loader import GameData

class ObjectsTab(QWidget):
    """Tab for creating and managing 'objects' array in JSON."""
    def __init__(self, editor_reference):
        super().__init__()
        self.editor_reference = editor_reference
        self.objects = []  # List of added objects

        # Layouts
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Object selection and alias
        self.objclass = QComboBox()
        self.objclass.addItem("<default-class>")
        self.objclass.addItems(GameData.get_flat_list("Objclasses"))

        self.aliases_input = QLineEdit()
        form_layout.addRow("Object Class:", self.objclass)
        form_layout.addRow("Aliases (comma separated):", self.aliases_input)

        # NEW: auto-suggest alias when objectclass changes
        self.objclass.currentTextChanged.connect(self.suggest_alias_for_current_class)

        # Buttons
        btn_add = QPushButton("➕ Add Object")
        btn_add.clicked.connect(self.add_object)

        btn_remove = QPushButton("🗑 Remove Selected")
        btn_remove.clicked.connect(self.remove_object)

        button_layout = QHBoxLayout()
        button_layout.addWidget(btn_add)
        button_layout.addWidget(btn_remove)

        # List of added objects
        self.objects_list = QListWidget()
        self.objects_list.itemDoubleClicked.connect(self.edit_object)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(QLabel("Added Objects:"))
        main_layout.addWidget(self.objects_list)

        self.setLayout(main_layout)

    # ----------------------- NEW HELPERS -----------------------
    def existing_aliases(self):
        aliases = []
        for o in self.objects:
            for a in o.get("aliases", []):
                aliases.append(a)
        return set(aliases)

    def next_wave_alias(self):
        # Find highest WaveN and return Wave{N+1}
        max_n = 0
        wave_re = re.compile(r"^Wave(\d+)$", re.IGNORECASE)
        for a in self.existing_aliases():
            m = wave_re.match(a)
            if m:
                try:
                    max_n = max(max_n, int(m.group(1)))
                except ValueError:
                    pass
        return f"Wave{max_n+1 if max_n >= 0 else 1}"

    def unique_alias(self, base):
        # Ensure alias is unique by appending numeric suffixes if needed
        existing = self.existing_aliases()
        if base not in existing:
            return base
        i = 1
        while True:
            candidate = f"{base}{i}"
            if candidate not in existing:
                return candidate
            i += 1

    def derive_alias_from_class(self, cls_name):
        # Special case
        if cls_name == "SpawnZombiesJitteredWaveActionProps":
            return self.next_wave_alias()

        # Generic: strip trailing 'Properties' (case-insensitive)
        if cls_name.lower().endswith("properties"):
            base = cls_name[: -len("properties")]
        else:
            base = cls_name
        # Tidy: if base ends with 'Module' redundantly (e.g., WaveManagerModule), keep as-is
        # Make sure not empty
        base = base or "Object"
        return self.unique_alias(base)

    def suggest_alias_for_current_class(self):
        # Only prefill if user hasn't typed anything
        if self.aliases_input.text().strip():
            return
        cls_name = self.objclass.currentText()
        suggested = self.derive_alias_from_class(cls_name)
        self.aliases_input.setText(suggested)

    # ----------------------------------------------------------
    def add_object(self):
        """Open the appropriate editor dialog for the chosen objclass."""
        objclass = self.objclass.currentText()
        aliases_text = self.aliases_input.text().strip()

        # If user left empty, auto-suggest now for convenience
        if not aliases_text:
            suggested = self.derive_alias_from_class(objclass)
            self.aliases_input.setText(suggested)
            aliases_text = suggested

        if not aliases_text:
            QMessageBox.warning(self, "Missing Alias", "You must specify at least one alias for this object.")
            return

        dlg = ObjectEditorFactory.create(objclass, parent=self)
        if dlg is not None:
            dlg.object_list_ref = self.objects
            # Has a registered custom dialog
            if dlg.exec() == dlg.DialogCode.Accepted:
                objdata = dlg.get_data()
            else:
                return
        else:
            # fallback to manual JSON entry
            from PyQt6.QtWidgets import QInputDialog
            text, ok = QInputDialog.getMultiLineText(
                self, "Custom Object Data",
                f"Enter JSON for {objclass}:",
                '{ "key": "value" }'
            )
            if not ok:
                return
            try:
                objdata = json.loads(text)
            except Exception as e:
                QMessageBox.warning(self, "Invalid JSON", str(e))
                return

        # Add object to list
        obj = {"objclass": objclass, "objdata": objdata}
        if aliases_text:
            obj["aliases"] = [a.strip() for a in aliases_text.split(",") if a.strip()]

        self.objects.append(obj)
        self.objects_list.addItem(f"{objclass} (aliases: {aliases_text or 'None'})")
        self.aliases_input.clear()

        # Convenience: if user is adding many Waves in a row, prefill next WaveN
        if objclass == "SpawnZombiesJitteredWaveActionProps":
            self.aliases_input.setText(self.next_wave_alias())

        # refresh reference completers everywhere
        for dlg in self.findChildren(QDialog):
            for edit in dlg.findChildren(QLineEdit):
                if isinstance(edit, ReferenceLineEdit):
                    edit.object_list = self.objects
                    edit.refresh_suggestions()

    # ----------------------------------------------------------
    def edit_object(self, item):
        """Double-click to open the registered dialog for editing (including aliases)."""
        index = self.objects_list.row(item)
        obj = self.objects[index]
        objclass = obj["objclass"]

        # --- Edit aliases first
        from PyQt6.QtWidgets import QInputDialog
        alias_text = ", ".join(obj.get("aliases", []))
        new_aliases_text, ok_alias = QInputDialog.getText(
            self,
            "Edit Aliases",
            f"Edit aliases for {objclass} (comma separated):",
            text=alias_text
        )
        if ok_alias:
            new_aliases = [a.strip() for a in new_aliases_text.split(",") if a.strip()]
            if not new_aliases:
                QMessageBox.warning(self, "Alias Required", "You must keep at least one alias for this object.")
                return
            # Enforce uniqueness when user edits
            deduped = []
            for a in new_aliases:
                if a in self.existing_aliases() and a not in obj.get("aliases", []):
                    a = self.unique_alias(a)
                deduped.append(a)
            obj["aliases"] = deduped

        # --- Edit objdata
        dlg = ObjectEditorFactory.create(objclass, parent=self, existing_data=obj["objdata"])
        if dlg is not None:
            dlg.object_list_ref = self.objects
            if dlg.exec() == dlg.DialogCode.Accepted:
                obj["objdata"] = dlg.get_data()
        else:
            # fallback manual JSON edit
            text, ok = QInputDialog.getMultiLineText(
                self,
                "Edit Object Data",
                f"Edit JSON for {objclass}:",
                json.dumps(obj["objdata"], indent=2)
            )
            if ok:
                try:
                    obj["objdata"] = json.loads(text)
                except Exception as e:
                    QMessageBox.warning(self, "Invalid JSON", str(e))
                    return

        alias_display = ", ".join(obj.get("aliases", [])) or "None"
        item.setText(f"{objclass} (aliases: {alias_display})")
        self.objects[index] = obj

        # refresh completers
        for dlg in self.findChildren(QDialog):
            for edit in dlg.findChildren(QLineEdit):
                if isinstance(edit, ReferenceLineEdit):
                    edit.object_list = self.objects
                    edit.refresh_suggestions()

    # ----------------------------------------------------------
    def remove_object(self):
        """Remove selected item(s)."""
        for item in self.objects_list.selectedItems():
            idx = self.objects_list.row(item)
            self.objects_list.takeItem(idx)
            self.objects.pop(idx)
        for dlg in self.findChildren(QDialog):
            for edit in dlg.findChildren(QLineEdit):
                if isinstance(edit, ReferenceLineEdit):
                    edit.object_list = self.objects
                    edit.refresh_suggestions()

    # ----------------------------------------------------------
    def load_from_json(self, objects):
        """Load existing objects from file."""
        self.objects = []
        self.objects_list.clear()
        for obj in objects:
            self.objects.append(obj)
            alias_text = ", ".join(obj.get("aliases", []))
            self.objects_list.addItem(f"{obj['objclass']} (aliases: {alias_text or 'None'})")