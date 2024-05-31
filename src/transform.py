from __future__ import annotations

import json
import sys
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator
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


class PretalxSlot(BaseModel):
    room: str | None = None
    start: datetime | None = None
    end: datetime | None = None

    @field_validator("room", mode="before")
    @classmethod
    def handle_localized(cls, v):
        if isinstance(v, dict):
            return v.get("en")
        return v


class PretalxSpeaker(BaseModel):
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
    gitx_url: str | None = None

    @model_validator(mode="before")
    @classmethod
    def extract(cls, values) -> dict:
        values["slug"] = slugify(values["name"])

        answers = [PretalxAnswer.model_validate(ans) for ans in values["answers"]]

        for answer in answers:
            if answer.question_text == SpeakerQuestion.affiliation:
                values["affiliation"] = answer.answer_text

            if answer.question_text == SpeakerQuestion.homepage:
                values["homepage"] = answer.answer_text

            # Handle handles (pun intended)
            if answer.question_text == SpeakerQuestion.twitter:
                twitter_url = answer.answer_text.strip().split()[0]

                if twitter_url.startswith("@"):
                    twitter_url = f"https://x.com/{twitter_url[1:]}"
                elif not twitter_url.startswith(("https://", "http://", "www.")):
                    twitter_url = f"https://x.com/{twitter_url}"
                else:
                    twitter_url = f"https://{twitter_url.removeprefix('https://').removeprefix('http://')}"

                values["twitter_url"] = twitter_url.split("?")[0]

            # If it's like @user@instance, we need to convert it to a URL
            if answer.question_text == SpeakerQuestion.mastodon:
                mastodon_url = answer.answer_text.strip().split()[0]

                if (
                    not mastodon_url.startswith(("https://", "http://"))
                    and mastodon_url.count("@") == 2
                ):
                    mastodon_url = f"https://{mastodon_url.split('@')[2]}/@{mastodon_url.split('@')[1]}"
                else:
                    mastodon_url = f"https://{mastodon_url.removeprefix('https://').removeprefix('http://')}"

                values["mastodon_url"] = mastodon_url.split("?")[0]

            if answer.question_text == SpeakerQuestion.linkedin:
                linkedin_url = answer.answer_text.strip().split()[0]

                if linkedin_url.startswith("in/"):
                    linkedin_url = f"https://linkedin.com/{linkedin_url}"
                elif not linkedin_url.startswith(("https://", "http://", "www.")):
                    linkedin_url = f"https://linkedin.com/in/{linkedin_url}"
                else:
                    linkedin_url = f"https://{linkedin_url.removeprefix('https://').removeprefix('http://')}"

                values["linkedin_url"] = linkedin_url.split("?")[0]

            if answer.question_text == SpeakerQuestion.gitx:
                values["gitx_url"] = answer.answer_text.strip().split()[0]

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
    slot: PretalxSlot | None = Field(..., exclude=True)
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

    @field_validator("submission_type", "track", mode="before")
    @classmethod
    def handle_localized(cls, v) -> str:
        if isinstance(v, dict):
            return v.get("en")
        return v

    @field_validator("duration", mode="before")
    @classmethod
    def duration_to_string(cls, v) -> str:
        if isinstance(v, int):
            return str(v)
        return v

    @model_validator(mode="before")
    @classmethod
    def extract(cls, values) -> dict:
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

        if values.get("slot"):
            slot = PretalxSlot.model_validate(values["slot"])
            values["room"] = slot.room
            values["start"] = slot.start
            values["end"] = slot.end

        slug = slugify(values["title"])
        values["slug"] = slug
        values["website_url"] = (
            f"https://ep{Config.event.split('-')[1]}.europython.eu/session/{slug}"
        )

        return values

    @property
    def is_accepted(self) -> bool:
        return self.state == SubmissionState.accepted

    @property
    def is_confirmed(self) -> bool:
        return self.state == SubmissionState.confirmed

    @property
    def is_publishable(self) -> bool:
        return self.is_accepted or self.is_confirmed

    @staticmethod
    def set_talks_in_parallel(
        submission: PretalxSubmission, all_sessions: dict[str, PretalxSubmission]
    ) -> None:
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
    ) -> None:
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

        # Set the next talk in the same room, or a keynote
        for session in unique_sessions:
            if session.room == submission.room or session.submission_type == "Keynote":
                submission.next_talk = session.code
                break

    @staticmethod
    def set_talks_before(
        submission: PretalxSubmission, all_sessions: dict[str, PretalxSubmission]
    ) -> None:
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
