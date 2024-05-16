import json
from pathlib import Path

import requests

try:
    from config import Config
except ImportError:
    from src.config import Config


headers = {
    "Accept": "application/json, text/javascript",
    "Authorization": f"Token {Config.token()}",
}

base_url = f"https://pretalx.com/api/events/{Config.event}/"

resources = [
    # Questions needs to be passed to include answers in the same endpoint,
    # saving us later time with joining the answers.
    "submissions?questions=all",
    "speakers?questions=all",
]

for resource in resources:
    print("Downloading: ", resource)
    url = base_url + f"{resource}"

    res0 = []
    data = {"next": url}
    n = 0

    while url := data["next"]:
        n += 1
        print(f"Page {n}")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")
        
        data = response.json()
        res0 += data["results"]

    filename = resource.split("?")[0]  # To get rid of "?questions"
    filename = f"{filename}_latest.json"
    filepath = Path.joinpath(Config.raw_path, filename)

    with open(filepath, "w") as fd:
        json.dump(res0, fd)
