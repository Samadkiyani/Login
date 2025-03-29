import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import streamlit as st
import os
import uuid
import base64
from datetime import datetime

def set_background(image_url):
    bg_css = f"""
    <style>
    .stApp {{
        background-image: url("{image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

# Set background
set_background("https://img.freepik.com/premium-photo/business-data-financial-figures-visualiser-graphic_31965-24532.jpg?semt=ais_hybrid")

st.image("https://media.istockphoto.com/id/1488294044/photo/businessman-works-on-laptop-showing-business-analytics-dashboard-with-charts-metrics-and-kpi.jpg?s=612x612&w=0&k=20&c=AcxzQAe1LY4lGp0C6EQ6reI7ZkFC2ftS09yw_3BVkpk=", use_container_width =True)

data_file = "budget_data.csv"
users_file = "users.csv"

def load_users():
    if os.path.exists(users_file) and os.stat(users_file).st_size > 0:
        return pd.read_csv(users_file)
    else:
        return pd.DataFrame(columns=["Username", "Password"])

def save_users(df):
    df.to_csv(users_file, index=False)

def load_data():
    if os.path.exists(data_file) and os.stat(data_file).st_size > 0:
        return pd.read_csv(data_file)
    else:
        return pd.DataFrame(columns=["ID", "Date", "Customer", "Category", "Amount", "Type"])

def save_data(df):
    df.to_csv(data_file, index=False)

data = load_data()
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""

def login_page():
    users = load_users()
    st.title("🔑 Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if not users.empty and ((users["Username"] == username) & (users["Password"] == password)).any():
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success("Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("Invalid username or password")

def signup_page():
    st.title("📝 Sign Up for an Account")
    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")
    
    if st.button("Sign Up"):
        users = load_users()
        if new_username.strip() == "" or new_password.strip() == "":
            st.error("Please fill in both fields.")
        elif new_username in users["Username"].values:
            st.error("Username already exists. Choose another.")
        else:
            new_user = pd.DataFrame([[new_username, new_password]], columns=["Username", "Password"])
            users = pd.concat([users, new_user], ignore_index=True)
            save_users(users)
            st.success("Account created successfully! You can now log in.")

def budget_dashboard():
    global data
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    st.title(f"💰 {greeting}, {st.session_state['username']}! Welcome to Samad Kiani Budget Dashboard")
    
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.rerun()
    
    st.sidebar.header("Add a New Transaction")
    date = st.sidebar.date_input("Date")
    customer = st.sidebar.text_input("Customer Name")
    category = st.sidebar.selectbox("Category", ["Salary", "Groceries", "Bills", "Entertainment", "Transport", "Other"])
    amount = st.sidebar.slider("Amount", min_value=0, max_value=10000, step=10)
    transaction_type = st.sidebar.radio("Type", ("Income", "Expense"))
    
    if st.sidebar.button("Add Transaction"):
        existing_customer = data[data["Customer"] == customer]
        if not existing_customer.empty:
            customer_id = existing_customer.iloc[0]["ID"]
        else:
            customer_id = str(uuid.uuid4())[:8]
        
        new_data = pd.DataFrame([[customer_id, date, customer, category, amount, transaction_type]], columns=["ID", "Date", "Customer", "Category", "Amount", "Type"])
        data = pd.concat([data, new_data], ignore_index=True)
        save_data(data)
        st.sidebar.success(f"Transaction added successfully! Customer ID: {customer_id}")
    
    st.subheader("Transaction History")
    st.dataframe(data if not data.empty else pd.DataFrame(columns=["ID", "Date", "Customer", "Category", "Amount", "Type"]))
    
    total_income = data[data["Type"] == "Income"]["Amount"].sum()
    total_expense = data[data["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense
    
    st.subheader("Summary")
    st.write(f"**Total Income:** ${total_income:.2f}")
    st.write(f"**Total Expense:** ${total_expense:.2f}")
    st.write(f"**Balance:** ${balance:.2f}")
    
    st.subheader("📊 Financial Overview")
    if not data.empty:
        income_expense_data = data.groupby("Type")["Amount"].sum()
        st.bar_chart(income_expense_data)
        
        category_expense_data = data[data["Type"] == "Expense"].groupby("Category")["Amount"].sum()
        if not category_expense_data.empty:
            fig, ax = plt.subplots()
            category_expense_data.plot.pie(ax=ax, autopct='%1.1f%%', startangle=90)
            ax.set_ylabel('')
            st.pyplot(fig)
    
    st.subheader("🗑️ Delete a Transaction")
    delete_id = st.text_input("Enter the Customer ID to Delete")
    if st.button("Delete Transaction"):
        data = data[data["ID"] != delete_id]
        save_data(data)
        st.success("Transaction deleted successfully!")
        st.rerun()

if not st.session_state["authenticated"]:
    option = st.sidebar.radio("Select an Option", ["Login", "Sign Up"])
    if option == "Login":
        login_page()
    else:
        signup_page()
else:
    budget_dashboard()
