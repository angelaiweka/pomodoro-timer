import tkinter as tk
import json
from datetime import datetime
from spotify_handler import create_spotify_client, get_playlists, play_playlist, pause_music, resume_music
from ai_handler import get_break_suggestion, get_weekly_summary

is_running = False
timer_id = None
session_type = "Work"
work_duration = 25 * 60
break_duration = 5 * 60
remaining_seconds = work_duration
session_count = 0
study_sessions = []
sp = None
selected_playlist_uri = None

# Functions
def start_timer():
    global is_running, remaining_seconds, selected_playlist_uri
    is_running = True
    if sp:
        idx = playlist_dropdown.current()
        if idx >= 0:
            selected_playlist_uri = playlist_dropdown.playlist_uris[idx]
            play_playlist(sp, selected_playlist_uri)
    countdown(remaining_seconds)

def pause_timer():
    global is_running, timer_id, remaining_seconds
    is_running = False
    if timer_id:
        window.after_cancel(timer_id)
    if sp:
        pause_music(sp)

def reset_timer():
    global is_running, timer_id, remaining_seconds
    is_running = False
    if timer_id:
        window.after_cancel(timer_id)
    if session_type == "Work":
        remaining_seconds = work_duration
        time_label.config(text=f"{work_duration//60:02d}:00")
    else:
        remaining_seconds = break_duration
        time_label.config(text=f"{break_duration//60:02d}:00")

def session_complete():
    from tkinter import messagebox
    if session_type == "Work":
        topic = topic_entry.get()
        if topic:
            suggestion = get_break_suggestion(topic)
            messagebox.showinfo("Break Time!", f"Work session done!\n\n💡 Break idea:\n{suggestion}")
        else:
            messagebox.showinfo("Session Complete", "Work session done! Time for a break.")
    else:
        messagebox.showinfo("Session Complete", "Break's over! Ready to work?")

def save_session():
    topic = topic_entry.get()
    if topic:
        session_data = {
            "topic": topic,
            "type": session_type,
            "duration": work_duration // 60 if session_type == "Work" else break_duration // 60,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        study_sessions.append(session_data)
        with open("study_sessions.json", "w") as f:
            json.dump(study_sessions, f, indent=4)
        print(f"Saved: {session_data}")

def load_sessions():
    global study_sessions
    try:
        with open("study_sessions.json", "r") as f:
            study_sessions = json.load(f)
    except FileNotFoundError:
        study_sessions = []

def countdown(seconds):
    global is_running, timer_id, remaining_seconds, session_count
    if seconds > 0 and is_running:
        remaining_seconds = seconds
        mins = seconds // 60
        secs = seconds % 60
        time_label.config(text=f"{mins:02d}:{secs:02d}")
        timer_id = window.after(1000, countdown, seconds - 1)
    elif seconds == 0 and is_running:
        time_label.config(text="00:00")
        is_running = False
        if session_type == "Work":
            session_count += 1
            count_label.config(text=f"Sessions: {session_count}")
            save_session()
        session_complete()

def apply_settings():
    global work_duration, break_duration, remaining_seconds
    try:
        work_duration = int(work_entry.get()) * 60
        break_duration = int(break_entry.get()) * 60
        if session_type == "Work":
            remaining_seconds = work_duration
            time_label.config(text=f"{work_duration//60:02d}:00")
        else:
            remaining_seconds = break_duration
            time_label.config(text=f"{break_duration//60:02d}:00")
    except ValueError:
        pass

def switch_to_work():
    global session_type, remaining_seconds
    session_type = "Work"
    remaining_seconds = work_duration
    session_label.config(text="Work Session")
    time_label.config(text=f"{work_duration//60:02d}:00")
    reset_timer()

def switch_to_break():
    global session_type, remaining_seconds
    session_type = "Break"
    remaining_seconds = break_duration
    session_label.config(text="Break Session")
    time_label.config(text=f"{break_duration//60:02d}:00")
    reset_timer()

def view_history():
    history_window = tk.Toplevel(window)
    history_window.title("Study History")
    if not study_sessions:
        tk.Label(history_window, text="No sessions yet!", font=("Arial", 14)).pack(pady=20)
        return
    for session in study_sessions:
        text = f"{session['date']} | {session['type']} | {session['topic']} | {session['duration']} min"
        tk.Label(history_window, text=text, font=("Arial", 12)).pack(anchor="w", padx=10, pady=2)

def init_spotify():
    global sp
    try:
        sp = create_spotify_client()
        playlists = get_playlists(sp)
        playlist_dropdown['values'] = [p[0] for p in playlists]
        playlist_dropdown.playlist_uris = [p[1] for p in playlists]
        if playlists:
            playlist_dropdown.current(0)
    except Exception as e:
        print(f"Spotify init error: {e}")

def show_weekly_summary():
    summary = get_weekly_summary(study_sessions)
    summary_window = tk.Toplevel(window)
    summary_window.title("Weekly Summary")
    tk.Label(summary_window, text=summary, font=("Arial", 12), wraplength=400, justify="left").pack(padx=20, pady=20)

# Create window
window = tk.Tk()
window.title("Pomodoro Timer")

# Time display
time_label = tk.Label(window, text="25:00", font=("Arial", 48))
time_label.pack(pady=20)

# Session type label
session_label = tk.Label(window, text="Work Session", font=("Arial", 20))
session_label.pack(pady=10)

# Session counter
count_label = tk.Label(window, text="Sessions: 0", font=("Arial", 16))
count_label.pack(pady=5)

# Study topic input
topic_frame = tk.Frame(window)
topic_frame.pack(pady=10)

# Spotify controls
spotify_frame = tk.Frame(window)
spotify_frame.pack(pady=10)

tk.Label(spotify_frame, text="Playlist:", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)

import tkinter.ttk as ttk
playlist_dropdown = ttk.Combobox(spotify_frame, width=30, font=("Arial", 12))
playlist_dropdown.pack(side=tk.LEFT, padx=5)

spotify_btn = tk.Button(spotify_frame, text="Connect Spotify", font=("Arial", 12), command=init_spotify)
spotify_btn.pack(side=tk.LEFT, padx=5)

tk.Label(topic_frame, text="Studying:", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)
topic_entry = tk.Entry(topic_frame, width=30, font=("Arial", 14))
topic_entry.pack(side=tk.LEFT, padx=5)

# Work/Break buttons
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

work_btn = tk.Button(button_frame, text="Work", font=("Arial", 14), command=switch_to_work)
work_btn.pack(side=tk.LEFT, padx=5)

break_btn = tk.Button(button_frame, text="Break", font=("Arial", 14), command=switch_to_break)
break_btn.pack(side=tk.LEFT, padx=5)

# View History button
history_button = tk.Button(window, text="View History", font=("Arial", 16), command=view_history)
history_button.pack(pady=10)

#AI Summary Button
summary_button = tk.Button(window, text="Weekly Summary", font=("Arial", 16), command=show_weekly_summary)
summary_button.pack(pady=10)

# Settings
settings_frame = tk.Frame(window)
settings_frame.pack(pady=10)

tk.Label(settings_frame, text="Work (min):", font=("Arial", 12)).grid(row=0, column=0, padx=5)
work_entry = tk.Entry(settings_frame, width=5, font=("Arial", 12))
work_entry.insert(0, "25")
work_entry.grid(row=0, column=1, padx=5)

tk.Label(settings_frame, text="Break (min):", font=("Arial", 12)).grid(row=0, column=2, padx=10)
break_entry = tk.Entry(settings_frame, width=5, font=("Arial", 12))
break_entry.insert(0, "5")
break_entry.grid(row=0, column=3, padx=(10, 5))

apply_btn = tk.Button(settings_frame, text="Apply", font=("Arial", 12), command=apply_settings)
apply_btn.grid(row=0, column=4, padx=5)

# Control buttons
start_button = tk.Button(window, text="Start", font=("Arial", 16), command=start_timer)
start_button.pack(pady=10)

pause_button = tk.Button(window, text="Pause", font=("Arial", 16), command=pause_timer)
pause_button.pack(pady=10)

reset_button = tk.Button(window, text="Reset", font=("Arial", 16), command=reset_timer)
reset_button.pack(pady=10)

load_sessions()
window.mainloop()