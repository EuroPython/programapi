from enum import Enum


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
