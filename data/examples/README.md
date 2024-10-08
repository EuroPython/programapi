# Explaining the Output Data

**Note:** Some of the fields may be `null` or empty (`""`).

## `sessions.json`

<details>
<summary>Example session data JSON</summary>

```json
{
    "A1B2C3": {
        "code": "A1B2C3",
        "title": "Example talk",
        "speakers": [
        "B4D5E6",
        ...
        ],
        "session_type": "Talk",
        "slug": "example-talk",
        "track": "Some Track",
        "state": "confirmed",
        "abstract": "This is an example talk. It is a great talk.",
        "tweet": "This is an example talk.",
        "duration": "60",
        "level": "intermediate",
        "delivery": "in-person",
        "resources": [
            {
                "resource": "https://example.com/slides.pdf",
                "description": "Slides for the session"
            }
        ...
        ],
        "room": "South Hall 2A",
        "start": "2099-07-10T14:00:00+02:00",
        "end": "2099-07-10T15:00:00+02:00",
        "website_url": "https://ep2099.europython.eu/session/example-talk/",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUJcmljayByb2xs",
        "sessions_in_parallel": [
        "F7G8H9",
        ...
        ],
        "sessions_after": [
        "I0J1K2",
        ...
        ],
        "sessions_before": [
        "L3M4N5",
        ...
        ],
        "next_session": "O6P7Q8",
        "prev_session": "R9S0T1"
    },
}
```
</details>

&nbsp;

The fields are as follows:

| Key                    | Type                                      | Notes                                                         |
|------------------------|-------------------------------------------|---------------------------------------------------------------|
| `code`                 | `string`                                  | Unique identifier for the session                             |
| `title`                | `string`                                  | Title of the session                                          |
| `speakers`             | `array[string]`                           | List of codes of the speakers                                 |
| `session_type`         | `string`                                  | Type of the session (e.g. Talk, Workshop, Poster, etc.)       |
| `slug`                 | `string`                                  | URL-friendly version of the title                             |
| `track`                | `string` \| `null`                        | Track of the session (e.g. PyData, Web, etc.)                 |
| `abstract`             | `string`                                  | Abstract of the session                                       |
| `tweet`                | `string`                                  | Tweet-length description of the session                       |
| `duration`             | `string`                                  | Duration of the session in minutes                            |
| `level`                | `string`                                  | Level of the session (e.g. beginner, intermediate, advanced)  |
| `delivery`             | `string`                                  | Delivery mode of the session (e.g. in-person, remote)         |
| `resources`            | `array[object[string, string]]` \| `null` | List of resources for the session: `{"resource": <url>, "description": <description>}` |
| `room`                 | `string` \| `null`                        | Room where the session will be held                           |
| `start`                | `string (datetime ISO format)` \| `null`  | Start time of the session                                     |
| `end`                  | `string (datetime ISO format)` \| `null`  | End time of the session                                       |
| `website_url`          | `string`                                  | URL of the session on the conference website                  |
| `youtube_url`          | `string` \| `null`                        | URL of the session's video on YouTube                         |
| `sessions_in_parallel` | `array[string]` \| `null`                 | List of codes of sessions happening in parallel               |
| `sessions_after`       | `array[string]` \| `null`                 | List of codes of sessions happening after this session        |
| `sessions_before`      | `array[string]` \| `null`                 | List of codes of sessions happening before this session       |
| `next_session`         | `string` \| `null`                        | Code of the next session in the same room                     |
| `prev_session`         | `string` \| `null`                        | Code of the previous session in the same room                 |

&nbsp;

## `speakers.json`

<details>
<summary>Example speaker data JSON</summary>

```json
{
  "B4D5E6": {
    "code": "B4D5E6",
    "name": "A Speaker",
    "biography": "Some bio",
    "avatar": "https://pretalx.com/media/avatars/picture.jpg",
    "slug": "a-speaker",
    "submissions": [
      "A1B2C3",
      ...
    ],
    "affiliation": "A Company",
    "homepage": "https://example.com",
    "gitx": "https://github.com/B4D5E6",
    "linkedin_url": "https://www.linkedin.com/in/B4D5E6",
    "mastodon_url": "https://mastodon.social/@B4D5E6",
    "twitter_url": "https://x.com/B4D5E6"
  },
  ...
}
```
</details>

&nbsp;

The fields are as follows:

| Key            | Type               | Notes                                                                 |
|----------------|--------------------|-----------------------------------------------------------------------|
| `code`         | `string`           | Unique identifier for the speaker                                     |
| `name`         | `string`           | Name of the speaker                                                   |
| `biography`    | `string` \| `null` | Biography of the speaker                                              |
| `avatar`       | `string`           | URL of the speaker's avatar                                           |
| `slug`         | `string`           | URL-friendly version of the name                                      |
| `submissions`  | `array[string]`    | List of codes of the sessions the speaker is speaking at              |
| `affiliation`  | `string` \| `null` | Affiliation of the speaker                                            |
| `homepage`     | `string` \| `null` | URL/text of the speaker's homepage                                    |
| `gitx`         | `string` \| `null` | URL/text of the speaker's GitHub/GitLab/etc. profile                  |
| `linkedin_url` | `string` \| `null` | URL of the speaker's LinkedIn profile                                 |
| `twitter_url`  | `string` \| `null` | URL of the speaker's Twitter profile                                  |
| `mastodon_url` | `string` \| `null` | URL of the speaker's Mastodon profile                                 |
| `website_url`  | `string`           | URL of the speaker's profile on the conference website                |

&nbsp;

## `schedule.json`

<details>
<summary>Example schedule data JSON</summary>

```json
{
    "days": {
        "2099-07-08": {
            "events": [
                {
                    "code": "LMN123",
                    "title": "Welcome and Keynote",
                    "speakers": [],
                    "session_type": "Announcements",
                    "slug": "welcome-keynote",
                    "track": null,
                    "level": "beginner",
                    "rooms": [
                        "Room A",
                        "Room B"
                    ],
                    "start": "2099-07-08T08:00:00+02:00",
                    "duration": 60,
                    "tweet": "",
                    "website_url": "https://ep2099.europython.eu/session/welcome-keynote"
                },
                {
                    "code": "OPQ456",
                    "title": "Advanced Python Techniques",
                    "speakers": [
                        {
                            "avatar": "https://pretalx.com/media/avatars/picture.jpg",
                            "code": "RST789",
                            "name": "John Doe",
                            "slug": "john-doe",
                            "website_url": "https://ep2099.europython.eu/speaker/john-doe"
                        }
                    ],
                    "session_type": "Tutorial",
                    "slug": "advanced-python-techniques",
                    "track": "CPython Internals",
                    "level": "advanced",
                    "rooms": [
                        "Room C"
                    ],
                    "start": "2099-07-08T10:00:00+02:00",
                    "duration": 90,
                    "tweet": "",
                    "website_url": "https://ep2099.europython.eu/advanced-python-techniques"
                }
            ]
        }
    }
}
```
</details>

&nbsp;

The fields are as follows:

| Key            | Type                        | Notes                                                      |
|----------------|-----------------------------|------------------------------------------------------------|
| `days`         | `object`                    | Contains schedule by date                                  |
| `events`       | `array[object]`             | List of events for a particular day                        |
| `code`         | `string`                    | Unique identifier for the event                            |
| `title`        | `string`                    | Title of the event                                         |
| `speakers`     | `array[object]`             | List of speakers for the event (if applicable)             |
| `session_type` | `string`                    | Type of event (e.g. Announcements, Workshop, etc.)         |
| `slug`         | `string`                    | URL-friendly version of the event title                    |
| `track`        | `string` \| `null`          | Track associated with the event (e.g. Web, PyData, etc.)   |
| `level`        | `string`                    | Level of the event (beginner, intermediate, advanced)       |
| `rooms`        | `array[string]`             | List of rooms the event is being held in                   |
| `start`        | `string (datetime ISO)`      | Start time of the event                                    |
| `duration`     | `integer`                   | Duration of the event in minutes                           |
| `tweet`        | `string` \| `null`          | Tweet-length description of the event                      |
| `website_url`  | `string`                    | URL of the event on the conference website                 |
