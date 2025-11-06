import json
import os


class GameData:
    _data = None

    @classmethod
    def load(cls, path="game_data.json"):
        if cls._data is None:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Cannot find {path}")
            with open(path, "r", encoding="utf-8") as f:
                cls._data = json.load(f)
        return cls._data

    @classmethod
    def get(cls, key):
        data = cls.load()
        return data.get(key, {})

    @classmethod
    def get_flat_list(cls, section):
        """Flatten nested section (like Zombies / Plants) into a single list of codes."""
        data = cls.get(section)
        codes = []
        if isinstance(data, dict):
            for sub, entries in data.items():
                for e in entries:
                    codes.append(e["code"])
        elif isinstance(data, list):
            for e in data:
                codes.append(e["code"])
        return sorted(set(codes))