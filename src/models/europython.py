from datetime import datetime

from pydantic import BaseModel, Field, computed_field, model_validator

from src.config import Config
from src.misc import SpeakerQuestion, SubmissionQuestion
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
    homepage: str | None = None
    twitter_url: str | None = None
    mastodon_url: str | None = None
    linkedin_url: str | None = None
    gitx: str | None = None

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
