import os

# with open("config.toml", "rb") as fd:
#     conf = tomllib.load(fd)

conf = {
    "pretalx-token": os.environ["PRETALX_TOKEN"],
}
