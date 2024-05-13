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
    "submissions",
    "speakers",
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

    fnames = [
        f"../data/raw/{Config.event}/{resource}_latest.json",
    ]
    for fname in fnames:
        with open(fname, "w") as fd:
            json.dump(res0, fd)
