import streamlit as st
import google.generativeai as genai
import random

# --- 1. КОНФИГУРАЦИЯ И СТИЛИ ---
st.set_page_config(page_title="Exam Simulator PRO", page_icon="📝", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main .block-container { padding-top: 2rem; max-width: 850px; }
    h1, h2, h3, p, li { color: #000000 !important; font-family: 'Times New Roman', serif; }
    .stTextArea textarea { 
        background-color: #ffffff !important; 
        border: 1px solid #000000 !important; 
        font-size: 16px; 
    }
    .exam-header { border-bottom: 2px solid #000; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ПОДКЛЮЧЕНИЕ КЛЮЧА ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-flash-latest')
except:
    st.error("Check your Streamlit Secrets for GEMINI_API_KEY")
    st.stop()

# --- 3. ЛОГИКА ТЕМ (РАНДОМАЙЗЕР) ---
def load_topics():
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            return lines if lines else ["Standard Exam Topic"]
    except:
        return ["Education in the 21st Century"]

all_topics = load_topics()

# Используем st.session_state, чтобы тема не "прыгала" при вводе текста
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = random.choice(all_topics)

# --- 4. ИНТЕРФЕЙС ---
st.markdown("<div class='exam-header'><h1>Task 2</h1><h2>Essay (16 points)</h2></div>", unsafe_allow_html=True)

# Кнопка для выбора новой случайной темы
if st.button("GET NEW TOPIC 🎲"):
    st.session_state.current_topic = random.choice(all_topics)
    st.rerun()

st.subheader(f"Topic: {st.session_state.current_topic}")

st.markdown("""
**Instructions:**
Write an essay in which you formulate the problem, propose two solutions, and conclude.
**Target: 250–300 words.**
""")

user_text = st.text_area("Your Response:", height=400, placeholder="Start writing here...")

word_count = len(user_text.split())
st.write(f"**Word count: {word_count}**")

# --- 5. ПРОВЕРКА ---
if st.button("SUBMIT FOR EVALUATION"):
    if word_count < 100:
        st.error("Text is too short (min 100 words).")
    elif user_text:
        with st.spinner('Examiner is evaluating...'):
            try:
                # Тот самый строгий промпт с жирным выделением ошибок
                prompt = f"""
                Ты — строгий экзаменатор VISC. Оцени эссе на тему: "{st.session_state.current_topic}".
                
                1. Сначала выведи текст ученика. Ошибки выдели жирным и в скобках напиши исправление, например: "He **go (goes)** to school".
                2. Раздел "Corrections": кратко объясни ошибки.
                3. Раздел "Scores" (0-5 за каждый):
                   - Sagatavotā runa: /5
                   - Mijiedarbība: /5
                   - Valodas bagātība: /5
                   - Valodas lietojuma pareizība: /5
                   - Valodas plūdums: /5
                ИТОГ: Сумма/25.
                
                Текст: {user_text}
                Отвечай на русском.
                """
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error: {e}")        transition: 0.3s;
    }

    /* Эффект при наведении на кнопку */
    div.stButton > button:hover {
        background-color: #333333 !important;
        border-color: #333333 !important;
        color: #ffffff !important;
    }

    .exam-header { border-bottom: 2px solid #000; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ПОДКЛЮЧЕНИЕ КЛЮЧА ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-flash-latest')
except:
    st.error("Check your Streamlit Secrets for GEMINI_API_KEY")
    st.stop()

# --- 3. ЛОГИКА ТЕМ (РАНДОМАЙЗЕР) ---
def load_topics():
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            return lines if lines else ["Standard Exam Topic"]
    except:
        return ["Education in the 21st Century"]

all_topics = load_topics()

# Используем st.session_state, чтобы тема не "прыгала" при вводе текста
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = random.choice(all_topics)

# --- 4. ИНТЕРФЕЙС ---
st.markdown("<div class='exam-header'><h1>Task 2</h1><h2>Essay (16 points)</h2></div>", unsafe_allow_html=True)

# Кнопка для выбора новой случайной темы
if st.button("GET NEW TOPIC 🎲"):
    st.session_state.current_topic = random.choice(all_topics)
    st.rerun()

st.subheader(f"Topic: {st.session_state.current_topic}")

st.markdown("""
**Instructions:**
Write an essay in which you formulate the problem, propose two solutions, and conclude.
**Target: 250–300 words.**
""")

user_text = st.text_area("Your Response:", height=400, placeholder="Start writing here...")

word_count = len(user_text.split())
st.write(f"**Word count: {word_count}**")

# --- 5. ПРОВЕРКА ---
if st.button("SUBMIT FOR EVALUATION"):
    if word_count < 100:
        st.error("Text is too short (min 100 words).")
    elif user_text:
        with st.spinner('Examiner is evaluating...'):
            try:
                # Тот самый строгий промпт с жирным выделением ошибок
                prompt = f"""
                Ты — строгий экзаменатор VISC. Оцени эссе на тему: "{st.session_state.current_topic}".
                
                1. Сначала выведи текст ученика. Ошибки выдели жирным и в скобках напиши исправление, например: "He **go (goes)** to school".
                2. Раздел "Corrections": кратко объясни ошибки.
                3. Раздел "Scores" (0-5 за каждый):
                   - Sagatavotā runa: /5
                   - Mijiedarbība: /5
                   - Valodas bagātība: /5
                   - Valodas lietojuma pareizība: /5
                   - Valodas plūdums: /5
                ИТОГ: Сумма/25.
                
                Текст: {user_text}
                Отвечай на русском.
                """
                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
