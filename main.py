import sys
from PyQt6.QtWidgets import QApplication
from editor_window import EditorWindow
from data_loader import GameData

def __init__():
    from editors.protect_the_plant import ProtectThePlantDialog
    from editors.base import ObjectEditorFactory
    from editors.spawn_zombies import SpawnZombiesJitteredDialog
    from editors.wave_manager import WaveManagerDialog
    from editors.wave_manager_module import WaveManagerModuleDialog
    from editors.gravestone_properties import GravestonePropertiesDialog
    from editors.zombie_potion_module import ZombiePotionModuleDialog
    from editors.seedbank_properties import SeedBankPropertiesDialog

    ObjectEditorFactory.register("SeedBankProperties", SeedBankPropertiesDialog)
    ObjectEditorFactory.register("GravestoneProperties", GravestonePropertiesDialog)
    ObjectEditorFactory.register("ZombiePotionModuleProperties", ZombiePotionModuleDialog)
    ObjectEditorFactory.register("ProtectThePlantChallengeProperties", ProtectThePlantDialog)
    ObjectEditorFactory.register("WaveManagerProperties", WaveManagerDialog)
    ObjectEditorFactory.register("SpawnZombiesJitteredWaveActionProps", SpawnZombiesJitteredDialog)
    ObjectEditorFactory.register("WaveManagerModuleProperties", WaveManagerModuleDialog)

    try:
        GameData.load("game_data.json")
    except Exception as e:
        print(f"⚠️ Failed to load game_data.json: {e}")


if __name__ == "__main__":
    __init__()
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.show()
    sys.exit(app.exec())