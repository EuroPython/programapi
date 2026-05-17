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

    auditorium_s1 = "Auditorium Hall (S1)"
    theatre_s2 = "Theatre Hall (S2)"
    conference_s4 = "Conference Hall Complex (S4)"
    chamber_s3a = "Chamber Hall A (S3A)"
    chamber_s3b = "Chamber Hall B (S3B)"
    conference_s4a = "Conference Hall Complex A (S4A)"
    conference_s4b = "Conference Hall Complex B (S4B)"
    glass_room_f0 = "Conference room F0 (Glass room)"
    multifunctional_1 = "Multifunctional room 1 (2.015/2.016)"
    fishbowl_f2 = "Reception Room F2 (Fishbowl)"
    exhibit_hall = "Exhibit Hall"


class EventType(Enum):
    SESSION = "session"
    BREAK = "break"
