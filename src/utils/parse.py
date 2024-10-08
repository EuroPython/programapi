import json
from collections.abc import KeysView
from pathlib import Path

from src.models.pretalx import PretalxSchedule, PretalxSpeaker, PretalxSubmission
from src.utils.utils import Utils


class Parse:
    @staticmethod
    def publishable_submissions(input_file: Path | str) -> dict[str, PretalxSubmission]:
        """
        Returns only publishable submissions
        """
        with open(input_file) as fd:
            js = json.load(fd)
            all_submissions = [PretalxSubmission.model_validate(s) for s in js]
            publishable_submissions = [s for s in all_submissions if s.is_publishable]
            publishable_submissions_by_code = {
                s.code: s for s in publishable_submissions
            }

        return publishable_submissions_by_code

    @staticmethod
    def publishable_speakers(
        input_file: Path | str,
        publishable_sessions_keys: KeysView[str],
    ) -> dict[str, PretalxSpeaker]:
        """
        Returns only speakers with publishable sessions
        """
        with open(input_file) as fd:
            js = json.load(fd)
            all_speakers = [PretalxSpeaker.model_validate(s) for s in js]

            speakers_with_publishable_sessions: list[PretalxSubmission] = []
            for speaker in all_speakers:
                if publishable_sessions := Utils.publishable_sessions_of_speaker(
                    speaker, publishable_sessions_keys
                ):
                    speaker.submissions = publishable_sessions
                    speakers_with_publishable_sessions.append(speaker)

            publishable_speakers_by_code = {
                s.code: s for s in speakers_with_publishable_sessions
            }

        return publishable_speakers_by_code

    @staticmethod
    def schedule(input_file: Path | str) -> PretalxSchedule:
        """
        Returns the schedule:

        PretalxSchedule.slots: list[PretalxSubmission]
        PretalxSchedule.breaks: list[PretalxScheduleBreak]
        """
        with open(input_file) as fd:
            js = json.load(fd)
            schedule = PretalxSchedule.model_validate(js)

        return schedule

    @staticmethod
    def youtube(input_file: Path | str) -> dict[str, str]:
        """
        Returns the Session code to YouTube URL mapping
        """
        with open(input_file) as fd:
            js = json.load(fd)
            youtube_data = {s["submission"]: s["youtube_link"] for s in js}

        return youtube_data
