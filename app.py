import streamlit as st
import google.generativeai as genai
import random

# --- 1. CONFIG & STYLES ---
st.set_page_config(page_title="Exam Simulator PRO", page_icon="📝", layout="centered")

# CSS стили запакованы строго в многострочную строку
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main .block-container { padding-top: 2rem; max-width: 850px; }
    
    h1, h2, h3, p, li, span, label, div { 
        color: #000000 !important; 
        font-family: 'Times New Roman', serif; 
    }

    .stTextArea textarea { 
        background-color: #ffffff !important; 
        border: 1px solid #000000 !important; 
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-size: 16px !important;
        font-family: 'Arial', sans-serif !important;
    }

    div.stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #000000;
        border-radius: 4px;
        font-weight: bold;
        width: 100%;
        height: 3em;
    }

    div.stButton > button:hover {
        background-color: #444444 !important;
        color: #ffffff !important;
    }

    [data-baseweb="select"] * { color: #000000 !important; }

    .exam-header { 
        border-bottom: 2px solid #000000; 
        margin-bottom: 20px; 
    }
</style>
""", unsafe_allow_html=True)

# --- 2. API KEY SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-flash-latest')
except Exception as e:
    st.error("API Key not found in Secrets!")
    st.stop()

# --- 3. TOPICS LOGIC ---
def load_topics():
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            return lines if lines else ["Standard Exam Topic"]
    except:
        return ["Education in the 21st Century"]

all_topics = load_topics()

if 'current_topic' not in st.session_state:
    st.session_state.current_topic = random.choice(all_topics)

# --- 4. INTERFACE ---
st.markdown("<div class='exam-header'><h1>Task 2</h1><h2>Essay (16 points)</h2></div>", unsafe_allow_html=True)

if st.button("GET NEW TOPIC 🎲"):
    st.session_state.current_topic = random.choice(all_topics)
    st.rerun()

st.subheader(f"Topic: {st.session_state.current_topic}")
st.write("Write an essay in which you formulate the problem, propose two solutions, and conclude.")
st.write("**Target: 250-300 words.**")

user_text = st.text_area("Your Response:", height=400, placeholder="Start writing here...")

word_count = len(user_text.split())
st.write(f"Word count: {word_count}")

# --- 5. EVALUATION ---
if st.button("SUBMIT FOR EVALUATION"):
    if word_count < 100:
        st.error("Text is too short (min 100 words).")
    elif user_text:
        with st.spinner('Examiner is evaluating...'):
            try:
                prompt = f"""
                Ты строгий экзаменатор. Проверь эссе на тему '{st.session_state.current_topic}'.
                1. Сначала выведи текст ученика, выделяя ошибки жирным и в скобках давая исправленный вариант.
                2. Ниже напиши краткий разбор ошибок.
                3. В конце поставь баллы (0-5) по критериям VISC:
                - Sagatavota runa
                - Mijiedarbiba
                - Valodas bagatiba
                - Gramatika
                - Pludums
                Отвечай на русском.
                Текст: {user_text}
                """
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error during evaluation: {str(e)}")
