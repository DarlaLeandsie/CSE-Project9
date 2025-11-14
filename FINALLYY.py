import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from functools import partial
import re

FADE_STEP = 0.1
FADE_DELAY = 50

class ScreenBase(tk.Frame):
    """Base class for screens with fade animation support."""
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.widgets = []

    def on_show(self):
        """Called when screen becomes active."""
        self.fade_in_widgets()

    def fade_in_widgets(self):
        for w in self.widgets:
            try:
                w.grid_remove()
            except:
                pass
        self._fade_in_step(0)

    def _fade_in_step(self, idx):
        if idx >= len(self.widgets):
            return
        self.widgets[idx].grid()
        self.after(FADE_DELAY, lambda: self._fade_in_step(idx + 1))

# ------------------- Splash Screen -------------------
class SplashScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#f7fbff")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        logo_path = "BBlogo.png"
        try:
            self.logo_img = tk.PhotoImage(file=logo_path)
            logo_lbl = tk.Label(self, image=self.logo_img, bg="#f7fbff")
        except:
            logo_lbl = tk.Label(self, text="BudgetBuddy", font=("Inter", 42, "bold"), bg="#f7fbff")
        logo_lbl.grid(row=0, column=0, pady=(120,10))
        self.widgets.append(logo_lbl)

        instr = tk.Label(self, text="(click anywhere to begin)", font=("Helvetica", 14), bg="#f7fbff")
        instr.grid(row=1, column=0, pady=(4,40))
        self.widgets.append(instr)

        self.bind_all("<Button-1>", self._on_click)

    def _on_click(self, event=None):
        self.unbind_all("<Button-1>")
        self.app.show_screen("intro")

# ------------------- Intro Screen -------------------
class IntroScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="white")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        self.title_lbl = tk.Label(self, text="To begin this program, enter your name.", font=("Helvetica", 20), bg="white")
        self.title_lbl.grid(row=0, column=0, pady=(80,18))
        self.widgets.append(self.title_lbl)

        self.name_var = tk.StringVar(value=self.app.state.get("user_name",""))
        self.name_entry = ttk.Entry(self, textvariable=self.name_var, font=("Arial", 14), width=30)
        self.name_entry.grid(row=1, column=0, pady=6)
        self.widgets.append(self.name_entry)

        self.val_lbl = tk.Label(self, text="", font=("Arial", 10), fg="red", bg="white")
        self.val_lbl.grid(row=2, column=0, pady=(6,14))
        self.widgets.append(self.val_lbl)

        # Buttons frame
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.grid(row=3, column=0, pady=(40,12))

        self.back_btn = ttk.Button(btn_frame, text="Back", command=lambda: self.app.show_screen("splash"))
        self.back_btn.grid(row=0, column=0, padx=(0,10))

        self.continue_btn = ttk.Button(btn_frame, text="Continue", command=self.validate)
        self.continue_btn.grid(row=0, column=1, padx=(10,0))

        self.widgets.extend([btn_frame, self.back_btn, self.continue_btn])

    def validate(self):
        name = self.name_var.get().strip()
        if not name:
            self._show_validation("Please enter a name.")
            return
        if not re.fullmatch(r"[A-Za-z ]+", name):
            self._show_validation("Name may only contain letters and spaces.")
            return
        self.app.state["user_name"] = name
        self.app.show_screen("process")

    def _show_validation(self, msg):
        self.val_lbl.config(text=msg)

# ------------------- Process Screen -------------------
class ProcessScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#f0fbf7")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        self.greet_lbl = tk.Label(self, text="", font=("Helvetica", 20, "bold"), bg="#f0fbf7")
        self.greet_lbl.grid(row=0, column=0, pady=(80,12))
        self.widgets.append(self.greet_lbl)

        self.steps_lbl = tk.Label(self, text="You will take the following steps to use BudgetBuddy:", font=("Arial", 12), bg="#f0fbf7")
        self.steps_lbl.grid(row=1, column=0, pady=(6,12))
        self.widgets.append(self.steps_lbl)

        logo_path = "BBlogo.png"
        try:
            self.logo_img = tk.PhotoImage(file=logo_path)
            self.logo_lbl = tk.Label(self, image=self.logo_img, bg="#f0fbf7")
        except:
            self.logo_lbl = tk.Label(self, text="(logo)", font=("Arial",18), bg="#f0fbf7")
        self.logo_lbl.grid(row=2, column=0, pady=(10,20))
        self.widgets.append(self.logo_lbl)

        btn_frame = tk.Frame(self, bg="#f0fbf7")
        btn_frame.grid(row=3, column=0, pady=(40,12))

        self.back_btn = ttk.Button(btn_frame, text="Back", command=lambda: self.app.show_screen("intro"))
        self.back_btn.grid(row=0, column=0, padx=(0,10))

        self.continue_btn = ttk.Button(btn_frame, text="Continue", command=lambda: self.app.show_screen("datafile"))
        self.continue_btn.grid(row=0, column=1, padx=(10,0))

        self.widgets.extend([btn_frame, self.back_btn, self.continue_btn])

    def on_show(self):
        name = self.app.state.get("user_name","User")
        self.greet_lbl.config(text=f"Hey {name}, this is BudgetBuddy! Your personal Budgeting Assistant.")
        self.fade_in_widgets()

# ------------------- Datafile Screen -------------------
# ------------------- Datafile Screen -------------------
class DatafileScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#fff8f0")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        # Question label
        self.label = tk.Label(self, text="Do you want to edit an existing datafile?", font=("Arial", 16), bg="#fff8f0")
        self.label.grid(row=0, column=0, pady=(80,20))
        self.widgets.append(self.label)

        # Yes/No buttons
        self.btn_yesno_frame = tk.Frame(self, bg="#fff8f0")
        self.btn_yesno_frame.grid(row=1, column=0, pady=(0,20))
        self.widgets.append(self.btn_yesno_frame)

        self.yes_btn = ttk.Button(self.btn_yesno_frame, text="Yes", command=self.select_yes)
        self.yes_btn.grid(row=0, column=0, padx=5)
        self.widgets.append(self.yes_btn)

        self.no_btn = ttk.Button(self.btn_yesno_frame, text="No", command=self.select_no)
        self.no_btn.grid(row=0, column=1, padx=5)
        self.widgets.append(self.no_btn)

        # Entry for filename (initially hidden)
        self.entry_label = tk.Label(self, text="", font=("Arial",12), bg="#fff8f0")
        self.entry = ttk.Entry(self, width=30)

        # Back/Continue buttons (always visible, beside each other)
        self.btn_frame = tk.Frame(self, bg="#fff8f0")
        self.btn_frame.grid(row=4, column=0, pady=(10,20))

        self.back_btn = ttk.Button(self.btn_frame, text="Back", command=lambda: self.app.show_screen("process"))
        self.back_btn.grid(row=0, column=0, padx=(0,10))

        self.cont_btn = ttk.Button(self.btn_frame, text="Continue", command=self.save_filename)
        self.cont_btn.grid(row=0, column=1, padx=(10,0))
        self.cont_btn.config(state="disabled")  # disabled until entry is active

        self.widgets.extend([self.btn_frame, self.back_btn, self.cont_btn])

    def select_yes(self):
        self.entry_label.config(text="Enter the name of an existing datafile:")
        self._show_entry()

    def select_no(self):
        self.entry_label.config(text="Enter the name of a new datafile:")
        self._show_entry()

    def _show_entry(self):
        self.entry_label.grid(row=2, column=0, pady=(10,4))
        self.entry.grid(row=3, column=0, pady=(0,10))

        # populate previous if exists
        self.entry.delete(0, tk.END)
        if self.app.state.get("datafile_name"):
            self.entry.insert(0, self.app.state["datafile_name"])

        # enable Continue button
        self.cont_btn.config(state="normal")

        # add entry label and entry to widgets if not already
        for w in [self.entry_label, self.entry]:
            if w not in self.widgets:
                self.widgets.append(w)

    def save_filename(self):
        fname = self.entry.get().strip()
        if not fname:
            messagebox.showerror("Validation", "File name cannot be empty")
            return
        if not re.fullmatch(r"[A-Za-z0-9_]+", fname):
            messagebox.showerror("Validation", "Filename may only contain letters, numbers, underscores")
            return
        self.app.state["datafile_name"] = fname
        self.app.show_screen("income")

# ------------------- Income Screen -------------------
class IncomeScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#f0fff0")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        self.label = tk.Label(self, text="Enter your monthly income:", font=("Arial",16), bg="#f0fff0")
        self.label.grid(row=0, column=0, pady=(80,20))
        self.widgets.append(self.label)

        self.income_var = tk.StringVar(value=str(self.app.state.get("income","")))
        self.entry = ttk.Entry(self, textvariable=self.income_var, font=("Arial",14))
        self.entry.grid(row=1, column=0)
        self.widgets.append(self.entry)

        btn_frame = tk.Frame(self, bg="#f0fff0")
        btn_frame.grid(row=2, column=0, pady=(10,20))

        self.back_btn = ttk.Button(btn_frame, text="Back", command=lambda: self.app.show_screen("datafile"))
        self.back_btn.grid(row=0, column=0, padx=(0,10))

        self.cont_btn = ttk.Button(btn_frame, text="Continue", command=self.save_income)
        self.cont_btn.grid(row=0, column=1, padx=(10,0))

        self.widgets.extend([btn_frame, self.back_btn, self.cont_btn])

    def save_income(self):
        val = self.income_var.get()
        try:
            income = float(val)
            if income < 0:
                raise ValueError
        except:
            messagebox.showerror("Validation","Income must be a positive number")
            return
        self.app.state["income"] = income
        self.app.show_screen("category")

# ------------------- Category Screen -------------------
class CategoryScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#f8f0ff")
        self.columnconfigure(0, weight=1)
        self.categories = {}
        self.build()

    def build(self):
        self.label = tk.Label(self, text="Add categories and expenses:", font=("Arial",16), bg="#f8f0ff")
        self.label.grid(row=0, column=0, pady=(40,20))
        self.widgets.append(self.label)

        self.add_cat_btn = ttk.Button(self, text="Add Category", command=self.add_category)
        self.add_cat_btn.grid(row=1, column=0, pady=(0,20))
        self.widgets.append(self.add_cat_btn)

        self.cat_frame = tk.Frame(self, bg="#f8f0ff")
        self.cat_frame.grid(row=2, column=0)
        self.widgets.append(self.cat_frame)

        btn_frame = tk.Frame(self, bg="#f8f0ff")
        btn_frame.grid(row=3, column=0, pady=(20,10))

        self.back_btn = ttk.Button(btn_frame, text="Back", command=lambda: self.app.show_screen("income"))
        self.back_btn.grid(row=0, column=0, padx=(0,10))

        self.cont_btn = ttk.Button(btn_frame, text="Continue", command=lambda: self.app.show_screen("summary"))
        self.cont_btn.grid(row=0, column=1, padx=(10,0))

        self.widgets.extend([btn_frame, self.back_btn, self.cont_btn])

    def add_category(self):
        cat_name = simpledialog.askstring("Add Category","Enter category name:", parent=self)
        if not cat_name: return
        if cat_name in self.categories:
            messagebox.showerror("Error","Category already exists")
            return
        self.categories[cat_name] = []

        btn_frame = tk.Frame(self.cat_frame, bg="#f8f0ff")
        btn_frame.pack(pady=2)

        cat_btn = ttk.Button(btn_frame, text=f"{cat_name}: Add Expense", command=partial(self.add_expense, cat_name))
        cat_btn.pack(side="left", padx=2)
        del_btn = ttk.Button(btn_frame, text="Delete", command=partial(self.delete_category, cat_name, btn_frame))
        del_btn.pack(side="left", padx=2)

    def add_expense(self, cat_name):
        dlg = ExpenseDialog(self, cat_name)
        self.wait_window(dlg.top)
        if dlg.result:
            self.categories[cat_name].append(dlg.result)

    def delete_category(self, cat_name, frame):
        if messagebox.askyesno("Delete","Are you sure you want to delete this category?"):
            frame.destroy()
            del self.categories[cat_name]

# ------------------- Expense Dialog -------------------
class ExpenseDialog:
    def __init__(self, parent, cat_name):
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.transient(parent)
        self.top.grab_set()
        self.top.title(f"Add Expense to {cat_name}")

        tk.Label(self.top, text="Expense Name:").pack(pady=4)
        self.name_var = tk.StringVar()
        tk.Entry(self.top, textvariable=self.name_var).pack(pady=4)

        tk.Label(self.top, text="Amount (integer):").pack(pady=4)
        self.amount_var = tk.StringVar()
        tk.Entry(self.top, textvariable=self.amount_var).pack(pady=4)

        tk.Label(self.top, text="Cost (number):").pack(pady=4)
        self.cost_var = tk.StringVar()
        tk.Entry(self.top, textvariable=self.cost_var).pack(pady=4)

        ttk.Button(self.top, text="Add", command=self.on_add).pack(pady=8)

    def on_add(self):
        name = self.name_var.get().strip()
        amount = self.amount_var.get().strip()
        cost = self.cost_var.get().strip()
        if not name or not re.fullmatch(r"[A-Za-z ]+", name):
            messagebox.showerror("Error","Name invalid")
            return
        try:
            amount = int(amount)
            cost = float(cost)
        except:
            messagebox.showerror("Error","Amount must be int, cost must be number")
            return
        self.result = (name, amount, cost)
        self.top.destroy()

# ------------------- Summary Screen -------------------
class SummaryScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#fff8f0")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        self.title_lbl = tk.Label(self, text="Summary", font=("Arial",18,"bold"), bg="#fff8f0")
        self.title_lbl.grid(row=0, column=0, pady=(40,10))
        self.widgets.append(self.title_lbl)

        self.text = tk.Text(self, width=50, height=15)
        self.text.grid(row=1, column=0, pady=(0,10))
        self.text.config(state="disabled")
        self.widgets.append(self.text)

        btn_frame = tk.Frame(self, bg="#fff8f0")
        btn_frame.grid(row=2, column=0, pady=(10,20))

        self.back_btn = ttk.Button(btn_frame, text="Back", command=lambda: self.app.show_screen("category"))
        self.back_btn.grid(row=0, column=0, padx=(0,10))

        self.quit_btn = ttk.Button(btn_frame, text="Quit", command=self.app.root.destroy)
        self.quit_btn.grid(row=0, column=1, padx=(10,0))

        self.widgets.extend([btn_frame, self.back_btn, self.quit_btn])

    def on_show(self):
        self.text.config(state="normal")
        self.text.delete("1.0", tk.END)
        total_expenses = 0
        for cat, items in self.app.screens["category"].categories.items():
            self.text.insert(tk.END, f"Category: {cat}\n")
            for name, amount, cost in items:
                subtotal = amount*cost
                total_expenses += subtotal
                self.text.insert(tk.END, f"  {name}: {amount} x {cost} = {subtotal}\n")
            self.text.insert(tk.END, "\n")
        income = self.app.state.get("income",0)
        diff = income - total_expenses
        self.text.insert(tk.END, f"Monthly Income: {income}\n")
        self.text.insert(tk.END, f"Total Expenses: {total_expenses}\n")
        self.text.insert(tk.END, f"Income - Expenses: {diff}\n")
        self.text.config(state="disabled")

        if total_expenses > income:
            messagebox.showwarning("Overspending", "You are overspending!")

# ------------------- Main App -------------------
class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BudgetBuddy")
        try:
            self.root.state("zoomed")
        except:
            try:
                self.root.attributes("-zoomed", True)
            except:
                self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")

        self.state = {}
        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.screens = {
            "splash": SplashScreen(self.container, self),
            "intro": IntroScreen(self.container, self),
            "process": ProcessScreen(self.container, self),
            "datafile": DatafileScreen(self.container, self),
            "income": IncomeScreen(self.container, self),
            "category": CategoryScreen(self.container, self),
            "summary": SummaryScreen(self.container, self)
        }

        self.current = None
        self.show_screen("splash")

    def show_screen(self, name):
        if self.current:
            self.current.grid_remove()
        self.current = self.screens[name]
        self.current.grid()
        self.current.on_show()

def main():
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
