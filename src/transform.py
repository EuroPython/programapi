import json
import sys
from collections.abc import KeysView, ValuesView
from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator
from slugify import slugify

from src.config import Config


class SpeakerQuestion:
    affiliation = "Company / Organization / Educational Institution"
    homepage = "Social (Homepage)"
    twitter = "Social (X/Twitter)"
    mastodon = "Social (Mastodon)"
    linkedin = "Social (LinkedIn)"
    gitx = "Social (Github/Gitlab)"


class SubmissionQuestion:
    outline = "Outline"
    tweet = "Abstract as a tweet / toot"
    delivery = "My presentation can be delivered"
    level = "Expected audience expertise"


class SubmissionState(Enum):
    accepted = "accepted"
    confirmed = "confirmed"
    withdrawn = "withdrawn"
    rejected = "rejected"
    canceled = "canceled"
    submitted = "submitted"


class PretalxAnswer(BaseModel):
    question_text: str
    answer_text: str
    answer_file: str | None = None
    submission_id: str | None = None
    speaker_id: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract(cls, values) -> dict:
        values["question_text"] = values["question"]["question"]["en"]
        values["answer_text"] = values["answer"]
        values["answer_file"] = values["answer_file"]
        values["submission_id"] = values["submission"]
        values["speaker_id"] = values["person"]
        return values


class PretalxSlot(BaseModel):
    room: str | None = None
    start: datetime | None = None
    end: datetime | None = None

    @field_validator("room", mode="before")
    @classmethod
    def handle_localized(cls, v) -> str | None:
        if isinstance(v, dict):
            return v.get("en")
        return v


class PretalxSpeaker(BaseModel):
    """
    Model for Pretalx speaker data
    """

    code: str
    name: str
    biography: str | None = None
    avatar: str
    submissions: list[str]
    answers: list[PretalxAnswer]


class PretalxSubmission(BaseModel):
    """
    Model for Pretalx submission data
    """

    code: str
    title: str
    speakers: list[str]  # We only want the code, not the full info
    submission_type: str
    track: str | None = None
    state: SubmissionState
    abstract: str = ""
    duration: str = ""
    resources: list[dict[str, str]] | None = None
    answers: list[PretalxAnswer]
    slot: PretalxSlot | None = Field(..., exclude=True)

    # Extracted from slot data
    room: str | None = None
    start: datetime | None = None
    end: datetime | None = None

    @field_validator("submission_type", "track", mode="before")
    @classmethod
    def handle_localized(cls, v) -> str | None:
        if isinstance(v, dict):
            return v.get("en")
        return v

    @field_validator("duration", mode="before")
    @classmethod
    def duration_to_string(cls, v) -> str:
        if isinstance(v, int):
            return str(v)
        return v

    @field_validator("resources", mode="before")
    @classmethod
    def handle_resources(cls, v) -> list[dict[str, str]] | None:
        return v or None

    @model_validator(mode="before")
    @classmethod
    def process_values(cls, values) -> dict:
        values["speakers"] = sorted([s["code"] for s in values["speakers"]])

        # Set slot information
        if values.get("slot"):
            slot = PretalxSlot.model_validate(values["slot"])
            values["room"] = slot.room
            values["start"] = slot.start
            values["end"] = slot.end

        return values

    @property
    def is_publishable(self) -> bool:
        return self.state in (SubmissionState.accepted, SubmissionState.confirmed)


class EuroPythonSpeaker(BaseModel):
    """
    Model for EuroPython speaker data, transformed from Pretalx data
    """

    code: str
    name: str
    biography: str | None = None
    avatar: str
    slug: str
    answers: list[PretalxAnswer] = Field(..., exclude=True)
    submissions: list[str]

    # Extracted
    affiliation: str | None = None
    homepage: str | None = None
    twitter_url: str | None = None
    mastodon_url: str | None = None
    linkedin_url: str | None = None
    gitx: str | None = None

    @computed_field
    def website_url(self) -> str:
        return (
            f"https://ep{Config.event.split('-')[1]}.europython.eu/speaker/{self.slug}"
        )

    @model_validator(mode="before")
    @classmethod
    def extract_answers(cls, values) -> dict:
        answers = [PretalxAnswer.model_validate(ans) for ans in values["answers"]]

        for answer in answers:
            if answer.question_text == SpeakerQuestion.affiliation:
                values["affiliation"] = answer.answer_text

            if answer.question_text == SpeakerQuestion.homepage:
                values["homepage"] = answer.answer_text

            if answer.question_text == SpeakerQuestion.twitter:
                values["twitter_url"] = cls.extract_twitter_url(
                    answer.answer_text.strip().split()[0]
                )

            if answer.question_text == SpeakerQuestion.mastodon:
                values["mastodon_url"] = cls.extract_mastodon_url(
                    answer.answer_text.strip().split()[0]
                )

            if answer.question_text == SpeakerQuestion.linkedin:
                values["linkedin_url"] = cls.extract_linkedin_url(
                    answer.answer_text.strip().split()[0]
                )

            if answer.question_text == SpeakerQuestion.gitx:
                values["gitx"] = answer.answer_text.strip().split()[0]

        return values

    @staticmethod
    def extract_twitter_url(text: str) -> str:
        """
        Extract the Twitter URL from the answer
        """
        if text.startswith("@"):
            twitter_url = f"https://x.com/{text[1:]}"
        elif not text.startswith(("https://", "http://", "www.")):
            twitter_url = f"https://x.com/{text}"
        else:
            twitter_url = (
                f"https://{text.removeprefix('https://').removeprefix('http://')}"
            )

        return twitter_url.split("?")[0]

    @staticmethod
    def extract_mastodon_url(text: str) -> str:
        """
        Extract the Mastodon URL from the answer, handle @username@instance format
        """
        if not text.startswith(("https://", "http://")) and text.count("@") == 2:
            mastodon_url = f"https://{text.split('@')[2]}/@{text.split('@')[1]}"
        else:
            mastodon_url = (
                f"https://{text.removeprefix('https://').removeprefix('http://')}"
            )

        return mastodon_url.split("?")[0]

    @staticmethod
    def extract_linkedin_url(text: str) -> str:
        """
        Extract the LinkedIn URL from the answer
        """
        if text.startswith("in/"):
            linkedin_url = f"https://linkedin.com/{text}"
        elif not text.startswith(("https://", "http://", "www.")):
            linkedin_url = f"https://linkedin.com/in/{text}"
        else:
            linkedin_url = (
                f"https://{text.removeprefix('https://').removeprefix('http://')}"
            )

        return linkedin_url.split("?")[0]


class EuroPythonSession(BaseModel):
    """
    Model for EuroPython session data, transformed from Pretalx data
    """

    code: str
    title: str
    speakers: list[str]
    session_type: str
    slug: str
    track: str | None = None
    abstract: str = ""
    tweet: str = ""
    duration: str = ""
    level: str = ""
    delivery: str = ""
    resources: list[dict[str, str]] | None = None
    room: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    answers: list[PretalxAnswer] = Field(..., exclude=True)
    sessions_in_parallel: list[str] | None = None
    sessions_after: list[str] | None = None
    sessions_before: list[str] | None = None
    next_session: str | None = None
    prev_session: str | None = None

    @computed_field
    def website_url(self) -> str:
        return (
            f"https://ep{Config.event.split('-')[1]}.europython.eu/session/{self.slug}"
        )

    @model_validator(mode="before")
    @classmethod
    def extract_answers(cls, values) -> dict:
        answers = [PretalxAnswer.model_validate(ans) for ans in values["answers"]]

        for answer in answers:
            # TODO if we need any other questions
            if answer.question_text == SubmissionQuestion.tweet:
                values["tweet"] = answer.answer_text

            if answer.question_text == SubmissionQuestion.delivery:
                if "in-person" in answer.answer_text:
                    values["delivery"] = "in-person"
                else:
                    values["delivery"] = "remote"

            if answer.question_text == SubmissionQuestion.level:
                values["level"] = answer.answer_text.lower()

        return values


class Utils:
    @staticmethod
    def publishable_sessions_of_speaker(
        speaker: PretalxSpeaker, accepted_proposals: KeysView[str]
    ) -> set[str]:
        return set(speaker.submissions) & accepted_proposals

    @staticmethod
    def find_duplicate_attributes(
        objects: (
            dict[str, EuroPythonSession]
            | dict[str, EuroPythonSpeaker]
            | dict[str, PretalxSubmission]
            | dict[str, PretalxSpeaker]
        ),
        attributes: list[str],
    ) -> dict[str, list[str]]:
        """
        Find duplicates in the given objects based on the given attributes

        Returns: dict[attribute_value, list[object_code]]
        """
        duplicates: dict[str, list[str]] = {}
        for obj in objects.values():
            for attribute in attributes:
                value = getattr(obj, attribute)
                if value in duplicates:
                    duplicates[value].append(obj.code)
                else:
                    duplicates[value] = [obj.code]

        return duplicates

    @staticmethod
    def replace_duplicate_slugs(code_to_slug: dict[str, str]) -> dict[str, str]:
        slug_count: dict[str, int] = {}
        seen_slugs: set[str] = set()

        for code, slug in code_to_slug.items():
            original_slug = slug

            if original_slug in seen_slugs:
                if original_slug in slug_count:
                    slug_count[original_slug] += 1
                else:
                    slug_count[original_slug] = 1
                code_to_slug[code] = f"{original_slug}-{slug_count[original_slug]}"
            else:
                seen_slugs.add(original_slug)

        return code_to_slug

    @staticmethod
    def warn_duplicates(
        session_attributes_to_check: list[str],
        speaker_attributes_to_check: list[str],
        sessions_to_check: dict[str, EuroPythonSession] | dict[str, PretalxSubmission],
        speakers_to_check: dict[str, EuroPythonSpeaker] | dict[str, PretalxSpeaker],
    ) -> None:
        """
        Warns about duplicate attributes in the given objects
        """
        print(
            f"Checking for duplicate {'s, '.join(session_attributes_to_check)}s in sessions..."
        )
        duplicate_sessions = Utils.find_duplicate_attributes(
            sessions_to_check, session_attributes_to_check
        )

        for attribute, codes in duplicate_sessions.items():
            if len(codes) > 1:
                print(f"Duplicate ``{attribute}`` in sessions: {codes}")

        print(
            f"Checking for duplicate {'s, '.join(speaker_attributes_to_check)}s in speakers..."
        )
        duplicate_speakers = Utils.find_duplicate_attributes(
            speakers_to_check, speaker_attributes_to_check
        )

        for attribute, codes in duplicate_speakers.items():
            if len(codes) > 1:
                print(f"Duplicate ``{attribute}`` in speakers: {codes}")

    @staticmethod
    def compute_unique_slugs_by_attribute(
        objects: dict[str, PretalxSubmission] | dict[str, PretalxSpeaker],
        attribute: str,
    ) -> dict[str, str]:
        """
        Compute the slugs based on the given attribute
        and replace the duplicate slugs with incrementing
        numbers at the end.

        Returns: dict[code, slug]
        """
        object_code_to_slug = {}
        for obj in objects.values():
            object_code_to_slug[obj.code] = slugify(getattr(obj, attribute))

        return Utils.replace_duplicate_slugs(object_code_to_slug)

    @staticmethod
    def write_to_file(
        output_file: Path | str,
        data: dict[str, EuroPythonSession] | dict[str, EuroPythonSpeaker],
    ) -> None:
        with open(output_file, "w") as fd:
            json.dump(
                {k: json.loads(v.model_dump_json()) for k, v in data.items()},
                fd,
                indent=2,
            )


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
            speakers_with_publishable_sessions = [
                s
                for s in all_speakers
                if Utils.publishable_sessions_of_speaker(s, publishable_sessions_keys)
            ]
            publishable_speakers_by_code = {
                s.code: s for s in speakers_with_publishable_sessions
            }

        return publishable_speakers_by_code


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


if __name__ == "__main__":
    print(f"Parsing the data from {Config.raw_path}...")
    pretalx_submissions = Parse.publishable_submissions(
        Config.raw_path / "submissions_latest.json"
    )
    pretalx_speakers = Parse.publishable_speakers(
        Config.raw_path / "speakers_latest.json", pretalx_submissions.keys()
    )

    print("Computing timing relationships...")
    TimingRelationships.compute(pretalx_submissions.values())

    print("Transforming the data...")
    ep_sessions = Transform.pretalx_submissions_to_europython_sessions(
        pretalx_submissions
    )
    ep_speakers = Transform.pretalx_speakers_to_europython_speakers(pretalx_speakers)

    # Warn about duplicates if the flag is set
    if len(sys.argv) > 1 and sys.argv[1] == "--warn-dupes":
        Utils.warn_duplicates(
            session_attributes_to_check=["title"],
            speaker_attributes_to_check=["name"],
            sessions_to_check=ep_sessions,
            speakers_to_check=ep_speakers,
        )

    print(f"Writing the data to {Config.public_path}...")
    Utils.write_to_file(Config.public_path / "sessions.json", ep_sessions)
    Utils.write_to_file(Config.public_path / "speakers.json", ep_speakers)
