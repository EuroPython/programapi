from __future__ import annotations

import json
import sys
from collections.abc import KeysView
from datetime import datetime

from pydantic import BaseModel, Field, RootModel, field_validator, model_validator
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


class TimingRelationship(BaseModel):
    talks_in_parallel: list[str]
    talks_after: list[str]
    talks_before: list[str]
    next_talk: str | None = None
    prev_talk: str | None = None

    @model_validator(mode="before")
    @classmethod
    def compute(cls, values):
        session = values["session"]
        all_sessions = values["all_sessions"]

        talks_in_parallel = cls.compute_talks_in_parallel(session, all_sessions)
        talks_after_data = cls.compute_talks_after(
            session, all_sessions, talks_in_parallel
        )
        talks_before_data = cls.compute_talks_before(
            session, all_sessions, talks_in_parallel
        )

        values["talks_in_parallel"] = talks_in_parallel
        values["talks_after"] = talks_after_data.get("talks_after")
        values["talks_before"] = talks_before_data.get("talks_before")
        values["next_talk"] = talks_after_data.get("next_talk")
        values["prev_talk"] = talks_before_data.get("prev_talk")

        return values

    @staticmethod
    def compute_talks_in_parallel(
        session: PretalxSession, all_sessions: list[PretalxSession]
    ) -> list[str]:
        talks_parallel = []
        for other_session in all_sessions:
            if (
                other_session.code == session.code
                or other_session.start is None
                or session.start is None
            ):
                continue

            # If they intersect, they are in parallel
            if other_session.start < session.end and other_session.end > session.start:
                talks_parallel.append(other_session.code)

        return talks_parallel

    @staticmethod
    def compute_talks_after(
        session: PretalxSession,
        all_sessions: list[PretalxSession],
        talks_in_parallel: list[str] = [],
    ) -> dict[str, list[str] | str | None]:
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
            and other_session.code not in talks_in_parallel
            and other_session.code != session.code
            and other_session.start.day == session.start.day
            and not other_session.submission_type
            == session.submission_type
            == "Announcements"
        ]

        # Add sessions to the list if they are in different rooms
        seen_rooms = set()
        unique_sessions = []

        for other_session in remaining_sessions:
            if other_session.room not in seen_rooms:
                unique_sessions.append(other_session)
                seen_rooms.add(other_session.room)

        # If there is a keynote next, only show that
        if any(s.submission_type == "Keynote" for s in unique_sessions):
            unique_sessions = [
                s for s in unique_sessions if s.submission_type == "Keynote"
            ]

        # Set the next talks in all rooms
        talks_after = [s.code for s in unique_sessions]

        # Set the next talk in the same room, or a keynote
        next_talk = None
        for other_session in unique_sessions:
            if (
                other_session.room == session.room
                or other_session.submission_type == "Keynote"
            ):
                next_talk = other_session.code
                break

        return {"talks_after": talks_after, "next_talk": next_talk}

    @staticmethod
    def compute_talks_before(
        session: PretalxSession,
        all_sessions: list[PretalxSession],
        talks_in_parallel: list[str] = [],
    ) -> dict[str, list[str] | str | None]:
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
            and other_session.code not in talks_in_parallel
            and other_session.start <= session.start
            and other_session.code != session.code
            and other_session.start.day == session.start.day
            and other_session.submission_type != "Announcements"
        ]

        seen_rooms = set()
        unique_sessions = []

        for other_session in remaining_sessions:
            if other_session.room not in seen_rooms:
                unique_sessions.append(other_session)
                seen_rooms.add(other_session.room)

        talks_before = [session.code for session in unique_sessions]

        prev_talk = None
        for other_session in unique_sessions:
            if other_session.room == session.room:
                prev_talk = other_session.code
                break

        return {"talks_before": talks_before, "prev_talk": prev_talk}


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
        # Extract the twitter URL from the answer
        def extract_twitter_url(text: str) -> str:
            if text.startswith("@"):
                twitter_url = f"https://x.com/{text[1:]}"
            elif not text.startswith(("https://", "http://", "www.")):
                twitter_url = f"https://x.com/{text}"
            else:
                twitter_url = (
                    f"https://{text.removeprefix('https://').removeprefix('http://')}"
                )

            return twitter_url.split("?")[0]

        # If it's like @user@instance, we need to convert it to a URL
        def extract_mastodon_url(text: str) -> str:
            if not text.startswith(("https://", "http://")) and text.count("@") == 2:
                mastodon_url = f"https://{text.split('@')[2]}/@{text.split('@')[1]}"
            else:
                mastodon_url = (
                    f"https://{text.removeprefix('https://').removeprefix('http://')}"
                )

            return mastodon_url.split("?")[0]

        # Extract the linkedin URL from the answer
        def extract_linkedin_url(text: str) -> str:
            if text.startswith("in/"):
                linkedin_url = f"https://linkedin.com/{text}"
            elif not text.startswith(("https://", "http://", "www.")):
                linkedin_url = f"https://linkedin.com/in/{text}"
            else:
                linkedin_url = (
                    f"https://{text.removeprefix('https://').removeprefix('http://')}"
                )

            return linkedin_url.split("?")[0]

        answers = [PretalxAnswer.model_validate(ans) for ans in values["answers"]]

        for answer in answers:
            if answer.question_text == SpeakerQuestion.affiliation:
                values["affiliation"] = answer.answer_text

            if answer.question_text == SpeakerQuestion.homepage:
                values["homepage"] = answer.answer_text

            if answer.question_text == SpeakerQuestion.twitter:
                values["twitter_url"] = extract_twitter_url(
                    answer.answer_text.strip().split()[0]
                )

            if answer.question_text == SpeakerQuestion.mastodon:
                values["mastodon_url"] = extract_mastodon_url(
                    answer.answer_text.strip().split()[0]
                )

            if answer.question_text == SpeakerQuestion.linkedin:
                values["linkedin_url"] = extract_linkedin_url(
                    answer.answer_text.strip().split()[0]
                )

            if answer.question_text == SpeakerQuestion.gitx:
                values["gitx_url"] = answer.answer_text.strip().split()[0]

        # Set the slug
        values["slug"] = slugify(values["name"])

        return values


class PretalxSubmissions(RootModel):
    root: list[PretalxSession]

    @model_validator(mode="before")
    @classmethod
    def initiate(cls, root):
        """
        Returns only the publishable sessions, and computes their timings
        """
        publishable = []
        for submission in root:
            sub = PretalxSession.model_validate(submission)
            if sub.is_publishable:
                publishable.append(sub)

        for session in publishable:
            if session.start and session.end:
                timings = TimingRelationship.model_validate(
                    dict(session=session, all_sessions=publishable)
                )

                session.talks_in_parallel = timings.talks_in_parallel
                session.talks_after = timings.talks_after
                session.talks_before = timings.talks_before
                session.next_talk = timings.next_talk
                session.prev_talk = timings.prev_talk

        return publishable


class PretalxSession(BaseModel):
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

    talks_in_parallel: list[str] | None = None
    talks_after: list[str] | None = None
    talks_before: list[str] | None = None
    next_talk: str | None = None
    prev_talk: str | None = None

    website_url: str

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


def parse_publishable_submissions() -> dict[str, PretalxSession]:
    """
    Returns only publishable sessions
    """
    with open(Config.raw_path / "submissions_latest.json") as fd:
        js = json.load(fd)
        subs = PretalxSubmissions.model_validate(js).root
        subs_dict = {s.code: s for s in subs}
    return subs_dict


def parse_speakers() -> list[PretalxSpeaker]:
    """
    Returns only speakers with publishable sessions
    """
    with open(Config.raw_path / "speakers_latest.json") as fd:
        js = json.load(fd)
        speakers = [PretalxSpeaker.model_validate(item) for item in js]
    return speakers


def publishable_speakers(
    accepted_proposals: KeysView[str],
) -> dict[str, PretalxSpeaker]:
    sp = parse_speakers()
    output = {}
    for speaker in sp:
        accepted = set(speaker.submissions) & accepted_proposals
        if accepted:
            # Overwrite with only the accepted proposals
            speaker.submissions = list(accepted)
            output[speaker.code] = speaker

    return output


def save_publishable_sessions(publishable: dict[str, PretalxSession]):
    path = Config.public_path / "sessions.json"

    data = {k: json.loads(v.model_dump_json()) for k, v in publishable.items()}
    with open(path, "w") as fd:
        json.dump(data, fd, indent=2)


def save_publishable_speakers(publishable: dict[str, PretalxSession]):
    path = Config.public_path / "speakers.json"

    speakers = publishable_speakers(publishable.keys())

    data = {k: v.model_dump() for k, v in speakers.items()}
    with open(path, "w") as fd:
        json.dump(data, fd, indent=2)


def save_all(all_sessions: dict[str, PretalxSession]):
    Config.public_path.mkdir(parents=True, exist_ok=True)

    save_publishable_sessions(all_sessions)
    save_publishable_speakers(all_sessions)


def check_duplicate_slugs(all_sessions: dict[str, PretalxSession]) -> bool:
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

    all_sessions = parse_publishable_submissions()

    if not check_duplicate_slugs(all_sessions) and (
        len(sys.argv) <= 1 or sys.argv[1] != "--allow-dupes"
    ):
        print("Exiting. Use ``make transform ALLOW_DUPES=true`` to continue.")
        sys.exit(1)

    print("Saving publishable data...")
    save_all(all_sessions)
    print("Done")
