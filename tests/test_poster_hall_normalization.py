from datetime import datetime

import pytest

from src.misc import Room
from src.models.europython import EuroPythonScheduleBreak, EuroPythonSession

POSTER_HALLS = ["Poster Hall A", "Poster Hall B", "Poster Hall C"]


def _session(room: str) -> EuroPythonSession:
    return EuroPythonSession.model_validate(
        {
            "code": "TEST",
            "title": "Test",
            "speakers": [],
            "session_type": "Talk",
            "slug": "test",
            "answers": [],
            "slot_count": 1,
            "room": room,
        }
    )


def _break(rooms: list[str]) -> EuroPythonScheduleBreak:
    return EuroPythonScheduleBreak(
        title="Break",
        duration=30,
        rooms=rooms,
        start=datetime(2026, 7, 14, 10, 0),
    )


@pytest.mark.parametrize("poster_hall", POSTER_HALLS)
def test_session_poster_hall_becomes_exhibit_hall(poster_hall: str) -> None:
    assert _session(poster_hall).room == "Exhibit Hall"


def test_break_poster_halls_become_exhibit_hall() -> None:
    brk = _break(POSTER_HALLS)
    assert all(r == Room.exhibit_hall for r in brk.rooms)
