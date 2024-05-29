# Explaining the data

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
        "submission_type": "Talk",
        "slug": "example-talk",
        "track": "Some Track",
        "state": "confirmed",
        "abstract": "This is an example talk. It is a great talk.",
        "tweet": "This is an example talk.",
        "duration": "60",
        "level": "intermediate",
        "delivery": "in-person",
        "room": "South Hall 2A",
        "start": "2024-07-10T14:00:00+02:00",
        "end": "2024-07-10T15:00:00+02:00",
        "talks_in_parallel": [
        "F7G8H9",
        ...
        ],
        "talks_after": [
        "I0J1K2",
        ...
        ],
        "talks_before": [
        "L3M4N5",
        ...
        ],
        "next_talk": "O6P7Q8",
        "prev_talk": "R9S0T1",
        "website_url": "https://ep2024.europython.eu/session/example-talk/"
    },
}
```
</details>

&nbsp;

The fields are as follows:

| Key                | Type                              | Notes                                                         |
|--------------------|-----------------------------------|---------------------------------------------------------------|
| `code`             | `string`                          | Unique identifier for the session                             |
| `title`            | `string`                          | Title of the session                                          |
| `speakers`         | `list[string]`                    | List of codes of the speakers                                 |
| `submission_type`  | `string`                          | Type of the session (e.g. Talk, Workshop, Poster, etc.)       |
| `slug`             | `string`                          | URL-friendly version of the title                             |
| `track`            | `string` \| `null`                | Track of the session (e.g. PyData, Web, etc.)                 |
| `state`            | `string`                          | State of the session (e.g. confirmed, canceled, etc.)         |
| `abstract`         | `string`                          | Abstract of the session                                       |
| `tweet`            | `string`                          | Tweet-length description of the session                       |
| `duration`         | `string`                          | Duration of the session in minutes                            |
| `level`            | `string`                          | Level of the session (e.g. beginner, intermediate, advanced)  |
| `delivery`         | `string`                          | Delivery mode of the session (e.g. in-person, remote)         |
| `room`             | `string` \| `null`                | Room where the session will be held                           |
| `start`            | `datetime (ISO format)` \| `null` | Start time of the session                                     |
| `end`              | `datetime (ISO format)` \| `null` | End time of the session                                       |
| `talks_in_parallel`| `list[string]` \| `null`          | List of codes of sessions happening in parallel               |
| `talks_after`      | `list[string]` \| `null`          | List of codes of sessions happening after this session        |
| `talks_before`     | `list[string]` \| `null`          | List of codes of sessions happening before this session       |
| `next_talk`        | `string` \| `null`                | Code of the next session in the same room                     |
| `prev_talk`        | `string` \| `null`                | Code of the previous session in the same room                 |
| `website_url`      | `string`                          | URL of the session on the conference website                  |

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
    "twitter": "example",
    "mastodon": "example"
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
| `avatar`       | `string` \| `null` | URL of the speaker's avatar                                           |
| `slug`         | `string`           | URL-friendly version of the name                                      |
| `submissions`  | `list[string]`     | List of codes of the sessions the speaker is speaking at              |
| `affiliation`  | `string` \| `null` | Affiliation of the speaker                                            |
| `homepage`     | `string` \| `null` | URL of the speaker's homepage                                         |
| `twitter`      | `string` \| `null` | Twitter handle of the speaker                                         |
| `mastodon`     | `string` \| `null` | Mastodon handle of the speaker                                        |
