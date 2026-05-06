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

    /* Светлая плашка для Overall Score */
    .overall-box {
        background-color: #f0f2f6;
        color: #000000 !important;
        padding: 20px;
        text-align: center;
        border: 2px solid #000000;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .overall-box h2 { color: #000000 !important; margin: 0; font-size: 32px; }

    /* Сетка критериев */
    .criteria-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 10px;
        margin-bottom: 30px;
    }
    .criterion-card {
        border: 1px solid #000000;
        padding: 10px;
        text-align: center;
        border-radius: 5px;
        background-color: #ffffff;
    }
    .criterion-name { font-weight: bold; display: block; margin-bottom: 5px; }
    .criterion-score { font-size: 18px; }

    /* Обычные кнопки */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 5px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    .exam-header { border-bottom: 2px solid #000000; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. API SETUP ---
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

def get_topic():
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f.readlines() if line.strip()]
            return random.choice(topics)
    except:
        return "Impact of technology on youth"

if 'current_topic' not in st.session_state:
    st.session_state.current_topic = get_topic()

# --- 4. PAGE: RESULTS ---
if st.session_state.page == 'results':
    data = st.session_state.results_data
    
    st.markdown("<div class='exam-header'><h1>Examination Results</h1></div>", unsafe_allow_html=True)
    
    # Нормальный блок Overall
    st.markdown(f"""
        <div class="overall-box">
            <p style="margin:0; font-weight: bold;">OVERALL SCORE</p>
            <h2>{data.get('total', 0)} / 25</h2>
        </div>
    """, unsafe_allow_html=True)

    # Карточки критериев
    st.markdown(f"""
        <div class="criteria-grid">
            <div class="criterion-card"><span class="criterion-name">Sagatavota</span><span class="criterion-score">{data.get('c1', 0)}/5</span></div>
            <div class="criterion-card"><span class="criterion-name">Mijiedarbība</span><span class="criterion-score">{data.get('c2', 0)}/5</span></div>
            <div class="criterion-card"><span class="criterion-name">Bagātība</span><span class="criterion-score">{data.get('c3', 0)}/5</span></div>
            <div class="criterion-card"><span class="criterion-name">Gramatika</span><span class="criterion-score">{data.get('c4', 0)}/5</span></div>
            <div class="criterion-card"><span class="criterion-name">Plūdums</span><span class="criterion-score">{data.get('c5', 0)}/5</span></div>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("Revised Text")
    # Используем st.markdown для корректного отображения **жирного** текста
    st.markdown(data.get('text', ''))
    
    st.write("---")
    if st.button("⬅️ BACK TO MAIN PAGE"):
        st.session_state.page = 'input'
        st.rerun()

# --- 5. PAGE: INPUT ---
else:
    st.markdown("<div class='exam-header'><h1>English Exam Simulator</h1></div>", unsafe_allow_html=True)
    
    if st.button("GET NEW TOPIC 🎲"):
        st.session_state.current_topic = get_topic()
        st.rerun()
    
    st.write(f"### Topic: {st.session_state.current_topic}")
    user_text = st.text_area("Type your essay here (min 100 words):", height=350)
    
    if st.button("SUBMIT FOR EVALUATION"):
        if len(user_text.split()) < 100:
            st.error("Text is too short!")
        else:
            with st.spinner('Examiner is evaluating...'):
                prompt = f"""
                Analyze this essay on "{st.session_state.current_topic}": "{user_text}"
                Strictly use this format:
                SCORE_C1: [0-5]
                SCORE_C2: [0-5]
                SCORE_C3: [0-5]
                SCORE_C4: [0-5]
                SCORE_C5: [0-5]
                TOTAL: [sum]
                TEXT: [Rewritten student's text. Surround errors with double asterisks and brackets, e.g. **wrong (right)**]
                """
                try:
                    resp = model.generate_content(prompt).text
                    
                    def ex(label, text):
                        m = re.search(rf'{label}:\s*(\d+)', text)
                        return m.group(1) if m else "0"

                    res = {
                        'c1': ex('SCORE_C1', resp),
                        'c2': ex('SCORE_C2', resp),
                        'c3': ex('SCORE_C3', resp),
                        'c4': ex('SCORE_C4', resp),
                        'c5': ex('SCORE_C5', resp),
                        'total': ex('TOTAL', resp),
                        'text': resp.split("TEXT:")[1].strip() if "TEXT:" in resp else user_text
                    }
                    st.session_state.results_data = res
                    st.session_state.page = 'results'
                    st.rerun()
                except:
                    st.error("Evaluation failed. Please try again.")
