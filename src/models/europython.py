from __future__ import annotations

import re
from datetime import date, datetime
from urllib.parse import quote

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

from src.config import Config
from src.misc import EventType, Room, SpeakerQuestion, SubmissionQuestion
from src.models.pretalx import PretalxAnswer


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
    occupation: str | None = None
    homepage: str | None = None
    twitter_url: str | None = None
    mastodon_url: str | None = None
    linkedin_url: str | None = None
    bluesky_url: str | None = None
    gitx_url: str | None = None
    instagram_url: str | None = None
    timezone: str | None = None

    @computed_field
    def website_url(self) -> str:
        return f"https://{Config.event.split('-')[1]}.conference.pyladies.com/speaker/{self.slug}"

    @model_validator(mode="before")
    @classmethod
    def extract_answers(cls, values) -> dict:
        answers = [PretalxAnswer.model_validate(ans) for ans in values["answers"]]

        for answer in answers:
            if answer.question_text == SpeakerQuestion.affiliation:
                values["affiliation"] = answer.answer_text

            if answer.question_text == SpeakerQuestion.occupation:
                values["occupation"] = answer.answer_text

            if answer.question_text == SpeakerQuestion.homepage:
                values["homepage"] = answer.answer_text

            if answer.question_text == SpeakerQuestion.twitter:
                values["twitter_url"] = cls.extract_twitter_url(answer.answer_text)

            if answer.question_text == SpeakerQuestion.mastodon:
                values["mastodon_url"] = cls.extract_mastodon_url(answer.answer_text)

            if answer.question_text == SpeakerQuestion.bluesky:
                values["bluesky_url"] = cls.extract_bluesky_url(answer.answer_text)

            if answer.question_text == SpeakerQuestion.linkedin:
                values["linkedin_url"] = cls.extract_linkedin_url(answer.answer_text)

            if answer.question_text == SpeakerQuestion.gitx:
                values["gitx_url"] = cls.extract_gitx_url(answer.answer_text)

            if answer.question_text == SpeakerQuestion.instagram:
                values["instagram_url"] = cls.extract_instagram_url(answer.answer_text)

            if answer.question_text == SpeakerQuestion.timezone:
                values["timezone"] = answer.answer_text

        return values

    @staticmethod
    def extract_twitter_url(text: str) -> str | None:
        """
        Extracts a Twitter profile URL from the given text.
        Cleans the input and handles following formats:
        - @username
        - username
        - twitter.com/username
        - x.com/username
        """
        cleaned = EuroPythonSpeaker._clean_social_input(text)
        if cleaned is None:
            print(f"Invalid Twitter URL: {text}")
            return None

        # https://twitter.com/username (username max 15 chars)
        match = re.match(r"^(twitter\.com|x\.com)/([\w]{1,15})$", cleaned)
        if match:
            _, username = match.groups()
            return f"https://x.com/{username}"

        # only username
        if re.match(r"^[\w]{1,15}$", cleaned):
            return f"https://x.com/{cleaned}"

        print(f"Invalid Twitter URL: {cleaned}")
        return None

    @staticmethod
    def extract_mastodon_url(text: str) -> str | None:
        """
        Extracts a Mastodon profile URL from the given text.
        Supports formats like:
        - @username@instance
        - username@instance
        - instance/@username
        - instance/@username@instance (with redirect)
        Returns: https://<instance>/@<username>
        """
        cleaned = EuroPythonSpeaker._clean_social_input(text)
        if not cleaned:
            print(f"Invalid Mastodon URL: {text}")
            return None

        # instance/@username
        match = re.match(r"^([\w\.-]+)/@([\w\.-]+)$", cleaned)
        if match:
            instance, username = match.groups()
            return f"https://{instance}/@{username}"

        parts = cleaned.split("@")
        if len(parts) == 3:  # instance@username@instance
            _, username, instance = parts
        elif len(parts) == 2:  # username@instance
            username, instance = parts
        else:
            print(f"Invalid Mastodon URL: {cleaned}")
            return None

        if username and instance:
            return f"https://{instance}/@{username}"

        print(f"Invalid Mastodon URL: {cleaned}")
        return None

    @staticmethod
    def extract_linkedin_url(text: str) -> str | None:
        """
        Extracts a LinkedIn personal profile URL from the given text.
        Cleans the input and handles formats like:
        - username
        - linkedin.com/in/username
        - @username
        - tr.linkedin.com/in/username (country subdomains)
        """
        cleaned = EuroPythonSpeaker._clean_social_input(text)
        if cleaned is None:
            print(f"Invalid LinkedIn URL: {text}")
            return None

        if cleaned.startswith("in/"):
            linkedin_url = f"https://linkedin.com/{cleaned}"
        elif not cleaned.startswith(("linkedin.", "in/")) and "." not in cleaned:
            linkedin_url = f"https://linkedin.com/in/{cleaned}"
        else:
            linkedin_url = f"https://{cleaned}"

        if not re.match(
            r"^https://([\w-]+\.)?linkedin\.com/in/(?:[\w\-]|%[0-9A-Fa-f]{2})+(?:/[\w\-]+)*$",
            linkedin_url,
        ):
            print(f"Invalid LinkedIn URL: {linkedin_url}")
            return None

        return linkedin_url

    @staticmethod
    def extract_bluesky_url(text: str) -> str | None:
        """
        Extracts a Bluesky profile URL from the given text.
        Cleans the input and handles formats like:
        - username
        - bsky.app/profile/username
        - bsky/username
        - username.dev
        - @username
        - username.bsky.social
        """
        cleaned = EuroPythonSpeaker._clean_social_input(text)
        if cleaned is None:
            print(f"Invalid Bluesky URL: {text}")
            return None

        for marker in ("bsky.app/profile/", "bsky/"):
            if marker in cleaned:
                cleaned = cleaned.split(marker, 1)[1]
                break
        else:
            cleaned = cleaned.rsplit("/", 1)[-1]

        if "." not in cleaned:
            cleaned += ".bsky.social"

        bluesky_url = f"https://bsky.app/profile/{cleaned}"

        if not re.match(r"^https://bsky\.app/profile/[\w\.-]+\.[\w\.-]+$", bluesky_url):
            print(f"Invalid Bluesky URL: {bluesky_url}")
            return None

        return bluesky_url

    @staticmethod
    def extract_gitx_url(text: str) -> str | None:
        """
        Extracts a GitHub/GitLab URL from the given text.
        Cleans the input and handles formats like:
        - username
        - github.com/username
        - gitlab.com/username
        - @username
        """
        cleaned = EuroPythonSpeaker._clean_social_input(text)
        if cleaned is None:
            print(f"Invalid GitHub/GitLab URL: {text}")
            return None

        if cleaned.startswith(("github.com/", "gitlab.com/")):
            return f"https://{cleaned}"

        if re.match(r"^[\w-]+$", cleaned):  # assume github.com
            return f"https://github.com/{cleaned}"

        print(f"Invalid GitHub/GitLab URL: {cleaned}")
        return None

    @staticmethod
    def extract_instagram_url(text: str) -> str | None:
        """
        Extracts an Instagram profile URL from the given text.
        Cleans the input and handles following formats:
        - @username
        - username
        - instagram.com/username
        """
        cleaned = EuroPythonSpeaker._clean_social_input(text)
        if cleaned is None:
            print(f"Invalid Instagram URL: {text}")
            return None

        # https://instagram.com/username (username max 30 chars)
        match = re.match(r"^instagram\.com/([\w\.]{1,30})$", cleaned)
        if match:
            username = match.groups()[0]
            return f"https://instagram.com/{username}"

        # only username
        if re.match(r"^[\w\.]{1,30}$", cleaned):
            return f"https://instagram.com/{cleaned}"

        print(f"Invalid Instagram URL: {cleaned}")
        return None

    @staticmethod
    def _is_blank_or_na(text: str) -> bool:
        """
        Check if the text is blank or (equals "N/A" or "-")
        """
        return not text or text.strip().lower() in {"n/a", "-"}

    @staticmethod
    def _clean_social_input(text: str) -> str | None:
        """
        Cleans the input string for social media URLs.
        Returns None if the input is blank or "N/A",
        removes prefixes like "LinkedIn: " or "GH: ",
        removes parameters like "?something=true",
        removes trailing slashes,
        removes "http://" or "https://",
        removes "www." prefix,
        removes "@" prefix,
        removes invisible Unicode control characters,
        and decodes URL-encoded characters.
        """
        if EuroPythonSpeaker._is_blank_or_na(text):
            print(f"Blank or N/A input: {text}")
            return None

        # Strip leading/trailing whitespace
        text = text.strip()

        # Remove any text prefix like "LinkedIn: " or "GH: "
        text = text.split(" ", 1)[1] if ": " in text else text

        # Remove query strings and trailing commas or slashes
        text = text.split("?", 1)[0]
        text = text.split(",", 1)[0]
        text = text.rstrip("/")

        # Remove URL schemes
        if text.startswith("https://"):
            text = text[8:]
        elif text.startswith("http://"):
            text = text[7:]

        # Remove "www." prefix
        if text.startswith("www."):
            text = text[4:]

        # Remove leading @
        if text.startswith("@"):
            text = text[1:]

        # Remove invisible Unicode control characters (Bidi, LTR/RTL marks, etc.)
        invisible_chars = [
            "\u200e",
            "\u200f",  # LTR / RTL marks
            "\u202a",
            "\u202b",
            "\u202c",
            "\u202d",
            "\u202e",  # Directional overrides
            "\u2066",
            "\u2067",
            "\u2068",
            "\u2069",  # Isolates
        ]
        text = re.sub(f"[{''.join(invisible_chars)}]", "", text)

        # Percent-encode if needed (e.g., non-ASCII chars)
        if not text.isascii():
            text = quote(text, safe="@/-_.+~#=:")

        return text.lower() if text else None


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
    language: str = ""
    resources: list[dict[str, str | None]] | None = None
    room: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    answers: list[PretalxAnswer] = Field(..., exclude=True)
    sessions_in_parallel: list[str] | None = None
    sessions_after: list[str] | None = None
    sessions_before: list[str] | None = None
    next_session: str | None = None
    prev_session: str | None = None
    slot_count: int = Field(..., exclude=True)
    youtube_url: str | None = None

    @field_validator("room", mode="before")
    @classmethod
    def handle_poster_room(cls, value) -> str | None:
        if value and "Main Hall" in value:
            return "Exhibit Hall"
        return value

    @computed_field
    def website_url(self) -> str:
        return f"https://{Config.event.split('-')[1]}.conference.pyladies.com/session/{self.slug}"

    @model_validator(mode="before")
    @classmethod
    def extract_answers(cls, values) -> dict:
        answers = [PretalxAnswer.model_validate(ans) for ans in values["answers"]]

        for answer in answers:
            if answer.question_text == SubmissionQuestion.talk_topic and not values.get(
                "track"
            ):
                values["track"] = answer.answer_text

            if answer.question_text == SubmissionQuestion.tweet:
                values["tweet"] = answer.answer_text

            if answer.question_text == SubmissionQuestion.delivery:
                if "Yes" in answer.answer_text:
                    values["delivery"] = "in-person"
                else:
                    values["delivery"] = "remote"

            if answer.question_text == SubmissionQuestion.level:
                values["level"] = answer.answer_text.lower()

        return values


class EuroPythonScheduleSpeaker(BaseModel):
    """
    Model for EuroPython schedule speaker data
    """

    code: str
    name: str
    avatar: str
    slug: str
    website_url: str


class EuroPythonScheduleSession(BaseModel):
    """
    Model for EuroPython schedule session data
    """

    event_type: EventType = EventType.SESSION
    code: str
    slug: str
    title: str
    session_type: str
    speakers: list[EuroPythonScheduleSpeaker]
    track: str | None
    tweet: str
    level: str
    total_duration: int = Field(..., exclude=True)
    rooms: list[Room]
    start: datetime
    slot_count: int = Field(..., exclude=True)
    website_url: str

    @computed_field
    def duration(self) -> int:
        return self.total_duration // self.slot_count


class EuroPythonScheduleBreak(BaseModel):
    """
    Model for EuroPython schedule break data
    """

    event_type: EventType = EventType.BREAK
    title: str
    duration: int
    rooms: list[Room]
    start: datetime


class DaySchedule(BaseModel):
    rooms: list[Room]
    events: list[EuroPythonScheduleSession | EuroPythonScheduleBreak]


class Schedule(BaseModel):
    days: dict[date, DaySchedule]

    @classmethod
    def from_events(
        cls, events: list[EuroPythonScheduleSession | EuroPythonScheduleBreak]
    ) -> Schedule:
        day_dict = {}
        for event in events:
            event_date = event.start.date()
            if event_date not in day_dict:
                day_dict[event_date] = {"rooms": list(set(event.rooms)), "events": []}
            else:
                day_dict[event_date]["rooms"] = list(
                    set(day_dict[event_date]["rooms"] + event.rooms)
                )
            day_dict[event_date]["events"].append(event)

        # Registration session should cover all rooms
        for day in day_dict.values():
            for event in day["events"]:
                if "Registration & Welcome" in event.title:
                    event.rooms = list(set(day["rooms"]))

        day_schedule_dict = {k: DaySchedule(**v) for k, v in day_dict.items()}
        return cls(days=day_schedule_dict)
