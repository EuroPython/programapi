import json

from src.utils.parse import Parse
from src.utils.timing_relationships import TimingRelationships
from src.utils.transform import Transform

pretalx_submissions = Parse.publishable_submissions(
    "./data/examples/pretalx/submissions.json"
)

youtube_data = Parse.youtube("./data/examples/pretalx/youtube.json")


def test_e2e_sessions() -> None:
    TimingRelationships.compute(pretalx_submissions.values())

    ep_sessions = Transform.pretalx_submissions_to_europython_sessions(
        pretalx_submissions,
        youtube_data,
    )
    ep_sessions_dump = {
        k: json.loads(v.model_dump_json()) for k, v in ep_sessions.items()
    }

    with open("./data/examples/europython/sessions.json") as fd:
        ep_sessions_expected = json.load(fd)

    assert ep_sessions_dump == ep_sessions_expected


def test_e2e_speakers() -> None:
    pretalx_speakers = Parse.publishable_speakers(
        "./data/examples/pretalx/speakers.json", pretalx_submissions.keys()
    )
    ep_speakers = Transform.pretalx_speakers_to_europython_speakers(pretalx_speakers)
    ep_speakers_dump = {
        k: json.loads(v.model_dump_json()) for k, v in ep_speakers.items()
    }

    with open("./data/examples/europython/speakers.json") as fd:
        ep_speakers_expected = json.load(fd)

    assert ep_speakers_dump == ep_speakers_expected
