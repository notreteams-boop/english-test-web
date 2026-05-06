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
    .overall-box h2 { color: #000000 !important; margin: 0; font-size: 36px; }

    /* Сетка критериев */
    .criteria-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
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
    .criterion-name { font-weight: bold; display: block; margin-bottom: 5px; font-size: 14px; }
    .criterion-score { font-size: 20px; font-weight: bold; }

    /* Рамка для объявления в Task 1 */
    .announcement-box {
        border: 2px solid #000000;
        padding: 20px;
        margin: 20px 0;
        background-color: #fff;
        line-height: 1.5;
    }

    /* Стиль кнопок */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #000000 !important;
        border-radius: 5px;
        font-weight: bold;
        width: 100%;
        height: 3em;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    .exam-header { border-bottom: 2px solid #000000; margin-bottom: 20px; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. API SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')
except:
    st.error("API Key error! Please check your Streamlit Secrets.")
    st.stop()

# --- 3. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'current_task' not in st.session_state: st.session_state.current_task = None
if 'results_data' not in st.session_state: st.session_state.results_data = {}
if 'current_topic' not in st.session_state: st.session_state.current_topic = ""

def load_random_topic(task_type):
    filename = "topics_task1.txt" if task_type == "Task 1" else "topics.txt"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            return random.choice(lines)
    except:
        return "Error: File not found or empty."

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.markdown("<div class='exam-header'><h1>English Exam Preparation</h1></div>", unsafe_allow_html=True)
    st.write("### Choose your practice task:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("TASK 1: E-mail (Formal/Neutral)"):
            st.session_state.current_task = "Task 1"
            st.session_state.current_topic = load_random_topic("Task 1")
            st.session_state.page = 'input'
            st.rerun()
    with col2:
        if st.button("TASK 2: Essay (Problem/Solution)"):
            st.session_state.current_task = "Task 2"
            st.session_state.current_topic = load_random_topic("Task 2")
            st.session_state.page = 'input'
            st.rerun()

# --- PAGE: INPUT ---
elif st.session_state.page == 'input':
    st.markdown(f"<div class='exam-header'><h1>{st.session_state.current_task} Practice</h1></div>", unsafe_allow_html=True)
    
    if st.button("Get New Topic 🎲"):
        st.session_state.current_topic = load_random_topic(st.session_state.current_task)
        st.rerun()

    if st.session_state.current_task == "Task 1":
        st.write("#### Read the announcement and write your e-mail:")
        st.markdown(f"<div class='announcement-box'>{st.session_state.current_topic}</div>", unsafe_allow_html=True)
        st.info("Write 120-150 words. Focus on: role choice, availability, skills, and asking questions.")
    else:
        st.write("#### Essay Topic:")
        st.subheader(st.session_state.current_topic)
        st.info("Write 250-300 words. Focus on: problem formulation, 2 solutions, and conclusion.")

    user_text = st.text_area("Your Response:", height=380, placeholder="Start typing here...")
    word_count = len(user_text.split())
    st.write(f"**Word count: {word_count}**")

    if st.button("SUBMIT FOR EVALUATION"):
        min_limit = 50 if st.session_state.current_task == "Task 1" else 100
        if word_count < min_limit:
            st.error(f"Your text is too short ({word_count} words). Minimum required is {min_limit} words.")
        else:
            with st.spinner('The examiner is checking your work...'):
                prompt = f"""
                You are a strict examiner. Analyze this {st.session_state.current_task}. 
                Topic/Announcement: {st.session_state.current_topic}
                
                Strictly follow this format for your response:
                SCORE_C1: [0-5]
                SCORE_C2: [0-5]
                SCORE_C3: [0-5]
                SCORE_C4: [0-5]
                SCORE_C5: [0-5]
                TOTAL: [sum of all scores]
                TEXT: [Rewritten version of the student's text. You MUST highlight every correction by making it bold and putting the fix in brackets, like this: **wrong (right)**. Example: **She go (She goes)** to school.]

                Student's text: {user_text}
                """
                try:
                    response_obj = model.generate_content(prompt)
                    resp = response_obj.text
                    
                    def ex(label, text):
                        m = re.search(rf'{label}:\s*(\d+)', text)
                        return m.group(1) if m else "0"

                    st.session_state.results_data = {
                        'c1': ex('SCORE_C1', resp),
                        'c2': ex('SCORE_C2', resp),
                        'c3': ex('SCORE_C3', resp),
                        'c4': ex('SCORE_C4', resp),
                        'c5': ex('SCORE_C5', resp),
                        'total': ex('TOTAL', resp),
                        'text': resp.split("TEXT:")[1].strip() if "TEXT:" in resp else user_text
                    }
                    st.session_state.page = 'results'
                    st.rerun()
                except Exception as e:
                    st.error(f"Limit reached or API error. Wait 1 minute. Error: {e}")

# --- PAGE: RESULTS ---
elif st.session_state.page == 'results':
    data = st.session_state.results_data
    st.markdown("<div class='exam-header'><h1>Evaluation Report</h1></div>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="overall-box">
            <p style="margin:0; font-weight: bold;">TOTAL SCORE</p>
            <h2>{data.get('total', 0)} / 25</h2>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="criteria-grid">
            <div class="criterion-card"><span class="criterion-name">Sagatavota</span><span class="criterion-score">{data.get('c1', 0)}</span></div>
            <div class="criterion-card"><span class="criterion-name">Mijiedarbība</span><span class="criterion-score">{data.get('c2', 0)}</span></div>
            <div class="criterion-card"><span class="criterion-name">Bagātība</span><span class="criterion-score">{data.get('c3', 0)}</span></div>
            <div class="criterion-card"><span class="criterion-name">Gramatika</span><span class="criterion-score">{data.get('c4', 0)}</span></div>
            <div class="criterion-card"><span class="criterion-name">Plūdums</span><span class="criterion-score">{data.get('c5', 0)}</span></div>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("Revised Text & Corrections")
    st.markdown(data.get('text', ''))
    
    st.write("---")
    if st.button("⬅️ PRACTICE AGAIN"):
        st.session_state.page = 'home'
        st.rerun()
