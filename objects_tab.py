import json
import re
import copy
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout,
    QComboBox, QLineEdit, QPushButton, QLabel,
    QListWidget, QMessageBox, QDialog, QInputDialog
)
from PyQt6.QtGui import QShortcut, QKeySequence
from editors.base import ObjectEditorFactory, ReferenceLineEdit
from data_loader import GameData
from PyQt6.QtCore import Qt

class ObjectsTab(QWidget):
    """Tab for creating and managing 'objects' array in JSON."""
    clipboard = None  # in-memory full-object clipboard

    def __init__(self, editor_reference):
        super().__init__()
        self.editor_reference = editor_reference
        self.objects = []  # List of added objects

        # Layouts
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        # --- Build mapping display_name -> code_name ---
        self.objclass_display_map = {}

        objclasses = GameData.get("Objclasses")
        # Build mapping: display name -> code (sorted by display name)
        temp_map = {}

        for entry in objclasses:
            code = entry.get("code", "")
            name = entry.get("name", code)
            temp_map[name] = code

        # Sort alphabetically by display name
        self.objclass_display_map = dict(sorted(temp_map.items(), key=lambda x: x[0].lower()))

        # Object selection and alias
        self.objclass = QComboBox()
        self.objclass.addItem("<default-class>")
        self.objclass.addItems(self.objclass_display_map.keys())

        self.aliases_input = QLineEdit()
        form_layout.addRow("Object Class:", self.objclass)
        form_layout.addRow("Aliases (comma separated):", self.aliases_input)

        # auto-suggest alias when objectclass changes
        self.objclass.currentTextChanged.connect(self.suggest_alias_for_current_class)

        # Buttons
        btn_add = QPushButton("➕ Add Object")
        btn_add.clicked.connect(self.add_object)

        btn_remove = QPushButton("🗑 Remove Selected")
        btn_remove.clicked.connect(self.remove_object)

        btn_copy = QPushButton("📋 Copy")
        btn_copy.clicked.connect(self.copy_object)

        btn_paste = QPushButton("📥 Paste")
        btn_paste.clicked.connect(self.paste_object)

        button_layout = QHBoxLayout()
        button_layout.addWidget(btn_add)
        button_layout.addWidget(btn_remove)
        button_layout.addWidget(btn_copy)
        button_layout.addWidget(btn_paste)

        # List of added objects
        self.objects_list = QListWidget()
        self.objects_list.itemDoubleClicked.connect(self.edit_object)

        # Enable drag & drop reordering
        self.objects_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.objects_list.setDefaultDropAction(Qt.DropAction.MoveAction)

        # Sync data after reordering
        self.objects_list.model().rowsMoved.connect(self.on_rows_moved)

        # Keyboard shortcuts (Ctrl+C / Ctrl+V)
        self.sc_copy = QShortcut(QKeySequence.StandardKey.Copy, self)
        self.sc_copy.activated.connect(self.copy_object)
        self.sc_paste = QShortcut(QKeySequence.StandardKey.Paste, self)
        self.sc_paste.activated.connect(self.paste_object)
        self.sc_paste_raw = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        self.sc_paste_raw.activated.connect(self.paste_object_raw)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(QLabel("Added Objects:"))
        main_layout.addWidget(self.objects_list)

        self.setLayout(main_layout)
        self.alias_tree = {}  # key = parent alias, value = list of child aliases

    # ----------------------- HELPERS -----------------------
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
        if cls_name.lower().endswith("challengeproperties"):
            base = cls_name[: -len("challengeproperties")]
        elif cls_name.lower().endswith("props"):
            base = cls_name[: -len("props")]
        elif cls_name.lower().endswith("properties"):
            base = cls_name[: -len("properties")]
        else:
            base = cls_name

        if base.lower().startswith("starchallenge"):
            base = base[len("StarChallenge"):]
        base = base or "Object"
        return self.unique_alias(base)

    def suggest_alias_for_current_class(self):
        display_name = self.objclass.currentText()

        real_code = self.objclass_display_map.get(display_name, display_name)

        suggested = self.derive_alias_from_class(real_code)
        self.aliases_input.setText(suggested)

    # --------------------- ALIAS EXTRACTION ---------------------
    def _extract_aliases_from_objdata(self, obj):
        """Recursively extract RTID(xxx@CurrentLevel) children for 1 object."""
        child_aliases = []

        def extract_aliases(node):
            if isinstance(node, dict):
                for v in node.values():
                    extract_aliases(v)
            elif isinstance(node, list):
                for v in node:
                    extract_aliases(v)
            elif isinstance(node, str):
                if node.startswith("RTID(") and "@CurrentLevel)" in node:
                    name = node.replace("RTID(", "").replace("@CurrentLevel)", "")
                    if name not in child_aliases:
                        child_aliases.append(name)

        # Special handling for StarChallengeModuleProperties: Challenges can be list[list[str]] or list[str]
        if obj["objclass"] == "StarChallengeModuleProperties":
            challenges = obj["objdata"].get("Challenges", [])
            if isinstance(challenges, list):
                for group in challenges:
                    if isinstance(group, list):
                        for ref in group:
                            if isinstance(ref, str) and ref.startswith("RTID(") and "@CurrentLevel)" in ref:
                                name = ref.replace("RTID(", "").replace("@CurrentLevel)", "")
                                if name not in child_aliases:
                                    child_aliases.append(name)
                    elif isinstance(group, str) and "RTID(" in group:
                        name = group.replace("RTID(", "").replace("@CurrentLevel)", "")
                        if name not in child_aliases:
                            child_aliases.append(name)
        else:
            extract_aliases(obj["objdata"])

        return list(set(child_aliases))

    def rebuild_alias_tree(self):
        """Recompute alias->children mapping from scratch for all objects."""
        self.alias_tree = {}
        for obj in self.objects:
            child_aliases = self._extract_aliases_from_objdata(obj)
            for parent_alias in obj.get("aliases", []):
                self.alias_tree[parent_alias] = child_aliases

    # ----------------------------------------------------------
    def add_object(self):
        """Open the appropriate editor dialog for the chosen objclass."""
        display_name = self.objclass.currentText()
        objclass = self.objclass_display_map.get(display_name, display_name)
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
                if objdata is None:
                    return  # validation failed inside dialog, do nothing
            else:
                return
        else:
            # fallback to manual JSON entry
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

        # --- rebuild alias tree globally (robust for all ops)
        self.rebuild_alias_tree()

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
        alias_before = list(obj.get("aliases", []))
        alias_text = ", ".join(alias_before)

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
            # Enforce uniqueness when user edits (ignore collisions with self)
            deduped = []
            current_aliases = self.existing_aliases() - set(alias_before)
            for a in new_aliases:
                if a in current_aliases:
                    a = self.unique_alias(a)
                deduped.append(a)
            obj["aliases"] = deduped

        # --- Edit objdata
        dlg = ObjectEditorFactory.create(objclass, parent=self, existing_data=obj["objdata"])
        if dlg is not None:
            dlg.object_list_ref = self.objects
            if dlg.exec() == dlg.DialogCode.Accepted:
                newdata = dlg.get_data()
                if newdata is None:
                    return
                obj["objdata"] = newdata
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

        # Update list display text
        alias_display = ", ".join(obj.get("aliases", [])) or "None"
        item.setText(f"{objclass} (aliases: {alias_display})")
        self.objects[index] = obj

        # --- rebuild alias tree since aliases/objdata may have changed
        self.rebuild_alias_tree()

        # refresh completers
        for dlg in self.findChildren(QDialog):
            for edit in dlg.findChildren(QLineEdit):
                if isinstance(edit, ReferenceLineEdit):
                    edit.object_list = self.objects
                    edit.refresh_suggestions()

    # ----------------------------------------------------------
    def remove_object(self):
        """Remove selected item(s)."""
        selected = self.objects_list.selectedItems()
        if not selected:
            return
        # Remove from data & UI
        for item in selected:
            idx = self.objects_list.row(item)
            self.objects_list.takeItem(idx)
            self.objects.pop(idx)

        # --- rebuild alias tree after removal
        self.rebuild_alias_tree()

        # refresh completers
        for dlg in self.findChildren(QDialog):
            for edit in dlg.findChildren(QLineEdit):
                if isinstance(edit, ReferenceLineEdit):
                    edit.object_list = self.objects
                    edit.refresh_suggestions()

    # ----------------------- COPY / PASTE -----------------------
    def copy_object(self):
        """Copy selected object (deep) into in-memory clipboard."""
        idx = self.objects_list.currentRow()
        if idx < 0:
            QMessageBox.warning(self, "Copy Object", "Please select an object to copy.")
            return
        ObjectsTab.clipboard = copy.deepcopy(self.objects[idx])

    def paste_object(self):
        """Paste a copied object as a new one; aliases auto-uniq'ed."""
        if not ObjectsTab.clipboard:
            QMessageBox.warning(self, "Paste Object", "Clipboard is empty. Copy an object first.")
            return

        new_obj = copy.deepcopy(ObjectsTab.clipboard)

        # Ensure aliases exist and are unique
        aliases = new_obj.get("aliases", [])
        if not aliases:
            aliases = ["PastedObject"]
        aliases = [self.unique_alias(a) for a in aliases]
        new_obj["aliases"] = aliases

        # Append & show
        self.objects.append(new_obj)
        alias_text = ", ".join(aliases)
        self.objects_list.addItem(f"{new_obj['objclass']} (aliases: {alias_text})")

        # --- rebuild alias tree after paste
        self.rebuild_alias_tree()

        # Refresh reference completers
        for dlg in self.findChildren(QDialog):
            for edit in dlg.findChildren(QLineEdit):
                if isinstance(edit, ReferenceLineEdit):
                    edit.object_list = self.objects
                    edit.refresh_suggestions()

    def paste_object_raw(self):
        """Paste a copied object as a new one, keeping original alias names."""
        if not ObjectsTab.clipboard:
            QMessageBox.warning(self, "Paste Object", "Clipboard is empty. Copy an object first.")
            return

        new_obj = copy.deepcopy(ObjectsTab.clipboard)
        aliases = new_obj.get("aliases", [])

        if not aliases:
            QMessageBox.warning(self, "Invalid Object", "The copied object has no aliases.")
            return

        # Append object as-is
        self.objects.append(new_obj)
        alias_text = ", ".join(aliases)
        self.objects_list.addItem(f"{new_obj['objclass']} (aliases: {alias_text})")

        # --- rebuild alias tree after paste raw
        self.rebuild_alias_tree()

        # Refresh all completers
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

        # --- rebuild alias tree after loading
        self.rebuild_alias_tree()

    def get_root_aliases(self):
        """Return only aliases that are not referenced as children anywhere."""
        all_children = set()
        for childs in self.alias_tree.values():
            all_children.update(childs)

        roots = []
        for obj in self.objects:
            for alias in obj.get("aliases", []):
                if alias not in all_children:
                    roots.append(alias)
        return roots
    
    def on_rows_moved(self, parent, start, end, destination, row):
        """
        Sync internal self.objects[] when user drag/drops items in QListWidget.
        """
        # QListWidget has already moved the visible item.
        # Now we must reorder self.objects to match the list.

        # Build new order from QListWidget
        new_order = []
        for i in range(self.objects_list.count()):
            text = self.objects_list.item(i).text()
            # find matching object
            for obj in self.objects:
                alias_text = ", ".join(obj.get("aliases", [])) or "None"
                if text == f"{obj['objclass']} (aliases: {alias_text})":
                    new_order.append(obj)
                    break

        # Replace internal array
        if len(new_order) == len(self.objects):
            self.objects = new_order
        else:
            print("Warning: reorder sync mismatch!")

        # Rebuild alias tree because order might affect module chains
        self.rebuild_alias_tree()

        # Refresh all autocomplete reference editors
        for dlg in self.findChildren(QDialog):
            for edit in dlg.findChildren(QLineEdit):
                if hasattr(edit, "object_list"):
                    edit.object_list = self.objects
                    edit.refresh_suggestions()