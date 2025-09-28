from pathlib import Path
import json, time

class State:
    def __init__(self, root: Path):
        self.root = root
        self.version = 0
        self.updated_at = None
        self.cache = {
            "hazard": None,
            "demand": None,
            "transport": None,
            "shelter": None,
            "resources": None,
            "equity": None,
            "comms": None,
            "plan": None,
            "event": None
        }

    def set_all(self, d: dict):
        for k in self.cache.keys():
            self.cache[k] = d.get(k)
        self.version += 1
        self.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")
        for k, v in self.cache.items():
            if v is not None:
                (self.root / f"{k}.json").write_text(json.dumps(v))

    def snapshot(self):
        s = {**self.cache}
        s["version"] = self.version
        s["updatedAt"] = self.updated_at
        return s
