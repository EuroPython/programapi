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
schedule_url = base_url + "schedules/latest/"

resources = [
    # Questions need to be passed to include answers in the same endpoint,
    # saving us later time with joining the answers.
    "submissions?questions=all&state=confirmed",
    "speakers?questions=all",
    "p/youtube",
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

    # To get the resource name without extra parameters
    filename = resource.split("?")[0].split("/")[-1]
    filename = f"{filename}_latest.json"
    filepath = Config.raw_path / filename

    with open(filepath, "w") as fd:
        json.dump(res0, fd)


# Download schedule
response = requests.get(schedule_url, headers=headers)

if response.status_code != 200:
    raise Exception(f"Error {response.status_code}: {response.text}")

data = response.json()
filename = "schedule_latest.json"
filepath = Config.raw_path / filename

with open(filepath, "w") as fd:
    json.dump(data, fd)
