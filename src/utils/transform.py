from src.models.europython import (
    EuroPythonScheduleBreak,
    EuroPythonScheduleSession,
    EuroPythonScheduleSpeaker,
    EuroPythonSession,
    EuroPythonSpeaker,
    Schedule,
)
from src.models.pretalx import PretalxScheduleBreak, PretalxSpeaker, PretalxSubmission
from src.utils.timing_relationships import TimingRelationships
from src.utils.utils import Utils


class Transform:
    @staticmethod
    def pretalx_submissions_to_europython_sessions(
        submissions: dict[str, PretalxSubmission],
    ) -> dict[str, EuroPythonSession]:
        """
        Transforms the given Pretalx submissions to EuroPython sessions
        """
        # Sort the submissions based on start time for deterministic slug computation
        submissions = {
            k: v
            for k, v in sorted(
                submissions.items(),
                key=lambda item: (item[1].start is None, item[1].start),
            )
        }

        session_code_to_slug = Utils.compute_unique_slugs_by_attribute(
            submissions, "title"
        )

        ep_sessions = {}
        for code, submission in submissions.items():
            ep_session = EuroPythonSession(
                code=submission.code,
                title=submission.title,
                speakers=submission.speakers,
                session_type=submission.submission_type,
                slug=session_code_to_slug[submission.code],
                track=submission.track,
                abstract=submission.abstract,
                duration=submission.duration,
                resources=submission.resources,
                room=submission.room,
                start=submission.start,
                end=submission.end,
                answers=submission.answers,
                sessions_in_parallel=TimingRelationships.get_sessions_in_parallel(
                    submission.code
                ),
                sessions_after=TimingRelationships.get_sessions_after(submission.code),
                sessions_before=TimingRelationships.get_sessions_before(
                    submission.code
                ),
                next_session=TimingRelationships.get_next_session(submission.code),
                prev_session=TimingRelationships.get_prev_session(submission.code),
                slot_count=submission.slot_count,
            )
            ep_sessions[code] = ep_session

        return ep_sessions

    @staticmethod
    def pretalx_speakers_to_europython_speakers(
        speakers: dict[str, PretalxSpeaker],
    ) -> dict[str, EuroPythonSpeaker]:
        """
        Transforms the given Pretalx speakers to EuroPython speakers
        """
        # Sort the speakers based on code for deterministic slug computation
        speakers = {k: v for k, v in sorted(speakers.items(), key=lambda item: item[0])}

        speaker_code_to_slug = Utils.compute_unique_slugs_by_attribute(speakers, "name")

        ep_speakers = {}
        for code, speaker in speakers.items():
            ep_speaker = EuroPythonSpeaker(
                code=speaker.code,
                name=speaker.name,
                biography=speaker.biography,
                avatar=speaker.avatar,
                slug=speaker_code_to_slug[speaker.code],
                answers=speaker.answers,
                submissions=speaker.submissions,
            )
            ep_speakers[code] = ep_speaker

        return ep_speakers

    @staticmethod
    def pretalx_schedule_to_europython_schedule(
        breaks: list[PretalxScheduleBreak],
        ep_sessions: dict[str, EuroPythonSession],
        ep_speakers: dict[str, EuroPythonSpeaker],
    ) -> Schedule:
        """
        Transforms the given Pretalx schedule to EuroPython schedule
        """

        # Merge breaks with the same start and end times
        breaks = Utils.merge_breaks(breaks)
        ep_breaks = []
        for title, duration, rooms, start in breaks:
            ep_break = EuroPythonScheduleBreak(
                title=title,
                duration=duration,
                rooms=rooms,
                start=start,
            )
            ep_breaks.append(ep_break)

        # Split the sessions that covers multiple slots
        ep_schedule_sessions_split = []
        for session in ep_sessions.values():
            # Skip the sessions that are not assigned in the schedule
            if not session.start or not session.room:
                continue
            start_times = Utils.start_times(session)
            for start_time in start_times:
                ep_schedule_session = EuroPythonScheduleSession(
                    code=session.code,
                    slug=session.slug,
                    title=session.title,
                    session_type=session.session_type,
                    speakers=[
                        EuroPythonScheduleSpeaker(
                            code=speaker_code,
                            name=ep_speakers[speaker_code].name,
                            avatar=ep_speakers[speaker_code].avatar,
                            slug=ep_speakers[speaker_code].slug,
                            website_url=ep_speakers[speaker_code].website_url,
                        )
                        for speaker_code in session.speakers
                    ],
                    tweet=session.tweet,
                    level=session.level,
                    total_duration=int(session.duration),
                    rooms=[session.room],
                    start=start_time,
                    website_url=session.website_url,
                    slot_count=session.slot_count,
                )

                ep_schedule_sessions_split.append(ep_schedule_session)

        return Schedule.from_events(ep_breaks + ep_schedule_sessions_split)
