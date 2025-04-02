import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")

        # Connect to SQLite database
        self.conn = sqlite3.connect('expenses.db')
        self.create_table()

        # Create a left frame for entry and treeview
        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Create a right frame for pie chart and summary
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # Expense Entry Section
        self.entry_label = tk.Label(self.left_frame, text='Expense Entry', font=('Helvetica', 14, 'bold'))
        self.entry_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.date_label = tk.Label(self.left_frame, text='Date:')
        self.date_label.grid(row=1, column=0, sticky=tk.E)
        self.date_entry = tk.Entry(self.left_frame)
        self.date_entry.grid(row=1, column=1, pady=5)

        self.category_label = tk.Label(self.left_frame, text='Category:')
        self.category_label.grid(row=2, column=0, sticky=tk.E)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.left_frame, textvariable=self.category_var, state='readonly')
        self.category_dropdown['values'] = ('Groceries', 'Utilities', 'Rent', 'Entertainment', 'Other')
        self.category_dropdown.grid(row=2, column=1, pady=5)

        self.amount_label = tk.Label(self.left_frame, text='Amount:')
        self.amount_label.grid(row=3, column=0, sticky=tk.E)
        self.amount_entry = tk.Entry(self.left_frame)
        self.amount_entry.grid(row=3, column=1, pady=5)

        self.add_button = tk.Button(self.left_frame, text='Add Expense', command=self.add_expense)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.modify_button = tk.Button(self.left_frame, text='Modify Expense', command=self.update_expense)
        self.modify_button.grid(row=5, column=0, pady=5)

        self.delete_button = tk.Button(self.left_frame, text='Delete Expense', command=self.delete_expense)
        self.delete_button.grid(row=5, column=1, pady=5)

        # Expense Treeview Section
        self.tree_label = tk.Label(self.left_frame, text='Expense List', font=('Helvetica', 14, 'bold'))
        self.tree_label.grid(row=6, column=0, columnspan=2, pady=(20, 10))

        self.tree = ttk.Treeview(self.left_frame, columns=('Date', 'Category', 'Amount'))
        self.tree.heading('#0', text='ID')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Amount', text='Amount')
        self.tree.column('#0', width=50, anchor='center')
        self.tree.column('Date', width=100, anchor='center')
        self.tree.column('Category', width=150, anchor='center')
        self.tree.column('Amount', width=100, anchor='center')
        self.tree.grid(row=7, column=0, columnspan=2, pady=10)

        # Summary Section
        self.summary_label = tk.Label(self.right_frame, text='Summary', font=('Helvetica', 14, 'bold'))
        self.summary_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.total_expense_label = tk.Label(self.right_frame, text='Total Expenses:')
        self.total_expense_label.grid(row=1, column=0, sticky=tk.E)
        self.total_expense_value = tk.Label(self.right_frame, text='0.00')
        self.total_expense_value.grid(row=1, column=1)


        # Display pie chart to the right of the application
        self.pie_chart_frame = tk.Frame(self.right_frame)
        self.pie_chart_frame.grid(row=3, column=0, columnspan=2, pady=(20, 10))

        # Load existing data from the SQLite database
        self.load_data_from_db()

        # Set up event binding for selecting items in the treeview
        self.tree.bind('<ButtonRelease-1>', self.load_selected_expense)
    
    def add_expense(self):
        date = self.date_entry.get()
        category = self.category_var.get()
        amount = self.amount_entry.get()

        if date and category and amount:
            # Add the data to the treeview
            expense_id = len(self.tree.get_children()) + 1
            self.tree.insert('', 'end', text=expense_id, values=(date, category, amount))

            # Add the data to the database
            self.add_data_to_db(date, category, amount)

            # Update summary
            self.update_summary()

            # Clear the entry fields
            self.clear_entry_fields()
        else:
            print("Please fill in all fields.")

    def delete_expense(self):
        selected_item = self.tree.selection()

        if selected_item:
            # Delete the selected item from the treeview
            self.tree.delete(selected_item)

            # Delete the selected item from the database
            self.delete_data_from_db(selected_item[0])

            # Update summary
            self.update_summary()

            # Clear the entry fields
            self.clear_entry_fields()

    def update_expense(self):
        selected_item = self.tree.selection()

        if selected_item:
            # Get data from the entry fields
            date = self.date_entry.get()
            category = self.category_var.get()
            amount = self.amount_entry.get()

            if date and category and amount:
                # Update the selected item in the treeview
                self.tree.item(selected_item, values=(date, category, amount))

                # Update the selected item in the database
                self.update_data_in_db(selected_item[0], date, category, amount)

                # Update summary
                self.update_summary()

                # Clear the entry fields
                self.clear_entry_fields()
            else:
                print("Please fill in all fields.")

    
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                date TEXT,
                category TEXT,
                amount REAL
            )
        ''')
        self.conn.commit()

    def add_data_to_db(self, date, category, amount):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (date, category, amount)
            VALUES (?, ?, ?)
        ''', (date, category, amount))
        self.conn.commit()

    def load_data_from_db(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM expenses')
            rows = cursor.fetchall()

            for row in rows:
                expense_id, date, category, amount = row
                self.tree.insert('', 'end', text=expense_id, values=(date, category, amount))

            # Update summary
            self.update_summary()
        except sqlite3.Error as e:
            print(f"Error loading data from database: {e}")

    def delete_data_from_db(self, selected_item):
        # Extract the numeric part from the selected item text
        selected_id = selected_item.lstrip('I')

        # Connect to the SQLite database
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        try:
            # Delete the selected item from the database
            cursor.execute('DELETE FROM expenses WHERE id = ?', (int(selected_id),))
            conn.commit()
        except Exception as e:
            print(f"Error deleting data from the database: {e}")
        finally:
            conn.close()
    
    def update_data_in_db(self, selected_item, date, category, amount):
        # Extract the numeric part from the selected item text
        selected_id = selected_item.lstrip('I')

        # Connect to the SQLite database
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        try:
            # Update the selected item in the database
            cursor.execute('''
            UPDATE expenses 
            SET date = ?, category = ?, amount = ? 
            WHERE id = ?
            ''', (date, category, amount, int(selected_id)))

            conn.commit()
        except Exception as e:
            print(f"Error updating data in the database: {e}")
        finally:
            conn.close()
    
    def load_selected_expense(self, event):
        selected_item = self.tree.selection()

        if selected_item:
            item_id = self.tree.item(selected_item, 'text')
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM expenses WHERE id = ?', (int(item_id),))
            row = cursor.fetchone()

            if row:
                item_values = row
                self.date_entry.delete(0, 'end')
                self.date_entry.insert(0, item_values[1])

                self.category_var.set(item_values[2])

                self.amount_entry.delete(0, 'end')
                self.amount_entry.insert(0, item_values[3])


    def update_summary(self):
        total_expenses = sum(float(self.tree.item(item)['values'][2]) for item in self.tree.get_children())

        # Update labels in the summary section
        self.total_expense_value.config(text=f'{total_expenses:.2f}')

        # Update pie chart
        self.show_pie_chart()


    def show_pie_chart(self):
        # Load data from the SQLite database
        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()
        cursor.execute('SELECT category, amount FROM expenses')
        data = cursor.fetchall()
        conn.close()

        # Get data for the pie chart
        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]

        # Define 5 colors for the pie chart
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

        # Create a pie chart with the defined colors
        fig, ax = plt.subplots()
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.

        # Clear previous pie chart in the frame
        for widget in self.pie_chart_frame.winfo_children():
            widget.destroy()

        # Display the pie chart in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.pie_chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def clear_entry_fields(self):
        # Clear the entry fields
        self.date_entry.delete(0, 'end')
        self.category_var.set('')
        self.amount_entry.delete(0, 'end')

    def __del__(self):
        # Close the database connection when the object is deleted
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
