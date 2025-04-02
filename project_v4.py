import tkinter as tk
from tkinter import ttk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.conn = sqlite3.connect('expenses.db')  # Connect to the database
        self.create_table()

        self.root = root
        self.root.title('Expense Tracker')
        self.root.geometry('800x600')

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.expense_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.expense_tab, text='Expenses')

        self.monthly_summary_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.monthly_summary_tab, text='Monthly Summary')

        self.create_expense_tab()
        self.create_pie_chart_tab()
        self.create_monthly_summary_tab()

    def create_table(self):
        cursor = self.conn.cursor()
        # Create table for expenses
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL
        )''')

        # Create table for budget
        cursor.execute('''CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget REAL
        )''')
        self.conn.commit()

    def create_expense_tab(self):
        # Left frame for entries
        left_frame = ttk.Frame(self.expense_tab, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Entry section (Add New Expense)
        ttk.Label(left_frame, text='Add New Expense', font=('Helvetica', 14, 'bold')).pack(anchor=tk.W, pady=5)

        # Existing fields (Date, Category, Amount)
        ttk.Label(left_frame, text='Date (YYYY-MM-DD):').pack(anchor=tk.W)
        self.date_entry = ttk.Entry(left_frame)
        self.date_entry.pack(fill=tk.X, pady=5)

        ttk.Label(left_frame, text='Category:').pack(anchor=tk.W)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(left_frame, textvariable=self.category_var, state='readonly')
        self.category_dropdown['values'] = ('Groceries', 'Utilities', 'Rent', 'Entertainment', 'Other')
        self.category_dropdown.pack(fill=tk.X, pady=5)

        ttk.Label(left_frame, text='Amount:').pack(anchor=tk.W)
        self.amount_entry = ttk.Entry(left_frame)
        self.amount_entry.pack(fill=tk.X, pady=5)

        ttk.Button(left_frame, text='Add Expense', command=self.add_expense).pack(pady=10)

        # Treeview for expenses
        ttk.Label(self.expense_tab, text='Expense List', font=('Helvetica', 14, 'bold')).pack(pady=(10, 5))
        self.tree = ttk.Treeview(self.expense_tab, columns=('Date', 'Category', 'Amount'), show='headings')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Amount', text='Amount')
        self.tree.column('Date', width=150, anchor=tk.CENTER)
        self.tree.column('Category', width=150, anchor=tk.CENTER)
        self.tree.column('Amount', width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons to modify data
        button_frame = ttk.Frame(self.expense_tab)
        button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text='Modify Expense', command=self.update_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Delete Expense', command=self.delete_expense).pack(side=tk.LEFT, padx=5)

        # Display total budget
        self.total_budget_label = ttk.Label(self.expense_tab, text='Total Budget: $0.00', font=('Helvetica', 12, 'bold'))
        self.total_budget_label.pack(side=tk.BOTTOM, pady=10)

        # Load existing data
        self.load_data_from_db()
        self.tree.bind('<ButtonRelease-1>', self.load_selected_expense)

        # Update total budget
        self.update_total_budget()

        # Budget Entry Section
        self.budget_label = ttk.Label(left_frame, text="Set Monthly Budget:")
        self.budget_label.pack(fill=tk.X, pady=5)

        self.budget_entry = ttk.Entry(left_frame)
        self.budget_entry.pack(fill=tk.X, pady=5)

        ttk.Button(left_frame, text="Set Budget", command=self.set_budget).pack(pady=10)

    def update_total_budget(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT budget FROM budget WHERE id = 1')  # Assuming there is one record for the budget
        result = cursor.fetchone()
        total_budget = result[0] if result else 0
        self.total_budget_label.config(text=f'Total Budget: ${total_budget:.2f}')

    def set_budget(self):
        try:
            budget = float(self.budget_entry.get())
            cursor = self.conn.cursor()
            cursor.execute('''INSERT OR REPLACE INTO budget (id, budget) VALUES (1, ?)''', (budget,))
            self.conn.commit()
            self.update_total_budget()  # Update the total budget label
        except ValueError:
            print("Invalid budget amount.")

    def add_expense(self):
        date = self.date_entry.get()
        category = self.category_var.get()
        amount = self.amount_entry.get()

        if date and category and amount:
            try:
                amount = float(amount)
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)",
                               (date, category, amount))
                self.conn.commit()
                self.load_data_from_db()
                self.date_entry.delete(0, tk.END)
                self.amount_entry.delete(0, tk.END)
                self.category_var.set('')
            except ValueError:
                print("Invalid amount.")
        else:
            print("Please fill all fields.")

    def load_data_from_db(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM expenses")
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row[1:])

    def load_selected_expense(self, event):
        selected_item = self.tree.selection()[0]
        expense_data = self.tree.item(selected_item, 'values')

        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, expense_data[0])

        self.category_var.set(expense_data[1])

        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, expense_data[2])

    def update_expense(self):
        selected_item = self.tree.selection()[0]
        expense_data = self.tree.item(selected_item, 'values')

        date = self.date_entry.get()
        category = self.category_var.get()
        amount = self.amount_entry.get()

        if date and category and amount:
            try:
                amount = float(amount)
                cursor = self.conn.cursor()
                cursor.execute('''UPDATE expenses SET date = ?, category = ?, amount = ? WHERE id = ?''',
                               (date, category, amount, expense_data[0]))
                self.conn.commit()
                self.load_data_from_db()
            except ValueError:
                print("Invalid amount.")
        else:
            print("Please fill all fields.")

    def delete_expense(self):
        selected_item = self.tree.selection()[0]
        expense_data = self.tree.item(selected_item, 'values')

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_data[0],))
        self.conn.commit()
        self.load_data_from_db()

    def create_pie_chart_tab(self):
        self.pie_chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pie_chart_frame, text='Expense Distribution')

        self.bar_chart_container = ttk.Frame(self.pie_chart_frame)
        self.bar_chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Generate Pie Chart or Bar Chart
        self.show_bar_chart()

    def show_bar_chart(self):
        # Get total expense from the database
        cursor = self.conn.cursor()
        cursor.execute('SELECT SUM(amount) FROM expenses')
        total_expense = cursor.fetchone()[0] or 0

        # Get monthly budget from the database
        cursor.execute('SELECT budget FROM budget WHERE id = 1')
        result = cursor.fetchone()
        total_budget = result[0] if result else 0

        # Calculate remaining budget
        remaining_budget = total_budget - total_expense

        # Create bar chart
        categories = ['Total Expense', 'Remaining Budget']
        values = [total_expense, remaining_budget]

        fig, ax = plt.subplots()
        ax.bar(categories, values, color=['red', 'green'])
        ax.set_ylabel('Amount')
        ax.set_title('Expense vs Remaining Budget')

        # Display the chart on the Tkinter canvas
        for widget in self.bar_chart_container.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.bar_chart_container)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_monthly_summary_tab(self):
        self.summary_frame = ttk.Frame(self.monthly_summary_tab, padding=10)
        self.summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Labels for summary
        ttk.Label(self.summary_frame, text="Monthly Summary", font=("Helvetica", 14, "bold")).pack(pady=5)

        self.summary_label = ttk.Label(self.summary_frame, text="Total Expenses: $0.00\nRemaining Budget: $0.00", font=("Helvetica", 12))
        self.summary_label.pack(pady=10)

        # Update monthly summary
        self.update_monthly_summary()

    def update_monthly_summary(self):
        current_month = datetime.now().strftime('%Y-%m')  # Get the current month in YYYY-MM format
        cursor = self.conn.cursor()

        # Get total expenses for the current month
        cursor.execute('''SELECT SUM(amount) FROM expenses WHERE strftime('%Y-%m', date) = ?''', (current_month,))
        total_expenses = cursor.fetchone()[0] or 0

        # Get monthly budget
        cursor.execute('SELECT budget FROM budget WHERE id = 1')
        result = cursor.fetchone()
        total_budget = result[0] if result else 0

        # Calculate remaining budget
        remaining_budget = total_budget - total_expenses

        # Update the summary label
        self.summary_label.config(text=f"Total Expenses: ${total_expenses:.2f}\nRemaining Budget: ${remaining_budget:.2f}")


if __name__ == '__main__':
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
