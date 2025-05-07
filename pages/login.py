import streamlit as st
import time
import json
import os

st.set_page_config(page_title="Calorie Advisor", layout="centered")

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user(username, data):
    users = load_users()
    users[username] = data
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Load user data from file
users = load_users()

# Already logged in check
if "user_data" in st.session_state:
    st.success("Already logged in!")
    st.switch_page("pages/main.py")

# Login / Registration form
st.markdown('<div class="typewriter"><h1>🥗 Insight in Every Bite...!</h1></div>', unsafe_allow_html=True)
st.subheader("Please enter your details:")

with st.form("login_form"):
    username = st.text_input("Username").lower().strip()
    age = st.number_input("Age", min_value=1, max_value=120)
    gender = st.selectbox("Gender", ["Male", "Female"])
    height = st.number_input("Height (cm)", min_value=30, max_value=250)
    weight = st.number_input("Weight (kg)", min_value=10, max_value=200)

    health_issues = st.multiselect(
        "Are you suffering from any of the following health issues?",
        options=["BP", "Sugar", "Obesity", "Colestrol", "None"]
    )

    submitted = st.form_submit_button("Continue")

    if submitted:
        if "None" in health_issues and len(health_issues) > 1:
            health_issues.remove("None")

        user_data = {
            "username": username,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "conditions": health_issues
        }

        # Save to file
        save_user(username, user_data)

        # Set in session
        st.session_state["user_data"] = user_data

        st.success("Login successful! Redirecting...")
        time.sleep(1)
        st.switch_page("pages/main.py")
