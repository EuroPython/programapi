from enum import Enum


class SpeakerQuestion:
    affiliation = "Company/Organization/Educational Institution"
    occupation: "Position, Job or Occupation"
    homepage = "Social (Homepage)"
    twitter = "Social (X/twitter)"
    bluesky = "Social (Bluesky)"
    linkedin = "Social (LinkedIn)"
    mastodon = "Social (Mastodon)"
    instagram = "Social (Instagram)"
    gitx = "Social (GitHub/GitLab)"
    timezone = "Timezone"


class SubmissionQuestion:
    talk_topic = "Talk topic"
    outline = "Outline"
    tweet = "Abstract as a short post (150 character max)"
    delivery = "My presentation can be delivered in-person"
    level = "Level"
    language = "Language"


class SubmissionState(Enum):
    accepted = "accepted"
    confirmed = "confirmed"
    withdrawn = "withdrawn"
    rejected = "rejected"
    canceled = "canceled"
    submitted = "submitted"


class Room(Enum):
    """
    Rooms at the conference venue, this can change year to year
    """

    main_stream = "Main Stream"
    other_stream = "Activities & Open Spaces"


class EventType(Enum):
    SESSION = "session"
    BREAK = "break"
