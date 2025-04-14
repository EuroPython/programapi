# 📄 ProgramAPI Output Documentation

> ⚠️ Some fields may be `null`, `""`, or excluded from specific contexts.
> 🍭 Also, yes, Rick Astley may appear in test videos. You're welcome.

---

## 🗣 `speakers.json`

<details>
<summary>Example speaker data</summary>

```json
{
  "B4D5E6": {
    "code": "B4D5E6",
    "name": "A Speaker",
    "biography": "Some bio",
    "avatar": "https://pretalx.com/media/avatars/picture.jpg",
    "slug": "a-speaker",
    "submissions": ["A1B2C3"],
    "affiliation": "A Company",
    "homepage": "https://example.com",
    "twitter_url": "https://x.com/B4D5E6",
    "linkedin_url": "https://linkedin.com/in/B4D5E6",
    "mastodon_url": "https://mastodon.social/@B4D5E6",
    "bluesky_url": "https://bsky.app/profile/B4D5E6.bsky.social",
    "gitx_url": "https://github.com/B4D5E6",
    "website_url": "https://ep2099.europython.eu/speaker/a-speaker"
  }
}
```
</details>

### Fields

| Key            | Type               | Notes                                                                 |
|----------------|--------------------|-----------------------------------------------------------------------|
| `code`         | `string`           | Unique identifier for the speaker                                     |
| `name`         | `string`           | Full name of the speaker                                              |
| `biography`    | `string` \| `null` | Short biography                                                       |
| `avatar`       | `string`           | URL of speaker's avatar                                               |
| `slug`         | `string`           | URL-safe speaker name                                                 |
| `submissions`  | `array[string]`    | Codes of sessions the speaker is involved in                          |
| `affiliation`  | `string` \| `null` | Affiliated institution or organization                                |
| `homepage`     | `string` \| `null` | Personal or professional homepage                                     |
| `twitter_url`  | `string` \| `null` | Normalized Twitter/X profile URL                                      |
| `mastodon_url` | `string` \| `null` | Normalized Mastodon profile URL                                       |
| `linkedin_url` | `string` \| `null` | Normalized LinkedIn profile URL                                       |
| `bluesky_url`  | `string` \| `null` | Normalized Bluesky profile URL                                        |
| `gitx_url`     | `string` \| `null` | Normalized GitHub/GitLab profile URL                                  |
| `website_url`  | `string`           | Auto-generated speaker profile on the EuroPython site                 |

---

## 📚 `sessions.json`

<details>
<summary>Example session data</summary>

```json
{
  "A1B2C3": {
    "code": "A1B2C3",
    "title": "Example talk",
    "speakers": ["B4D5E6"],
    "session_type": "Talk",
    "slug": "example-talk",
    "track": "Some Track",
    "abstract": "This is an example talk.",
    "tweet": "This is an example talk.",
    "duration": "60",
    "level": "intermediate",
    "delivery": "in-person",
    "resources": [
      {
        "resource": "https://example.com/slides.pdf",
        "description": "Slides for the session"
      }
    ],
    "room": "South Hall 2A",
    "start": "2099-07-10T14:00:00+02:00",
    "end": "2099-07-10T15:00:00+02:00",
    "website_url": "https://ep2099.europython.eu/session/example-talk",
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "sessions_in_parallel": ["F7G8H9"],
    "sessions_after": ["I0J1K2"],
    "sessions_before": ["L3M4N5"],
    "next_session": "O6P7Q8",
    "prev_session": "R9S0T1"
  }
}
```
</details>

### Fields

| Key                    | Type                                      | Notes                                                           |
|------------------------|-------------------------------------------|-----------------------------------------------------------------|
| `code`                 | `string`                                  | Unique session identifier                                       |
| `title`                | `string`                                  | Title of the session                                            |
| `speakers`             | `array[string]`                           | List of speaker codes                                           |
| `session_type`         | `string`                                  | Type of session (e.g. Talk, Workshop)                           |
| `slug`                 | `string`                                  | URL-friendly session name                                       |
| `track`                | `string` \| `null`                        | Associated track                                                |
| `abstract`             | `string`                                  | Abstract or session description                                 |
| `tweet`                | `string`                                  | Short summary (tweet-style)                                     |
| `duration`             | `string`                                  | Duration in minutes as string                                   |
| `level`                | `string`                                  | Level of session (e.g. beginner, intermediate)                  |
| `delivery`             | `string`                                  | Delivery format (in-person or remote)                           |
| `resources`            | `array[object]` \| `null`                 | Supplementary materials (URL and description)                   |
| `room`                 | `string` \| `null`                        | Assigned room (e.g. "Exhibit Hall" auto-mapped for posters)     |
| `start`                | `datetime` \| `null`                      | ISO datetime of start                                           |
| `end`                  | `datetime` \| `null`                      | ISO datetime of end                                             |
| `website_url`          | `string`                                  | URL of session on the EuroPython site                           |
| `youtube_url`          | `string` \| `null`                        | YouTube link to session video (🎵 never gonna give you up?)     |
| `sessions_in_parallel` | `array[string]` \| `null`                 | Session codes running at the same time                          |
| `sessions_after`       | `array[string]` \| `null`                 | Sessions immediately after this one                             |
| `sessions_before`      | `array[string]` \| `null`                 | Sessions immediately before this one                            |
| `next_session`         | `string` \| `null`                        | Next session in the same room                                   |
| `prev_session`         | `string` \| `null`                        | Previous session in the same room                               |

---

## 🗓️ `schedule.json`

<details>
<summary>Example schedule day</summary>

```json
{
  "days": {
    "2099-07-08": {
      "rooms": ["Room A", "Room B", "Room C"],
      "events": [
        {
          "event_type": "SESSION",
          "code": "OPQ456",
          "slug": "advanced-python",
          "title": "Advanced Python Techniques",
          "session_type": "Tutorial",
          "speakers": [
            {
              "code": "RST789",
              "name": "John Doe",
              "avatar": "https://pretalx.com/media/avatars/picture.jpg",
              "slug": "john-doe",
              "website_url": "https://ep2099.europython.eu/speaker/john-doe"
            }
          ],
          "track": "CPython Internals",
          "tweet": "",
          "level": "advanced",
          "rooms": ["Room C"],
          "start": "2099-07-08T10:00:00+02:00",
          "duration": 90,
          "website_url": "https://ep2099.europython.eu/session/advanced-python"
        },
        {
          "event_type": "BREAK",
          "title": "Coffee Break",
          "duration": 30,
          "rooms": ["Room A", "Room B"],
          "start": "2099-07-08T11:30:00+02:00"
        }
      ]
    }
  }
}
```
</details>

### Fields

| Key         | Type                             | Notes                                                |
|-------------|----------------------------------|------------------------------------------------------|
| `days`      | `dict[date, DaySchedule]`        | Schedule grouped by day                              |
| `rooms`     | `list[string]`                   | All rooms active on that day                         |
| `events`    | `list[Session or Break]`         | Mixed list of sessions and breaks                    |

#### `Session` (EventType = `"SESSION"`)

| Field         | Type                                 | Notes                                               |
|---------------|--------------------------------------|-----------------------------------------------------|
| `event_type`  | `"SESSION"`                          | Constant                                            |
| `code`        | `string`                             | Session code                                        |
| `slug`        | `string`                             | URL-friendly name                                   |
| `title`       | `string`                             | Title of the session                                |
| `session_type`| `string`                             | Talk, Workshop, etc.                                |
| `speakers`    | `array[Speaker]`                     | Mini speaker profiles                               |
| `track`       | `string` \| `null`                   | Optional topic track                                |
| `tweet`       | `string`                             | Short description                                   |
| `level`       | `string`                             | Beginner, Intermediate, etc.                        |
| `rooms`       | `array[string]`                      | One or more rooms                                   |
| `start`       | `datetime`                           | ISO 8601                                            |
| `duration`    | `int`                                | Computed from `total_duration / slot_count`         |
| `website_url` | `string`                             | Link to session page                                |

#### `Break` (EventType = `"BREAK"`)

| Field         | Type              | Notes                          |
|---------------|-------------------|--------------------------------|
| `event_type`  | `"BREAK"`         | Constant                       |
| `title`       | `string`          | Name of the break              |
| `duration`    | `int`             | Minutes                        |
| `rooms`       | `array[string]`   | Rooms where the break applies |
| `start`       | `datetime`        | Start time                     |

---

### 🛠 Notes & Logic

- `room` normalization maps `"Main Hall"` sessions to `"Exhibit Hall"` — Poster sessions rejoice!
- All `"Registration & Welcome"` events automatically include **all active rooms**.
- Various `social_*_url` fields handle malformed inputs like `@name`, full URLs, or just `username`.
