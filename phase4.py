import streamlit as st
from openai import OpenAI
import dotenv
import os
import requests

# Load environment variables from .env
dotenv.load_dotenv()

# Retrieve API keys
api_key = os.getenv("OPENAI_API_KEY")
slack_webhook = os.getenv("SLACK_WEBHOOK_URL")

# Optional: check API key
if not api_key:
    st.error("API key not found. Please set OPENAI_API_KEY in your .env file.")

# OpenAI endpoint and model
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o"

# Initialize OpenAI client
client = OpenAI(
    api_key=api_key,
    base_url=endpoint,
)

# Define categories and their colors
CATEGORY_COLORS = {
    "billing inquiries": "#FFB6C1",
    "technical support": "#87CEEB",
    "order tracking": "#90EE90",
    "product information": "#FFD700",
    "general questions": "#D3D3D3",
}
st.set_page_config(page_title="SS ChatBot", layout="centered")
col1, col2 = st.columns([1, 8])
with col1:
    st.image("logo.png", use_container_width=True)  # Replace "logo.png" with the path to your logo file
with col2:
    # App title and input
    st.title(":red[Smart Support ChatBot] ")
# Set page config and background


st.html("""
<style>
[data-testid="stSidebarContent"] {
    color: black;
    background-color: #F7AD45;
}
</style>
""")

# Sidebar setup
st.sidebar.title("🧭 Instructions")

st.sidebar.markdown("""
<div style='
    background-color: #FAD59A;
    padding: 15px;
    border-radius: 5px;
    border: 1px solid #FAD59A;
    color: black;
    font-size: 14px;
'>
    This app classifies customer support messages into one of the following categories:<br><br>
    - 📄 Billing Inquiries<br>
    - 🛠️ Technical Support<br>
    - 📦 Order Tracking<br>
    - 🛍️ Product Information<br>
    - ❓ General Questions
    <hr>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("💡**How to use:**")
st.sidebar.markdown("""
<div style='
    background-color: #FAD59A;
    padding: 14px;
    border-radius: 5px;
    border: 1px solid #AFAD59A;
    color: black;
    font-size: 14px;
'>
    <ol>
        <li>Type a message in the text box. <em>(Supports multiple languages! 🌍 French, Spanish, German, etc.)</em></li>
        <li>The app will translate (if needed), classify, and style the result.</li>
        <li>A summary will also be sent to Slack.</li>
    </ol>
    <hr>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("📞 Contact Info")

st.sidebar.markdown("""
<div style='
    background-color: #FAD59A;
    padding: 15px;
    border-radius: 5px;
    border: 1px solid #FAD59A;
    color: black;
    font-size: 14px;
'>
    <strong>Francis Chizey</strong><br>
    Data Scientist & Software Engineer<br><br>
    <span title="chizeyfrancis@gmail.com" style="cursor: help;">Email</span><br>
    <span title="+2348135874318" style="cursor: help;">Phone</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("❓ Help")

st.sidebar.markdown("""
<div style='
    background-color: #FAD59A;
    padding: 15px;
    border-radius: 5px;
    border: 1px solid #FAD59A;
    color: black;
    font-size: 14px;
'>
    For any issues, please refer to the documentation or contact support.<br>
    <a href="https://platform.openai.com/docs" target="_blank" style="color: black;">OpenAI Docs</a>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("🔗 Links")

st.sidebar.markdown("""
<div style='
    background-color: #FAD59A;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #FAD59A;
    color: black;
    font-size: 14px;
'>
    <a href="https://github.com/1Chizey/GoMyCode-Project-#" title="View my GitHub Repo" target="_blank" style="color: black;">GitHub</a><br>
    <a href="https://www.linkedin.com/in/francis-chizey-8838a5256" title="Visit my LinkedIn profile" target="_blank" style="color: black;">LinkedIn</a>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("### ⚙️ Settings")



user_input = st.text_area("Kindly Type in Your Message in any Language:")


#footer

st.markdown("© 2025 Chizey_GoMyCode.Nigeria. All rights reserved.")


# Translate to English
def translate_to_english(message):
    prompt = (
        "Detect the language of the message and translate it to English. "
        "Return only the translated text. If it's already in English, return it unchanged.\n\n"
        f"Message: {message}"
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

# Classify message
def classify_intent(message):
    system_prompt = (
        "You are an assistant that classifies customer queries into one of the following categories:\n"
        "- billing inquiries\n"
        "- technical support\n"
        "- order tracking\n"
        "- product information\n"
        "- general questions\n\n"
        "Return only the category name in the way they are typed."
    )

    response = client.chat.completions.create(
        model=model_name,
        max_tokens=500,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
    )

    return response.choices[0].message.content.strip().lower()

# Send to Slack
def send_to_slack(original_msg, translated_msg, category):
    if not slack_webhook:
        st.warning("Slack webhook URL not configured.")
        return

    payload = {
        "text": (
            f"*New Customer Query Classified!*\n"
            f"> *Category:* `{category}`\n"
            f"> *Original Message:* {original_msg}\n"
            f"> *Translated:* {translated_msg if original_msg != translated_msg else 'N/A'}"
        )
    }

    response = requests.post(slack_webhook, json=payload)
    if response.status_code != 200:
        st.error("Failed to send to Slack.")
    else:
        st.success("Message sent to Slack successfully!")

# Main logic
if user_input:
    translated_input = translate_to_english(user_input)
    category = classify_intent(translated_input)
    color = CATEGORY_COLORS.get(category, "#FFFFFF")

    if user_input.lower() != translated_input.lower():
        st.markdown(f"**Translated Message:** _{translated_input}_")

    st.markdown(f"""
        <div style='
            background-color:{color};
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            font-size: 1.5rem;
            font-weight: bold;
        '>
            Prediction: {category.title()}
        </div>
    """, unsafe_allow_html=True)

    send_to_slack(user_input, translated_input, category)
