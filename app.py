import streamlit as st
import google.generativeai as genai
import random
import re
import json

# --- 1. CONFIG & STYLES ---
st.set_page_config(page_title="English Exam Coach", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, li, span, label, div { color: #000000 !important; font-family: 'Times New Roman', serif; }
    div.stButton > button { background-color: #fff !important; color: #000 !important; border: 1px solid #000 !important; font-weight: bold; width: 100%; }
    div.stButton > button:hover { background-color: #000 !important; color: #fff !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA (READING) ---
READING_TASKS = [
    {
        "id": 1,
        "questions": ["Who decided to gain practical skills?", "Who mentions social anxieties?", "Who became more focused?", "Who warns about planning?", "Who had to work to fund travels?", "Who discovered a hidden talent?", "Who felt pressured by peers?"],
        "correct_data": {
            "q1": {"ans": "A", "exp": "Mark learned to care for birds."},
            "q2": {"ans": "C", "exp": "Elena was shy but transformed."},
            "q3": {"ans": "E", "exp": "Julian missed academic theory."},
            "q4": {"ans": "D", "exp": "Tom warns that without a goal, time slips."},
            "q5": {"ans": "B", "exp": "Sarah worked two jobs to afford trip."},
            "q6": {"ans": "B", "exp": "Sarah gifted in marketing."},
            "q7": {"ans": "A", "exp": "Mark felt like a failure watching friends."}
        },
        "texts": {
            "A. Mark": "I felt like a failure... volunteering helped.",
            "B. Sarah": "Working two jobs... started a vlog.",
            "C. Elena": "I was shy... job transformed me.",
            "D. Tom": "Without a plan, you achieve nothing.",
            "E. Julian": "Physical labour made me miss theory."
        }
    }
]

# --- 3. API SETUP ---
try:
    # Замени на свой ключ в Streamlit Secrets или вставь сюда строкой: "ТВОЙ_КЛЮЧ"
    api_key = st.secrets.get("GEMINI_API_KEY", "YOUR_KEY_HERE")
    genai.configure(api_key=api_key)
    AVAILABLE_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
except Exception as e:
    st.error(f"API Setup Error: {e}")

# --- 4. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'current_topic' not in st.session_state: st.session_state.current_topic = None
if 'drill_type' not in st.session_state: st.session_state.drill_type = "Essay"
if 'results_data' not in st.session_state: st.session_state.results_data = {}
if 'reading_answers' not in st.session_state: st.session_state.reading_answers = {}
if 'current_reading_task' not in st.session_state: st.session_state.current_reading_task = None

# --- 5. PAGE LOGIC ---

# HOME PAGE
if st.session_state.page == 'home':
    st.title("🇬🇧 English Exam Coach")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("WRITING"):
            st.session_state.page = 'writing_menu'
            st.rerun()
    with col2:
        if st.button("READING"):
            st.session_state.page = 'reading'
            st.rerun()

# WRITING MENU
elif st.session_state.page == 'writing_menu':
    st.title("✍️ Writing Practice")
    if st.button("Back"): st.session_state.page = 'home'; st.rerun()
    if st.button("Start Task 2 Essay"):
        st.session_state.drill_type = "Task 2 Essay"
        st.session_state.page = 'input'
        st.rerun()

# READING PAGE
elif st.session_state.page == 'reading':
    if not st.session_state.current_reading_task:
        st.session_state.current_reading_task = random.choice(READING_TASKS)
    task = st.session_state.current_reading_task
    st.title("📖 Reading")
    if st.button("Back"): st.session_state.page = 'home'; st.rerun()
    
    for i, q in enumerate(task["questions"], 1):
        st.session_state.reading_answers[f"q{i}"] = st.text_input(f"{i}. {q}", max_chars=1).upper()
    
    if st.button("Check Answers"):
        st.session_state.page = 'reading_results'
        st.rerun()

# READING RESULTS
elif st.session_state.page == 'reading_results':
    st.title("Results")
    task = st.session_state.current_reading_task
    score = 0
    for i in range(1, len(task["questions"])+1):
        key = f"q{i}"
        ans = st.session_state.reading_answers.get(key, "")
        correct = task["correct_data"][key]["ans"]
        if ans == correct: score += 1
        st.write(f"Q{i}: {ans} (Correct: {correct})")
    st.subheader(f"Total: {score}")
    if st.button("Home"): st.session_state.page = 'home'; st.rerun()

# INPUT PAGE (AI LOGIC HERE)
elif st.session_state.page == 'input':
    st.title("Write your text")
    user_text = st.text_area("Type here (min 100 words):", height=300)
    
    if st.button("SUBMIT FOR EVALUATION"):
        if len(user_text.split()) < 10: # Уменьшил для теста, верни 100 потом
            st.error("Too short!")
        else:
            prompt = f"""Evaluate this English text as an examiner. Return ONLY JSON:
            {{"c1":5, "c2":5, "c3":5, "c4":5, "c5":5, "total":25, "feedback":"...", "strengths":[], "improvements":[], "corrected":"..."}}
            Text: {user_text}"""
            
            with st.spinner("AI is thinking..."):
                response_text = None
                errors = []
                for model_name in AVAILABLE_MODELS:
                    try:
                        m = genai.GenerativeModel(model_name)
                        res = m.generate_content(prompt)
                        if res and res.text:
                            response_text = res.text
                            break
                    except Exception as e:
                        errors.append(f"{model_name}: {str(e)}")
                
                if response_text:
                    try:
                        # Чистим JSON от Markdown ```json ... ```
                        clean = re.search(r'\{.*\}', response_text, re.DOTALL).group()
                        st.session_state.results_data = json.loads(clean)
                        st.session_state.page = 'results'
                        st.rerun()
                    except:
                        st.error("AI output error. Try again.")
                else:
                    st.error("All models failed.")
                    for e in errors: st.write(e)

# RESULTS PAGE
elif st.session_state.page == 'results':
    st.title("📝 Evaluation Results")
    data = st.session_state.results_data
    st.metric("Total Score", f"{data.get('total')}/25")
    
    cols = st.columns(5)
    labels = ["Content", "Comm.", "Org.", "Grammar", "Fluency"]
    keys = ["c1", "c2", "c3", "c4", "c5"]
    for i, col in enumerate(cols):
        col.write(labels[i])
        col.subheader(data.get(keys[i]))

    st.write("### Feedback")
    st.write(data.get('feedback'))
    
    st.write("### Corrected Version")
    st.info(data.get('corrected'))
    
    if st.button("Start Again"):
        st.session_state.page = 'home'
        st.rerun()
