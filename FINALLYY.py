import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from functools import partial
import re
import os

FADE_STEP = 0.1      
FADE_DELAY = 50      

# -------------------------------------------------------------
# BASE SCREEN
# -------------------------------------------------------------
class ScreenBase(tk.Frame):
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
# DATAFILE SCREEN
# -------------------------------------------------------------
class DatafileScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#fff8f0")
        self.columnconfigure(0, weight=1)
        self.selected_choice = None
        self.build()

    def build(self):
        # Question
        q_label = tk.Label(self, text="Do you want to edit an existing save file?",
                           font=("Arial",16), bg="#fff8f0")
        q_label.grid(row=0, column=0, pady=(60,20))
        self.widgets.append(q_label)

        # YES / NO buttons
        button_row = tk.Frame(self, bg="#fff8f0")
        button_row.grid(row=1, column=0, pady=(0,20))
        self.widgets.append(button_row)

        yes_btn = ttk.Button(button_row, text="Yes",
                             command=lambda: self.select_choice("Yes"))
        no_btn = ttk.Button(button_row, text="No",
                            command=lambda: self.select_choice("No"))

        yes_btn.grid(row=0, column=0, padx=10)
        no_btn.grid(row=0, column=1, padx=10)

        self.widgets.extend([yes_btn, no_btn])

        # Filename label (hidden initially)
        self.entry_label = tk.Label(self,
                                    text="Enter filename (.txt):",
                                    font=("Arial",16),
                                    bg="#fff8f0")
        self.widgets.append(self.entry_label)

        # Filename entry (hidden initially)
        self.filename_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.filename_var,
                               width=30, font=("Arial",14))
        self.widgets.append(self.entry)

        # Validation label
        self.val_lbl = tk.Label(self, text="", fg="red", bg="#fff8f0")
        self.val_lbl.grid(row=4, column=0, pady=10)
        self.widgets.append(self.val_lbl)

        # Back / Continue buttons
        btn_row = tk.Frame(self, bg="#fff8f0")
        btn_row.grid(row=5, column=0, pady=25)
        self.widgets.append(btn_row)

        self.back_btn = ttk.Button(btn_row, text="Back",
                                   command=lambda: self.app.show_screen("process"))
        self.cont_btn = ttk.Button(btn_row, text="Continue",
                                   command=self.validate_and_save)
        self.cont_btn.state(["disabled"])  # 🔒 Continue disabled initially

        self.back_btn.grid(row=0, column=0, padx=10)
        self.cont_btn.grid(row=0, column=1, padx=10)

        self.widgets.extend([self.back_btn, self.cont_btn])

    def select_choice(self, choice):
        """Called when Yes/No is clicked, reveals filename box and enables Continue."""
        self.selected_choice = choice

        # Show label + entry
        self.entry_label.grid(row=2, column=0, pady=(20,10))
        self.entry.grid(row=3, column=0)

        # Clear validation
        self.val_lbl.config(text="")

        # Enable Continue button
        self.cont_btn.state(["!disabled"])

    def validate_and_save(self):
        """Validates filename depending on Yes/No selection."""
        if not self.selected_choice:
            self.val_lbl.config(text="Please choose Yes or No.")
            return

        name = self.filename_var.get().strip()

        if not name:
            self.val_lbl.config(text="Filename cannot be empty.")
            return

        if not re.fullmatch(r"[A-Za-z0-9_]+", name):
            self.val_lbl.config(text="Letters, numbers, underscores only.")
            return

        path = name + ".txt"

        # YES → file must exist
        if self.selected_choice == "Yes":
            if not os.path.isfile(path):
                self.val_lbl.config(text="File does not exist.")
                return

        # Save choice to state
        self.app.state["datafile_name"] = name
        self.app.state["editing_existing"] = (self.selected_choice == "Yes")

        # Go forward
        self.app.show_screen("income")


# -------------------------------------------------------------
# INCOME SCREEN
# -------------------------------------------------------------
class IncomeScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#e8f7ff")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        title = tk.Label(self, text="Enter your monthly income:",
                         font=("Helvetica", 20), bg="#e8f7ff")
        title.grid(row=0, column=0, pady=(80, 10))
        self.widgets.append(title)

        self.income_var = tk.StringVar(value=str(self.app.state.get("income", "")))
        entry = ttk.Entry(self, textvariable=self.income_var,
                          width=20, font=("Arial", 14))
        entry.grid(row=1, column=0)
        self.widgets.append(entry)

        self.val_lbl = tk.Label(self, text="", fg="red", bg="#e8f7ff")
        self.val_lbl.grid(row=2, column=0, pady=10)
        self.widgets.append(self.val_lbl)

        # Buttons
        btn_row = tk.Frame(self, bg="#e8f7ff")
        btn_row.grid(row=3, column=0, pady=20)
        self.widgets.append(btn_row)

        back = ttk.Button(btn_row, text="Back",
                          command=lambda: self.app.show_screen("datafile"))
        cont = ttk.Button(btn_row, text="Continue", command=self.validate)

        back.grid(row=0, column=0, padx=10)
        cont.grid(row=0, column=1, padx=10)

        self.widgets.extend([back, cont])

    def validate(self):
        try:
            income = float(self.income_var.get())
            if income < 0:
                raise ValueError
            self.app.state["income"] = income
            self.app.show_screen("category")
        except:
            self.val_lbl.config(text="Please enter a valid income.")


# -------------------------------------------------------------
# EXPENSE DIALOG
# -------------------------------------------------------------
class ExpenseDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Expense")
        self.resizable(False, False)
        self.result = None

        # Center the pop-up over parent
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        w = 300
        h = 150
        x = parent.winfo_rootx() + parent.winfo_width()//2 - w//2
        y = parent.winfo_rooty() + parent.winfo_height()//2 - h//2
        self.geometry(f"{w}x{h}+{x}+{y}")

        tk.Label(self, text="Expense Name:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Cost:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.cost_entry = tk.Entry(self)
        self.cost_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self, text="Quantity:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.qty_entry = tk.Entry(self)
        self.qty_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self, text="Add", command=self.on_add).grid(row=3, column=0, columnspan=2, pady=10)

    def on_add(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Expense name is required.")
            return

        try:
            cost = float(self.cost_entry.get())
            qty = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Cost must be a number and quantity an integer.")
            return

        self.result = (name, qty, cost)
        self.destroy()


# -------------------------------------------------------------
# CATEGORY BOX
# -------------------------------------------------------------
class CategoryBox(tk.Frame):
    BOX_WIDTH = 200
    BOX_HEIGHT = 140
    BOX_PADDING = 15  # padding for content

    def __init__(self, master, category_name, remove_callback):
        super().__init__(master, bd=2, relief="groove", width=self.BOX_WIDTH, height=self.BOX_HEIGHT)
        self.grid_propagate(False)

        self.category_name = category_name
        self.expenses = []
        self.remove_callback = remove_callback

        self.content_frame = tk.Frame(self)
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.name_label = tk.Label(self.content_frame, text=category_name, font=("Arial", 12, "bold"), wraplength=self.BOX_WIDTH-10, justify="center")
        self.name_label.pack()
        self.divider = tk.Frame(self.content_frame, height=2, bg="black")
        self.divider.pack(fill="x", pady=5)
        self.no_expense_label = tk.Label(self.content_frame, text="(no added expenses)", font=("Arial", 10, "italic"), fg="gray", justify="center")
        self.no_expense_label.pack()

        self.add_btn = tk.Button(self, text=f"Add expense to {category_name}", wraplength=self.BOX_WIDTH-10, justify="center", command=self.add_expense)
        self.del_btn = tk.Button(self, text=f"Delete {category_name}", wraplength=self.BOX_WIDTH-10, justify="center", command=self.delete_category)

        self.bind_recursive(self, "<Enter>", self.on_hover)
        self.bind_recursive(self, "<Leave>", self.on_leave)

    def bind_recursive(self, widget, event, func):
        widget.bind(event, func)
        for child in widget.winfo_children():
            self.bind_recursive(child, event, func)

    def on_hover(self, event=None):
        self.content_frame.place_forget()
        self.add_btn.place(relx=0.5, rely=0.35, anchor="center")
        self.del_btn.place(relx=0.5, rely=0.65, anchor="center")

    def on_leave(self, event=None):
        self.add_btn.place_forget()
        self.del_btn.place_forget()
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")

    def add_expense(self):
        dlg = ExpenseDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            name, qty, cost = dlg.result
            self.expenses.append((name, qty, cost))
            self.update_content()

    def update_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text=self.category_name, font=("Arial", 12, "bold"), wraplength=self.BOX_WIDTH-10, justify="center").pack()
        tk.Frame(self.content_frame, height=2, bg="black").pack(fill="x", pady=5)

        if not self.expenses:
            tk.Label(self.content_frame, text="(no added expenses)", font=("Arial", 10, "italic"), fg="gray", justify="center").pack()
        else:
            for name, qty, cost in self.expenses:
                tk.Label(self.content_frame, text=f"{name} x{qty} = ${cost*qty:.2f}", wraplength=self.BOX_WIDTH-10, justify="center").pack()

        req_height = max(self.BOX_HEIGHT, self.content_frame.winfo_reqheight() + 2*self.BOX_PADDING)
        self.config(height=req_height)
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")

    def delete_category(self):
        self.remove_callback(self)


# -------------------------------------------------------------
# CATEGORY SCREEN
# -------------------------------------------------------------
class CategoryScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, bg="#f8f0ff")
        self.category_boxes = []
        self.max_cols = 4
        self.build()

    def build(self):
        self.add_btn = ttk.Button(self, text="Add Category", command=self.add_category)
        self.add_btn.grid(row=0, column=0, pady=20)

        self.box_frame = tk.Frame(self, bg="#f8f0ff")
        self.box_frame.grid(row=1, column=0)

        btn_row = tk.Frame(self, bg="#f8f0ff")
        btn_row.grid(row=2, column=0, pady=20)
        back = ttk.Button(btn_row, text="Back", command=lambda: self.app.show_screen("income"))
        cont = ttk.Button(btn_row, text="Continue", command=self.finish)
        back.grid(row=0, column=0, padx=10)
        cont.grid(row=0, column=1, padx=10)

    def add_category(self):
        name = simpledialog.askstring("New Category", "Enter your new category's name:", parent=self)
        if not name: return
        box = CategoryBox(self.box_frame, name, self.remove_category)
        self.category_boxes.append(box)
        self.reposition_boxes()

    def remove_category(self, box):
        box.destroy()
        self.category_boxes.remove(box)
        self.reposition_boxes()

    def reposition_boxes(self):
        for b in self.category_boxes: b.grid_forget()
        row = 0; col = 0; current_row_boxes = []
        for i, box in enumerate(self.category_boxes):
            current_row_boxes.append(box)
            col += 1
            if col >= self.max_cols or i == len(self.category_boxes)-1:
                total_boxes = len(current_row_boxes)
                start_col = (self.max_cols - total_boxes)//2
                for j, b in enumerate(current_row_boxes):
                    b.grid(row=row, column=start_col+j, padx=5, pady=5)
                current_row_boxes = []; col=0; row+=1

    def finish(self):
        # Save expenses to app.state
        categories = {}
        for box in self.category_boxes:
            categories[box.category_name] = {name:(qty,cost) for name, qty, cost in box.expenses}
        self.app.state["categories"] = categories
        self.app.show_screen("summary")


# -------------------------------------------------------------
# SUMMARY SCREEN
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
        if leftover < 0: output.append("\n⚠ WARNING: You are overspending!")

        self.summary_text = "\n".join(output)
        self.text.insert(tk.END, self.summary_text)

        self.fade_in_widgets()

    def save_to_file(self):
        fname = self.app.state.get("datafile_name","budget")
        path = fname + ".txt"
        cats = self.app.state.get("categories",{})
        lines = []
        for cat, items in cats.items():
            lines.append(f"{cat}")
            for name, (amt, cost) in items.items():
                total = amt * cost
                lines.append(f"{name} : ${total:.2f}")
            lines.append("")

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
        try: self.root.state("zoomed")
        except: self.root.attributes("-zoomed", True)

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
        if self.current: self.current.grid_remove()
        self.current = self.screens[name]
        self.current.grid()
        self.current.on_show()


def main():
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
