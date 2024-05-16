import json
from transform import PretalxSubmission

with open("./data/examples/pretalx/submissions.json") as fd:
    pretalx_submissions = json.load(fd)

with open("./data/examples/pretalx/speakers.json") as fd:
    pretalx_speakers = json.load(fd)


def test_sessions_example():
    assert pretalx_submissions[0]["code"] == "A8CD3F"
    pretalx = pretalx_submissions[0]

    transformed = PretalxSubmission.parse_obj(pretalx)

    with open("./data/examples/output/sessions.json") as fd:
        sessions = json.load(fd)

    assert transformed.dict() == sessions["A8CD3F"]
