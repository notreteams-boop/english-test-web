import streamlit as st
import google.generativeai as genai
import random
import re

# --- 1. CONFIG & STYLES ---
st.set_page_config(page_title="Exam Simulator PRO", page_icon="📝", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, li, span, label, div { 
        color: #000000 !important; 
        font-family: 'Times New Roman', serif; 
    }

    /* Окошко Overall Score */
    .overall-box {
        background-color: #000000;
        color: #ffffff !important;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .overall-box h2 { color: #ffffff !important; margin: 0; }

    /* Сетка для критериев */
    .criteria-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 10px;
        margin-bottom: 30px;
    }
    .criterion-card {
        border: 2px solid #000000;
        padding: 10px;
        text-align: center;
        border-radius: 5px;
        font-weight: bold;
    }

    /* Поле с текстом и ошибками */
    .essay-results {
        border-top: 2px solid #000000;
        padding-top: 20px;
        line-height: 1.6;
        font-size: 18px;
    }

    .stTextArea textarea { 
        background-color: #ffffff !important; 
        border: 1px solid #000000 !important; 
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    div.stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        width: 100%;
        height: 3em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. API KEY SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-flash-latest')
except:
    st.error("API Key error!")
    st.stop()

# --- 3. SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = 'input'
if 'results_data' not in st.session_state:
    st.session_state.results_data = {}

# --- 4. FUNCTIONS ---
def get_topic():
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f.readlines() if line.strip()]
            return random.choice(topics)
    except:
        return "Standard Exam Topic"

if 'current_topic' not in st.session_state:
    st.session_state.current_topic = get_topic()

# --- 5. PAGE: RESULTS ---
if st.session_state.page == 'results':
    data = st.session_state.results_data
    
    # Прямоугольник OVERALL
    st.markdown(f"""
        <div class="overall-box">
            <p style="margin:0; font-size: 14px; color: #bbb !important;">OVERALL SCORE</p>
            <h2>{data.get('total', 0)} / 25</h2>
        </div>
    """, unsafe_allow_html=True)

    # Окошки критериев
    st.markdown(f"""
        <div class="criteria-grid">
            <div class="criterion-card">Sagatavota<br>{data.get('c1', 0)}/5</div>
            <div class="criterion-card">Mijiedarbība<br>{data.get('c2', 0)}/5</div>
            <div class="criterion-card">Bagātība<br>{data.get('c3', 0)}/5</div>
            <div class="criterion-card">Gramatika<br>{data.get('c4', 0)}/5</div>
            <div class="criterion-card">Plūdums<br>{data.get('c5', 0)}/5</div>
        </div>
    """, unsafe_allow_html=True)

    # Текст с ошибками
    st.markdown("### Revised Text")
    st.markdown(f"<div class='essay-results'>{data.get('text', '')}</div>", unsafe_allow_html=True)

    if st.button("⬅️ TRY NEW TOPIC"):
        st.session_state.page = 'input'
        st.session_state.current_topic = get_topic()
        st.rerun()

# --- 6. PAGE: INPUT ---
else:
    st.markdown("<h1>Exam Task 2</h1>", unsafe_allow_html=True)
    if st.button("RANDOMIZE TOPIC 🎲"):
        st.session_state.current_topic = get_topic()
        st.rerun()
    
    st.subheader(f"Topic: {st.session_state.current_topic}")
    
    # Поле ввода
    user_text = st.text_area("Write your essay here:", height=350, placeholder="Start typing your essay...")
    
    # Счётчик слов
    word_count = len(user_text.split())
    st.write(f"Word count: {word_count}")
    
    if st.button("SUBMIT FOR EVALUATION"):
        if word_count < 100:
            st.error(f"Text too short! You have only {word_count} words. Minimum is 100.")
        else:
            with st.spinner('Examiner is marking your work...'):
                prompt = f"""
                Analyze this essay on "{st.session_state.current_topic}": "{user_text}"
                
                You must provide exactly this labels and nothing else:
                SCORE_C1: [0-5]
                SCORE_C2: [0-5]
                SCORE_C3: [0-5]
                SCORE_C4: [0-5]
                SCORE_C5: [0-5]
                TOTAL: [sum]
                TEXT: [The student's text, highlight errors in bold and brackets: **error (correction)**]
                """
                
                try:
                    response_text = model.generate_content(prompt).text
                    
                    # Вспомогательная функция для поиска цифр
                    def extract_score(label, text):
                        match = re.search(rf'{label}:\s*(\d+)', text)
                        return match.group(1) if match else "0"

                    # Собираем данные
                    res = {}
                    res['c1'] = extract_score('SCORE_C1', response_text)
                    res['c2'] = extract_score('SCORE_C2', response_text)
                    res['c3'] = extract_score('SCORE_C3', response_text)
                    res['c4'] = extract_score('SCORE_C4', response_text)
                    res['c5'] = extract_score('SCORE_C5', response_text)
                    res['total'] = extract_score('TOTAL', response_text)
                    
                    # Извлекаем исправленный текст
                    if "TEXT:" in response_text:
                        res['text'] = response_text.split("TEXT:")[1].strip()
                    else:
                        res['text'] = user_text  # Запасной вариант

                    # Сохраняем и переключаем страницу
                    st.session_state.results_data = res
                    st.session_state.page = 'results'
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error during evaluation: {e}")
                    st.info("Please try clicking Submit again.")
