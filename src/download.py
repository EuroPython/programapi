import json
from datetime import datetime
from pathlib import Path
from pprint import pprint as pp

import requests

from config import conf


class Config:
    token = conf["pretalx-token"]
    event = "europython-2024"


headers = {
    "Accept": "application/json, text/javascript",
    "Authorization": f"Token {Config.token}",
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
        data = response.json()
        res0 += data["results"]

    filename = resource.split("?")[0]  # To get rid of "?questions"
    filename = f"{filename}_latest.json"
    filepath = f"../data/raw/{Config.event}/{filename}"

    with open(filepath, "w") as fd:
        json.dump(res0, fd)
