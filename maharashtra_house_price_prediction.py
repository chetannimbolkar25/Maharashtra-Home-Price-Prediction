# ================= IMPORTS ================= #
import streamlit as st
import pickle
import json
import numpy as np
import random
import time
import hashlib
import os
from datetime import datetime

# ================= PAGE CONFIG ================= #
st.set_page_config(
    page_title="Smart House Price Predictor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= STYLING ================= #
st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 5rem;
}

/* Header */
.header {
    background: linear-gradient(90deg,#2563eb,#06b6d4);
    padding: 16px;
    border-radius: 10px;
    color: white;
    text-align: center;
    font-size: 26px;
    font-weight: 600;
    margin-bottom: 20px;
}

/* Cards */
.main-card {
    background-color: #1c1f26;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.35);
}

.metric-card {
    background: #1c1f26;
    padding: 18px;
    border-radius: 12px;
    text-align: center;
    border: 1px solid #2a2d34;
}

/* Section title */
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 15px;
}

/* Buttons */
.stButton>button {
    width: 100%;
    height: 44px;
    border-radius: 8px;
    font-weight: 600;
}

/* Footer */
.footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: #111827;
    color: #9ca3af;
    text-align: center;
    padding: 10px;
    font-size: 14px;
    border-top: 1px solid #2a2d34;
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER ================= #
st.markdown(
    '<div class="header">🏠 Maharashtra House Price Prediction System</div>',
    unsafe_allow_html=True
)

# ================= MODEL ================= #
__data_columns = None
__locality_name = None
__model = None

def load_saved_artifacts():
    global __data_columns, __locality_name, __model

    with open("column.json", "r") as f:
        __data_columns = json.load(f)["data_columns"]
        __locality_name = __data_columns[2:]

    if __model is None:
        with open("maharashtra_region_model.pickle", "rb") as f:
            __model = pickle.load(f)

def get_estimated_price(locality, sqft, bhk):
    try:
        loc_index = __data_columns.index(locality.lower())
    except:
        loc_index = -1

    x = np.zeros(len(__data_columns))
    x[0] = sqft
    x[1] = bhk

    if loc_index >= 0:
        x[loc_index] = 1

    return round(__model.predict([x])[0], 2)

# ================= USER STORAGE ================= #
USER_FILE = "users.json"

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ================= SECURITY ================= #
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    otp = random.randint(100000, 999999)
    st.session_state.otp = otp
    st.session_state.otp_time = time.time()
    return otp

# ================= SESSION ================= #
defaults = {
    "logged_in": False,
    "otp": None,
    "otp_time": None,
    "current_user": None,
    "attempts": 0
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ================= SIGNUP ================= #
def signup():
    users = load_users()

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("Create Account")

        username = st.text_input("Username")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Create Account"):
            if username in users:
                st.error("User already exists")
            elif password != confirm:
                st.error("Passwords do not match")
            else:
                users[username] = {
                    "email": email,
                    "phone": phone,
                    "password": hash_password(password),
                    "history": []
                }
                save_users(users)
                st.success("Account created successfully")

        st.markdown('</div>', unsafe_allow_html=True)

# ================= LOGIN ================= #
def login():
    users = load_users()

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("Secure Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Generate OTP"):
            if username in users and users[username]["password"] == hash_password(password):
                otp = generate_otp()
                st.session_state.current_user = username

                st.success(
                    f"OTP sent to Email ({users[username]['email']}) "
                    f"and Phone ({users[username]['phone']})"
                )
                st.info(f"Demo OTP: {otp}")
            else:
                st.error("Invalid credentials")

        otp_input = st.text_input("Enter OTP")

        if st.button("Verify OTP"):
            if otp_input == str(st.session_state.otp):
                st.session_state.logged_in = True
                st.success("Login Successful")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid OTP")

        st.markdown('</div>', unsafe_allow_html=True)

# ================= DASHBOARD ================= #
def dashboard():
    users = load_users()
    history = users[st.session_state.current_user]["history"]

    st.markdown('<div class="section-title">Dashboard Overview</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Predictions", len(history))
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        last = history[-1]["price"] if history else 0
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Last Price", f"₹ {last}")
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Active User", st.session_state.current_user)
        st.markdown('</div>', unsafe_allow_html=True)

# ================= HISTORY ================= #
def history_page():
    users = load_users()
    history = users[st.session_state.current_user]["history"]

    st.subheader("Prediction History")

    if history:
        st.dataframe(history, use_container_width=True)
    else:
        st.info("No predictions yet")

# ================= ADMIN ================= #
def admin_panel():
    users = load_users()

    st.subheader("Admin Panel")

    total_predictions = sum(len(users[u]["history"]) for u in users)

    col1, col2 = st.columns(2)
    col1.metric("Total Users", len(users))
    col2.metric("Total Predictions", total_predictions)

# ================= SAVE ================= #
def save_prediction(user, locality, sqft, bhk, price):
    users = load_users()

    users[user]["history"].append({
        "location": locality,
        "sqft": sqft,
        "bhk": bhk,
        "price": price,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    save_users(users)

# ================= AUTH FLOW ================= #
if not st.session_state.logged_in:
    tab = st.radio("Account", ["Login", "Sign Up"])

    if tab == "Login":
        login()
    else:
        signup()

    st.stop()

# ================= SIDEBAR ================= #
st.sidebar.title("Navigation")
st.sidebar.success(f"Welcome {st.session_state.current_user}")

menu = ["Dashboard", "Predict Price", "History"]

if st.session_state.current_user == "admin":
    menu.append("Admin Panel")

menu.append("Logout")

choice = st.sidebar.radio("", menu)

if choice == "Logout":
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

load_saved_artifacts()

# ================= PAGES ================= #
if choice == "Dashboard":
    dashboard()

elif choice == "Predict Price":
    st.markdown('<div class="section-title">House Price Prediction</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        sqft = st.number_input("Area (sqft)", 300, 5000)
        locality = st.selectbox("Location", __locality_name)

    with col2:
        bhk = st.select_slider("BHK", [1,2,3,4,5])

    if st.button("Predict Price"):
        price = get_estimated_price(locality, sqft, bhk)

        st.markdown(
            f"<div class='main-card'><h2 style='text-align:center;'>₹ {price} Lakhs</h2></div>",
            unsafe_allow_html=True
        )

        save_prediction(st.session_state.current_user, locality, sqft, bhk, price)

elif choice == "History":
    history_page()

elif choice == "Admin Panel":
    admin_panel()

# ================= FOOTER ================= #
st.markdown(
    """
    <div class="footer">
        © 2026 Smart Property Analytics Pvt Ltd | 
        House Price Prediction System v1.0 | 
        support@smartproperty.ai
    </div>
    """,
    unsafe_allow_html=True
)
