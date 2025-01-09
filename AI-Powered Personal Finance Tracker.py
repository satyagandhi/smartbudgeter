import streamlit as st
import pandas as pd
import sqlite3
from sklearn.linear_model import LinearRegression
import numpy as np

# SQLite database setup
conn = sqlite3.connect("finance_tracker.db")
c = conn.cursor()

# Create tables for users and expenses
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    username TEXT,
    date TEXT,
    category TEXT,
    amount REAL,
    FOREIGN KEY (username) REFERENCES users (username)
)
""")
conn.commit()

# Preload data (optional)
def preload_data():
    # Check if the table is empty
    c.execute("SELECT * FROM users")
    if not c.fetchall():
        # Add a default user
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("demo_user", "password123"))
        conn.commit()
        # Add some example expenses
        example_expenses = [
            ("demo_user", "2025-01-01", "Food", 50.00),
            ("demo_user", "2025-01-03", "Transport", 15.00),
            ("demo_user", "2025-01-05", "Shopping", 100.00),
        ]
        c.executemany("INSERT INTO expenses (username, date, category, amount) VALUES (?, ?, ?, ?)", example_expenses)
        conn.commit()

# Call the preload function
preload_data()

# Function for user authentication
def authenticate_user(username, password):
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return c.fetchone()

# Function for user registration
def register_user(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Function to add an expense
def add_expense(username, date, category, amount):
    c.execute("INSERT INTO expenses (username, date, category, amount) VALUES (?, ?, ?, ?)", (username, date, category, amount))
    conn.commit()

# Function to get expenses for a user
def get_expenses(username):
    c.execute("SELECT date, category, amount FROM expenses WHERE username = ?", (username,))
    return pd.DataFrame(c.fetchall(), columns=["Date", "Category", "Amount"])

# Function for AI prediction
def predict_expenses(data):
    if len(data) < 2:
        return "Not enough data for prediction"
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.sort_values(by="Date")
    data["Days"] = (data["Date"] - data["Date"].min()).dt.days
    model = LinearRegression()
    model.fit(data[["Days"]], data["Amount"])
    next_day = data["Days"].max() + 30
    return model.predict([[next_day]])[0]

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# App structure
st.title("Smart Budgeter: AI-Powered Personal Finance Tracker")
menu = ["Login", "Register", "Dashboard"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.subheader("Create a New Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    if st.button("Register"):
        if register_user(new_user, new_password):
            st.success("Account created successfully!")
        else:
            st.error("Username already exists. Try a different one.")

elif choice == "Login":
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(username, password):
            st.success(f"Welcome, {username}!")
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
        else:
            st.error("Invalid username or password")

# Dashboard access
if choice == "Dashboard":
    if not st.session_state["logged_in"]:
        st.error("Please log in to access the Dashboard.")
        st.stop()
    username = st.session_state["username"]

    # Add Expense
    st.subheader("Add Expense")
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Utilities", "Entertainment", "Others"])
    amount = st.number_input("Amount", min_value=0.01, format="%.2f")
    if st.button("Add Expense"):
        add_expense(username, str(date), category, amount)
        st.success("Expense added successfully!")

    # View Summary
    st.subheader("Expense Summary")
    expenses = get_expenses(username)
    if not expenses.empty:
        st.dataframe(expenses)

        # Total expenses
        total = expenses["Amount"].sum()
        st.subheader(f"Total Expenses: ${total:.2f}")

        # Category-wise breakdown
        st.bar_chart(expenses.groupby("Category")["Amount"].sum())

        # AI Prediction
        prediction = predict_expenses(expenses)
        if isinstance(prediction, str):
            st.info(prediction)
        else:
            st.subheader(f"Predicted Expenses for Next Month: ${prediction:.2f}")
    else:
        st.warning("No expenses added yet!")




