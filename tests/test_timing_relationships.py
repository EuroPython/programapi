from src.models.pretalx import PretalxSubmission
from src.utils.timing_relationships import TimingRelationships
from src.utils.transform import Transform
from src.utils.utils import Utils


def submission(
    code: str,
    start: str | None,
    end: str | None,
    room: str | None = "Room A",
    slots: list[dict] | None = None,
) -> PretalxSubmission:
    return PretalxSubmission.model_validate(
        {
            "code": code,
            "title": code,
            "speakers": [],
            "submission_type": "Talk",
            "state": "confirmed",
            "answers": [],
            "slot_count": len(slots) if slots else 1,
            "slots": slots
            if slots is not None
            else [{"room": room, "start": start, "end": end}],
        }
    )


def test_submission_uses_last_timed_slot_before_blank_placeholders() -> None:
    session = submission(
        "BTTFFJ",
        None,
        None,
        slots=[
            {
                "room": "Reception Room F2 (Fishbowl)",
                "start": "2026-07-14T09:30:00+02:00",
                "end": "2026-07-14T11:00:00+02:00",
            },
            {
                "room": "Reception Room F2 (Fishbowl)",
                "start": "2026-07-14T11:15:00+02:00",
                "end": "2026-07-14T12:45:00+02:00",
            },
            {"room": None, "start": None, "end": None},
            {"room": None, "start": None, "end": None},
        ],
    )

    assert session.room == "Reception Room F2 (Fishbowl)"
    assert session.start.isoformat() == "2026-07-14T09:30:00+02:00"
    assert session.end.isoformat() == "2026-07-14T12:45:00+02:00"


def test_timing_relationships_ignore_partial_sessions_and_reset_state() -> None:
    first = submission(
        "FIRST", "2026-07-14T09:30:00+02:00", "2026-07-14T10:30:00+02:00"
    )
    parallel = submission(
        "PARALLEL",
        "2026-07-14T10:00:00+02:00",
        "2026-07-14T11:00:00+02:00",
        room="Room B",
    )
    partial = submission("PARTIAL", "2026-07-14T10:15:00+02:00", None)

    TimingRelationships.compute([first, parallel, partial])

    assert TimingRelationships.get_sessions_in_parallel("FIRST") == ["PARALLEL"]
    assert TimingRelationships.get_sessions_in_parallel("PARTIAL") is None

    TimingRelationships.compute([partial])

    assert TimingRelationships.get_sessions_in_parallel("FIRST") is None


def test_schedule_start_times_use_only_scheduled_slots() -> None:
    session = submission(
        "BTTFFJ",
        None,
        None,
        slots=[
            {
                "room": "Reception Room F2 (Fishbowl)",
                "start": "2026-07-14T09:30:00+02:00",
                "end": "2026-07-14T11:00:00+02:00",
            },
            {
                "room": "Reception Room F2 (Fishbowl)",
                "start": "2026-07-14T11:15:00+02:00",
                "end": "2026-07-14T12:45:00+02:00",
            },
            {"room": None, "start": None, "end": None},
            {"room": None, "start": None, "end": None},
        ],
    )
    session.slot_count = 4

    TimingRelationships.compute([session])
    ep_session = Transform.pretalx_submissions_to_europython_sessions(
        {session.code: session}, {}
    )[session.code]

    assert [dt.isoformat() for dt in Utils.start_times(ep_session)] == [
        "2026-07-14T09:30:00+02:00",
        "2026-07-14T11:15:00+02:00",
    ]
