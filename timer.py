import tkinter as tk
is_running = False
timer_id = None
session_type = "Work"
work_duration = 25 * 60
break_duration = 5 * 60
remaining_seconds = work_duration

# Create the main window
def start_timer():
    global is_running, remaining_seconds
    is_running = True
    countdown(remaining_seconds)

def pause_timer():
    global is_running, timer_id, remaining_seconds
    is_running = False
    if timer_id:
        window.after_cancel(timer_id)

def reset_timer():
    global is_running, timer_id, remaining_seconds
    is_running = False
    if timer_id:
        window.after_cancel(timer_id)
    remaining_seconds = 25 * 60
    time_label.config(text="25:00")

def countdown(seconds):
    global is_running, timer_id, remaining_seconds
    if seconds >= 0 and is_running:
        remaining_seconds = seconds
        mins = seconds // 60
        secs = seconds % 60
        time_label.config(text=f"{mins:02d}:{secs:02d}")
        timer_id = window.after(1000, countdown, seconds - 1)
window = tk.Tk()
window.title("Pomodoro Timer")

# Label to display the time
time_label = tk.Label(window, text="25:00", font=("Arial", 48))
time_label.pack(pady=20)

# Session type label
session_label = tk.Label(window, text="Work Session", font=("Arial", 20))
session_label.pack(pady=10)

# Session type buttons
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

button_frame = tk.Frame(window)
button_frame.pack(pady=10)

work_btn = tk.Button(button_frame, text="Work", font=("Arial", 14), command=switch_to_work)
work_btn.pack(side=tk.LEFT, padx=5)

break_btn = tk.Button(button_frame, text="Break", font=("Arial", 14), command=switch_to_break)
break_btn.pack(side=tk.LEFT, padx=5)

#Start button
start_button = tk.Button(window, text="Start", font=("Arial", 16), command=start_timer)
start_button.pack(pady=10)

# Pause Button
pause_button = tk.Button(window, text="Pause", font=("Arial", 16), command=pause_timer)
pause_button.pack(pady=10)

# Reset Button
reset_button = tk.Button(window, text="Reset", font=("Arial", 16), command=reset_timer)
reset_button.pack(pady=10)

# Run the window
window.mainloop()