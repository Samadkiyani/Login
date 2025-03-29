import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns # type: ignore
import streamlit as st
import os
import uuid


st.image("https://media.istockphoto.com/id/1488294044/photo/businessman-works-on-laptop-showing-business-analytics-dashboard-with-charts-metrics-and-kpi.jpg?s=612x612&w=0&k=20&c=AcxzQAe1LY4lGp0C6EQ6reI7ZkFC2ftS09yw_3BVkpk=", use_column_width=True)

data_file = "budget_data.csv"

def load_data():
    if os.path.exists(data_file) and os.stat(data_file).st_size > 0:
        return pd.read_csv(data_file)
    else:
        return pd.DataFrame(columns=["ID", "Date", "Customer", "Category", "Amount", "Type"])

def save_data(df):
    df.to_csv(data_file, index=False)

data = load_data()

st.title("💰 Welcome to Samad Kiani Budget Dashboard")

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
        customer_id = str(uuid.uuid4())[:8]  # Generate a unique ID for new customers
    
    new_data = pd.DataFrame([[customer_id, date, customer, category, amount, transaction_type]], columns=["ID", "Date", "Customer", "Category", "Amount", "Type"])
    data = pd.concat([data, new_data], ignore_index=True)
    save_data(data)
    st.sidebar.success(f"Transaction added successfully! Customer ID: {customer_id}")

st.sidebar.header("Delete Customer Transactions")
delete_input = st.sidebar.text_input("Enter Customer ID or Name to Delete")
if st.sidebar.button("Delete Customer Transactions"):
    data = data[(data["ID"] != delete_input) & (data["Customer"] != delete_input)]
    save_data(data)
    st.sidebar.success(f"All transactions for Customer {delete_input} deleted successfully!")

st.sidebar.header("Check Customer Data")
check_customer_id = st.sidebar.text_input("Enter Customer ID to Check Transactions")
if st.sidebar.button("Check Transactions"):
    customer_data = data[data["ID"] == check_customer_id]
    if not customer_data.empty:
        st.subheader(f"Transactions for Customer ID: {check_customer_id}")
        st.dataframe(customer_data)
    else:
        st.sidebar.warning("No transactions found for this Customer ID.")

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

st.subheader("Budget Utilization")
customer_budget = data.groupby("Customer")["Amount"].sum().reset_index()
if not customer_budget.empty:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(data=customer_budget, x="Customer", y="Amount", palette="muted", ax=ax)
    ax.set_ylabel("Total Expense ($)")
    ax.set_title("Budget Utilization by Customer")
    plt.xticks(rotation=45)
    st.pyplot(fig)

st.subheader("Income vs. Expense Trend")
data["Date"] = pd.to_datetime(data["Date"], errors='coerce')
data = data.dropna(subset=["Date"])
data["Month"] = data["Date"].dt.strftime('%Y-%m')
customer_groups = data.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)

if not customer_groups.empty:
    fig, ax = plt.subplots(figsize=(10, 5))
    customer_groups.plot(kind='bar', stacked=True, ax=ax, color=["#1f77b4", "#ff7f0e"])
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount ($)")
    ax.set_title("Income vs. Expense Trend")
    st.pyplot(fig)

st.sidebar.subheader("Download Data")
st.sidebar.download_button(
    label="Download CSV",
    data=data.to_csv(index=False),
    file_name="budget_data.csv",
    mime="text/csv"
)
