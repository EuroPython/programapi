# 🎤 programapi

This project powers the **EuroPython 2026** website, Discord bot, and internal bot 🦜 by downloading, transforming, and serving clean, structured JSON files for sessions, speakers, and the schedule, all pulled from Pretalx.

Built for transparency. Designed for reuse. Optimized for EuroPython.

---

## 🚀 What This Project Does

1. **Downloads** submission and speaker data from Pretalx.
2. **Transforms** raw data:
   - Removes private/irrelevant fields
   - Normalizes formats
   - Adds computed fields (e.g. URLs, delivery mode)
3. **Serves** the transformed JSON files via a static API.

---

## ⚙️ Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/EuroPython/programapi.git
   cd programapi
   ```

2. **Install [uv](https://docs.astral.sh/uv/getting-started/installation/)** (fast Python package manager)

3. **Create a Python 3.13 virtual environment**
   ```bash
   uv venv -p 3.13
   ```

4. **Install dev dependencies**
   ```bash
   make dev
   ```

5. **Enable pre-commit hooks**
   ```bash
   make pre-commit
   ```

---

## 🛠️ Configuration

You can update the event year or shortname in [`src/config.py`](src/config.py).

Also, create a `.env` file in the project root and set:

```env
PRETALX_TOKEN=your_api_token_here
```

(Yes, Pretalx has rate limits. Please be nice. 🤪)

---

## 📦 Usage

- Run the **entire pipeline**:
  ```bash
  make all
  ```

- Run only the **download step**:
  ```bash
  make download
  ```

- Run only the **transformation step**:
  ```bash
  make transform
  ```

- (Optional) **Exclude components**:
  ```bash
  make all EXCLUDE="schedule youtube"
  ```

---

## 🌐 API Endpoints

Hosted at:

```
https://static.europython.eu/programme/ep2026/releases/current
```

| Endpoint                                                                                            | Description                   |
|-----------------------------------------------------------------------------------------------------|-------------------------------|
| [`/speakers.json`](https://static.europython.eu/programme/ep2026/releases/current/speakers.json)    | List of confirmed speakers    |
| [`/sessions.json`](https://static.europython.eu/programme/ep2026/releases/current/sessions.json)    | List of confirmed sessions    |
| [`/schedule.json`](https://static.europython.eu/programme/ep2026/releases/current/schedule.json)    | Latest conference schedule    |

---

## 📖 Schema Documentation

Looking for field definitions and examples?
Check out the 👉 [`data/examples/README.md`](data/examples/README.md) for a full schema reference with example payloads and explanations.

---

## 💬 Questions? Feedback?

Feel free to open an issue or reach us at [infra@europython.eu](mailto:infra@europython.eu). We love contributors 💜

---

📅 Last updated for: **EuroPython 2026**
