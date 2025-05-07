import streamlit as st
from streamlit_lottie import st_lottie
import json
import os


st.set_page_config(page_title="Calorie Advisor - Welcome", layout="centered")


def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


lottie_animation = load_lottie_file("food_animation.json")


st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Playwrite+DK+Loopet&display=swap');
    body {
        background-image: url('https://img.freepik.com/free-photo/close-up-healthy-food-table-vegetarian-food-has-avocado-lettuce-tomato-healthy-eating-concept_1150-19171.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Orbitron', sans-serif;
    }
    .title {
        font-family: 'Playwrite DK Loopet', sans-serif;
        font-size: 2.4em;
        color: #ff7f00;
        text-align: center;
        margin-top: 30px;
        animation: slidein 1s ease-in-out;
        text-shadow: 3px 3px 5px #000000, 5px 5px 12px #00ffcc;
    }
    .message-box {
        background: rgba(0, 0, 0, 0.6);
        border: 2px solid #00ff99;
        border-radius: 15px;
        padding: 25px;
        margin: 40px auto;
        width: 80%;
        max-width: 700px;
        text-align: center;
        font-size: 1.2em;
        color: #ffffff;
        box-shadow: 0 0 15px #00ff99;
    }
    .stButton>button {
        background-color: #f77f00;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #d62828;
    }
    @keyframes slidein {
        from { transform: translateY(-100px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    </style>
""", unsafe_allow_html=True)


st.markdown('<div class="title">Welcome to Calorie Advisor</div>', unsafe_allow_html=True)


st_lottie(lottie_animation, speed=2, width=700, height=150, key="welcome_animation")


st.markdown("""<div class="message-box">
    📸 <strong>Upload your meal</strong> and let our AI instantly reveal your <strong>calories, nutrition</strong>, and <strong>health tips</strong>.<br><br>
    🌱 Our personalized suggestions help you <strong>stay fit</strong>, <strong>eat smart</strong>, and <strong>download your diet report</strong> with ease.<br><br>
    🚀 <em>Your healthy journey starts here!</em>
</div>""", unsafe_allow_html=True)


if st.button("Continue to Login"):
    st.switch_page("pages/login.py")



st.markdown("""<div class="footer">
    <p>Developed by Team AI Maverick</p>
    <lottie-player src="https://assets7.lottiefiles.com/packages/lf20_tuujp4.json" background="transparent"
     speed="1" style="width: 50px; height: 50px;" loop autoplay></lottie-player>
</div>""", unsafe_allow_html=True)
