import streamlit as st
import google.generativeai as genai
import random

# --- 1. API SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# --- 2. СТИЛИЗАЦИЯ ПОД ЭКЗАМЕН (Screenshot Style) ---
st.markdown("""
<style>
    .exam-container {
        font-family: 'Times New Roman', serif !important;
        color: #000000 !important;
        background-color: #ffffff;
        line-height: 1.5;
    }
    .task-title {
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 2px;
    }
    .task-points {
        font-style: italic;
        margin-bottom: 10px;
    }
    .instruction-bold {
        font-weight: bold;
        margin-top: 15px;
    }
    .source-box {
        border: 1px solid #000;
        padding: 15px;
        margin-top: 20px;
        background-color: #ffffff;
    }
    .source-header {
        font-weight: bold;
        margin-bottom: 5px;
    }
    /* Убираем лишние отступы у TextArea */
    .stTextArea textarea {
        border: 1px solid #000 !important;
        border-radius: 0px !important;
        font-family: 'Times New Roman', serif !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'wr_page' not in st.session_state: st.session_state.wr_page = 'home'
if 'wr_current_task' not in st.session_state: st.session_state.wr_current_task = None

# Данные на основе скриншота
tasks = [
    {
        "title": "Task 2",
        "type": "Essay",
        "points": "16 points",
        "time": "55 minutes",
        "instruction": "You are participating in an international youth newspaper essay competition on students’ time management skills. Read the information provided and write an essay in which you:",
        "bullets": [
            "formulate the problem raised in the sources and explain why it should be addressed;",
            "propose and support at least two solutions to the problem which address the causes;",
            "come to a conclusion."
        ],
        "word_limit": "Write between 250–300 words. Texts shorter than 100 words will not be evaluated.",
        "source1": "Time management is an essential skill for it allows students to effectively balance their academic, personal, and social responsibilities. It helps them stay organized, meet deadlines, reduce stress, improve productivity, and achieve better outcomes.",
        "source2": "Many students struggle with procrastination and failing to prioritize tasks. Digital distractions and poor planning often lead to last-minute cramming and lower quality of work."
    }
]

# --- PAGE: HOME ---
if st.session_state.wr_page == 'home':
    st.markdown("<div class='exam-container'><h1>Writing Section</h1></div>", unsafe_allow_html=True)
    if st.button("Start Task 2 (Essay)"):
        st.session_state.wr_current_task = tasks[0]
        st.session_state.wr_page = 'input'
        st.rerun()

# --- PAGE: INPUT ---
elif st.session_state.wr_page == 'input':
    t = st.session_state.wr_current_task
    
    # Весь контент оборачиваем в стилизованный div
    st.markdown(f"""
    <div class="exam-container">
        <div class="task-title">{t['title']}</div>
        <div class="task-points"><i>{t['type']} ({t['points']})</i></div>
        <div class="instruction-bold">You should spend about {t['time']} on this task.</div>
        <p>{t['instruction']}</p>
        <ul style="margin-top: -10px;">
            {"".join([f"<li>{b}</li>" for b in t['bullets']])}
        </ul>
        <div class="instruction-bold">{t['word_limit']}</div>
        <p><i>Do not forget to use “quotation marks” if you decide to quote a phrase from the sources.</i></p>
        
        <div class="source-box">
            <div class="source-header">Source 1:</div>
            <div>{t['source1']}</div>
            <br>
            <div class="source-header">Source 2:</div>
            <div>{t['source2']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("") # Отступ
    user_text = st.text_area("Write your essay here:", height=400, label_visibility="collapsed")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅ Back"):
            st.session_state.wr_page = 'home'
            st.rerun()
    with col2:
        if st.button("SUBMIT FOR EVALUATION", use_container_width=True):
            st.success("Sent to AI Examiner!")
