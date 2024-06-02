import json

from src.transform import PretalxSession, PretalxSpeaker

with open("./data/examples/pretalx/submissions.json") as fd:
    pretalx_submissions = json.load(fd)

with open("./data/examples/pretalx/speakers.json") as fd:
    pretalx_speakers = json.load(fd)


def test_sessions_example():
    assert pretalx_submissions[0]["code"] == "A8CD3F"
    pretalx = pretalx_submissions[0]

    transformed = PretalxSession.model_validate(pretalx)

    with open("./data/examples/output/sessions.json") as fd:
        sessions = json.load(fd)

    assert transformed.model_dump() == sessions["A8CD3F"]


def test_speakers_example():
    assert pretalx_speakers[0]["code"] == "F3DC8A"
    pretalx = pretalx_speakers[0]

    transformed = PretalxSpeaker.model_validate(pretalx)

    with open("./data/examples/output/speakers.json") as fd:
        speakers = json.load(fd)

    assert transformed.model_dump() == speakers["F3DC8A"]
