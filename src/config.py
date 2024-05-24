import os
from pathlib import Path


class Config:
    event = "europython-2023"
    project_root = Path(__file__).resolve().parents[1]
    raw_path = Path(f"{project_root}/data/raw/{event}")
    public_path = Path(f"{project_root}/data/public/{event}")

    @staticmethod
    def token():
        return os.environ["PRETALX_TOKEN"]
