import tkinter as tk
from library import functions
from library.classes_9 import Budget
import os

# Main Window
window = tk.Tk()

# Sets Title and Size of Window
window.title("BudgetBuddy")
window.geometry("1050x600")  # Bigger window for logo + content

# Variables
user_name = tk.StringVar()
income = tk.DoubleVar()
grocery = Budget("Grocery")

def fade_in(label, step=0):
    if step > 10:
        return
    gray = int(255 - (step * 20))               # from 255 → ~55
    color = f"#{gray:02x}{gray:02x}{gray:02x}" # grayscale
    label.config(fg=color)
    window.after(40, lambda: fade_in(label, step + 1))

def fade_out(label, step=0):
    if step > 10:
        return
    gray = int(55 + (step * 20))               # from ~55 → 255
    color = f"#{gray:02x}{gray:02x}{gray:02x}"
    label.config(fg=color)
    window.after(40, lambda: fade_out(label, step + 1))

# Start screen with logo and name input
start_frame = tk.Frame(window)
start_frame.pack(fill="both", expand=True)

### Sets logo at top
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "BBlogo.png")
logo = tk.PhotoImage(file=logo_path)
logo_label = tk.Label(start_frame, image=logo)
logo_label.pack(pady=10)

### Name input
tk.Label(start_frame, text="To begin, enter your name:").pack(pady=10)
name_entry = tk.Entry(start_frame)
name_entry.pack()
msg_label = tk.Label(start_frame, fg="blue")
msg_label.pack(pady=5)

def start_app():
    name = name_entry.get().strip()
    if not name:
        msg_label.config(text="Enter a valid name.")
        return
    
    fade_out(name_entry)               # fade out start text
    fade_out(msg_label)

    window.after(450, next_screen)      # delay until fade ends

def next_screen():
    user_name.set(name_entry.get().strip())
    start_frame.pack_forget()
    income_frame.pack(fill="both", expand=True)
    welcome_label.config(text=f"Hey {user_name.get()}, welcome to BudgetBuddy!")
    fade_in(welcome_label)

tk.Button(start_frame, text="Begin", command=start_app).pack(pady=10)
