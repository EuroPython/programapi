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

    ## to be updated when the 2026 schedule is out

    # Tutorial/workshop rooms
    club_a = "Club A"
    club_b = "Club B"
    club_c = "Club C"
    club_d = "Club D"
    club_e = "Club E"
    club_h = "Club H"

    # Conference rooms
    forum_hall = "Forum Hall"
    terrace_2a = "Terrace 2A"
    terrace_2b = "Terrace 2B"
    north_hall = "North Hall"
    south_hall_2a = "South Hall 2A"
    south_hall_2b = "South Hall 2B"
    exhibit_hall = "Exhibit Hall"


class EventType(Enum):
    SESSION = "session"
    BREAK = "break"
