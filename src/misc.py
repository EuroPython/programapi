from enum import Enum


class SpeakerQuestion:
    affiliation = "Company / Institute"
    homepage = "Homepage"
    twitter = "Twitter handle"
    bluesky = "Social (Bluesky)"
    linkedin = "LinkedIn"
    mastodon = "Social (Mastodon)"
    gitx = "Github/Gitlab"


class SubmissionQuestion:
    tweet = "Abstract as a tweet"
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

    liffey_a = "Liffey A"
    liffey_b = "Liffey B"
    liffey_hall_1 = "Liffey Hall 1"
    liffey_hall_2 = "Liffey Hall 2"
    wicklow_hall_1 = "Wicklow Hall 1"
    wicklow_hall_2 = "Wicklow Hall 2"
    wicklow_hall_2a = "Wicklow Hall 2A"
    wicklow_hall_2b = "Wicklow Hall 2B"
    the_auditorium = "The Auditorium"
    liffey_meeting_room_2 = "Liffey Meeting Room 2"
    forum = "Forum"


class EventType(Enum):
    SESSION = "session"
    BREAK = "break"
