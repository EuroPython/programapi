import json
from argparse import ArgumentParser
from typing import Any

import requests
from tqdm import tqdm

from src.config import Config

parser = ArgumentParser(description="Download Pretalx data for EuroPython processing.")
parser.add_argument(
    "-e",
    "--exclude",
    choices=["schedule", "youtube"],
    action="append",
    help="Exclude certain resources from download.",
)
args = parser.parse_args()
exclude = set(args.exclude or [])

headers = {
    "Accept": "application/json, text/javascript",
    "Authorization": f"Token {Config.token()}",
    "Pretalx-Version": Config.api_version,
}

base_url = f"https://pretalx.com/api/events/{Config.event}/"
schedule_url = (
    base_url
    + "schedules/latest?expand="
    + "slots,slots.submission,slots.submission.submission_type,slots.submission.track,slots.room"
)

# Build resource list dynamically based on exclusions
resources = [
    "submissions?state=confirmed&expand=answers.question,submission_type,track,slots.room",
    "speakers?expand=answers.question",
]

if "youtube" not in exclude:
    resources.append("p/youtube")

Config.raw_path.mkdir(parents=True, exist_ok=True)

for resource in resources:
    # To get the resource name without extra parameters
    resource_name = resource.split("?")[0].split("/")[-1]
    url = base_url + resource

    res0: list[dict[str, Any]] = []
    data: dict[str, Any] = {"next": url}
    n = 0

    pbar = tqdm(desc=f"Downloading {resource_name}", unit=" page", dynamic_ncols=True)

    while url := data["next"]:
        n += 1
        pbar.update(1)
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")

        data = response.json()
        res0 += data["results"]

    pbar.close()

    # Save the data to a file
    filename = f"{resource_name}_latest.json"
    filepath = Config.raw_path / filename

    with open(filepath, "w") as fd:
        json.dump(res0, fd)

# Download schedule unless excluded
if "schedule" not in exclude:
    print("Downloading schedule...", end="")
    response = requests.get(schedule_url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    data = response.json()
    filename = "schedule_latest.json"
    filepath = Config.raw_path / filename

    with open(filepath, "w") as fd:
        json.dump(data, fd)
    print(" done.")
