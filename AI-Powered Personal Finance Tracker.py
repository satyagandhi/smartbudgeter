#!/usr/bin/env python
# coding: utf-8

# In[23]:


import streamlit as st
import pandas as pd
import sqlite3
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import numpy as np


# In[25]:


# SQLite database setup
conn = sqlite3.connect("finance_tracker.db")
c = conn.cursor()


# In[27]:


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


# In[29]:


# Function for user authentication
def authenticate_user(username, password):
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return c.fetchone()


# In[31]:


# Function for user registration
def register_user(username, password):
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


# In[33]:


# Function to add expense
def add_expense(username, date, category, amount):
    c.execute("INSERT INTO expenses (username, date, category, amount) VALUES (?, ?, ?, ?)", (username, date, category, amount))
    conn.commit()


# In[35]:


# Function to get expenses for a user
def get_expenses(username):
    c.execute("SELECT date, category, amount FROM expenses WHERE username = ?", (username,))
    return pd.DataFrame(c.fetchall(), columns=["Date", "Category", "Amount"])


# In[37]:


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


# In[47]:


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

if "logged_in" in st.session_state:
    st.sidebar.success(f"Logged in as {st.session_state['username']}")


# In[53]:


# Dashboard
if choice == "Dashboard":
    username = st.session_state["username"]


# In[65]:


# Add Expense
st.subheader("Add Expense")
date = st.date_input("Date")
category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Utilities", "Entertainment", "Others"])
amount = st.number_input("Amount", min_value=0.01, format="%.2f")
if st.button("Add Expense"):
    add_expense(username, str(date), category, amount)
    st.success("Expense added successfully!")


# In[69]:


# View Summary
st.subheader("Expense Summary")
expenses = get_expenses(username)
if not expenses.empty:
            st.dataframe(expenses)


# In[71]:


# Total expenses
total = expenses["Amount"].sum()
st.subheader(f"Total Expenses: ${total:.2f}")


# In[75]:


# Category-wise breakdown
st.bar_chart(expenses.groupby("Category")["Amount"].sum())


# In[95]:


# AI Prediction
prediction = predict_expenses(expenses)

if isinstance(prediction, str):
    st.info(prediction)
else:
    st.subheader(f"Predicted Expenses for Next Month: ${prediction:.2f}")

# Check if the DataFrame is empty
if expenses.empty:
    st.warning("No expenses added yet!")


# In[97]:



# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




