import tomllib

with open("config.toml", "rb") as fd:
    conf = tomllib.load(fd)
