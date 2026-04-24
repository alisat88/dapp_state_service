import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="CyberFlow Payments", layout="wide")

# =====================================================
# SESSION STATE INIT
# =====================================================

if "accounts" not in st.session_state:
    st.session_state.accounts = {
        "Treasury": 0
    }

if "transactions" not in st.session_state:
    st.session_state.transactions = []

if "total_volume" not in st.session_state:
    st.session_state.total_volume = 0

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def create_account(name):
    if name in st.session_state.accounts:
        return False
    st.session_state.accounts[name] = 0
    return True


def mint_tokens(amount):
    st.session_state.accounts["Treasury"] += amount


def send_payment(sender, receiver, amount):
    if sender not in st.session_state.accounts or receiver not in st.session_state.accounts:
        return "Account not found"

    if st.session_state.accounts[sender] < amount:
        return "Insufficient funds"

    # Execute transaction
    st.session_state.accounts[sender] -= amount
    st.session_state.accounts[receiver] += amount

    # Log transaction
    tx = {
        "timestamp": datetime.now(),
        "sender": sender,
        "receiver": receiver,
        "amount": amount
    }

    st.session_state.transactions.append(tx)
    st.session_state.total_volume += amount

    return "Success"

# =====================================================
# HEADER
# =====================================================

st.title("💳 CyberFlow Payment System")
st.caption("Demo: Treasury • Accounts • Transactions • Monitoring")

# =====================================================
# TABS
# =====================================================

tab1, tab2 = st.tabs(["📊 Dashboard", "⚙️ Actions"])

# =====================================================
# DASHBOARD TAB
# =====================================================

with tab1:
    st.subheader("📊 System Metrics")

    col1, col2, col3 = st.columns(3)

    total_accounts = len(st.session_state.accounts)
    total_transactions = len(st.session_state.transactions)
    total_volume = st.session_state.total_volume

    velocity = total_transactions  # simple version for now

    col1.metric("Total Accounts", total_accounts)
    col2.metric("Transactions", total_transactions)
    col3.metric("Total Volume", f"${total_volume:,.2f}")

    st.markdown("---")

    st.subheader("🏦 Account Balances")

    accounts_df = pd.DataFrame(
        list(st.session_state.accounts.items()),
        columns=["Account", "Balance"]
    )

    st.dataframe(accounts_df, use_container_width=True)

    st.markdown("---")

    st.subheader("📜 Transaction History")

    if st.session_state.transactions:
        tx_df = pd.DataFrame(st.session_state.transactions)
        st.dataframe(tx_df, use_container_width=True)
    else:
        st.info("No transactions yet.")

# =====================================================
# ACTIONS TAB
# =====================================================

with tab2:
    st.subheader("⚙️ System Actions")

    col1, col2, col3 = st.columns(3)

    # -------------------------------
    # CREATE ACCOUNT
    # -------------------------------
    with col1:
        st.markdown("### 👤 Create Account")
        new_account = st.text_input("Account Name")

        if st.button("Create Account"):
            if new_account:
                success = create_account(new_account)
                if success:
                    st.success(f"Account '{new_account}' created!")
                else:
                    st.warning("Account already exists.")
            else:
                st.error("Please enter a name.")

    # -------------------------------
    # TREASURY (MINT TOKENS)
    # -------------------------------
    with col2:
        st.markdown("### 🏦 Treasury Minting")
        mint_amount = st.number_input("Amount", min_value=0.0, step=100.0)

        if st.button("Mint Tokens"):
            mint_tokens(mint_amount)
            st.success(f"${mint_amount:,.2f} added to Treasury")

    # -------------------------------
    # SEND PAYMENT
    # -------------------------------
    with col3:
        st.markdown("### 💸 Send Payment")

        accounts_list = list(st.session_state.accounts.keys())

        sender = st.selectbox("Sender", accounts_list)
        receiver = st.selectbox("Receiver", accounts_list)
        amount = st.number_input("Payment Amount", min_value=0.0, step=50.0)

        if st.button("Send Payment"):
            result = send_payment(sender, receiver, amount)

            if result == "Success":
                st.success("Payment completed!")
            else:
                st.error(result)

# =====================================================
# FOOTER (OPTIONAL FUTURE CYBERFLOW INTEGRATION)
# =====================================================

st.markdown("---")
st.caption("Future: AI Monitoring • Fraud Detection • Workflow Automation")