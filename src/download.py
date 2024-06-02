import json
from typing import Any

import requests
from tqdm import tqdm

from src.config import Config

headers = {
    "Accept": "application/json, text/javascript",
    "Authorization": f"Token {Config.token()}",
}

base_url = f"https://pretalx.com/api/events/{Config.event}/"

resources = [
    # Questions need to be passed to include answers in the same endpoint,
    # saving us later time with joining the answers.
    "submissions?questions=all",
    "speakers?questions=all",
]

Config.raw_path.mkdir(parents=True, exist_ok=True)

for resource in resources:
    url = base_url + f"{resource}"

    res0: list[dict[str, Any]] = []
    data: dict[str, Any] = {"next": url}
    n = 0

    pbar = tqdm(desc=f"Downloading {resource}", unit=" page", dynamic_ncols=True)

    while url := data["next"]:
        n += 1
        pbar.update(1)
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")

        data = response.json()
        res0 += data["results"]

    pbar.close()

    filename = resource.split("?")[0]  # To get rid of "?questions"
    filename = f"{filename}_latest.json"
    filepath = Config.raw_path / filename

    with open(filepath, "w") as fd:
        json.dump(res0, fd)
