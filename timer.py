import tkinter as tk
import tkinter.ttk as ttk
import json
from datetime import datetime
from radio_handler import search_stations, play_station, stop_station, is_playing, GENRE_TAGS
from ai_handler import get_break_suggestion, get_weekly_summary

# ── Theme ─────────────────────────────────────────────────────────────────────
BG       = "#e7e9d8"
TEAL     = "#03695e"
BLUE     = "#1a8fbf"
WHITE    = "#ffffff"
BREAK_BG = "#d6eef8"
GREEN    = "#6daf5f"
MUTED    = "#a5c6db"
FONT     = "Press Start 2P"

# ── State ─────────────────────────────────────────────────────────────────────
is_running        = False
timer_id          = None
session_type      = "Work"
work_duration     = 25 * 60
break_duration    = 5  * 60
remaining_seconds = work_duration
session_count     = 0
study_sessions    = []
station_list      = []
todo_items        = []
weekly_goal_hours = 10

# ── Label-based button (Mac-safe colored button) ──────────────────────────────
def btn(parent, text, cmd, w=9, sz=11, color=BLUE):
    return tk.Button(
        parent, text=text, command=cmd,
        font=(FONT, sz),
        fg="black",
        relief="groove", bd=2,
        padx=10, pady=8,
        width=w,
        cursor="hand2",
    )

# ── Radio ─────────────────────────────────────────────────────────────────────
def load_stations_for_genre(event=None):
    tag = genre_var.get()
    status_var.set("loading...")
    window.update_idletasks()
    stations = search_stations(tag, limit=15)
    global station_list
    station_list = stations
    station_combo["values"] = [s[0] for s in stations]
    if stations:
        station_combo.current(0)
        status_var.set(f"{len(stations)} stations found")
    else:
        status_var.set("no stations found")

def toggle_radio():
    if is_playing():
        stop_station()
        radio_btn.config(text="▶ play")
        status_var.set("stopped")
    else:
        idx = station_combo.current()
        if idx < 0 or not station_list:
            status_var.set("pick a genre + station first")
            return
        _, url = station_list[idx]
        play_station(url)
        radio_btn.config(text="■ stop")
        status_var.set(f"♪ {station_list[idx][0][:24]}")

# ── Todo ──────────────────────────────────────────────────────────────────────
def add_todo(text=None):
    if text is None:
        text = todo_entry.get().strip()
    if not text or text == "add a task...":
        return
    todo_entry.delete(0, tk.END)
    var = tk.BooleanVar(value=False)
    row = tk.Frame(todo_body, bg=WHITE)
    row.pack(fill="x", pady=2, padx=6)
    cb_box = tk.Label(row, text="☐", font=(FONT, 16), bg=WHITE, fg=TEAL, cursor="hand2", width=2)
    cb_box.pack(side="left", padx=(4,4))
    lbl = tk.Label(row, text=text, font=(FONT, 11), bg=WHITE, fg=TEAL, anchor="w", cursor="hand2")
    lbl.pack(side="left", fill="x", expand=True, pady=5)
    del_lbl = tk.Label(row, text="x", font=(FONT, 11), bg=WHITE, fg=MUTED, cursor="hand2")
    del_lbl.pack(side="right", padx=8)
    item = {"text": text, "done": var, "frame": row, "label": lbl, "check": cb_box}
    todo_items.append(item)
    def toggle(e, it=item):
        it["done"].set(not it["done"].get())
        if it["done"].get():
            it["check"].config(text="☑", fg=GREEN)
            it["label"].config(fg=MUTED)
        else:
            it["check"].config(text="☐", fg=TEAL)
            it["label"].config(fg=TEAL)
        save_todos()
    def delete(e, it=item, r=row):
        todo_items.remove(it)
        r.destroy()
        save_todos()
    cb_box.bind("<Button-1>", toggle)
    lbl.bind("<Button-1>", toggle)
    del_lbl.bind("<Button-1>", delete)
    save_todos()

def save_todos():
    data = [{"text": it["text"], "done": it["done"].get()} for it in todo_items]
    with open("todos.json", "w") as f:
        json.dump(data, f, indent=2)

def load_todos():
    try:
        with open("todos.json", "r") as f:
            data = json.load(f)
        for item in data:
            add_todo(item["text"])
            if item.get("done") and todo_items:
                last = todo_items[-1]
                last["done"].set(True)
                last["check"].config(text="☑", fg=GREEN)
                last["label"].config(fg=MUTED)
    except FileNotFoundError:
        pass

# ── Progress ──────────────────────────────────────────────────────────────────
def update_progress():
    total = work_duration
    pct = (total - remaining_seconds) / total if total > 0 else 0
    pb_fill.place(relx=0, rely=0, relwidth=pct, relheight=1.0)

def update_weekly_goal():
    total_mins = sum(s.get("duration", 0) for s in study_sessions if s.get("type") == "Work")
    total_hrs  = total_mins / 60
    pct = min(total_hrs / weekly_goal_hours, 1.0)
    goal_fill.place(relx=0, rely=0, relwidth=pct, relheight=1.0)
    goal_label_var.set(f"{total_hrs:.1f}h / {weekly_goal_hours}h")

# ── Timer mode colors ─────────────────────────────────────────────────────────
def set_work_colors():
    timer_box.config(bg=WHITE, highlightbackground=TEAL)
    time_label.config(bg=WHITE, fg=TEAL)
    count_label.config(bg=WHITE)

def set_break_colors():
    timer_box.config(bg=BREAK_BG, highlightbackground=BLUE)
    time_label.config(bg=BREAK_BG, fg=BLUE)
    count_label.config(bg=BREAK_BG)

# ── Timer logic ───────────────────────────────────────────────────────────────
def start_timer():
    global is_running
    is_running = True
    countdown(remaining_seconds)

def pause_timer():
    global is_running, timer_id
    is_running = False
    if timer_id:
        window.after_cancel(timer_id)

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
    pb_fill.place(relwidth=0)

def countdown(seconds):
    global is_running, timer_id, remaining_seconds, session_count
    if seconds > 0 and is_running:
        remaining_seconds = seconds
        time_label.config(text=f"{seconds//60:02d}:{seconds%60:02d}")
        update_progress()
        timer_id = window.after(1000, countdown, seconds - 1)
    elif seconds == 0 and is_running:
        time_label.config(text="00:00")
        is_running = False
        pb_fill.place(relwidth=1.0)
        if session_type == "Work":
            session_count += 1
            count_label.config(text=f"🌿 session {session_count} of 4")
            save_session()
            update_weekly_goal()
        session_complete()

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
    notes = notes_entry.get("1.0", tk.END).strip()
    done_tasks = [it["text"] for it in todo_items if it["done"].get()]
    open_tasks = [it["text"] for it in todo_items if not it["done"].get()]
    if topic:
        study_sessions.append({
            "topic": topic, "notes": notes,
            "completed_tasks": done_tasks, "incomplete_tasks": open_tasks,
            "type": session_type,
            "duration": work_duration // 60 if session_type == "Work" else break_duration // 60,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        with open("study_sessions.json", "w") as f:
            json.dump(study_sessions, f, indent=4)

def load_sessions():
    global study_sessions
    try:
        with open("study_sessions.json", "r") as f:
            study_sessions = json.load(f)
    except FileNotFoundError:
        study_sessions = []

def apply_settings():
    global work_duration, break_duration, remaining_seconds, weekly_goal_hours
    try:
        work_duration     = int(work_entry.get()) * 60
        break_duration    = int(break_entry.get()) * 60
        weekly_goal_hours = int(goal_entry.get())
        if session_type == "Work":
            remaining_seconds = work_duration
            time_label.config(text=f"{work_duration//60:02d}:00")
        else:
            remaining_seconds = break_duration
            time_label.config(text=f"{break_duration//60:02d}:00")
        update_weekly_goal()
    except ValueError:
        pass

def switch_to_work():
    global session_type, remaining_seconds
    session_type = "Work"
    remaining_seconds = work_duration
    session_badge.config(text="🌱 work session")
    time_label.config(text=f"{work_duration//60:02d}:00")
    set_work_colors()
    reset_timer()

def switch_to_break():
    global session_type, remaining_seconds
    session_type = "Break"
    remaining_seconds = break_duration
    session_badge.config(text="☕ break session")
    time_label.config(text=f"{break_duration//60:02d}:00")
    set_break_colors()
    reset_timer()

def view_history():
    hw = tk.Toplevel(window)
    hw.title("Study History")
    hw.configure(bg=BG)
    tk.Label(hw, text="📋 study history", font=(FONT, 13),
             bg=TEAL, fg=WHITE, padx=10, pady=8).pack(fill="x")
    if not study_sessions:
        tk.Label(hw, text="no sessions yet!", font=(FONT, 12),
                 bg=BG, fg=TEAL, pady=20).pack()
        return
    for s in study_sessions:
        row = tk.Frame(hw, bg=WHITE, highlightthickness=1, highlightbackground=TEAL)
        row.pack(fill="x", padx=10, pady=3)
        tk.Label(row, text=f"{s['date']}  |  {s['type'].lower()}  |  {s['topic']}  |  {s['duration']}min",
                 font=(FONT, 10), bg=WHITE, fg=TEAL, anchor="w", padx=8, pady=6).pack(fill="x")

def show_weekly_summary():
    summary = get_weekly_summary(study_sessions)
    sw = tk.Toplevel(window)
    sw.title("Weekly Summary")
    sw.configure(bg=BG)
    tk.Label(sw, text="✨ weekly summary", font=(FONT, 13),
             bg=TEAL, fg=WHITE, padx=10, pady=8).pack(fill="x")
    tk.Label(sw, text=summary, font=(FONT, 11), bg=WHITE, fg=TEAL,
             wraplength=420, justify="left", padx=16, pady=16).pack(padx=10, pady=10)

def on_close():
    stop_station()
    window.destroy()

# ── Window ────────────────────────────────────────────────────────────────────
window = tk.Tk()
window.title("🌿 pomodoro.exe")
window.configure(bg=BG)
window.minsize(540, 600)
window.protocol("WM_DELETE_WINDOW", on_close)

# ── Scroll setup ──────────────────────────────────────────────────────────────
main_canvas = tk.Canvas(window, bg=BG, bd=0, highlightthickness=0)
scrollbar = tk.Scrollbar(window, orient="vertical", command=main_canvas.yview)
main_canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
main_canvas.pack(side="left", fill="both", expand=True)

body = tk.Frame(main_canvas, bg=BG)
body_id = main_canvas.create_window((0, 0), window=body, anchor="nw")

def on_body_configure(e):
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))
body.bind("<Configure>", on_body_configure)

def on_canvas_configure(e):
    main_canvas.itemconfig(body_id, width=e.width)
main_canvas.bind("<Configure>", on_canvas_configure)

def _scroll(e):
    # Mac trackpad sends large deltas; normalize
    delta = e.delta
    if abs(delta) >= 100:
        delta = delta // 100
    main_canvas.yview_scroll(-delta, "units")

window.bind_all("<MouseWheel>", _scroll)

# ── Banner ────────────────────────────────────────────────────────────────────
banner = tk.Canvas(body, height=90, bg="#239dca", bd=0, highlightthickness=0)
banner.pack(fill="x")

def draw_banner(e=None):
    banner.delete("all")
    w = banner.winfo_width() or 540
    banner.create_rectangle(0, 0, w, 90, fill="#239dca", outline="")
    banner.create_rectangle(0, 58, w, 90, fill=GREEN, outline="")
    banner.create_rectangle(0, 54, w, 60, fill=TEAL, outline="")
    def cloud(x, y, s=9):
        for dx, dy, cw, ch in [(0,2,2,2),(2,1,4,2),(2,0,3,1),(6,1,2,2),(1,3,6,1)]:
            banner.create_rectangle(x+dx*s, y+dy*s, x+(dx+cw)*s, y+(dy+ch)*s, fill=WHITE, outline="")
    cloud(30, 4); cloud(w//2-60, 8); cloud(w-140, 4)
    mx = w // 2
    banner.create_rectangle(mx-4, 58, mx+4, 72, fill=TEAL, outline="")
    banner.create_rectangle(mx-14, 48, mx+14, 60, fill=GREEN, outline="")
    banner.create_rectangle(mx-20, 40, mx+20, 50, fill=GREEN, outline="")
    for fx in [60, w-70]:
        banner.create_rectangle(fx, 62, fx+9, 70, fill="#e8a87c", outline="")
banner.bind("<Configure>", draw_banner)

# ── Padding frame ─────────────────────────────────────────────────────────────
pad = tk.Frame(body, bg=BG, padx=20, pady=12)
pad.pack(fill="both", expand=True)

# session badge
session_badge = tk.Label(pad, text="🌱 work session",
                          font=(FONT, 11), bg=TEAL, fg=WHITE, padx=10, pady=6)
session_badge.pack(pady=(0, 8))

# timer box
timer_box = tk.Frame(pad, bg=WHITE, highlightthickness=3, highlightbackground=TEAL)
timer_box.pack(fill="x", pady=(0, 4))
time_label = tk.Label(timer_box, text="25:00", font=(FONT, 48),
                      bg=WHITE, fg=TEAL, pady=14)
time_label.pack()
count_label = tk.Label(timer_box, text="🌿 session 0 of 4",
                       font=(FONT, 10), bg=WHITE, fg=GREEN)
count_label.pack(pady=(0, 12))

# progress bar
pb_frame = tk.Frame(pad, bg=BG, highlightthickness=2, highlightbackground=TEAL, height=14)
pb_frame.pack(fill="x", pady=(0, 2))
pb_frame.pack_propagate(False)
pb_fill = tk.Label(pb_frame, bg=BLUE)
pb_fill.place(relx=0, rely=0, relwidth=0, relheight=1.0)
tk.Label(pad, text="session progress", font=(FONT, 8),
         bg=BG, fg=TEAL, anchor="e").pack(fill="x", pady=(0, 8))

# ── work/break + settings block ───────────────────────────────────────────────
mode_row = tk.Frame(pad, bg=BG)
mode_row.pack(pady=(0, 8))
btn(mode_row, "work", switch_to_work, w=9, sz=11).pack(side="left", padx=6)
btn(mode_row, "break", switch_to_break, w=9, sz=11).pack(side="left", padx=6)

# start pause reset
ctrl_row = tk.Frame(pad, bg=BG)
ctrl_row.pack(pady=(0, 10))
btn(ctrl_row, "▶ start", start_timer, w=9, sz=11).pack(side="left", padx=6)
btn(ctrl_row, "⏸ pause", pause_timer, w=9, sz=11).pack(side="left", padx=6)
btn(ctrl_row, "↺ reset", reset_timer, w=9, sz=11).pack(side="left", padx=6)

# settings
settings_box = tk.Frame(pad, bg=WHITE, highlightthickness=2, highlightbackground=TEAL)
settings_box.pack(fill="x", pady=(0, 10))
sinner = tk.Frame(settings_box, bg=WHITE)
sinner.pack(padx=10, pady=8)
tk.Label(sinner, text="work:", font=(FONT, 9), bg=WHITE, fg=TEAL).pack(side="left", padx=(0,3))
work_entry = tk.Entry(sinner, width=3, font=(FONT, 9), bg=BG, fg=TEAL,
                      relief="flat", bd=1, insertbackground=TEAL)
work_entry.insert(0, "25")
work_entry.pack(side="left", padx=(0,10))
tk.Label(sinner, text="break:", font=(FONT, 9), bg=WHITE, fg=TEAL).pack(side="left", padx=(0,3))
break_entry = tk.Entry(sinner, width=3, font=(FONT, 9), bg=BG, fg=TEAL,
                       relief="flat", bd=1, insertbackground=TEAL)
break_entry.insert(0, "5")
break_entry.pack(side="left", padx=(0,10))
tk.Label(sinner, text="goal hrs:", font=(FONT, 9), bg=WHITE, fg=TEAL).pack(side="left", padx=(0,3))
goal_entry = tk.Entry(sinner, width=3, font=(FONT, 9), bg=BG, fg=TEAL,
                      relief="flat", bd=1, insertbackground=TEAL)
goal_entry.insert(0, "10")
goal_entry.pack(side="left", padx=(0,10))
btn(sinner, "apply", apply_settings, w=9, sz=9).pack(side="left")

tk.Frame(pad, bg=TEAL, height=2).pack(fill="x", pady=(0, 10))

# weekly goal bar
goal_outer = tk.Frame(pad, bg=WHITE, highlightthickness=2, highlightbackground=BLUE)
goal_outer.pack(fill="x", pady=(0, 10))
goal_inner = tk.Frame(goal_outer, bg=WHITE)
goal_inner.pack(fill="x", padx=8, pady=7)
tk.Label(goal_inner, text="weekly goal", font=(FONT, 8), bg=WHITE, fg=BLUE).pack(side="left")
goal_bar_frame = tk.Frame(goal_inner, bg=BG, highlightthickness=1,
                           highlightbackground=BLUE, height=12)
goal_bar_frame.pack(side="left", fill="x", expand=True, padx=8)
goal_bar_frame.pack_propagate(False)
goal_fill = tk.Label(goal_bar_frame, bg=BLUE)
goal_fill.place(relx=0, rely=0, relwidth=0.0, relheight=1.0)
goal_label_var = tk.StringVar(value="0.0h / 10h")
tk.Label(goal_inner, textvariable=goal_label_var, font=(FONT, 8), bg=WHITE, fg=BLUE).pack(side="left")

# studying
study_row = tk.Frame(pad, bg=WHITE, highlightthickness=2, highlightbackground=TEAL)
study_row.pack(fill="x", pady=(0, 8))
tk.Label(study_row, text="studying:", font=(FONT, 10),
         bg=WHITE, fg=TEAL, padx=8, pady=7).pack(side="left")
topic_entry = tk.Entry(study_row, font=(FONT, 10), bg=WHITE, fg=TEAL,
                       relief="flat", bd=0, insertbackground=TEAL)
topic_entry.pack(side="left", fill="x", expand=True, padx=(0,8))

# notes
notes_outer = tk.Frame(pad, bg=WHITE, highlightthickness=2, highlightbackground=GREEN)
notes_outer.pack(fill="x", pady=(0, 10))
tk.Label(notes_outer, text="session notes", font=(FONT, 8),
         bg=WHITE, fg=GREEN, padx=8, pady=5, anchor="w").pack(fill="x")
notes_entry = tk.Text(notes_outer, font=(FONT, 9), bg=WHITE, fg=TEAL,
                      relief="flat", bd=0, height=3, insertbackground=TEAL,
                      wrap="word", padx=8, pady=4)
notes_entry.insert("1.0", "how did it go?")
notes_entry.bind("<FocusIn>", lambda e: notes_entry.delete("1.0", tk.END)
                 if notes_entry.get("1.0", tk.END).strip() == "how did it go?" else None)
notes_entry.pack(fill="x")

# radio
radio_outer = tk.Frame(pad, bg=WHITE, highlightthickness=2, highlightbackground=BLUE)
radio_outer.pack(fill="x", pady=(0, 10))
radio_head = tk.Frame(radio_outer, bg=BLUE)
radio_head.pack(fill="x")
tk.Label(radio_head, text="📻 radio", font=(FONT, 10),
         bg=BLUE, fg=WHITE, padx=8, pady=5).pack(side="left")

genre_row_f = tk.Frame(radio_outer, bg=WHITE)
genre_row_f.pack(fill="x", padx=8, pady=(7,3))
tk.Label(genre_row_f, text="genre:", font=(FONT, 9), bg=WHITE, fg=BLUE).pack(side="left")
genre_var = tk.StringVar(value=GENRE_TAGS[0])
genre_combo = ttk.Combobox(genre_row_f, textvariable=genre_var, values=GENRE_TAGS,
                            width=14, state="readonly", font=(FONT, 9))
genre_combo.pack(side="left", padx=6)
btn(genre_row_f, "load", load_stations_for_genre, w=9, sz=9).pack(side="left")

station_row_f = tk.Frame(radio_outer, bg=WHITE)
station_row_f.pack(fill="x", padx=8, pady=(0,6))
tk.Label(station_row_f, text="station:", font=(FONT, 9), bg=WHITE, fg=BLUE).pack(side="left")
station_combo = ttk.Combobox(station_row_f, width=28, state="readonly", font=(FONT, 9))
station_combo.pack(side="left", padx=6)

radio_ctrl_f = tk.Frame(radio_outer, bg=WHITE)
radio_ctrl_f.pack(pady=(0,6))
radio_btn = btn(radio_ctrl_f, "▶ play", toggle_radio, w=9, sz=10)
radio_btn.pack()
radio_lbl = radio_btn
status_var = tk.StringVar(value="pick a genre and click load")
tk.Label(radio_outer, textvariable=status_var, font=(FONT, 8),
         bg=WHITE, fg=MUTED).pack(pady=(0,6))

# tasks
tasks_outer = tk.Frame(pad, bg=WHITE, highlightthickness=3, highlightbackground=TEAL)
tasks_outer.pack(fill="x", pady=(0, 10))
tk.Frame(tasks_outer, bg=TEAL).pack(fill="x")
tasks_head = tk.Frame(tasks_outer, bg=TEAL)
tasks_head.pack(fill="x")
tk.Label(tasks_head, text="📋 tasks", font=(FONT, 10),
         bg=TEAL, fg=WHITE, padx=8, pady=6).pack(side="left")

todo_body = tk.Frame(tasks_outer, bg=WHITE)
todo_body.pack(fill="x", padx=4, pady=4)

add_row_f = tk.Frame(tasks_outer, bg=WHITE)
add_row_f.pack(fill="x", padx=10, pady=(0,8))
tk.Label(add_row_f, text="+", font=(FONT, 14), bg=WHITE, fg=MUTED).pack(side="left", padx=(0,6))
todo_entry = tk.Entry(add_row_f, font=(FONT, 10), bg=WHITE, fg=TEAL,
                      relief="flat", bd=0, insertbackground=TEAL)
todo_entry.insert(0, "add a task...")
todo_entry.bind("<FocusIn>", lambda e: todo_entry.delete(0, tk.END)
                if todo_entry.get() == "add a task..." else None)
todo_entry.bind("<Return>", lambda e: add_todo())
todo_entry.pack(side="left", fill="x", expand=True)
btn(add_row_f, "add", add_todo, w=9, sz=9).pack(side="right")

tk.Frame(pad, bg=TEAL, height=2).pack(fill="x", pady=10)

# history / summary
sec_row = tk.Frame(pad, bg=BG)
sec_row.pack(pady=(0, 20))
btn(sec_row, "📋 history", view_history, w=9, sz=10).pack(side="left", padx=6)
btn(sec_row, "✨ summary", show_weekly_summary, w=9, sz=10).pack(side="left", padx=6)

load_sessions()
update_weekly_goal()
window.after(100, load_todos)
window.mainloop()