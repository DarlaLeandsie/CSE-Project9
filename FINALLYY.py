import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from functools import partial
import re
import os

FADE_STEP = 0.1      
FADE_DELAY = 50      

class ScreenBase(tk.Frame):
    """Base class for screens with fade animation support."""
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.widgets = []

    def on_show(self):
        self.fade_in_widgets()

    def fade_in_widgets(self):
        for w in self.widgets:
            try: w.grid_remove()
            except: pass
        self._fade_in_step(0)

    def _fade_in_step(self, idx):
        if idx >= len(self.widgets): return
        self.widgets[idx].grid()
        self.after(FADE_DELAY, lambda: self._fade_in_step(idx+1))


# -------------------------------------------------------------
# SPLASH SCREEN
# -------------------------------------------------------------
class SplashScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#f7fbff")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        try:
            self.logo_img = tk.PhotoImage(file="BBlogo.png")
            logo = tk.Label(self, image=self.logo_img, bg="#f7fbff")
        except:
            logo = tk.Label(self, text="BudgetBuddy", font=("Inter", 42, "bold"), bg="#f7fbff")

        logo.grid(row=0, column=0, pady=(120, 10))
        self.widgets.append(logo)

        instr = tk.Label(self, text="(click anywhere to begin)", font=("Helvetica", 14), bg="#f7fbff")
        instr.grid(row=1, column=0, pady=(4, 40))
        self.widgets.append(instr)

        self.bind_all("<Button-1>", self._click)

    def _click(self, event=None):
        self.unbind_all("<Button-1>")
        self.app.show_screen("intro")


# -------------------------------------------------------------
# INTRO SCREEN
# -------------------------------------------------------------
class IntroScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="white")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        title = tk.Label(self, text="To begin this program, enter your name.", font=("Helvetica", 20), bg="white")
        title.grid(row=0, column=0, pady=(80,18))
        self.widgets.append(title)

        self.name_var = tk.StringVar(value=self.app.state.get("user_name",""))
        name_entry = ttk.Entry(self, textvariable=self.name_var, width=30, font=("Arial",14))
        name_entry.grid(row=1, column=0)
        self.widgets.append(name_entry)

        self.val_lbl = tk.Label(self, text="", fg="red", bg="white")
        self.val_lbl.grid(row=2, column=0, pady=(6,14))
        self.widgets.append(self.val_lbl)

        # Button row
        btn_row = tk.Frame(self, bg="white")
        btn_row.grid(row=3, column=0, pady=20)
        self.widgets.append(btn_row)

        back = ttk.Button(btn_row, text="Back", command=lambda: self.app.show_screen("splash"))
        cont = ttk.Button(btn_row, text="Continue", command=self.validate)

        back.grid(row=0, column=0, padx=10)
        cont.grid(row=0, column=1, padx=10)

        self.widgets.append(back)
        self.widgets.append(cont)

    def validate(self):
        name = self.name_var.get().strip()
        if not name:
            self.val_lbl.config(text="Please enter a name.")
            return
        if not re.fullmatch(r"[A-Za-z ]+", name):
            self.val_lbl.config(text="Name may only contain letters and spaces.")
            return
        self.app.state["user_name"] = name
        self.app.show_screen("process")


# -------------------------------------------------------------
# PROCESS SCREEN
# -------------------------------------------------------------
class ProcessScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#f0fbf7")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        self.greet = tk.Label(self, text="", font=("Helvetica",20,"bold"), bg="#f0fbf7")
        self.greet.grid(row=0, column=0, pady=(80,10))
        self.widgets.append(self.greet)

        steps = tk.Label(self, text="You will take the following steps to use BudgetBuddy:",
                         font=("Arial",12), bg="#f0fbf7")
        steps.grid(row=1, column=0)
        self.widgets.append(steps)

        try:
            self.logo_img = tk.PhotoImage(file="BBlogo.png")
            logo = tk.Label(self, image=self.logo_img, bg="#f0fbf7")
        except:
            logo = tk.Label(self, text="(logo)", bg="#f0fbf7")

        logo.grid(row=2, column=0, pady=15)
        self.widgets.append(logo)

        btn_row = tk.Frame(self, bg="#f0fbf7")
        btn_row.grid(row=3, column=0, pady=20)
        self.widgets.append(btn_row)

        back = ttk.Button(btn_row, text="Back", command=lambda: self.app.show_screen("intro"))
        cont = ttk.Button(btn_row, text="Continue", command=lambda: self.app.show_screen("datafile"))

        back.grid(row=0, column=0, padx=10)
        cont.grid(row=0, column=1, padx=10)

        self.widgets.extend([back, cont])

    def on_show(self):
        name = self.app.state.get("user_name","User")
        self.greet.config(text=f"Hey {name}, this is BudgetBuddy! Your personal Budgeting Assistant.")
        self.fade_in_widgets()


# -------------------------------------------------------------
# DATAFILE SCREEN  **UPDATED**
# -------------------------------------------------------------
class DatafileScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#fff8f0")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        # Question: Edit existing file?
        q_label = tk.Label(self, text="Do you want to edit an existing save file?",
                           font=("Arial",16), bg="#fff8f0")
        q_label.grid(row=0, column=0, pady=(60,10))
        self.widgets.append(q_label)

        # Yes/No dropdown
        self.choice_var = tk.StringVar(value="No")
        choice_menu = ttk.Combobox(self, textvariable=self.choice_var,
                                   values=["Yes", "No"], state="readonly", width=10)
        choice_menu.grid(row=1, column=0)
        self.widgets.append(choice_menu)

        # Label for filename entry
        self.entry_label = tk.Label(self,
                                    text="Enter filename (.txt):",
                                    font=("Arial",16),
                                    bg="#fff8f0")
        self.entry_label.grid(row=2, column=0, pady=(30,10))
        self.widgets.append(self.entry_label)

        # Filename entry
        self.filename_var = tk.StringVar(value=self.app.state.get("datafile_name",""))
        self.entry = ttk.Entry(self, textvariable=self.filename_var, width=30, font=("Arial",14))
        self.entry.grid(row=3, column=0)
        self.widgets.append(self.entry)

        # Validation label
        self.val_lbl = tk.Label(self, text="", fg="red", bg="#fff8f0")
        self.val_lbl.grid(row=4, column=0, pady=10)
        self.widgets.append(self.val_lbl)

        # Back / Continue buttons
        btn_row = tk.Frame(self, bg="#fff8f0")
        btn_row.grid(row=5, column=0, pady=25)
        self.widgets.append(btn_row)

        back = ttk.Button(btn_row, text="Back",
                          command=lambda: self.app.show_screen("process"))
        cont = ttk.Button(btn_row, text="Continue",
                          command=self.validate_and_save)

        back.grid(row=0, column=0, padx=10)
        cont.grid(row=0, column=1, padx=10)

        self.widgets.extend([back, cont])

    def validate_and_save(self):
        """Validates either new or existing filename depending on Yes/No choice."""
        name = self.filename_var.get().strip()
        choice = self.choice_var.get()

        if not name:
            self.val_lbl.config(text="Filename cannot be empty.")
            return

        if not re.fullmatch(r"[A-Za-z0-9_]+", name):
            self.val_lbl.config(text="Letters, numbers, underscores only.")
            return

        # Path of file
        path = name + ".txt"

        # If user chose YES → must exist
        if choice == "Yes":
            if not os.path.isfile(path):
                self.val_lbl.config(text="File does not exist.")
                return

        # If NO → new file name (can overwrite later)
        self.app.state["datafile_name"] = name
        self.app.state["editing_existing"] = (choice == "Yes")

        self.app.show_screen("income")


# -------------------------------------------------------------
# INCOME SCREEN
# -------------------------------------------------------------
class IncomeScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#f0fff0")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        label = tk.Label(self, text="Enter your monthly income:", font=("Arial",16), bg="#f0fff0")
        label.grid(row=0, column=0, pady=(80,10))
        self.widgets.append(label)

        self.income_var = tk.StringVar(value=str(self.app.state.get("income","")))
        entry = ttk.Entry(self, textvariable=self.income_var, width=20)
        entry.grid(row=1, column=0)
        self.widgets.append(entry)

        btn_row = tk.Frame(self, bg="#f0fff0")
        btn_row.grid(row=2, column=0, pady=20)
        self.widgets.append(btn_row)

        back = ttk.Button(btn_row, text="Back", command=lambda: self.app.show_screen("datafile"))
        cont = ttk.Button(btn_row, text="Continue", command=self.save_income)

        back.grid(row=0, column=0, padx=10)
        cont.grid(row=0, column=1, padx=10)

        self.widgets.extend([back, cont])

    def save_income(self):
        try:
            val = float(self.income_var.get())
            if val < 0: raise ValueError
        except:
            messagebox.showerror("Error","Income must be a positive number.")
            return

        self.app.state["income"] = val
        self.app.show_screen("category")


# -------------------------------------------------------------
# CATEGORY SCREEN
# -------------------------------------------------------------
class CategoryScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#f8f0ff")
        self.columnconfigure(0, weight=1)
        self.categories = {}
        self.build()

    def build(self):
        label = tk.Label(self, text="Add categories and expenses:", font=("Arial",16), bg="#f8f0ff")
        label.grid(row=0, column=0, pady=(40,10))
        self.widgets.append(label)

        add_btn = ttk.Button(self, text="Add Category", command=self.add_category)
        add_btn.grid(row=1, column=0, pady=10)
        self.widgets.append(add_btn)

        self.cat_frame = tk.Frame(self, bg="#f8f0ff")
        self.cat_frame.grid(row=2, column=0)
        self.widgets.append(self.cat_frame)

        btn_row = tk.Frame(self, bg="#f8f0ff")
        btn_row.grid(row=3, column=0, pady=20)
        self.widgets.append(btn_row)

        back = ttk.Button(btn_row, text="Back", command=lambda: self.app.show_screen("income"))
        cont = ttk.Button(btn_row, text="Continue", command=self.finish)

        back.grid(row=0, column=0, padx=10)
        cont.grid(row=0, column=1, padx=10)

        self.widgets.extend([back, cont])

    def add_category(self):
        name = simpledialog.askstring("Add Category","Enter category name:", parent=self)
        if not name: return
        if name in self.categories:
            messagebox.showerror("Error","Category exists.")
            return
        self.categories[name] = {}

        row = tk.Frame(self.cat_frame, bg="#f8f0ff")
        row.pack(pady=5)

        cat_btn = ttk.Button(row, text=f"{name}: Add Expense",
                             command=partial(self.add_expense, name))
        del_btn = ttk.Button(row, text="Delete", command=partial(self.delete_cat, name, row))

        cat_btn.pack(side="left", padx=5)
        del_btn.pack(side="left", padx=5)

    def add_expense(self, category):
        dlg = ExpenseDialog(self, category)
        self.wait_window(dlg.top)

        if dlg.result:
            name, amount, cost = dlg.result
            # merging repeated items
            self.categories[category][name] = (amount, cost)

    def delete_cat(self, name, frame):
        if messagebox.askyesno("Confirm", "Delete category?"):
            frame.destroy()
            del self.categories[name]

    def finish(self):
        self.app.state["categories"] = self.categories
        self.app.show_screen("summary")


# -------------------------------------------------------------
# EXPENSE DIALOG
# -------------------------------------------------------------
class ExpenseDialog:
    def __init__(self, parent, cat):
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title(f"Add to {cat}")
        self.top.transient(parent)
        self.top.grab_set()

        tk.Label(self.top, text="Expense Name:").pack(pady=4)
        self.name_var = tk.StringVar()
        tk.Entry(self.top, textvariable=self.name_var).pack()

        tk.Label(self.top, text="Amount (integer):").pack(pady=4)
        self.amount_var = tk.StringVar()
        tk.Entry(self.top, textvariable=self.amount_var).pack()

        tk.Label(self.top, text="Cost (number):").pack(pady=4)
        self.cost_var = tk.StringVar()
        tk.Entry(self.top, textvariable=self.cost_var).pack()

        ttk.Button(self.top, text="Add", command=self.finish).pack(pady=10)

    def finish(self):
        try:
            name = self.name_var.get().strip()
            if not name or not re.fullmatch(r"[A-Za-z ]+", name):
                raise ValueError("Invalid name.")

            amount = int(self.amount_var.get())
            cost = float(self.cost_var.get())

            self.result = (name, amount, cost)
            self.top.destroy()
        except:
            messagebox.showerror("Error","Invalid input.")


# -------------------------------------------------------------
# SUMMARY SCREEN  **UPDATED**
# -------------------------------------------------------------
class SummaryScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="white")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        self.title = tk.Label(self, text="Summary", font=("Helvetica",22,"bold"), bg="white")
        self.title.grid(row=0, column=0, pady=(30,10))
        self.widgets.append(self.title)

        self.text = tk.Text(self, width=80, height=25, font=("Consolas",12))
        self.text.grid(row=1, column=0, pady=10)
        self.widgets.append(self.text)

        btn_row = tk.Frame(self, bg="white")
        btn_row.grid(row=2, column=0, pady=20)
        self.widgets.append(btn_row)

        back = ttk.Button(btn_row, text="Back", command=lambda: self.app.show_screen("category"))
        finish = ttk.Button(btn_row, text="Finish", command=self.save_to_file)

        back.grid(row=0, column=0, padx=10)
        finish.grid(row=0, column=1, padx=10)

        self.widgets.extend([back, finish])

    def on_show(self):
        self.text.delete("1.0", tk.END)

        income = self.app.state.get("income",0)
        cats = self.app.state.get("categories",{})

        total_expenses = 0

        output = []

        for cat, items in cats.items():
            output.append(f"{cat}:")
            for name, (amt, cost) in items.items():
                total = amt * cost
                total_expenses += total
                output.append(f"  {name} x{amt} = ${total:.2f}")
            output.append("")

        leftover = income - total_expenses

        output.append(f"Monthly Income: ${income:.2f}")
        output.append(f"Total Expenses: ${total_expenses:.2f}")
        output.append(f"Remaining Balance: ${leftover:.2f}")

        if leftover < 0:
            output.append("\n⚠ WARNING: You are overspending!")

        self.summary_text = "\n".join(output)
        self.text.insert(tk.END, self.summary_text)

        self.fade_in_widgets()

    def save_to_file(self):
        fname = self.app.state.get("datafile_name","budget")
        path = fname + ".txt"

        cats = self.app.state.get("categories",{})

        lines = []

        # file formatting EXACTLY as you requested
        for cat, items in cats.items():
            lines.append(f"{cat}")
            for name, (amt, cost) in items.items():
                total = amt * cost
                lines.append(f"{name} : ${total:.2f}")
            lines.append("")  # blank line between categories

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            messagebox.showinfo("Saved", f"Your data has been saved to:\n{path}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")


# -------------------------------------------------------------
# MAIN APP
# -------------------------------------------------------------
class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BudgetBuddy")

        try:
            self.root.state("zoomed")
        except:
            self.root.attributes("-zoomed", True)

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
