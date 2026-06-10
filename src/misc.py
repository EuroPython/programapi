from enum import Enum


class SpeakerQuestion:
    affiliation = "Company/Organization/Educational Institution"
    homepage = "Social (Homepage)"
    twitter = "Social (X/Twitter)"
    bluesky = "Social (Bluesky)"
    linkedin = "Social (LinkedIn)"
    mastodon = "Social (Mastodon)"
    gitx = "Social (GitHub/GitLab)"


class SubmissionQuestion:
    outline = "Outline"
    tweet = "Abstract as a short post (150 character max)"
    delivery = "My presentation can be delivered in-person"
    level = "Expected audience expertise"


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

    s1 = "S1"
    s2 = "S2"
    s4 = "S4"
    s3a = "S3A"
    s3b = "S3B"
    s4a = "S4A"
    s4b = "S4B"
    glass_room = "Glass room"
    room_2_017_2_018 = "2.017/2.018"
    fishbowl = "Fishbowl"
    poster_hall_a = "Poster Hall A"
    poster_hall_b = "Poster Hall B"
    poster_hall_c = "Poster Hall C"
    exhibit_hall = "Exhibit Hall"


class EventType(Enum):
    SESSION = "session"
    BREAK = "break"
