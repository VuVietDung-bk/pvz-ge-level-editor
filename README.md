# GE Level Editor

A **visual level editor** for creating and editing JSON/JSON5-based game levels.  
GE Level Editor makes it easy to design levels for PvZ GE without touching code.

---

## Quick Start (for non-developers)

If you just want to **use** the app, follow these simple steps:

### 1. Files you need
Download and place the following files **in the same folder**:
| File | Purpose |
|------|----------|
| `GE-Level-Editor.exe` | The main application |
| `game_data.json` | Internal data for autocomplete (plants, zombies, modules, etc.) |

---

### 2. Run the application
1. Double-click `GE-Level-Editor.exe`  
2. If Windows shows a message like *“Windows protected your PC”*, click  
   **More info → Run anyway**
3. The main window of the editor will open.

---

### 3. Basic usage

- **Information Tab:** Fill in author, category, difficulty, version, etc.  
- **Level Definition Tab:** Configure `LevelDefinition` — select stage, modules, and music.  
- **Objects Tab:** Add objects such as:
  - `ProtectThePlantChallengeProperties`
  - `SeedBankProperties`
  - `WaveManagerModuleProperties`
  - `SpawnZombiesJitteredWaveActionProps`
  - `GravestoneProperties`
  - `ZombiePotionModuleProperties`
  - `...`

Finally, click **Generate JSON** to export your level as a `.json` file.

> You can also open `.json5` files — the editor will automatically load and convert them.

---

## For Developers (run from source)

### 1. Install Python
Download and install **Python 3.11 or newer** from   [https://www.python.org/downloads/](https://www.python.org/downloads/)

Make sure to tick **“Add Python to PATH”** during installation.

---

### 2. Get the project
Clone it via Git or download and extract the ZIP:

```bash
git clone https://github.com/VuVietDung-bk/pvz-ge-level-editor.git
cd pvz-ge-level-editor
```

---

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

### 4. Run the app
```bash
python main.py
```

The editor will launch immediately.

---

### 5. Build as `.exe`
You can rebuild the executable using **PyInstaller** and the included build spec file:

```bash
pyinstaller ge_editor.spec
```

After building, your compiled app will be here:
```
dist/GE-Level-Editor/GE-Level-Editor.exe
```

You only need to distribute:
```
GE-Level-Editor.exe
game_data.json
```

---

## Project Structure

```
pvz-ge-level-editor/
│
├── editors/                # Object editor modules
├── game_data.json          # Internal game data (plants, zombies, etc.)
├── main.py                 # Main entry point
├── ge_editor.spec          # Build config for PyInstaller
├── info_tab.py             # Info tab (author, version, etc.)
├── leveldef_tab.py         # Level definition tab
├── objects_tab.py          # Objects editor tab
├── data_loader.py          # Loads global data
└── README.md               # This file
```

---

## Notes

- Always keep `game_data.json` in the same folder as the executable.  
- You can open and edit existing `.json` or `.json5` levels seamlessly.

---

## Build Output

| File | Description | Required |
|------|--------------|----------|
| `GE-Level-Editor.exe` | Main application | ✅ |
| `game_data.json` | Autocomplete data | ✅ |
| `ge_editor.spec` | Build config (for developers) | ❌ |
| `editors/` | Needed only for source version | ❌ |

---

## Credits

Created by **hinanarukami**  
Designed for the creative PvZ modding community

---

## Contact

For feedback or bug reports, please open a GitHub Issue or email:  
`vuvietdung20052005@gmail.com`
