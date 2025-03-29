import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # type: ignore
import streamlit as st
import os
import uuid

# File paths for authentication and budget data
users_file = "users.csv"
data_file = "budget_data.csv"

# Function to load users
def load_users():
    if os.path.exists(users_file):
        return pd.read_csv(users_file)
    else:
        return pd.DataFrame(columns=["Username", "Password"])

# Function to save users
def save_users(df):
    df.to_csv(users_file, index=False)

# Load or create users data
users = load_users()

# Streamlit session state for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""

def login_page():
    st.title("🔑 Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if (users["Username"] == username).any() and (users["Password"] == password).any():
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success("Login successful! Redirecting...")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

def signup_page():
    st.title("📝 Sign Up for an Account")
    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")
    
    if st.button("Sign Up"):
        if new_username in users["Username"].values:
            st.error("Username already exists. Choose another.")
        else:
            new_user = pd.DataFrame([[new_username, new_password]], columns=["Username", "Password"])
            updated_users = pd.concat([users, new_user], ignore_index=True)
            save_users(updated_users)
            st.success("Account created successfully! Please login.")
            st.experimental_rerun()

def budget_dashboard():
    st.title("💰 Welcome to Samad Kiani Budget Dashboard")
    
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.experimental_rerun()
    
    # Load budget data
    def load_data():
        if os.path.exists(data_file) and os.stat(data_file).st_size > 0:
            return pd.read_csv(data_file)
        else:
            return pd.DataFrame(columns=["ID", "Date", "Customer", "Category", "Amount", "Type"])
    
    def save_data(df):
        df.to_csv(data_file, index=False)
    
    data = load_data()
    
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
        
        new_data = pd.DataFrame([[customer_id, date, customer, category, amount, transaction_type]],
                                columns=["ID", "Date", "Customer", "Category", "Amount", "Type"])
        data = pd.concat([data, new_data], ignore_index=True)
        save_data(data)
        st.sidebar.success("Transaction added successfully!")
    
    st.subheader("Transaction History")
    st.dataframe(data)
    
    total_income = data[data["Type"] == "Income"]["Amount"].sum()
    total_expense = data[data["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense
    
    st.subheader("Summary")
    st.write(f"**Total Income:** ${total_income:.2f}")
    st.write(f"**Total Expense:** ${total_expense:.2f}")
    st.write(f"**Balance:** ${balance:.2f}")
    
    st.subheader("Expense Breakdown by Category")
    expense_data = data[data["Type"] == "Expense"].groupby("Category")["Amount"].sum().reset_index()
    if not expense_data.empty:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=expense_data, x="Category", y="Amount", palette="pastel", ax=ax)
        ax.set_ylabel("Amount ($)")
        ax.set_title("Expense Breakdown by Category")
        plt.xticks(rotation=45)
        st.pyplot(fig)

# Main App Logic
if not st.session_state["authenticated"]:
    option = st.sidebar.radio("Select an Option", ["Login", "Sign Up"])
    if option == "Login":
        login_page()
    else:
        signup_page()
else:
    budget_dashboard()
