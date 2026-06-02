# pomodoro.exe

A retro pixel-art Pomodoro timer built with Python. Study smarter with live radio, automatic break suggestions, session tracking, and a built-in to-do list.

<img width="531" height="791" alt="Screenshot 2026-06-01 at 9 22 01 PM" src="https://github.com/user-attachments/assets/2f6a4239-4c87-4d89-89ea-db2180261fbc" />
<img width="522" height="222" alt="Screenshot 2026-06-01 at 9 22 36 PM" src="https://github.com/user-attachments/assets/17e0b213-8738-4233-abc7-fb214435a3a2" />

<img width="496" height="441" alt="Screenshot 2026-06-01 at 9 22 59 PM" src="https://github.com/user-attachments/assets/60b47c7e-187b-4750-a528-8085067ab11d" />

---

## Features

- **Pomodoro Timer** — 25/5 minute work and break cycles with a live progress bar
- **Timer modes** — white background for work sessions, soft blue for break sessions
- **Live Radio** — stream stations by genre (lofi, jazz, anime, classical, and more) via the free [Radio Browser API](https://www.radio-browser.info/). No API key needed.
- **To-Do List** — add, check off, and delete tasks inline. Tasks persist across sessions and are included in your weekly summary.
- **Session Notes** — log how each session went. Saved with your session history.
- **Weekly Goal Bar** — track total study hours against a custom weekly target.
- **Break Suggestions** — at the end of each work session, a short creative break idea appears automatically based on what you were studying.
- **Weekly Summary** — a recap of your study patterns, task completion rate, and a personalized tip, generated on demand.
- **Study History** — full log of past sessions with topic, type, duration, notes, and task data.

---

## Requirements

- Python 3.10+
- macOS, Linux, or Windows
- [ffmpeg](https://ffmpeg.org/) (for radio streaming)
- A free [Groq API key](https://console.groq.com)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/pomodoro-timer.git
cd pomodoro-timer
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate       # Mac/Linux
.venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install ffmpeg

```bash
# Mac
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows — download from https://ffmpeg.org/download.html
```

### 5. Install the Press Start 2P font (Mac only)

```bash
brew install --cask font-press-start-2p
```

> On Windows/Linux, the app will fall back to a system monospace font.

### 6. Configure your API key

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

### 7. Run

```bash
python3 timer.py
```

---

## Usage

1. Enter your study topic in the **studying:** field
2. Add tasks for the session in the **tasks** panel
3. Pick a radio genre, click **load**, select a station, and hit **play**
4. Hit **start** and get to work
5. When the session ends a break suggestion will appear automatically
6. Click tasks to check them off as you complete them
7. Use the **summary** button to get your weekly study recap
8. Adjust work/break duration and weekly goal in the settings row, then hit **apply**

---

## Project Structure

```
pomodoro-timer/
├── timer.py              # Main app and UI
├── radio_handler.py      # Radio Browser API + ffplay streaming
├── ai_handler.py         # Groq integration (break suggestions + weekly summary)
├── study_sessions.json   # Auto-generated session history
├── todos.json            # Auto-generated task persistence
├── .env                  # API key (not committed)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
