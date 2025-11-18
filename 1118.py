import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from functools import partial
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import re
import os

# overall font
MAIN_FONT = ("Dubai Medium", 14)

# color palette
#fff4e6: Very pale (mostly white) orange
#be9b7b: Slightly desaturated orange
#854442: Dark moderate red
#4b3832: Very dark grayish red
#3c2f2f: Desaturated very dark red

# base screen
class ScreenBase(tk.Frame):
    def __init__(self, master, app, background_color="white"):
        super().__init__(master, bg=background_color)
        self.app = app
        self.background_color = background_color

    def on_show(self):
        pass

# logo screen
class SplashScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, background_color="#f7fbff")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        try: # if user has BBlogo.png
            self.logo_image = tk.PhotoImage(file="BBlogo.png")
            logo_label = tk.Label(self, image=self.logo_image, bg=self.background_color)
        except: # if user w/o BBlogo.png
            logo_label = tk.Label(self, text="BudgetBuddy", font=(MAIN_FONT[0], 42, "bold"), bg=self.background_color)

        logo_label.grid(row=0, column=0, pady=(120,10))

        # user can click anywhere to proceed to the next screen
        instruction_label = tk.Label(self, text="(click anywhere to begin)", font=MAIN_FONT, bg=self.background_color)
        instruction_label.grid(row=1, column=0, pady=(4,40))

        self.bind_all("<Button-1>", self.proceed)

    def proceed(self, event=None):
        self.unbind_all("<Button-1>")
        self.app.show_screen("intro")

# introduction screen
class IntroScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, background_color="white")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        # promting for the user's name
        title_label = tk.Label(self, text="To begin, enter your name:", font=MAIN_FONT, bg=self.background_color)
        title_label.grid(row=0, column=0, pady=(80,18))

        # textbox for user's name
        self.user_name_var = tk.StringVar(value=self.app.state.get("user_name",""))
        name_textbox = ttk.Entry(self, textvariable=self.user_name_var, width=30, font=MAIN_FONT)
        name_textbox.grid(row=1, column=0)

        # validation notice format
        self.validation = tk.Label(self, text="", fg="red", font=MAIN_FONT, bg=self.background_color)
        self.validation.grid(row=2, column=0, pady=(6,14))

        # back and continue buttons
        button_frame = tk.Frame(self, bg=self.background_color)
        button_frame.grid(row=3, column=0, pady=20)
        back_button = ttk.Button(button_frame, text="Back", command=lambda: self.app.show_screen("splash"))
        back_button.grid(row=0, column=0, padx=10)
        continue_button = ttk.Button(button_frame, text="Continue", command=self.validate)
        continue_button.grid(row=0, column=1, padx=10)

    # checks if the name is valid (only letters and spaces)
    def validate(self):
        name = self.user_name_var.get().strip()
        if not name:
            self.validation.config(text="Please enter a name.")
            return
        if not re.fullmatch(r"[A-Za-z ]+", name):
            self.validation.config(text="Name may only contain letters and spaces.")
            return
        self.app.state["user_name"] = name
        self.app.show_screen("process")

# hello screen
class ProcessScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, background_color="#f0fbf7")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        self.greeting_label = tk.Label(self, text="", font=(MAIN_FONT[0], 20, "bold"), bg=self.background_color)
        self.greeting_label.grid(row=0, column=0, pady=(80,10))

        steps_label = tk.Label(self, text="\nYou will take the following steps to use BudgetBuddy:", font=(MAIN_FONT, 14, "bold"), bg=self.background_color)
        steps_label.grid(row=1, column=0)

        # steps list
        try:
            self.logo_image = tk.PhotoImage(file="BBlogos.png")
            logo_label = tk.Label(self, image=self.logo_image, bg=self.background_color)
        # show BudgetBuddy text w/o BBlogo.png
        except:
            logo_label = tk.Label(self, text="" \
            "1.) Choose to edit an existing file.\n\n " \
            "2.) Input your monthly income.\n\n " \
            "3.) Organize your expenses through categories.\n\n" \
            "4.) View your summarized expenses.\n\n" \
            "5.) Save your expenses to a new or existing file.", font=MAIN_FONT, bg=self.background_color)

        logo_label.grid(row=2, column=0, pady=15)

        # back and continue buttons
        button_frame = tk.Frame(self, bg=self.background_color)
        button_frame.grid(row=3, column=0, pady=20)
        back_button = ttk.Button(button_frame, text="Back", command=lambda: self.app.show_screen("intro"))
        back_button.grid(row=0, column=0, padx=10)
        continue_button = ttk.Button(button_frame, text="Continue", command=lambda: self.app.show_screen("datafile"))
        continue_button.grid(row=0, column=1, padx=10)

    # greeting
    def on_show(self):
        name = self.app.state.get("user_name","User")
        self.greeting_label.config(text=f"Hey {name}! Welcome to BudgetBuddy, your personal Budgeting Assistant.")

# datafile screen
class DatafileScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, background_color="#fff8f0")
        self.columnconfigure(0, weight=1)
        self.selected_choice = None
        # display original categories if editing existing file
        self.original_categories = {}
        self.new_data = {}
        self.build()

    def build(self):
        datafile_question = tk.Label(self, text="Do you want to edit an existing save file?", font=MAIN_FONT, bg=self.background_color)
        datafile_question.grid(row=0, column=0, pady=(60,20))

        # yes and no buttons
        button_frame = tk.Frame(self, bg=self.background_color)
        button_frame.grid(row=1, column=0, pady=(0,20))
        yes_button = ttk.Button(button_frame, text="Yes", command=lambda: self.select_choice("Yes"))
        yes_button.grid(row=0, column=0, padx=10)
        no_button = ttk.Button(button_frame, text="No", command=lambda: self.select_choice("No"))
        no_button.grid(row=0, column=1, padx=10)

        # prompt user for filename whether existing or not
        self.filename = tk.Label(self, text="Enter filename (.txt):", font=MAIN_FONT, bg=self.background_color)
        self.filename_var = tk.StringVar()
        self.filename_textbox = ttk.Entry(self, textvariable=self.filename_var, width=30, font=MAIN_FONT)

        # validation notice format
        self.validation = tk.Label(self, text="", fg="red", font=MAIN_FONT, bg=self.background_color)
        self.validation.grid(row=4, column=0, pady=10)

        # back and continue buttons
        button_row = tk.Frame(self, bg=self.background_color)
        button_row.grid(row=5, column=0, pady=25)
        self.back_button = ttk.Button(button_row, text="Back", command=lambda: self.app.show_screen("process"))
        self.back_button.grid(row=0, column=0, padx=10)
        self.continue_button = ttk.Button(button_row, text="Continue", command=self.validate_and_save)
        self.continue_button.state(["disabled"])
        self.continue_button.grid(row=0, column=1, padx=10)

    def select_choice(self, choice):
        self.selected_choice = choice
        self.filename.grid(row=2, column=0, pady=(20,10))
        self.filename_textbox.grid(row=3, column=0)
        self.validation.config(text="")
        self.continue_button.state(["!disabled"])

    # validate filename
    def validate_and_save(self):
        if not self.selected_choice:
            self.validation.config(text="Please choose Yes or No.")
            return
        filename = self.filename_var.get().strip()
        if not filename:
            self.validation.config(text="Filename cannot be empty.")
            return
        if not re.fullmatch(r"[A-Za-z0-9_]+", filename):
            self.validation.config(text="Letters, numbers, underscores only.")
            return

        path = filename + ".txt"

        if self.selected_choice == "Yes":
            if not os.path.isfile(path):
                self.validation.config(text="File does not exist.")
                return
            # load past categories/expenses
            self.original_categories = load_categories(path)
            # initialize app state with all original categories
            self.app.state["categories"] = {cat: items.copy() for cat, items in self.original_categories.items()}
            self.new_data = {}
        else:
            self.original_categories = {}
            self.new_data = {}
            self.app.state["categories"] = {}

        self.app.state["datafile_name"] = filename
        self.app.state["editing_existing"] = (self.selected_choice == "Yes")
        self.app.show_screen("income")

    # save changes appending only new data
    def save_changes(self):
        datafile_name = self.app.state.get("datafile_name", "budget")
        path = datafile_name + ".txt"
        categories = self.app.state.get("categories", {})
        existing = self.original_categories.copy()

        # figure out new additions
        for category, items in categories.items():
            if category not in existing:
                self.new_data[category] = items
            else:
                # check for new expenses in existing categories
                for name, (quantity, cost) in items.items():
                    if name not in existing[category]:
                        if category not in self.new_data:
                            self.new_data[category] = {}
                        self.new_data[category][name] = (quantity, cost)

        # save new section
        with open(path, "a", encoding="utf-8") as f:
            if self.new_data:
                f.write("\n--- New Entries ---\n")
                for cat, items in self.new_data.items():
                    f.write(f"{cat}\n")
                    for name, (quantity, cost) in items.items():
                        f.write(f"{name} (x{quantity}) : ${cost:.2f}\n")
                    f.write("\n")

# income screen
class IncomeScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, background_color="#e8f7ff")
        self.columnconfigure(0, weight=1)
        self.build()

    def build(self):
        # prompt user's monthly income
        monthly_income_prompt = tk.Label(self, text="Enter your monthly income:", font=MAIN_FONT, bg=self.background_color)
        monthly_income_prompt.grid(row=0, column=0, pady=(80,10))

        self.income_var = tk.StringVar(value=str(self.app.state.get("income","")))
        income_textbox = ttk.Entry(self, textvariable=self.income_var, width=20, font=MAIN_FONT)
        income_textbox.grid(row=1, column=0)

        # validation notice format
        self.validation = tk.Label(self, text="", fg="red", font=MAIN_FONT, bg=self.background_color)
        self.validation.grid(row=2, column=0, pady=10)

        # back and continue buttons
        button_frame = tk.Frame(self, bg=self.background_color)
        button_frame.grid(row=3, column=0, pady=20)
        back_button = ttk.Button(button_frame, text="Back", command=lambda: self.app.show_screen("datafile"))
        continue_button = ttk.Button(button_frame, text="Continue", command=self.validate_income)
        back_button.grid(row=0, column=0, padx=10)
        continue_button.grid(row=0, column=1, padx=10)
    
    # checks if income is valid
    def validate_income(self):
        try:
            income = float(self.income_var.get())
            if income < 0:
                raise ValueError
            self.app.state["income"] = income
            self.app.show_screen("category")
        except:
            self.validation.config(text="Please enter a valid income.")

# pop-up for expense info
class ExpenseDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Expense")
        self.resizable(False, False)
        self.result = None
        self.transient(parent)
        self.grab_set()

        # center dialog over parent
        self.update_idletasks()
        w, h = 300, 170
        x = parent.winfo_rootx() + parent.winfo_width()//2 - w//2
        y = parent.winfo_rooty() + parent.winfo_height()//2 - h//2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # expense info
        tk.Label(self, text="Expense Name:", font=MAIN_FONT).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.name_textbox = tk.Entry(self, font=MAIN_FONT)
        self.name_textbox.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self, text="Cost:", font=MAIN_FONT).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.cost_textbox = tk.Entry(self, font=MAIN_FONT)
        self.cost_textbox.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self, text="Quantity:", font=MAIN_FONT).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.quantity_textbox = tk.Entry(self, font=MAIN_FONT)
        self.quantity_textbox.grid(row=2, column=1, padx=5, pady=5)

        # add and cancel buttons
        button_frame = tk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        cancel_button = tk.Button(button_frame, text="Cancel", font=MAIN_FONT, width=10, command=self.destroy)
        cancel_button.grid(row=0, column=0, padx=10)
        add_button = tk.Button(button_frame, text="Add", font=MAIN_FONT, width=10, command=self.on_add)
        add_button.grid(row=0, column=1, padx=10)
    
    # name is required for each expense while cost and quantity must be integers
    def on_add(self):
        name = self.name_textbox.get().strip()
        if not name:
            messagebox.showerror("Error", "Expense name is required.")
            return
        try:
            cost = float(self.cost_textbox.get())
            quantity = int(self.quantity_textbox.get())
        except:
            messagebox.showerror("Error", "Cost must be a number and quantity an integer.")
            return
        self.result = (name, quantity, cost)
        self.destroy()

# CATEGORY BOX
class CategoryBox(tk.Frame):
    BOX_WIDTH = 200
    BOX_HEIGHT = 140

    def __init__(self, master, category_name, remove_callback, expenses=None, is_new=False):
        super().__init__(master, bd=2, relief="groove", width=self.BOX_WIDTH, height=self.BOX_HEIGHT)
        self.grid_propagate(False)
        self.category_name = category_name
        self.expenses = expenses if expenses else []
        self.remove_callback = remove_callback
        self.is_new = is_new  # True if this is a newly created category

        self.content_frame = tk.Frame(self)
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.update_content()

        self.add_button = tk.Button(self, text="Add Expense", font=("Dubai Medium",10), command=self.add_expense)
        self.delete_button = tk.Button(self, text="Delete Category", font=("Dubai Medium",10), command=self.delete_category)

        # Hover effect
        self.bind_recursive(self, "<Enter>", self.on_hover)
        self.bind_recursive(self, "<Leave>", self.on_leave)

    def bind_recursive(self, widget, event, func):
        widget.bind(event, func)
        for child in widget.winfo_children():
            self.bind_recursive(child, event, func)

    def on_hover(self, event=None):
        self.content_frame.place_forget()
        self.add_button.place(relx=0.5, rely=0.35, anchor="center")
        self.delete_button.place(relx=0.5, rely=0.65, anchor="center")

    def on_leave(self, event=None):
        self.add_button.place_forget()
        self.delete_button.place_forget()
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")

    def add_expense(self):
        dlg = ExpenseDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            name, quantity, cost = dlg.result
            # combine any duplicates if any
            for i, (expense_name, expense_quantity, expense_cost) in enumerate(self.expenses):
                if expense_name == name:
                    self.expenses[i] = (expense_name, expense_quantity+quantity, expense_cost)
                    break
            else:
                self.expenses.append((name, quantity, cost))

            # Track in app.state
            categories = self.master.master.app.state.setdefault("categories", {})
            category_dict = categories.setdefault(self.category_name, {})
            for expense_name, expense_quantity, expense_cost in self.expenses:
                category_dict[expense_name] = (expense_quantity, expense_cost)

            # Track new additions separately for file saving
            if not hasattr(self.master.master.app, "new_entries"):
                self.master.master.app.new_entries = {}
            new_category = self.master.master.app.new_entries.setdefault(self.category_name, {})
            new_category[name] = (quantity, cost)

            self.update_content()

    def update_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        tk.Label(self.content_frame, text=self.category_name, font=("Dubai Medium", 12, "bold"),
                 wraplength=self.BOX_WIDTH-10, justify="center").pack()
        tk.Frame(self.content_frame, height=2, bg="black").pack(fill="x", pady=5)
        if not self.expenses:
            tk.Label(self.content_frame, text="(no added expenses)", font=("Dubai Medium",10,"italic"),
                     fg="gray", justify="center").pack()
        else:
            for expense_name, quantity, cost in self.expenses:
                tk.Label(self.content_frame, text=f"{expense_name} x{quantity} = ${cost*quantity:.2f}",
                         wraplength=self.BOX_WIDTH-10, justify="center").pack()
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")

    def delete_category(self):
        self.remove_callback(self)


# CATEGORY SCREEN
class CategoryScreen(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.category_boxes = []
        self.max_cols = 4
        self.build()

    def build(self):
        self.add_category_btn = ttk.Button(self, text="Add Category", command=self.add_category)
        self.add_category_btn.pack(pady=20)

        self.box_frame = tk.Frame(self)
        self.box_frame.pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        self.back_btn = ttk.Button(btn_frame, text="Back", command=lambda: self.app.show_screen("income"))
        self.back_btn.grid(row=0, column=0, padx=10)
        self.continue_btn = ttk.Button(btn_frame, text="Continue", command=self.finish)
        self.continue_btn.grid(row=0, column=1, padx=10)

    def on_show(self):
        for w in self.box_frame.winfo_children():
            w.destroy()
        self.category_boxes = []

        # Load all existing categories from state
        cats = self.app.state.get("categories", {})
        for cname, items in cats.items():
            box = CategoryBox(self.box_frame, cname, self.remove_category, expenses=[(ename, qty, cost) for ename, (qty, cost) in items.items()])
            self.category_boxes.append(box)

        self.reposition_boxes()

    def add_category(self):
        name = simpledialog.askstring("New Category", "Enter category name:", parent=self)
        if not name:
            return
        box = CategoryBox(self.box_frame, name, self.remove_category, is_new=True)
        self.category_boxes.append(box)
        self.reposition_boxes()

    def remove_category(self, box):
        box.destroy()
        self.category_boxes.remove(box)
        self.reposition_boxes()

    def reposition_boxes(self):
        for w in self.box_frame.winfo_children():
            w.grid_forget()
        row, col = 0, 0
        current_row = []
        for i, box in enumerate(self.category_boxes):
            current_row.append(box)
            col += 1
            if col >= self.max_cols or i == len(self.category_boxes)-1:
                total_boxes = len(current_row)
                start_col = (self.max_cols - total_boxes)//2
                for j, b in enumerate(current_row):
                    b.grid(row=row, column=start_col+j, padx=5, pady=5)
                current_row = []
                col = 0
                row += 1

    def finish(self):
        # Only save new entries under "New Entries"
        new_entries = getattr(self.app, "new_entries", {})
        if not new_entries:
            messagebox.showinfo("Saved", "No new entries to save.")
            self.app.show_screen("summary")
            return

        path = self.app.state.get("datafile_name", "budget") + ".txt"
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n--- New Entries ---\n")
            for cat, items in new_entries.items():
                f.write(f"{cat}\n")
                for name, (qty, cost) in items.items():
                    f.write(f"{name} (x{qty}) : ${cost:.2f}\n")
                f.write("\n")
        messagebox.showinfo("Saved", f"New entries appended to {path}")
        self.app.new_entries = {}
        self.app.show_screen("summary")

# summary screen with pie chart
class SummaryScreen(ScreenBase):
    def __init__(self, master, app):
        super().__init__(master, app, background_color="white")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.widgets = []
        self.build()

    def build(self):
        self.title = tk.Label(self, text="Summary", font=("Helvetica",22,"bold"), bg="white")
        self.title.grid(row=0, column=0, columnspan=2, pady=(30,10))
        self.widgets.append(self.title)

        # LEFT SIDE TEXT SUMMARY
        self.text = tk.Text(self, width=60, height=25, font=("Consolas",12))
        self.text.grid(row=1, column=0, padx=20, pady=10, sticky="n")
        self.widgets.append(self.text)

        # RIGHT SIDE PIE CHART
        self.chart_frame = tk.Frame(self, bg="white")
        self.chart_frame.grid(row=1, column=1, padx=20, pady=10, sticky="n")
        self.widgets.append(self.chart_frame)

        # BUTTONS
        btn_row = tk.Frame(self, bg="white")
        btn_row.grid(row=2, column=0, columnspan=2, pady=20)
        self.widgets.append(btn_row)

        back = ttk.Button(btn_row, text="Back", command=lambda: self.app.show_screen("category"))
        finish = ttk.Button(btn_row, text="Finish", command=lambda: messagebox.showinfo("Done", "You can close the app or continue"))

        back.grid(row=0, column=0, padx=10)
        finish.grid(row=0, column=1, padx=10)

    def on_show(self):
        # Clear previous pie chart
        for w in self.chart_frame.winfo_children():
            w.destroy()

        # TEXT SUMMARY
        self.text.delete("1.0", tk.END)
        income = self.app.state.get("income", 0)
        cats = self.app.state.get("categories", {})
        total_expenses = 0
        output = []
        category_totals = {}

        for cat, items in cats.items():
            output.append(f"{cat}:")
            cat_total = 0
            for name, (amt, cost) in items.items():
                total = amt * cost
                cat_total += total
                output.append(f"  {name} x{amt} = ${total:.2f}")
            category_totals[cat] = cat_total
            total_expenses += cat_total
            output.append("")

        leftover = income - total_expenses
        output.append(f"Monthly Income: ${income:.2f}")
        output.append(f"Total Expenses: ${total_expenses:.2f}")
        output.append(f"Remaining Balance: ${leftover:.2f}")
        if leftover < 0:
            output.append("\n⚠ WARNING: You are overspending!")

        self.text.insert(tk.END, "\n".join(output))

        # PIE CHART
        if category_totals:
            fig = plt.Figure(figsize=(5,5), dpi=100)
            ax = fig.add_subplot(111)
            labels = list(category_totals.keys())
            values = list(category_totals.values())
            colors = plt.cm.Pastel1(range(len(labels)))
            wedges, texts, autotexts = ax.pie(values, labels=None, autopct="%1.1f%%", startangle=90, colors=colors, textprops={"fontsize":10})
            ax.legend(wedges, labels, title="Categories", loc="lower center", bbox_to_anchor=(0.5,-0.22), fontsize=9, ncol=3)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()

    # save/load methods remain identical
    def save_to_file(self):
        fname = self.app.state.get("datafile_name","budget")
        path = fname + ".txt"
        cats = self.app.state.get("categories", {})
        lines = []
        for cat, items in cats.items():
            lines.append(f"{cat}:")
            for name, (amt, cost) in items.items():
                lines.append(f"{name} (x{amt}) : ${cost:.2f}")
            lines.append("")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Saved", f"Your data has been saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file:\n{e}")

# save and load functions
# save/load functions in human-readable format
def save_categories(filename, categories_data, new_entries=None):
    path = filename + ".txt"
    lines = []

    # First write past categories and expenses
    for cname, items in categories_data.items():
        lines.append(f"{cname}")
        for ename, (qty, cost) in items.items():
            lines.append(f"{ename} (x{qty}) : ${cost:.2f}")
        lines.append("")  # blank line between categories

    # Optionally write new entries under a section
    if new_entries:
        lines.append("New Entries")
        for cname, items in new_entries.items():
            lines.append(f"{cname}")
            for ename, (qty, cost) in items.items():
                lines.append(f"{ename} (x{qty}) : ${cost:.2f}")
            lines.append("")

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception as e:
        messagebox.showerror("Error", f"Could not save file:\n{e}")


def load_categories(filename):
    """
    Load categories and expenses from a file in the readable format.
    Returns a dict: {category_name: {item_name: (qty, cost), ...}, ...}
    """
    categories = {}
    current = None
    if not os.path.exists(filename):
        return categories

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            if line == "New Entries":
                current = None  # skip, user can handle separately if needed
                continue
            if "(" in line and ")" in line and ":" in line:
                # expense line: "item (xqty) : $cost"
                try:
                    name_part, cost_part = line.split(":")
                    name = name_part.split("(x")[0].strip()
                    quantity = int(name_part.split("(x")[1].split(")")[0])
                    cost = float(cost_part.strip().replace("$",""))
                    if current:
                        categories[current][name] = (quantity, cost)
                except:
                    continue  # skip malformed lines
            else:
                # new category
                current = line
                categories[current] = {}

    return categories

# apppppp
class BudgetBuddyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BudgetBuddy")
        self.state = {}
        self.geometry("900x700")
        self.screens = {}
        self.build_screens()
        self.show_screen("splash")

    def build_screens(self):
        for cls, name in [(SplashScreen,"splash"), (IntroScreen,"intro"), (ProcessScreen,"process"), (DatafileScreen,"datafile"), (IncomeScreen,"income"), (CategoryScreen,"category"), (SummaryScreen,"summary")]:
            screen = cls(self, self)
            self.screens[name] = screen
            screen.place(relwidth=1, relheight=1)

    def show_screen(self, name):
        screen = self.screens.get(name)
        if screen:
            screen.tkraise()
            screen.on_show()

if __name__ == "__main__":
    app = BudgetBuddyApp()
    app.mainloop()
