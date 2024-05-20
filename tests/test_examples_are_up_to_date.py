import json

from src.transform import PretalxSubmission

with open("./data/examples/pretalx/submissions.json") as fd:
    pretalx_submissions = json.load(fd)

with open("./data/examples/pretalx/speakers.json") as fd:
    pretalx_speakers = json.load(fd)


def test_sessions_example():
    assert pretalx_submissions[0]["code"] == "A8CD3F"
    pretalx = pretalx_submissions[0]
    pretalx["duration"] = str(pretalx["duration"])

    transformed = PretalxSubmission.model_validate(pretalx)

    with open("./data/examples/output/sessions.json") as fd:
        sessions = json.load(fd)

    assert transformed.model_dump() == sessions["A8CD3F"]
