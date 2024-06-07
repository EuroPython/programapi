from collections.abc import ValuesView

from src.models.pretalx import PretalxSubmission


class TimingRelationships:
    all_sessions_in_parallel: dict[str, list[str]] = {}
    all_sessions_after: dict[str, list[str]] = {}
    all_sessions_before: dict[str, list[str]] = {}
    all_next_session: dict[str, str | None] = {}
    all_prev_session: dict[str, str | None] = {}

    @classmethod
    def compute(
        cls, all_sessions: ValuesView[PretalxSubmission] | list[PretalxSubmission]
    ) -> None:
        for session in all_sessions:
            if not session.start or not session.end:
                continue

            sessions_in_parallel = cls.compute_sessions_in_parallel(
                session, all_sessions
            )
            sessions_after = cls.compute_sessions_after(
                session, all_sessions, sessions_in_parallel
            )
            sessions_before = cls.compute_sessions_before(
                session, all_sessions, sessions_in_parallel
            )

            cls.all_sessions_in_parallel[session.code] = sessions_in_parallel
            cls.all_sessions_after[session.code] = sessions_after
            cls.all_sessions_before[session.code] = sessions_before
            cls.all_next_session[session.code] = cls.compute_prev_or_next_session(
                session, sessions_after, all_sessions
            )
            cls.all_prev_session[session.code] = cls.compute_prev_or_next_session(
                session, sessions_before, all_sessions
            )

    @classmethod
    def get_sessions_in_parallel(
        cls, session_code: str | None = None
    ) -> list[str] | None:
        return cls.all_sessions_in_parallel.get(session_code)

    @classmethod
    def get_sessions_after(cls, session_code: str | None = None) -> list[str] | None:
        return cls.all_sessions_after.get(session_code)

    @classmethod
    def get_sessions_before(cls, session_code: str | None = None) -> list[str] | None:
        return cls.all_sessions_before.get(session_code)

    @classmethod
    def get_next_session(cls, session_code: str | None = None) -> str | None:
        return cls.all_next_session.get(session_code)

    @classmethod
    def get_prev_session(cls, session_code: str | None = None) -> str | None:
        return cls.all_prev_session.get(session_code)

    @staticmethod
    def compute_sessions_in_parallel(
        session: PretalxSubmission,
        all_sessions: ValuesView[PretalxSubmission] | list[PretalxSubmission],
    ) -> list[str]:
        sessions_parallel = []
        for other_session in all_sessions:
            if (
                other_session.code == session.code
                or other_session.start is None
                or session.start is None
            ):
                continue

            # If they intersect, they are in parallel
            if other_session.start < session.end and other_session.end > session.start:
                sessions_parallel.append(other_session.code)

        return sessions_parallel

    @staticmethod
    def compute_sessions_after(
        session: PretalxSubmission,
        all_sessions: ValuesView[PretalxSubmission] | list[PretalxSubmission],
        sessions_in_parallel: list[str],
    ) -> list[str]:
        # Sort sessions based on start time, early first
        all_sessions_sorted = sorted(
            all_sessions, key=lambda x: (x.start is None, x.start)
        )

        # Filter out sessions
        remaining_sessions = [
            other_session
            for other_session in all_sessions_sorted
            if other_session.start is not None
            and other_session.start >= session.end
            and other_session.code not in sessions_in_parallel
            and other_session.code != session.code
            and other_session.start.day == session.start.day
            and not other_session.submission_type
            == session.submission_type
            == "Announcements"
        ]

        # Add sessions to the list if they are in different rooms
        seen_rooms = set()
        unique_sessions: list[PretalxSubmission] = []

        for other_session in remaining_sessions:
            if other_session.room not in seen_rooms:
                unique_sessions.append(other_session)
                seen_rooms.add(other_session.room)

        # If there is a keynote next, only show that
        if any(s.submission_type == "Keynote" for s in unique_sessions):
            unique_sessions = [
                s for s in unique_sessions if s.submission_type == "Keynote"
            ]

        # Set the next sessions in all rooms
        sessions_after = [s.code for s in unique_sessions]

        return sessions_after

    @staticmethod
    def compute_sessions_before(
        session: PretalxSubmission,
        all_sessions: ValuesView[PretalxSubmission] | list[PretalxSubmission],
        sessions_in_parallel: list[str],
    ) -> list[str]:
        # Sort sessions based on start time, late first
        all_sessions_sorted = sorted(
            all_sessions,
            key=lambda x: (x.start is None, x.start),
            reverse=True,
        )

        remaining_sessions = [
            other_session
            for other_session in all_sessions_sorted
            if other_session.start is not None
            and other_session.code not in sessions_in_parallel
            and other_session.start <= session.start
            and other_session.code != session.code
            and other_session.start.day == session.start.day
            and other_session.submission_type != "Announcements"
        ]

        seen_rooms = set()
        unique_sessions: list[PretalxSubmission] = []

        for other_session in remaining_sessions:
            if other_session.room not in seen_rooms:
                unique_sessions.append(other_session)
                seen_rooms.add(other_session.room)

        sessions_before = [session.code for session in unique_sessions]

        return sessions_before

    @staticmethod
    def compute_prev_or_next_session(
        session: PretalxSubmission,
        sessions_before_or_after: list[str],
        all_sessions: ValuesView[PretalxSubmission] | list[PretalxSubmission],
    ) -> str | None:
        """
        Compute next_session or prev_session based on the given sessions_before_or_after.
        If passed sessions_before, it will return prev_session.
        If passed sessions_after, it will return next_session.

        Returns the previous or next session in the same room or a keynote.
        """
        if not sessions_before_or_after:
            return None

        sessions_before_or_after_object = [
            s for s in all_sessions if s.code in sessions_before_or_after
        ]

        session_in_same_room = None
        for other_session in sessions_before_or_after_object:
            if (
                other_session.room == session.room
                or other_session.submission_type == "Keynote"
            ):
                session_in_same_room = other_session.code
                break

        return session_in_same_room
