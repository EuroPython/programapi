import json
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.class_validators import root_validator
from slugify import slugify

from src.config import Config


class SpeakerQuestion:
    affiliation = "Company / Organization / Educational Institution"
    homepage = "Social (Homepage)"
    twitter = "Social (X/Twitter)"
    mastodon = "Social (Mastodon)"


class SubmissionQuestion:
    outline = "Outline"
    tweet = "Abstract as a tweet / toot"
    delivery = "My presentation can be delivered"
    level = "Expected audience expertise"


class SubmissionState:
    accepted = "accepted"
    confirmed = "confirmed"
    withdrawn = "withdrawn"


class PretalxAnswer(BaseModel):
    question_text: str
    answer_text: str
    answer_file: str | None
    submission_id: str | None
    speaker_id: str | None

    @root_validator(pre=True)
    def extract(cls, values):
        values["question_text"] = values["question"]["question"]["en"]
        values["answer_text"] = values["answer"]
        values["answer_file"] = values["answer_file"]
        values["submission_id"] = values["submission"]
        values["speaker_id"] = values["person"]
        return values


class PretalxSpeaker(BaseModel):
    code: str
    name: str
    biography: str | None
    avatar: str | None
    slug: str
    answers: list[PretalxAnswer] = Field(..., exclude=True)
    submissions: list[str]

    # Extracted
    affiliation: str | None = None
    homepage: str | None = None
    twitter: str | None = None
    mastodon: str | None = None

    @root_validator(pre=True)
    def extract(cls, values):
        values["slug"] = slugify(values["name"])

        answers = [PretalxAnswer.parse_obj(ans) for ans in values["answers"]]

        for answer in answers:
            if answer.question_text == SpeakerQuestion.affiliation:
                values["affiliation"] = answer.answer_text

            if answer.question_text == SpeakerQuestion.homepage:
                values["homepage"] = answer.answer_text

            # NOTE: in practice the format of the data here is different,
            # depending on the speaker. We could fix this here by parsing the
            # the answer_text to some standardised format (either @handle or
            # https://twitter.com/handle url, etc)
            if answer.question_text == SpeakerQuestion.twitter:
                values["twitter"] = answer.answer_text

            if answer.question_text == SpeakerQuestion.mastodon:
                values["mastodon"] = answer.answer_text

        return values


class PretalxSubmission(BaseModel):
    code: str
    title: str
    speakers: list[str]  # We only want the code, not the full info
    submission_type: str
    slug: str
    track: str | None
    state: str
    abstract: str
    answers: list[PretalxAnswer] = Field(..., exclude=True)
    tweet: str = ""
    duration: str

    level: str = ""
    delivery: str | None = ""

    # This is embedding a slot inside a submission for easier lookup later
    room: str | None = None
    start: datetime | None = None
    end: datetime | None = None

    # TODO: once we have schedule data then we can prefill those in the code
    # here
    talks_in_parallel: list[str] | None = None
    talks_after: list[str] | None = None
    next_talk_code: str | None = None
    prev_talk_code: str | None = None

    website_url: str | None = None

    @root_validator(pre=True)
    def extract(cls, values):
        # # SubmissionType and Track have localised names. For this project we
        # # only care about their english versions, so we can extract them here
        for field in ["submission_type", "track"]:
            if values[field] is None:
                continue
            else:
                # In 2024 some of those are localised, and some are not.
                # Instead of figuring out why and fixing the data, there's this
                # hack:
                if isinstance(values[field], dict):
                    values[field] = values[field]["en"]

        values["speakers"] = sorted([s["code"] for s in values["speakers"]])

        answers = [PretalxAnswer.parse_obj(ans) for ans in values["answers"]]

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

        slug = slugify(values["title"])
        values["slug"] = slug
        values["website_url"] = f"https://ep2024.europython.eu/session/{slug}"

        return values

    @property
    def is_accepted(self):
        return self.state == SubmissionState.accepted

    @property
    def is_confirmed(self):
        return self.state == SubmissionState.confirmed

    @property
    def is_publishable(self):
        return self.is_accepted or self.is_confirmed


def parse_submissions() -> list[PretalxSubmission]:
    """
    Returns only confirmed talks
    """
    with open(Config.raw_path / "submissions_latest.json") as fd:
        js = json.load(fd)
        subs = []
        for item in js:
            sub = PretalxSubmission.parse_obj(item)
            subs.append(sub)

    return subs


def parse_speakers() -> list[PretalxSpeaker]:
    """
    Returns only speakers with confirmed talks
    """
    with open(Config.raw_path / "speakers_latest.json") as fd:
        js = json.load(fd)
        speakers = []
        for item in js:
            speaker = PretalxSpeaker.parse_obj(item)
            speakers.append(speaker)

    return speakers


def publishable_submissions() -> dict[str, PretalxSubmission]:
    return {s.code: s for s in parse_submissions() if s.is_publishable}


def publishable_speakers(accepted_proposals: set[str]) -> dict[str, PretalxSpeaker]:
    sp = parse_speakers()
    output = {}
    for speaker in sp:
        accepted = set(speaker.submissions) & accepted_proposals
        if accepted:
            # Overwrite with only the accepted proposals
            speaker.submissions = list(accepted)
            output[speaker.code] = speaker

    return output


def save_publishable_sessions():
    path = Config.public_path / "sessions.json"

    publishable = publishable_submissions()

    data = {k: v.dict() for k, v in publishable.items()}
    with open(path, "w") as fd:
        json.dump(data, fd, indent=2)


def save_publishable_speakers():
    path = Config.public_path / "speakers.json"

    publishable = publishable_submissions()
    speakers = publishable_speakers(publishable.keys())

    data = {k: v.dict() for k, v in speakers.items()}
    with open(path, "w") as fd:
        json.dump(data, fd, indent=2)


assert len(set(s.slug for s in publishable_submissions().values())) == len(
    publishable_submissions()
)

if __name__ == "__main__":
    print("Saving publishable data...")
    save_publishable_sessions()
    save_publishable_speakers()
    print("Done")
