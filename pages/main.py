from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import google.generativeai as genai
import os
import requests
from PIL import Image
import io
from streamlit_lottie import st_lottie
import cv2
from fpdf import FPDF
import tempfile
import re


st.set_page_config(page_title="Calorie Advisor", page_icon="🥗", layout="wide")

if "user_data" not in st.session_state:
    st.error("⚠ Please login first on the Login tab!")
    st.switch_page("login.py")

if st.button("🔙 Logout and Return to Login"):
    st.session_state.clear()
    st.switch_page("login.py")


st.markdown("""
    <style>
        .big-title { font-size: 28px; font-weight: bold; color: #ff6600; }
        .sub-title { font-size: 24px; font-weight: bold; color: #2a9d8f; }
        .info-box { background-color: #f4f4f4; padding: 10px; border-radius: 10px; color: black; font-weight: bold; }
        .highlight-box { background-color: #ffcc99; padding: 10px; border-radius: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def input_image_setup(uploaded_file):
    image = Image.open(uploaded_file).convert("RGB")
    image = image.resize((64, 64))
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    byte_data = buf.getvalue()
    return {"mime_type": "image/png", "data": byte_data}

def get_gemini_response(prompt, image_part):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([prompt, image_part])
    return response.text

def extract_nutrients(response):
    nutrients = {"Carbs": 0, "Proteins": 0, "Fats": 0, "Fiber": 0, "Sugar": 0}
    total_calories = 0

    for line in response.splitlines():
        for key in nutrients:
            if key.lower() in line.lower():
                match = re.search(r"(\d+\.?\d*)", line)
                if match:
                    try:
                        nutrients[key] = int(float(match.group(1)))
                    except:
                        pass

        if "calorie" in line.lower():
            matches = re.findall(r"(\d+\.?\d*)", line)
            if matches:
                try:
                    cal = int(float(matches[0]))
                    total_calories += cal
                except:
                    pass

    return nutrients, total_calories

def capture_camera_image():
    picture = st.camera_input("Scan Food with Camera")
    return picture

def create_pdf_report(user, total_calories, recommended_calories, chart_path, advice, detailed_report):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, f"User Report\nUsername: {user['username']}\nAge: {user['age']}, Gender: {user['gender']}\nHeight: {user['height']} cm, Weight: {user['weight']} kg\nConditions: {', '.join(user.get('conditions', []))}\n")
    pdf.multi_cell(0, 10, f"Total Calorie Intake: {total_calories} kcal\nRecommended: {recommended_calories} kcal\n")
    pdf.multi_cell(0, 10, f"\nAdvice:\n{advice}\n")
    pdf.multi_cell(0, 10, f"\nDetailed Food Analysis:\n{detailed_report}")

    if os.path.exists(chart_path):
        pdf.image(chart_path, x=10, y=pdf.get_y() + 10, w=100)

    temp_path = tempfile.mktemp(suffix=".pdf")
    pdf.output(temp_path)
    return temp_path


user = st.session_state["user_data"]
conditions = user.get("conditions", [])

if not conditions:
    conditions = ["None"]

detailed_report = ""
with st.sidebar:
    lottie_url = "https://assets7.lottiefiles.com/packages/lf20_p8bfn5to.json"
    lottie_json = load_lottie_url(lottie_url)
    if lottie_json:
        st_lottie(lottie_json, height=200, key="nutrition")

    st.markdown('<div class="big-title">👤 User Information</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-box">Username: {user.get("username", "N/A")}<br>'
                f'Age: {user.get("age", "N/A")}<br>'
                f'Gender: {user.get("gender", "N/A")}<br>'
                f'Height: {user.get("height", "N/A")} cm<br>'
                f'Weight: {user.get("weight", "N/A")} kg<br>'
                f'Conditions: {", ".join(conditions)}</div>', unsafe_allow_html=True)
    st.markdown("---")

st.markdown('<div class="big-title">🍱 Calorie Advisor - AI Meal Analyzer</div>', unsafe_allow_html=True)

meal_sections = ["Breakfast", "Lunch", "Evening Snacks", "Dinner"]
nutrient_totals = {"Carbs": 0, "Proteins": 0, "Fats": 0, "Fiber": 0, "Sugar": 0}
calorie_total = 0


condition_prompts = {
    "sugar": """
You are a certified nutritionist. The user is a sugar patient and must consume no more than 500 kcal per meal. Analyze this food image and return:
1. List of visible food items with calorie estimate.
2. Whether the food is safe for a sugar patient.
3. Approximate percentage of Carbs, Proteins, Fats, Fiber, Sugar.
4. Suggestions for improvement if unsafe.
""",
    "diabetes": """
You are a certified nutritionist. The user has diabetes and must avoid high-glycemic foods and excessive carbs. Analyze this food image and return:
1. List of visible food items with calorie and carb estimates.
2. Whether this meal is diabetic-friendly.
3. Approximate percentage of Carbs, Proteins, Fats, Fiber, Sugar.
4. Suggestions to reduce glycemic impact.
""",
    "bp": """
You are a certified nutritionist. The user has high blood pressure and should limit salt and saturated fats. Analyze this food image and return:
1. Visible food items with calorie and fat estimate.
2. Is this meal suitable for someone with high BP?
3. Approximate percentage of Carbs, Proteins, Fats, Fiber, Sugar.
4. Suggestions to reduce sodium and fat content.
""",
    "obesity": """
You are a certified nutritionist. The user is managing obesity and should eat nutrient-dense, low-calorie meals. Analyze this food image and return:
1. Visible food items with calorie and portion estimate.
2. Whether this meal supports healthy weight loss.
3. Approximate percentage of Carbs, Proteins, Fats, Fiber, Sugar.
4. Suggestions for healthier alternatives.
""",
    "cardiac arrest": """
You are a certified nutritionist. The user has a history of cardiac issues and must avoid cholesterol-heavy, fried, or fatty foods. Analyze this food image and return:
1. Visible food items with fat and cholesterol estimate.
2. Whether the meal is heart-healthy.
3. Approximate percentage of Carbs, Proteins, Fats, Fiber, Sugar.
4. Suggestions for a more heart-friendly version.
"""
}

base_prompt = """
You are a certified nutritionist. Analyze this food image and return:
1. List of visible food items with calorie estimate.
2. Whether the food is healthy or not.
3. Approximate percentage of Carbs, Proteins, Fats, Fiber, Sugar.
"""

selected_prompt = base_prompt
for cond in conditions:
    if cond.lower() in condition_prompts:
        selected_prompt = condition_prompts[cond.lower()]
        break

for meal in meal_sections:
    st.markdown(f'<div class="sub-title">📷 Upload or Scan your {meal}</div>', unsafe_allow_html=True)
    option = st.radio(f"Choose input method for {meal}", ["Upload Image", "Scan with Camera"], key=f"method_{meal}")

    image_part = None
    if option == "Upload Image":
        uploaded = st.file_uploader(f"Upload {meal} Image", type=["jpg", "jpeg", "png"], key=meal)
        if uploaded:
            st.image(uploaded, caption=meal, width=100)
            image_part = input_image_setup(uploaded)
    else:
        picture = capture_camera_image()
        if picture:
            image_part = input_image_setup(picture)

    if image_part:
        report = get_gemini_response(selected_prompt, image_part)
        st.text_area(f"{meal} Analysis", report, height=200)
        detailed_report += f"\n---\n{meal} Report:\n{report}\n"
        nutrients, meal_calories = extract_nutrients(report)
        for key in nutrient_totals:
            nutrient_totals[key] += nutrients.get(key, 0)
        calorie_total += meal_calories


if calorie_total > 0:
    st.markdown('<div class="big-title">📊 Summary and Insights</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="highlight-box">🔥 Total Calorie Intake: {calorie_total} kcal</div>', unsafe_allow_html=True)

    age = int(user.get("age", 0))
    gender = user.get("gender", "").lower()

    recommended_calories = 2400 if gender == "male" else 2000
    if 31 <= age <= 50:
        recommended_calories -= 200
    elif age > 50:
        recommended_calories -= 400

    modifiers = {
        "bp": -200,
        "sugar": -300,
        "obesity": -400,
        "diabetes": -350,
        "cardiac arrest": -300
    }

    for cond in conditions:
        if cond.lower() in modifiers:
            recommended_calories += modifiers[cond.lower()]

    recommended_calories = max(1000, recommended_calories)

    st.markdown(f'<div class="highlight-box">🎯 Recommended Calorie Budget: {recommended_calories} kcal</div>', unsafe_allow_html=True)

    advice = ""
    if calorie_total < recommended_calories:
        advice = "You're under your target. Consider adding nutritious calories like lean proteins or healthy fats."
    elif calorie_total > recommended_calories:
        advice = "⚠ You've exceeded your recommended intake. Consider lighter meals and more physical activity."
    else:
        advice = "✅ Great job! Your intake is perfectly aligned."

    if "sugar" in [c.lower() for c in conditions] and nutrient_totals["Sugar"] > 30:
        advice += "\n🛑 High sugar detected. Reduce sweets or processed carbs."

    if "bp" in [c.lower() for c in conditions] and nutrient_totals["Fats"] > 40:
        advice += "\n⚠ High fat not ideal for BP. Focus on fiber-rich foods."

    if "diabetes" in [c.lower() for c in conditions] and nutrient_totals["Carbs"] > 100:
        advice += "\n⚠ High carb intake. Try low-GI foods like leafy greens."

    st.markdown(f'<div class="highlight-box">{advice}</div>', unsafe_allow_html=True)

    chart_path = "daily_calorie_chart.png"
    if os.path.exists(chart_path):
        st.image(chart_path, caption="Daily Calorie Needs", width=500)

    pdf_path = create_pdf_report(user, calorie_total, recommended_calories, chart_path, advice, detailed_report)
    with open(pdf_path, "rb") as f:
        st.download_button("🗕 Download Full Report (PDF)", f, file_name="calorie_summary.pdf", mime="application/pdf")