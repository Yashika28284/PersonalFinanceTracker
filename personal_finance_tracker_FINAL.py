# -*- coding: utf-8 -*-
"""
Created on Mon Jun 23 16:40:06 2025

@author: yashi
"""
import matplotlib.pyplot as plt
from tkinter import Toplevel


import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import csv
style_font = ("Segoe UI", 10)  
font_regular = ("Segoe UI", 10)
font_heading = ("Segoe UI", 11, "bold")


btn_style = {
    "bg": "#e0e0e0",
    "fg": "#000000",
    "activebackground": "#d0d0d0",
    "bd": 0,
    "font": font_regular,
    "padx": 10,
    "pady": 5
}



# Main application window
root = tk.Tk()
root.title("Personal Finance Tracker")
root.geometry("1000x1000")
root.resizable(False, False)
conn = sqlite3.connect('expenses.db')  # Creates DB file
cursor = conn.cursor()

# Create table (if not exists)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
''')
conn.commit()



# ------------------ Header ------------------
header = tk.Label(root, text="Expense Entry", font=("Helvetica", 16, "bold"))
header.pack(pady=10)

# ------------------ Input Fields ------------------

# Date
tk.Label(root, text="Date (YYYY-MM-DD):",font=style_font).pack()
date_entry = tk.Entry(root)
date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))  # Auto-fill today
date_entry.pack()

# Category
tk.Label(root, text="Category:",font=style_font).pack()
category_entry = ttk.Combobox(root, values=["Food", "Transport", "Bills", "Shopping", "Other"], state="readonly",font=style_font)

category_entry.pack()




# Amount
tk.Label(root, text="Amount:",font=style_font).pack()
amount_entry = tk.Entry(root)
amount_entry.pack()

# Description
tk.Label(root, text="Description:",font=style_font).pack()
desc_entry = tk.Entry(root)
desc_entry.pack()
def launch_chat_assistant():
    def get_reply():
        user_input = entry.get().lower()
        response = ""

        if "total" in user_input and "spend" in user_input:
            cursor.execute("SELECT SUM(amount) FROM expenses")
            total = cursor.fetchone()[0] or 0
            response = f"🧾 Your total spending is ₹{total:.2f}"

        elif "average" in user_input:
            cursor.execute("SELECT SUM(amount) FROM expenses")
            total = cursor.fetchone()[0] or 0
            cursor.execute("SELECT COUNT(DISTINCT date) FROM expenses")
            days = cursor.fetchone()[0] or 1
            avg = total / days
            response = f"📅 Your average daily spend is ₹{avg:.2f}"

        elif "highest" in user_input or "most" in user_input:
            cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                response = f"🔝 You spent the most on {row[0]} (₹{row[1]:.2f})"
            else:
                response = "No data yet."

        elif "save" in user_input:
            response = "💡 Tip: Track categories > 50% of total and reduce by 10–15%."

        else:
            response = "🤖 I didn't understand. Try: 'total spend', 'average', 'highest category', or 'how to save'."

        chat_log.config(state='normal')
        chat_log.insert(tk.END, f"You: {user_input}\nBot: {response}\n\n")
        chat_log.config(state='disabled')
        entry.delete(0, tk.END)

    # Popup
    top = Toplevel(root)
    top.title("💬 AI Assistant")

    chat_log = tk.Text(top, width=50, height=15, state='disabled', wrap='word')
    chat_log.pack(padx=10, pady=5)

    entry = tk.Entry(top, width=40)
    entry.pack(side=tk.LEFT, padx=10, pady=10)

    send_btn = tk.Button(top, text="Send", command=get_reply)
    send_btn.pack(side=tk.LEFT)

chat_btn = tk.Button(root, text="Ask Assistant 🤖", command=launch_chat_assistant, **btn_style)
chat_btn.pack(pady=10)

button_frame = tk.Frame(root)
def show_suggestions():
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_spent = cursor.fetchone()[0]

    if not total_spent:
        messagebox.showinfo("No Data", "Add some expenses to get suggestions.")
        return

    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()

    suggestion_text = ""

    for category, amount in data:
        percent = (amount / total_spent) * 100
        if percent > 50:
            suggestion_text += f"🔻 You spent {percent:.1f}% on {category}. Consider reducing this.\n"
        else:
            suggestion_text += f"✅ {category}: {percent:.1f}% of total.\n"

    cursor.execute("SELECT COUNT(DISTINCT date) FROM expenses")
    days = cursor.fetchone()[0]
    avg_daily = total_spent / days if days else total_spent
    suggestion_text += f"\n📅 Avg daily spend: ₹{avg_daily:.2f}"

    top = Toplevel(root)
    top.title("Smart Suggestions")
    tk.Label(top, text="💡 Financial Suggestions", font=font_heading).pack(pady=10)
    tk.Label(top, text=suggestion_text, justify="left", font=font_regular).pack(padx=15, pady=10)

suggest_btn = tk.Button(button_frame, text="Smart Suggestions", command=show_suggestions, **btn_style)





# ------------------ Submit Button ------------------

def submit_entry():
    date = date_entry.get()
    category = category_entry.get()
    amount = amount_entry.get()
    desc = desc_entry.get()

    if not date or not category or not amount:
        messagebox.showwarning("Missing Data", "Please fill in all required fields.")
        return

    try:
        float(amount)
    except ValueError:
        messagebox.showerror("Invalid Input", "Amount must be a number.")
        return

    # Save to database
    cursor.execute('''
        INSERT INTO expenses (date, category, amount, description)
        VALUES (?, ?, ?, ?)
    ''', (date, category, float(amount), desc))
    conn.commit()

    messagebox.showinfo("Success", f"Expense saved:\n{category} - ₹{amount}")

    # Debug: print all rows in the database
    with open("debug_log.txt", "w") as f:
        f.write("--- Current Expenses ---\n")
        # Clear form fields
        date_entry.delete(0, tk.END)
        category_entry.set('')
        amount_entry.delete(0, tk.END)
        desc_entry.delete(0, tk.END)
        for row in cursor.execute("SELECT * FROM expenses"):
            f.write(str(row) + "\n")
            date_entry.delete(0, tk.END)
            date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))
            category_entry.set('')  # Clear dropdown
            amount_entry.delete(0, tk.END)
            desc_entry.delete(0, tk.END)
    load_expenses()
    

def show_table():
    table_frame.pack(pady=10)
    expense_table.pack(side=tk.LEFT, fill='both', expand=True)  
    scrollbar.pack(side=tk.RIGHT, fill='y')
    hide_btn.pack(pady=5)
    load_expenses()
    filter_frame.pack(pady=5)
    button_frame.pack(pady=10)
    suggest_btn.pack(side=tk.LEFT, padx=5)
    predict_btn.pack(side=tk.LEFT, padx=5)





    total_label.pack(pady=5)  # Show total below the table
    export_btn.pack(pady=5)





def export_to_csv():
    with open("expenses_export.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Date", "Category", "Amount", "Description"])  # header row

        for row in cursor.execute("SELECT * FROM expenses ORDER BY id"):
            writer.writerow(row)

    messagebox.showinfo("Export Complete", "Expenses exported to 'expenses_export.csv'")



def hide_table():
    table_frame.pack_forget()
    hide_btn.pack_forget()
    bar_chart_btn.pack_forget()
    button_frame.pack_forget()
    predict_btn.pack_forget()


    suggest_btn.pack_forget()

    filter_frame.pack_forget()
    total_label.pack_forget()
    export_btn.pack_forget()
    delete_btn.pack_forget()
    chart_btn.pack_forget()
def show_prediction():
    # Get total amount and unique days
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_spent = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(DISTINCT date) FROM expenses")
    days = cursor.fetchone()[0] or 1

    avg_per_day = total_spent / days
    predicted_week = avg_per_day * 7
    predicted_month = avg_per_day * 30

    prediction_text = (
        f"📊 Based on your past spending:\n\n"
        f"• Average per day: ₹{avg_per_day:.2f}\n"
        f"• Predicted next 7 days: ₹{predicted_week:.2f}\n"
        f"• Predicted next 30 days: ₹{predicted_month:.2f}\n"
    )

    top = Toplevel(root)
    top.title("Spending Prediction")
    tk.Label(top, text="🔮 Spending Forecast", font=font_heading).pack(pady=10)
    tk.Label(top, text=prediction_text, justify="left", font=font_regular).pack(padx=15, pady=10)

def show_category_chart():
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()

    if not data:
        messagebox.showinfo("No Data", "No expenses to show.")
        return

    categories = [row[0] for row in data]
    totals = [row[1] for row in data]

    
    chart_win = Toplevel(root)
    chart_win.title("Spending by Category")

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(totals, labels=categories, autopct='%1.1f%%', startangle=90)
    ax.set_title("Spending Distribution")

    
    canvas = plt.get_current_fig_manager().canvas
    plt.tight_layout()
    canvas.draw()
    fig.savefig("category_chart.png")  # save it to file temporarily

    # Use Tkinter to show the image
    img = tk.PhotoImage(file="category_chart.png")
    label = tk.Label(chart_win, image=img)
    label.image = img  
    label.pack()
def show_daily_chart():
    cursor.execute("SELECT date, SUM(amount) FROM expenses GROUP BY date ORDER BY date")
    data = cursor.fetchall()

    if not data:
        messagebox.showinfo("No Data", "No expenses to show.")
        return

    dates = [row[0] for row in data]
    totals = [row[1] for row in data]

    # Create popup
    chart_win = Toplevel(root)
    chart_win.title("Daily Spending Chart")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(dates, totals, color="#4A90E2")
    ax.set_title("Total Spending per Day")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount Spent")
    ax.tick_params(axis='x', rotation=45)

    # Save and display
    fig.tight_layout()
    fig.savefig("daily_spending_chart.png")

    img = tk.PhotoImage(file="daily_spending_chart.png")
    label = tk.Label(chart_win, image=img)
    label.image = img
    label.pack()





    total_label.pack_forget()  
def delete_selected():
    selected_items = expense_table.selection()
    if not selected_items:
        messagebox.showwarning("No Selection", "Please select a row to delete.")
        return

    for item in selected_items:
        values = expense_table.item(item, 'values')
        if not values:
            continue

        expense_id = values[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Delete entry ID {expense_id}?")
        if confirm:
           
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()

            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS temp_expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    category TEXT,
                    amount REAL,
                    description TEXT
                )
            """)

            cursor.execute("""
                INSERT INTO temp_expenses (date, category, amount, description)
                SELECT date, category, amount, description FROM expenses ORDER BY id
            """)

            cursor.execute("DROP TABLE expenses")
            cursor.execute("ALTER TABLE temp_expenses RENAME TO expenses")
            conn.commit()

    load_expenses()
    messagebox.showinfo("Deleted", "Selected entry deleted and IDs renumbered.")



submit_btn = tk.Button(root, text="Submit", command=submit_entry,**btn_style)

submit_btn.pack(pady=10)
show_btn = tk.Button(root, text="Show All Expenses", command=show_table,**btn_style)
  
hide_btn = tk.Button(root, text="Hide Table", command=hide_table,**btn_style
)
#export_btn = tk.Button(root, text="Export to CSV", command=export_to_csv,**btn_style





show_btn.pack(pady=5)



# Reset to today
def clear_filter():
    filter_entry.delete(0, tk.END)  # clear the input box
    load_expenses()                 # reload all data

def load_expenses(filtered_date=None):
    # Clear previous data
    for item in expense_table.get_children():
        expense_table.delete(item)

    total = 0

    if filtered_date:
        query = "SELECT * FROM expenses WHERE date = ? ORDER BY id DESC"
        rows = cursor.execute(query, (filtered_date,))
    else:
        rows = cursor.execute("SELECT * FROM expenses ORDER BY id DESC")

    for row in rows:
        expense_table.insert("", tk.END, values=row)
        total += float(row[3])

    total_label.config(text=f"Total: ₹{total:.2f}")
def on_row_select(event):
    selected_items = expense_table.selection()
    if selected_items:
        delete_btn.pack(pady=5)
    else:
        delete_btn.pack_forget()



# ------------------ Filter Controls ------------------
filter_frame = tk.Frame(root)
#filter_frame.pack(pady=5)

tk.Label(filter_frame, text="Filter by Date (YYYY-MM-DD):").pack(side=tk.LEFT, padx=5)

export_btn = tk.Button(button_frame, text="Export to CSV", command=export_to_csv, **btn_style)
delete_btn = tk.Button(button_frame, text="Delete Selected", command=delete_selected, **btn_style)
chart_btn = tk.Button(button_frame, text="Spending by Category", command=show_category_chart, **btn_style)
bar_chart_btn = tk.Button(button_frame, text="Daily Spending Chart", command=show_daily_chart, **btn_style)
predict_btn = tk.Button(button_frame, text="Predict Spending", command=show_prediction, **btn_style)

filter_entry = tk.Entry(filter_frame)
filter_entry.pack(side=tk.LEFT, padx=5)

filter_btn = tk.Button(filter_frame, text="Apply Filter", command=lambda: load_expenses(filter_entry.get()))
filter_btn.pack(side=tk.LEFT, padx=5)

reset_btn = tk.Button(filter_frame, text="Clear Filter", command=lambda: clear_filter())

reset_btn.pack(side=tk.LEFT, padx=5)

export_btn.pack(side=tk.LEFT, padx=5, pady=5)
delete_btn.pack(side=tk.LEFT, padx=5, pady=5)
chart_btn.pack(side=tk.LEFT, padx=5, pady=5)
bar_chart_btn.pack(side=tk.LEFT, padx=5, pady=5)





    





# ------------------ Expense Table ------------------
table_frame = tk.Frame(root)
#table_frame.pack(pady=10)

columns = ("id", "date", "category", "amount", "description")

expense_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
expense_table.bind("<<TreeviewSelect>>", on_row_select)
style = ttk.Style()
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)

#expense_table.pack(side=tk.LEFT)

# Define column headings
for col in columns:
    expense_table.heading(col, text=col.capitalize())
    expense_table.column(col, width=80)
    expense_table.column("description", width=150)


# Scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=expense_table.yview)
expense_table.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill="y")
total_label = tk.Label(table_frame, text="Total: ₹0.00", font=("Arial", 10, "bold"))



# ------------------ Mainloop ------------------
root.mainloop()


