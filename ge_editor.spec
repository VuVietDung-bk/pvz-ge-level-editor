# ge_editor.spec — build configuration for PyInstaller

from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import os

# ----- Basic config -----
app_name = "GE-Level-Editor"
main_script = "main.py"

# Paths
base_path = os.path.abspath(".")
data_files = [
    (os.path.join(base_path, "game_data.json"), "."),
]

# Include folders (editors, ui, etc.)
extra_dirs = [
    ("editors", "editors"),
    ("ui", "ui"),
]

# ----- Collect data and dynamic modules -----
datas = []
for src, dst in data_files + extra_dirs:
    if os.path.exists(src):
        datas.append((src, dst))

hiddenimports = collect_submodules("editors")

# ----- PyInstaller Build Config -----
a = Analysis(
    [main_script],
    pathex=[base_path],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name=app_name,
    debug=False,
    strip=False,
    upx=True,
    console=False,  # Đặt True nếu bạn muốn console để debug
    icon=None  # Đặt "assets/icon.ico" nếu có icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name
)