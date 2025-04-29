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

# Set page config and background
st.set_page_config(page_title="Intent Classifier", layout="centered")



# App title and input
st.title("🌐 Multilingual Intent Classifier")
st.sidebar.title("Instructions")
st.sidebar.write("Enter any customer message — in any language!")

user_input = st.text_area("Enter your message:")

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
