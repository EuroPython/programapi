import os
from pathlib import Path

from dotenv import load_dotenv


class Config:
    event = "pyladiescon-2025"
    event_dir_name = "plc25"
    api_version = "v1"

    project_root = Path(__file__).resolve().parents[1]
    raw_path = Path(f"{project_root}/data/raw/{event_dir_name}")
    public_path = Path(f"{project_root}/data/public/{event_dir_name}")

    @classmethod
    def token(cls) -> str:
        dotenv_exists = load_dotenv(cls.project_root / ".env")
        if (token := os.getenv("PRETALX_TOKEN")) and not dotenv_exists:
            print("Please prefer .env file to store your token! It's more secure!")
            return token
        elif token is None:
            raise ValueError("Please set your token in .env file!")
        return token
