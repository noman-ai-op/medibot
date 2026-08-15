import streamlit as st
from groq import Groq
import os

st.set_page_config(
    page_title="MediBot AI",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp {
        background-color: #212121;
        color: #ECECEC;
    }

    #MainMenu, footer, header {visibility: hidden;}

    .app-title {
        text-align: center;
        padding: 18px 0 4px 0;
    }
    .app-title h1 {
        color: #ECECEC;
        font-size: 26px;
        font-weight: 600;
        margin: 0;
    }
    .app-title p {
        color: #9B9B9B;
        font-size: 13px;
        margin: 4px 0 0 0;
    }

    .disclaimer {
        text-align: center;
        color: #7A7A7A;
        font-size: 11.5px;
        margin: 4px auto 20px auto;
        max-width: 560px;
        line-height: 1.4;
    }

    [data-testid="stChatMessage"] {
        background-color: transparent;
        padding: 6px 0;
    }

    [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background-color: #2F2F2F;
        border-radius: 14px;
        padding: 10px 14px;
        margin-left: 15%;
    }

    [data-testid="stChatMessage"] p {
        color: #ECECEC !important;
        font-size: 15px;
        line-height: 1.6;
    }

    section[data-testid="stSidebar"] {
        background-color: #171717;
        border-right: 1px solid #2A2A2A;
    }
    section[data-testid="stSidebar"] * {
        color: #ECECEC !important;
    }
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #4FC3F7 !important;
    }

    .stButton>button {
        background-color: #2F2F2F;
        color: #ECECEC;
        border: 1px solid #3D3D3D;
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stButton>button:hover {
        border-color: #4FC3F7;
        color: #4FC3F7;
    }

    [data-testid="stChatInput"] {
        background-color: #2F2F2F;
        border-radius: 14px;
        border: 1px solid #3D3D3D;
    }
    [data-testid="stChatInput"] textarea {
        color: #ECECEC !important;
    }

    [data-baseweb="select"] {
        background-color: #2F2F2F;
    }
</style>
""", unsafe_allow_html=True)


def load_api_key():
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    key_file = os.path.join(os.path.dirname(__file__), "api-key.txt")
    if os.path.exists(key_file):
        with open(key_file, "r", encoding="utf-8-sig") as f:
            key = f.read().strip()
            if key and key != "PASTE_YOUR_GROQ_API_KEY_HERE":
                return key

    return os.environ.get("GROQ_API_KEY", "")


api_key = load_api_key()

SYSTEM_PROMPT = """You are MediBot AI, a knowledgeable and empathetic virtual health assistant.
You communicate like a caring, professional doctor would during a consultation: warm, clear,
and structured. Your job is to help users understand their symptoms and possible causes,
suggest sensible general care and well-known over-the-counter options, and guide them on next
steps, while always being responsible about safety.

Follow these rules on every response:
1. Ask brief clarifying questions when symptoms are vague (duration, severity, associated symptoms).
2. Explain likely causes in plain language, listing a few possibilities, not just one rigid diagnosis.
3. You may suggest general, well-known over-the-counter remedies and home care (rest, hydration,
   common OTC pain relievers like paracetamol at standard label doses, etc.), but do NOT provide
   exact dosages for prescription-only or controlled medications, instead advise seeing a doctor
   or pharmacist for those.
4. ALWAYS watch for red-flag / emergency symptoms (e.g. chest pain, difficulty breathing, severe
   bleeding, signs of stroke, high fever in infants, suicidal thoughts, severe allergic reaction).
   If any appear, clearly and immediately tell the user to seek emergency care or call emergency
   services right away, before anything else.
5. End every substantive answer with a short, natural reminder that this is general information
   and not a substitute for an in-person examination and diagnosis by a licensed doctor.
6. Keep tone supportive and non-alarming, but never withhold a safety warning to be polite.
7. Do not claim certainty about a diagnosis. Use phrases like "this could suggest..." rather than
   "you have...".
"""

with st.sidebar:
    st.markdown("## Settings")

    model_choice = st.selectbox(
        "Model",
        options=["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.6-27b"],
        index=0,
        help="120b = best quality, 20b = fastest response",
    )

    st.markdown("---")
    if st.button("New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("**About**")
    st.caption(
        "MediBot AI gives general health guidance and always tells you "
        "when to see a real doctor. It does not replace professional medical care."
    )

st.markdown("""
<div class="app-title">
    <h1>MediBot AI</h1>
    <p>Your friendly AI health assistant</p>
</div>
<div class="disclaimer">
    For general information only, not a substitute for professional medical advice.
    In an emergency, contact your local emergency services immediately.
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.error(
        "No Groq API key found. Add your key to api-key.txt (local) or to "
        "Streamlit Cloud -> Settings -> Secrets as GROQ_API_KEY (deployment)."
    )
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🩺"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

user_input = st.chat_input("Describe your symptoms or ask a health question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🩺"):
        placeholder = st.empty()
        full_reply = ""

        try:
            api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
            ]

            stream = client.chat.completions.create(
                model=model_choice,
                messages=api_messages,
                temperature=0.6,
                max_tokens=1024,
                stream=True,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_reply += delta
                placeholder.markdown(full_reply + "▌")

            placeholder.markdown(full_reply)

        except Exception as e:
            full_reply = f"Something went wrong: {e}"
            placeholder.error(full_reply)

    st.session_state.messages.append({"role": "assistant", "content": full_reply})