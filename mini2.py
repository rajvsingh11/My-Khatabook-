import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Expense Tracker")
        self.root.geometry("900x700")

        # Connect to SQLite database
        self.conn = sqlite3.connect('expenses.db')
        self.create_table()

        # Notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tabs: Expense Entry, Summary, Pie Chart, Yearly Summary
        self.expense_tab = ttk.Frame(self.notebook)
        self.summary_tab = ttk.Frame(self.notebook)
        self.pie_chart_tab = ttk.Frame(self.notebook)
        self.yearly_summary_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.expense_tab, text="Expense Entry")
        self.notebook.add(self.summary_tab, text="Monthly Summary")
        self.notebook.add(self.pie_chart_tab, text="Expense Distribution")
        self.notebook.add(self.yearly_summary_tab, text="Yearly Summary")

        self.create_expense_tab()
        self.create_summary_tab()
        self.create_pie_chart_tab()
        self.create_yearly_summary_tab()

    def create_expense_tab(self):
        # Left frame for entries
        left_frame = ttk.Frame(self.expense_tab, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Entry section
        ttk.Label(left_frame, text='Add New Expense', font=('Helvetica', 14, 'bold')).pack(anchor=tk.W, pady=5)

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

        ttk.Label(left_frame, text='Set Monthly Budget:', font=('Helvetica', 14, 'bold')).pack(anchor=tk.W, pady=(20, 5))
        ttk.Label(left_frame, text='Month:').pack(anchor=tk.W)
        self.budget_month_var = tk.StringVar()
        months = [calendar.month_name[i] for i in range(1, 13)]
        self.budget_month_dropdown = ttk.Combobox(left_frame, textvariable=self.budget_month_var, values=months, state='readonly')
        self.budget_month_dropdown.pack(fill=tk.X, pady=5)

        ttk.Label(left_frame, text='Budget Amount:').pack(anchor=tk.W)
        self.budget_amount_entry = ttk.Entry(left_frame)
        self.budget_amount_entry.pack(fill=tk.X, pady=5)

        ttk.Button(left_frame, text='Set Budget', command=self.set_monthly_budget).pack(pady=10)

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

        # Current month's budget display
        self.budget_label = ttk.Label(self.expense_tab, text="Current Month's Budget: N/A", font=('Helvetica', 12))
        self.budget_label.pack(pady=(10, 0))
        self.remaining_budget_label = ttk.Label(self.expense_tab, text="Remaining Budget: N/A", font=('Helvetica', 12))
        self.remaining_budget_label.pack(pady=(5, 10))


        # Load existing data
        self.load_data_from_db()
        self.tree.bind('<ButtonRelease-1>', self.load_selected_expense)

    def create_summary_tab(self):
        ttk.Label(self.summary_tab, text='Monthly Expense Summary', font=('Helvetica', 14, 'bold')).pack(pady=10)

        # Dropdown to select month
        month_frame = ttk.Frame(self.summary_tab)
        month_frame.pack(pady=5)

        ttk.Label(month_frame, text='Select Month:').pack(side=tk.LEFT, padx=5)
        self.month_var = tk.StringVar()
        months = [calendar.month_name[i] for i in range(1, 13)]
        self.month_dropdown = ttk.Combobox(month_frame, textvariable=self.month_var, values=months, state='readonly')
        self.month_dropdown.pack(side=tk.LEFT, padx=5)
        ttk.Button(month_frame, text='Show Summary', command=self.show_monthly_summary).pack(side=tk.LEFT, padx=5)

        # Treeview for monthly summary
        self.summary_tree = ttk.Treeview(self.summary_tab, columns=('Category', 'Amount'), show='headings')
        self.summary_tree.heading('Category', text='Category')
        self.summary_tree.heading('Amount', text='Amount')
        self.summary_tree.column('Category', width=150, anchor=tk.CENTER)
        self.summary_tree.column('Amount', width=100, anchor=tk.CENTER)
        self.summary_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_pie_chart_tab(self):
        ttk.Label(self.pie_chart_tab, text='Expense Distribution', font=('Helvetica', 14, 'bold')).pack(pady=10)
        self.pie_chart_frame = ttk.Frame(self.pie_chart_tab)
        self.pie_chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.show_pie_chart()

    def create_yearly_summary_tab(self):
        ttk.Label(self.yearly_summary_tab, text='Yearly Expense Summary', font=('Helvetica', 14, 'bold')).pack(pady=10)

        # Dropdown to select year
        year_frame = ttk.Frame(self.yearly_summary_tab)
        year_frame.pack(pady=5)

        ttk.Label(year_frame, text='Select Year:').pack(side=tk.LEFT, padx=5)
        self.year_var = tk.StringVar()
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 10, current_year + 1)]
        self.year_dropdown = ttk.Combobox(year_frame, textvariable=self.year_var, values=years, state='readonly')
        self.year_dropdown.pack(side=tk.LEFT, padx=5)
        ttk.Button(year_frame, text='Show Yearly Summary', command=self.show_yearly_summary).pack(side=tk.LEFT, padx=5)

        # Treeview for yearly summary
        self.yearly_summary_tree = ttk.Treeview(self.yearly_summary_tab, columns=('Month', 'Amount'), show='headings')
        self.yearly_summary_tree.heading('Month', text='Month')
        #self.yearly_summary_tree.heading('Category', text='Category')
        self.yearly_summary_tree.heading('Amount', text='Amount')
        self.yearly_summary_tree.column('Month', width=150, anchor=tk.CENTER)
        #self.yearly_summary_tree.column('Category', width=150, anchor=tk.CENTER)
        self.yearly_summary_tree.column('Amount', width=100, anchor=tk.CENTER)
        self.yearly_summary_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def add_expense(self):
        date = self.date_entry.get()
        category = self.category_var.get()
        amount = self.amount_entry.get()

        if date and category and amount:
            try:
                amount = float(amount)
                self.add_data_to_db(date, category, amount)
                self.tree.insert('', 'end', values=(date, category, f'{amount:.2f}'))
                self.clear_entry_fields()
                self.update_budget_display()
                self.show_pie_chart()
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
        else:
            print("All fields are required.")

    def delete_expense(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_id = self.tree.item(selected_item, 'text')
            self.delete_data_from_db(item_id)
            self.tree.delete(selected_item)
            self.update_budget_display()
            self.show_pie_chart()

    def update_expense(self):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            date = self.date_entry.get()
            category = self.category_var.get()
            amount = self.amount_entry.get()
            try:
                amount = float(amount)
                self.update_data_in_db(values[0], date, category, amount)
                self.tree.item(selected_item, values=(date, category, f'{amount:.2f}'))
                self.clear_entry_fields()
                self.update_budget_display()
                self.show_pie_chart()
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")

    def set_monthly_budget(self):
        month = self.budget_month_var.get()
        amount = self.budget_amount_entry.get()
        if month and amount:
            try:
                amount = float(amount)
                self.add_budget_to_db(month, amount)
                self.budget_month_var.set('')
                self.budget_amount_entry.delete(0, tk.END)
                self.update_budget_display()
            except ValueError:
                print("Invalid budget amount. Please enter a numeric value.")
        else:
            print("All fields are required.")

    def show_monthly_summary(self):
        month = self.month_var.get()
        if month:
            month_index = list(calendar.month_name).index(month)
            cursor = self.conn.cursor()
            cursor.execute('''SELECT category, SUM(amount) FROM expenses WHERE strftime('%m', date) = ? GROUP BY category''', (f'{month_index:02}',))
            rows = cursor.fetchall()

            # Clear existing data in the treeview
            for item in self.summary_tree.get_children():
                self.summary_tree.delete(item)

            # Insert new data
            for row in rows:
                self.summary_tree.insert('', 'end', values=(row[0], f'{row[1]:.2f}'))

    def show_pie_chart(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category')
        data = cursor.fetchall()

        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]

        if categories and amounts:
            fig, ax = plt.subplots()
            ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax.axis('equal')

            for widget in self.pie_chart_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.pie_chart_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_yearly_summary(self):
        year = self.year_var.get()
        if year:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT strftime('%m', date) AS month, SUM(amount)
                FROM expenses
                WHERE strftime('%Y', date) = ?
                GROUP BY month
                ORDER BY month
            ''', (year,))
            rows = cursor.fetchall()

            # Clear existing data in the treeview
            for item in self.yearly_summary_tree.get_children():
                self.yearly_summary_tree.delete(item)

            # Get monthly budgets for the year
            monthly_budgets = {}
            cursor.execute('SELECT month, amount FROM budgets WHERE month IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                        (calendar.month_name[1], calendar.month_name[2], calendar.month_name[3], calendar.month_name[4], 
                            calendar.month_name[5], calendar.month_name[6], calendar.month_name[7], calendar.month_name[8], 
                            calendar.month_name[9], calendar.month_name[10], calendar.month_name[11], calendar.month_name[12]))
            for row in cursor.fetchall():
                monthly_budgets[row[0]] = row[1]

            # Insert new data
            for row in rows:
                month_name = calendar.month_name[int(row[0])]
                budget = monthly_budgets.get(month_name, 'N/A')
                self.yearly_summary_tree.insert('', 'end', values=(month_name, f'{row[1]:.2f}', f'{budget}'))


    def add_budget_to_db(self, month, amount):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO budgets (month, amount) VALUES (?, ?)', (month, amount))
        self.conn.commit()

    def update_budget_display(self):
        current_month = datetime.now().strftime('%B')
        cursor = self.conn.cursor()
        cursor.execute('SELECT amount FROM budgets WHERE month = ?', (current_month,))
        row = cursor.fetchone()
        if row:
            budget_text = f"Current Month's Budget: {row[0]:.2f}"
            cursor.execute('SELECT SUM(amount) FROM expenses WHERE strftime("%m", date) = ?', (f'{datetime.now().month:02}',))
            total_expenses = cursor.fetchone()[0] or 0
            remaining_budget = row[0] - total_expenses
            remaining_budget_text = f"Remaining Budget: {remaining_budget:.2f}"
        else:
            budget_text = "Current Month's Budget: N/A"
            remaining_budget_text = "Remaining Budget: N/A"

        self.budget_label.config(text=budget_text)
        self.remaining_budget_label.config(text=remaining_budget_text)

    def clear_entry_fields(self):
        self.date_entry.delete(0, tk.END)
        self.category_var.set('')
        self.amount_entry.delete(0, tk.END)

    def create_table(self):
        cursor = self.conn.cursor()
        # Create expenses table
       # cursor.execute('DROP TABLE IF EXISTS budgets')
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                category TEXT,
                amount REAL
            ) 
        ''')
        # Create budgets table with 'amount' column
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                month TEXT PRIMARY KEY,
                amount REAL
            )
        ''')
        self.conn.commit()


    def add_data_to_db(self, date, category, amount):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)', (date, category, amount))
        self.conn.commit()

    def delete_data_from_db(self, expense_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        self.conn.commit()

    def update_data_in_db(self, expense_id, date, category, amount):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE expenses SET date = ?, category = ?, amount = ? WHERE id = ?', (date, category, amount, expense_id))
        self.conn.commit()

    def load_data_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, date, category, amount FROM expenses')
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert('', 'end', text=row[0], values=(row[1], row[2], f'{row[3]:.2f}'))

    def load_selected_expense(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, values[0])  # Insert the date
            self.category_var.set(values[1])  # Set the category from the selected expense
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, values[2])  # Insert the amount

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
