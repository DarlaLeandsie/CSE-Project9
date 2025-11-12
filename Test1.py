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

# Income Screen
income_frame = tk.Frame(window)

welcome_label = tk.Label(income_frame, text="", fg="blue")
welcome_label.pack(pady=5)

tk.Label(income_frame, text="Enter your monthly income:").pack(pady=10)
income_entry = tk.Entry(income_frame)
income_entry.pack()
income_error = tk.Label(income_frame, fg="red")
income_error.pack(pady=5)

def save_income():
    income_error.config(text="")
    try:
        income_value = float(income_entry.get())
        income.set(income_value)

        fade_out(welcome_label)

        window.after(450, lambda: (
            income_frame.pack_forget(),
            income_frame.pack(fill="both", expand=True)
        ))
    except ValueError:
        income_error.config(text="You must enter a valid number as your income.")

tk.Button(income_frame, text="Continue", command=save_income).pack(pady=10)

# Expenses Screen
expense_frame = tk.Frame(window)

tk.Label(expense_frame, text="Add Expense").pack(pady=10)

tk.Label(expense_frame, text="Category:").pack()
category_entry = tk.Entry(expense_frame)
category_entry.pack()

tk.Label(expense_frame, text="Amount:").pack()
amount_entry = tk.Entry(expense_frame)
amount_entry.pack()

expense_error = tk.Label(expense_frame, fg="red")
expense_error.pack(pady=5)

expense_success = tk.Label(expense_frame, fg="green")
expense_success.pack(pady=5)

def add_grocery_expense():
    #Clear previous messages
    expense_error.config(text='')
    expense_success.config(text='')

    category = category_entry.get().strip()
    value = amount_entry.get().strip()

    if not category:
        expense_error.config(text="Enter a valid category.")
        return
    try:
        val = float(value)
    except ValueError:
        expense_error.config(text="Amount must be a number.")
        return
    
    grocery.categories.append(category)
    grocery.expenses.append(val)
    
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    
    expense_success.config(text="Expense added.")

tk.Button(expense_frame, text="Add Expense", command=add_grocery_expense).pack(pady=5)

def finish_grocery():
    total = sum(grocery.expenses)
    bal = functions.calc_balance(income.get(), total)
    
    expense_frame.pack_forget()
    result_frame.pack(fill="both", expand=True)
    
    result_label.config(text=f"Total Grocery: ${total:.2f}\nRemaining Balance: ${bal:.2f}")
    
    expense_list.delete(0, tk.END)
    for c, e in zip(grocery.categories, grocery.expenses):
        expense_list.insert(tk.END, f"{c}: ${e:.2f}")

tk.Button(expense_frame, text="Finish", command=finish_grocery).pack(pady=10)

# ------------------ Frame 4: Results ------------------
result_frame = tk.Frame(window)

result_label = tk.Label(result_frame, text="", font=("Times New Roman", 12))
result_label.pack(pady=10)

expense_list = tk.Listbox(result_frame)
expense_list.pack(fill="both", expand=True, pady=5)

# ------------------ Run App ------------------
window.mainloop()
