# Creates a blank window

import tkinter as tk
from library import functions
from library.classes_9 import Budget
import os

# Main Window
window = tk.Tk()

# Sets Title and Size of Window
window.title("BudgetBuddy")
window.geometry("1050x600")  # Bigger window for logo + content

# Runs GUI
window.mainloop()
