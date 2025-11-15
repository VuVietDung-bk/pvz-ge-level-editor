from PyQt6.QtWidgets import QLineEdit, QCompleter
from PyQt6.QtCore import QStringListModel, Qt
from data_loader import GameData

class ReferenceLineEdit(QLineEdit):
    """QLineEdit with autocomplete suggestions for RTID references."""
    def __init__(self, object_list=None, allowed_classes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object_list = object_list or []
        self.allowed_classes = allowed_classes
        self.model = QStringListModel()
        self.completer = QCompleter(self.model, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(self.completer)
        self.refresh_suggestions()

    def refresh_suggestions(self):
        if not self.object_list:
            self.model.setStringList([])
            return
        aliases = []
        for obj in self.object_list:
            if self.allowed_classes and obj.get("objclass") not in self.allowed_classes:
                continue
            for alias in obj.get("aliases", []):
                aliases.append(alias)
        self.model.setStringList(aliases)

    def get_rtid_value(self):
        alias = self.text().strip()
        if not alias:
            return ""
        if alias.startswith("RTID("):
            return alias
        return f"RTID({alias}@CurrentLevel)"
    
class PlantLineEdit(ReferenceLineEdit):
    def __init__(self, *args, **kwargs):
        plants = []
        data = GameData.get("Plants")
        for world, arr in data.items():
            for e in arr:
                plants.append(e["code"])
        super().__init__(object_list=[{"aliases": plants}], *args, **kwargs)

    def get_rtid_value(self):
        alias = self.text().strip()
        if not alias:
            return ""
        return f"RTID({alias}@PlantTypes)"


class ZombieLineEdit(ReferenceLineEdit):
    def __init__(self, *args, **kwargs):
        zombies = []
        data = GameData.get("Zombies")
        for world, arr in data.items():
            for e in arr:
                zombies.append(e["code"])
        super().__init__(object_list=[{"aliases": zombies}], *args, **kwargs)

    def get_rtid_value(self):
        alias = self.text().strip()
        if not alias:
            return ""
        return f"RTID({alias}@ZombieTypes)"

class GridItemLineEdit(ReferenceLineEdit):
    """Autocomplete line edit for Grid Items from game_data.json."""
    def __init__(self, *args, **kwargs):
        grid_items = GameData.get_flat_list("Grid Items")
        super().__init__(object_list=[{"aliases": grid_items}], *args, **kwargs)
        self.setPlaceholderText("Enter grid item (e.g. gravestone_tutorial)")

    def get_rtid_value(self):
        alias = self.text().strip()
        if not alias:
            return ""
        return f"RTID({alias}@GridItem)"
    
class ConditionLineEdit(ReferenceLineEdit):
    """Autocomplete for condition strings from GameData."""
    def __init__(self, *args, **kwargs):
        conditions = GameData.get_flat_list("Conditions")
        super().__init__(object_list=[{"aliases": conditions}], *args, **kwargs)
        self.setPlaceholderText("Condition (e.g. icecubed, frozen, wet)")

class ReferenceValidator:
    """Cross-object RTID validator."""
    @staticmethod
    def is_reference_valid(reference: str, objects: list) -> bool:
        if not reference.startswith("RTID(") or "@CurrentLevel)" not in reference:
            return True
        alias = reference.replace("RTID(", "").replace("@CurrentLevel)", "")
        return any(alias in obj.get("aliases", []) for obj in objects)

    @staticmethod
    def list_missing_references(references: list[str], objects: list):
        missing = []
        for ref in references:
            if not ReferenceValidator.is_reference_valid(ref, objects):
                alias = ref.replace("RTID(", "").replace("@CurrentLevel)", "")
                missing.append(alias)
        return missing


class ObjectEditorFactory:
    """Factory for creating object editor dialogs dynamically."""
    _registry = {}

    @classmethod
    def register(cls, objclass_name, dialog_cls):
        cls._registry[objclass_name] = dialog_cls

    @classmethod
    def create(cls, objclass_name, parent=None, existing_data=None):
        dialog_cls = cls._registry.get(objclass_name)
        if not dialog_cls:
            return None
        return dialog_cls(parent=parent, existing_data=existing_data)