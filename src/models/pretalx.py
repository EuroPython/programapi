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
            return v["name"].get("en")
        return v


class PretalxSpeaker(BaseModel):
    """
    Model for Pretalx speaker data
    """

    code: str
    name: str
    biography: str | None = None
    avatar_url: str
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
    resources: list[dict[str, str | None]] | None = None
    answers: list[PretalxAnswer]
    slots: list[PretalxSlot] = Field(default_factory=list, exclude=True)
    slot_count: int = Field(..., exclude=True)

    # Extracted from slot data
    room: str | None = None
    start: datetime | None = None
    end: datetime | None = None

    @field_validator("submission_type", "track", mode="before")
    @classmethod
    def handle_localized(cls, v) -> str | None:
        if isinstance(v, dict):
            return v["name"].get("en")
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
        # Transform resource information
        if raw_resources := values.get("resources"):
            resources = [
                {"description": res["description"], "resource": res["resource"]}
                for res in raw_resources
            ]
            values["resources"] = resources

        # Set slot information
        if values.get("slots"):
            first_slot = PretalxSlot.model_validate(values["slots"][0])
            values["room"] = first_slot.room
            values["start"] = first_slot.start

            last_slot = PretalxSlot.model_validate(values["slots"][-1])
            values["end"] = last_slot.end
            if values["end"] is None:
                print(f"Warning: end time is None for submission {values['code']}")

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
        slot = PretalxSlot.model_validate(values)
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

    @model_validator(mode="before")
    @classmethod
    def process_values(cls, values) -> dict:
        submission_slots = []
        break_slots = []
        for slot_dict in values["slots"]:
            # extract nested slot fields into slot
            slot_object = PretalxSlot.model_validate(slot_dict)
            slot_dict["slot"] = slot_object
            slot_dict["room"] = slot_object.room
            slot_dict["start"] = slot_object.start
            slot_dict["end"] = slot_object.end

            if slot_dict.get("submission") is None:
                break_slots.append(slot_dict)
            else:
                # merge submission fields into slot
                slot_dict.update(slot_dict.get("submission", {}))

                # remove resource IDs (not expandable with API, not required for schedule)
                slot_dict.pop("resources", None)

                submission_slots.append(slot_dict)

        values["slots"] = submission_slots
        values["breaks"] = break_slots
        return values
