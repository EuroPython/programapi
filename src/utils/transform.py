from src.models.europython import EuroPythonSession, EuroPythonSpeaker
from src.models.pretalx import PretalxSpeaker, PretalxSubmission
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

        sessions = {}
        for code, submission in submissions.items():
            session = EuroPythonSession(
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
            )
            sessions[code] = session

        return sessions

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

        euro_python_speakers = {}
        for code, speaker in speakers.items():
            euro_python_speaker = EuroPythonSpeaker(
                code=speaker.code,
                name=speaker.name,
                biography=speaker.biography,
                avatar=speaker.avatar,
                slug=speaker_code_to_slug[speaker.code],
                answers=speaker.answers,
                submissions=speaker.submissions,
            )
            euro_python_speakers[code] = euro_python_speaker

        return euro_python_speakers
