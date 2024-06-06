import json
from collections.abc import KeysView
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


if __name__ == "__main__":
    print("Checking for duplicate slugs...")
    assert len(set(s.slug for s in publishable_submissions().values())) == len(
        publishable_submissions()
    )
    print("Saving publishable data...")
    save_publishable_sessions()
    save_publishable_speakers()
    print("Done")
