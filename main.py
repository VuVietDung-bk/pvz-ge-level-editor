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
    from editors.last_stand import LastStandMinigameDialog
    from editors.conveyor_seedbank import ConveyorSeedBankDialog
    from editors.modify_conveyor import ModifyConveyorDialog
    from editors.power_tile_properties import PowerTileDialog
    from editors.mold_colony_challenge import MoldColonyChallengeDialog
    from editors.pirate_plank_properties import PiratePlankDialog
    from editors.star_challenge_beat_level import StarChallengeBeatTheLevelDialog
    from editors.star_challenge_kill_zombies_time import StarChallengeKillZombiesInTimeDialog
    from editors.star_challenge_plants_lost import StarChallengePlantsLostDialog
    from editors.star_challenge_simultaneous_plants import StarChallengeSimultaneousPlantsDialog
    from editors.star_challenge_sun_produced import StarChallengeSunProducedDialog
    from editors.star_challenge_zombie_distance import StarChallengeZombieDistanceDialog
    from editors.star_challenge_module import StarChallengeModuleDialog
    from editors.star_challenge_sun_used import StarChallengeSunUsedPropsDialog
    from editors.initial_grid_item import InitialGridItemDialog
    from editors.initial_plant_properties import InitialPlantPropertiesEditor
    from editors.initial_zombie_properties import InitialZombiePropertiesEditor
    from editors.trap_tile_properties import TrapTilePropertiesEditor
    from editors.railcart_properties import RailcartPropertiesDialog

    ObjectEditorFactory.register("RailcartProperties", RailcartPropertiesDialog)
    ObjectEditorFactory.register("TrapTileProperties", TrapTilePropertiesEditor)
    ObjectEditorFactory.register("InitialZombieProperties", InitialZombiePropertiesEditor)
    ObjectEditorFactory.register("InitialPlantProperties", InitialPlantPropertiesEditor)
    ObjectEditorFactory.register("InitialGridItemProperties", InitialGridItemDialog)
    ObjectEditorFactory.register("PiratePlankProperties", PiratePlankDialog)
    ObjectEditorFactory.register("MoldColonyChallengeProps", MoldColonyChallengeDialog)
    ObjectEditorFactory.register("PowerTileProperties", PowerTileDialog)
    ObjectEditorFactory.register("ModifyConveyorWaveActionProps", ModifyConveyorDialog)
    ObjectEditorFactory.register("ConveyorSeedBankProperties", ConveyorSeedBankDialog)
    ObjectEditorFactory.register("LastStandMinigameProperties", LastStandMinigameDialog)
    ObjectEditorFactory.register("SeedBankProperties", SeedBankPropertiesDialog)
    ObjectEditorFactory.register("GravestoneProperties", GravestonePropertiesDialog)
    ObjectEditorFactory.register("ZombiePotionModuleProperties", ZombiePotionModuleDialog)
    ObjectEditorFactory.register("ProtectThePlantChallengeProperties", ProtectThePlantDialog)
    ObjectEditorFactory.register("WaveManagerProperties", WaveManagerDialog)
    ObjectEditorFactory.register("SpawnZombiesJitteredWaveActionProps", SpawnZombiesJitteredDialog)
    ObjectEditorFactory.register("WaveManagerModuleProperties", WaveManagerModuleDialog)
    ObjectEditorFactory.register("StarChallengeBeatTheLevelProps", StarChallengeBeatTheLevelDialog)
    ObjectEditorFactory.register("StarChallengeKillZombiesInTimeProps", StarChallengeKillZombiesInTimeDialog)
    ObjectEditorFactory.register("StarChallengePlantsLostProps", StarChallengePlantsLostDialog)
    ObjectEditorFactory.register("StarChallengeSimultaneousPlantsProps", StarChallengeSimultaneousPlantsDialog)
    ObjectEditorFactory.register("StarChallengeSunProducedProps", StarChallengeSunProducedDialog)
    ObjectEditorFactory.register("StarChallengeZombieDistanceProps", StarChallengeZombieDistanceDialog)
    ObjectEditorFactory.register("StarChallengeModuleProperties", StarChallengeModuleDialog)
    ObjectEditorFactory.register("StarChallengeSunUsedProps", StarChallengeSunUsedPropsDialog)

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