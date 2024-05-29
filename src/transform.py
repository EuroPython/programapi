from __future__ import annotations

import json
import sys
from datetime import datetime

from pydantic import BaseModel, Field, model_validator
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
    answer_file: str | None = None
    submission_id: str | None = None
    speaker_id: str | None = None

    @model_validator(mode="before")
    @classmethod
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
    biography: str | None = None
    avatar: str | None = None
    slug: str
    answers: list[PretalxAnswer] = Field(..., exclude=True)
    submissions: list[str]

    # Extracted
    affiliation: str | None = None
    homepage: str | None = None
    twitter: str | None = None
    mastodon: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract(cls, values):
        values["slug"] = slugify(values["name"])

        answers = [PretalxAnswer.model_validate(ans) for ans in values["answers"]]

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
    track: str | None = None
    state: str
    abstract: str
    answers: list[PretalxAnswer] = Field(..., exclude=True)
    tweet: str = ""
    duration: str

    level: str = ""
    delivery: str = ""

    # This is embedding a slot inside a submission for easier lookup later
    room: str | None = None
    start: datetime | None = None
    end: datetime | None = None

    # TODO: once we have schedule data then we can prefill those in the code here
    # These are added after the model is created
    talks_in_parallel: list[str] | None = None
    talks_after: list[str] | None = None
    talks_before: list[str] | None = None
    next_talk: str | None = None
    prev_talk: str | None = None

    website_url: str

    @model_validator(mode="before")
    @classmethod
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

        # Convert duration to string for model validation
        if isinstance(values["duration"], int):
            values["duration"] = str(values["duration"])

        if cls.is_publishable and values["slot"]:
            slot = values["slot"]

            if isinstance(slot["room"], dict):
                values["room"] = slot["room"]["en"]

            if slot["start"]:
                values["start"] = datetime.fromisoformat(slot["start"])
                values["end"] = datetime.fromisoformat(slot["end"])

        slug = slugify(values["title"])
        values["slug"] = slug
        values["website_url"] = (
            f"https://ep{Config.event.split('-')[1]}.europython.eu/session/{slug}"
        )

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

    @staticmethod
    def set_talks_in_parallel(
        submission: PretalxSubmission, all_sessions: dict[str, PretalxSubmission]
    ):
        parallel = []
        for session in all_sessions.values():
            if (
                session.code == submission.code
                or session.start is None
                or submission.start is None
            ):
                continue

            # If they intersect, they are in parallel
            if session.start < submission.end and session.end > submission.start:
                parallel.append(session.code)

        submission.talks_in_parallel = parallel

    @staticmethod
    def set_talks_after(
        submission: PretalxSubmission, all_sessions: dict[str, PretalxSubmission]
    ):
        # Sort sessions based on start time, early first
        all_sessions_sorted = sorted(
            all_sessions.values(), key=lambda x: (x.start is None, x.start)
        )

        # Filter out sessions
        remaining_sessions = [
            session
            for session in all_sessions_sorted
            if session.start is not None
            and session.start >= submission.end
            and session.code not in submission.talks_in_parallel
            and session.code != submission.code
            and submission.start.day == session.start.day
            and not submission.submission_type
            == session.submission_type
            == "Announcements"
        ]

        # Add sessions to the list if they are in different rooms
        seen_rooms = set()
        unique_sessions = []

        for session in remaining_sessions:
            if session.room not in seen_rooms:
                unique_sessions.append(session)
                seen_rooms.add(session.room)

        # If there is a keynote next, only show that
        if any(s.submission_type == "Keynote" for s in unique_sessions):
            unique_sessions = [
                s for s in unique_sessions if s.submission_type == "Keynote"
            ]

        # Set the next talks in all rooms
        submission.talks_after = [session.code for session in unique_sessions]

        # Set the next talk in the same room
        for session in unique_sessions:
            if session.room == submission.room:
                submission.next_talk = session.code
                break

    @staticmethod
    def set_talks_before(
        submission: PretalxSubmission, all_sessions: dict[str, PretalxSubmission]
    ):
        # Sort sessions based on start time, late first
        all_sessions_sorted = sorted(
            all_sessions.values(),
            key=lambda x: (x.start is None, x.start),
            reverse=True,
        )

        remaining_sessions = [
            session
            for session in all_sessions_sorted
            if session.start is not None
            and session.code not in submission.talks_in_parallel
            and session.start <= submission.start
            and session.code != submission.code
            and submission.start.day == session.start.day
            and session.submission_type != "Announcements"
        ]

        seen_rooms = set()
        unique_sessions = []

        for session in remaining_sessions:
            if session.room not in seen_rooms:
                unique_sessions.append(session)
                seen_rooms.add(session.room)

        submission.talks_before = [session.code for session in unique_sessions]

        for session in unique_sessions:
            if session.room == submission.room:
                submission.prev_talk = session.code
                break


def parse_submissions() -> list[PretalxSubmission]:
    """
    Returns only confirmed talks
    """
    with open(Config.raw_path / "submissions_latest.json") as fd:
        js = json.load(fd)
        subs = [PretalxSubmission.model_validate(item) for item in js]
    return subs


def parse_speakers() -> list[PretalxSpeaker]:
    """
    Returns only speakers with confirmed talks
    """
    with open(Config.raw_path / "speakers_latest.json") as fd:
        js = json.load(fd)
        speakers = [PretalxSpeaker.model_validate(item) for item in js]
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


def save_publishable_sessions(publishable: dict[str, PretalxSubmission]):
    path = Config.public_path / "sessions.json"

    for sub in publishable.values():
        if sub.start is not None:
            PretalxSubmission.set_talks_in_parallel(sub, publishable)
            PretalxSubmission.set_talks_after(sub, publishable)
            PretalxSubmission.set_talks_before(sub, publishable)

    data = {k: json.loads(v.model_dump_json()) for k, v in publishable.items()}
    with open(path, "w") as fd:
        json.dump(data, fd, indent=2)


def save_publishable_speakers(publishable: dict[str, PretalxSubmission]):
    path = Config.public_path / "speakers.json"

    speakers = publishable_speakers(publishable.keys())

    data = {k: v.model_dump() for k, v in speakers.items()}
    with open(path, "w") as fd:
        json.dump(data, fd, indent=2)


def save_all(all_sessions: dict[str, PretalxSubmission]):
    if not Config.public_path.exists():
        Config.public_path.mkdir(parents=True)

    save_publishable_sessions(all_sessions)
    save_publishable_speakers(all_sessions)


def check_duplicate_slugs(all_sessions: dict[str, PretalxSubmission]) -> bool:
    all_speakers = publishable_speakers(all_sessions.keys())

    session_slugs = [s.slug for s in all_sessions.values()]
    speaker_slugs = [s.slug for s in all_speakers.values()]

    session_duplicates = [
        slug for slug in set(session_slugs) if session_slugs.count(slug) > 1
    ]
    speaker_duplicates = [
        slug for slug in set(speaker_slugs) if speaker_slugs.count(slug) > 1
    ]

    if session_duplicates or speaker_duplicates:
        print("Found duplicate slugs:")
        for slug in session_duplicates:
            print(f"Session: {slug}")
        for slug in speaker_duplicates:
            print(f"Speaker: {slug}")
        return False
    return True


if __name__ == "__main__":
    print(f"Transforming {Config.event} data...")
    print("Checking for duplicate slugs...")

    all_sessions = publishable_submissions()

    if not check_duplicate_slugs(all_sessions) and (
        len(sys.argv) <= 1 or sys.argv[1] != "--allow-dupes"
    ):
        print("Exiting. Use ``make transform ALLOW_DUPES=true`` to continue.")
        sys.exit(1)

    print("Saving publishable data...")
    save_all(all_sessions)
    print("Done")
