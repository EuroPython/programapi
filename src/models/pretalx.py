from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from src.misc import SubmissionState


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


class PretalxScheduleBreak(BaseModel):
    """
    Model for Pretalx schedule break data
    """

    room: str
    start: datetime
    end: datetime
    description: dict[str, str] | str

    @field_validator("description", mode="before")
    @classmethod
    def handle_localized(cls, v) -> str | Any:
        if isinstance(v, dict):
            return v.get("en")
        return v

    @model_validator(mode="before")
    @classmethod
    def set_slot_info(cls, values) -> dict:
        slot = PretalxSlot.model_validate(values["slot"])
        values["room"] = slot.room
        values["start"] = slot.start
        values["end"] = slot.end

        return values


class PretalxSchedule(BaseModel):
    """
    Model for Pretalx schedule data
    """

    slots: list[PretalxSubmission]
    breaks: list[PretalxScheduleBreak]
