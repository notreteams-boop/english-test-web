import streamlit as st
import google.generativeai as genai
import random
import re

# --- 1. CONFIG & STYLES ---
st.set_page_config(page_title="Exam Simulator PRO", page_icon="📝", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, li, span, label, div { color: #000000 !important; font-family: 'Times New Roman', serif; }
    .overall-box { background-color: #f0f2f6; color: #000000 !important; padding: 20px; text-align: center; border: 2px solid #000000; border-radius: 10px; margin-bottom: 20px; }
    .overall-box h2 { color: #000000 !important; margin: 0; font-size: 32px; }
    .criteria-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 30px; }
    .criterion-card { border: 1px solid #000000; padding: 10px; text-align: center; border-radius: 5px; background-color: #ffffff; }
    .criterion-name { font-weight: bold; display: block; margin-bottom: 5px; }
    .announcement-box { border: 2px solid #000000; padding: 15px; margin: 15px 0; background-color: #fff; font-family: 'Arial', sans-serif; }
    div.stButton > button { background-color: #ffffff !important; color: #000000 !important; border: 1px solid #000000 !important; border-radius: 5px; font-weight: bold; width: 100%; transition: 0.3s; }
    div.stButton > button:hover { background-color: #000000 !important; color: #ffffff !important; }
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
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'current_task' not in st.session_state: st.session_state.current_task = None
if 'results_data' not in st.session_state: st.session_state.results_data = {}
if 'current_topic' not in st.session_state: st.session_state.current_topic = ""

def load_random_topic(task_type):
    file = "topics.txt" if task_type == "Task 2" else "topics_task1.txt"
    try:
        with open(file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            return random.choice(lines)
    except: return "No topics found."

# --- 4. NAVIGATION ---
def go_home():
    st.session_state.page = 'home'
    st.rerun()

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.markdown("<div class='exam-header'><h1>English Exam Trainer</h1></div>", unsafe_allow_html=True)
    st.write("### Select your task:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("TASK 1: E-mail (9 pts)"):
            st.session_state.current_task = "Task 1"
            st.session_state.current_topic = load_random_topic("Task 1")
            st.session_state.page = 'input'
            st.rerun()
    with col2:
        if st.button("TASK 2: Essay (16 pts)"):
            st.session_state.current_task = "Task 2"
            st.session_state.current_topic = load_random_topic("Task 2")
            st.session_state.page = 'input'
            st.rerun()

# --- PAGE: INPUT ---
elif st.session_state.page == 'input':
    st.markdown(f"<div class='exam-header'><h1>{st.session_state.current_task}</h1></div>", unsafe_allow_html=True)
    
    if st.button("CHANGE TOPIC 🎲"):
        st.session_state.current_topic = load_random_topic(st.session_state.current_task)
        st.rerun()

    if st.session_state.current_task == "Task 1":
        st.write("You see the following announcement on the school website:")
        st.markdown(f"<div class='announcement-box'>{st.session_state.current_topic}</div>", unsafe_allow_html=True)
        st.markdown("""
        **Write an e-mail to apply for one of these positions. In your e-mail:**
        * explain which role you're interested in and availability;
        * describe relevant skills and experience;
        * ask for more information about the work.
        **Target: 120-150 words.**
        """)
    else:
        st.subheader(f"Topic: {st.session_state.current_topic}")
        st.write("Write an essay: formulate the problem, propose two solutions, and conclude. **Target: 250-300 words.**")

    user_text = st.text_area("Type your response here:", height=350)
    word_count = len(user_text.split())
    st.write(f"Word count: {word_count}")

    if st.button("SUBMIT"):
        min_words = 50 if st.session_state.current_task == "Task 1" else 100
        if word_count < min_words:
            st.error(f"Text too short! Minimum {min_words} words.")
        else:
            with st.spinner('Evaluating...'):
                prompt = f"""
                Analyze this {st.session_state.current_task} response. Topic: {st.session_state.current_topic}
                Format strictly:
                SCORE_C1: [0-5]
                SCORE_C2: [0-5]
                SCORE_C3: [0-5]
                SCORE_C4: [0-5]
                SCORE_C5: [0-5]
                TOTAL: [sum]
                TEXT: [Rewritten text, errors in **bold (correction)**]
                Text to analyze: {user_text}
                """
                resp = model.generate_content(prompt).text
                def ex(label, text):
                    m = re.search(rf'{label}:\s*(\d+)', text)
                    return m.group(1) if m else "0"
                
                st.session_state.results_data = {
                    'c1': ex('SCORE_C1', resp), 'c2': ex('SCORE_C2', resp), 'c3': ex('SCORE_C3', resp),
                    'c4': ex('SCORE_C4', resp), 'c5': ex('SCORE_C5', resp), 'total': ex('TOTAL', resp),
                    'text': resp.split("TEXT:")[1].strip() if "TEXT:" in resp else user_text
                }
                st.session_state.page = 'results'
                st.rerun()

# --- PAGE: RESULTS ---
elif st.session_state.page == 'results':
    data = st.session_state.results_data
    st.markdown("<div class='overall-box'><p>OVERALL SCORE</p><h2>" + data.get('total','0') + " / 25</h2></div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="criteria-grid">
        <div class="criterion-card"><span class="criterion-name">Sagatavota</span>{data.get('c1',0)}/5</div>
        <div class="criterion-card"><span class="criterion-name">Mijiedarbība</span>{data.get('c2',0)}/5</div>
        <div class="criterion-card"><span class="criterion-name">Bagātība</span>{data.get('c3',0)}/5</div>
        <div class="criterion-card"><span class="criterion-name">Gramatika</span>{data.get('c4',0)}/5</div>
        <div class="criterion-card"><span class="criterion-name">Plūdums</span>{data.get('c5',0)}/5</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Revised Text")
    st.markdown(data.get('text', ''))
    
    if st.button("⬅️ HOME"): go_home()
