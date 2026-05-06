import streamlit as st
import google.generativeai as genai
import random
import re

# --- 1. CONFIG & STYLES ---
st.set_page_config(page_title="English Exam Coach", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, li, span, label, div { color: #000000 !important; font-family: 'Times New Roman', serif; }
    .overall-box { background-color: #f8f9fa; padding: 20px; text-align: center; border: 2px solid #000; border-radius: 10px; margin-bottom: 20px; }
    .overall-box h2 { color: #000 !important; font-size: 36px; margin: 0; }
    .announcement-box { border: 2px solid #000; padding: 15px; margin: 15px 0; background-color: #fff; }
    div.stButton > button { background-color: #fff !important; color: #000 !important; border: 1px solid #000 !important; font-weight: bold; width: 100%; transition: 0.3s; }
    div.stButton > button:hover { background-color: #000 !important; color: #fff !important; }
    .drill-label { background-color: #000; color: #fff; padding: 2px 8px; border-radius: 3px; font-size: 12px; margin-bottom: 10px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- 2. API SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Самое надежное имя на сегодня
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error(f"API Configuration Error: {e}")
    st.stop()

# --- 3. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'mode' not in st.session_state: st.session_state.mode = None # 'full' or 'drill'
if 'drill_type' not in st.session_state: st.session_state.drill_type = None
if 'current_topic' not in st.session_state: st.session_state.current_topic = ""
if 'results_data' not in st.session_state: st.session_state.results_data = {}

def get_topic():
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            return random.choice([l.strip() for l in f.readlines() if l.strip()])
    except: return "Global Warming and its impact."

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.title("🇬🇧 English Exam Coach")
    
    st.subheader("🏁 Full Task Simulation")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Task 1: E-mail"):
            st.session_state.mode = 'full'
            st.session_state.drill_type = "Task 1 Email"
            st.session_state.page = 'input'
            st.rerun()
    with c2:
        if st.button("Task 2: Full Essay"):
            st.session_state.mode = 'full'
            st.session_state.drill_type = "Task 2 Essay"
            st.session_state.page = 'input'
            st.rerun()

    st.write("---")
    st.subheader("🎯 Section Drills (Task 2 Focus)")
    d1, d2, d3 = st.columns(3)
    with d1:
        if st.button("Introduction"):
            st.session_state.mode = 'drill'
            st.session_state.drill_type = "Introduction"
            st.session_state.page = 'input'
            st.rerun()
    with d2:
        if st.button("Solutions"):
            st.session_state.mode = 'drill'
            st.session_state.drill_type = "Solutions"
            st.session_state.page = 'input'
            st.rerun()
    with d3:
        if st.button("Conclusion"):
            st.session_state.mode = 'drill'
            st.session_state.drill_type = "Conclusion"
            st.session_state.page = 'input'
            st.rerun()

# --- PAGE: INPUT ---
elif st.session_state.page == 'input':
    if not st.session_state.current_topic: 
        st.session_state.current_topic = get_topic()

    st.markdown(f"<span class='drill-label'>{st.session_state.drill_type.upper()} MODE</span>", unsafe_allow_html=True)
    st.subheader(f"Topic: {st.session_state.current_topic}")
    
    # Инструкции в зависимости от режима
    instructions = {
        "Introduction": "Write only the introduction. Paraphrase the topic and clearly state the problem.",
        "Solutions": "Write the body paragraphs. Propose 2 solutions with examples and consequences.",
        "Conclusion": "Write only the conclusion. Summarize your points and give a final thought.",
        "Task 2 Essay": "Write a full essay (250-300 words).",
        "Task 1 Email": "Write a formal/neutral email (120-150 words) based on the announcement."
    }
    st.info(instructions.get(st.session_state.drill_type, ""))

    user_text = st.text_area("Type your text:", height=300)
    
    col_back, col_sub = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Back"): 
            st.session_state.page = 'home'
            st.session_state.current_topic = ""
            st.rerun()
    with col_sub:
        if st.button("SUBMIT FOR FEEDBACK"):
            with st.spinner("Analyzing..."):
                # Специальный промпт для секций
                prompt = f"""
                Act as an IELTS/VISC examiner. Analyze this {st.session_state.drill_type} for the topic: {st.session_state.current_topic}.
                
                Format:
                SCORE: [0-10 for drills, 0-25 for full tasks]
                FEEDBACK: [Specific advice on how to improve this specific section]
                TEXT: [Corrected text with **bold (fixes)**]
                
                Student text: {user_text}
                """
                resp = model.generate_content(prompt).text
                
                # Парсинг (упрощенный для гибкости)
                score = re.search(r"SCORE:\s*(\d+)", resp)
                feedback = re.search(r"FEEDBACK:(.*?)TEXT:", resp, re.DOTALL)
                text_corr = resp.split("TEXT:")[1] if "TEXT:" in resp else "Error parsing"
                
                st.session_state.results_data = {
                    "score": score.group(1) if score else "N/A",
                    "feedback": feedback.group(1).strip() if feedback else "Keep practicing!",
                    "text": text_corr.strip()
                }
                st.session_state.page = 'results'
                st.rerun()

# --- PAGE: RESULTS ---
elif st.session_state.page == 'results':
    res = st.session_state.results_data
    max_score = 10 if st.session_state.mode == 'drill' else 25
    
    st.markdown(f"""
        <div class='overall-box'>
            <p>SCORE FOR {st.session_state.drill_type.upper()}</p>
            <h2>{res['score']} / {max_score}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("💡 Examiner's Feedback")
    st.write(res['feedback'])
    
    st.subheader("📝 Corrections")
    st.markdown(res['text'])
    
    if st.button("Try Another Exercise"):
        st.session_state.page = 'home'
        st.session_state.current_topic = ""
        st.rerun()
