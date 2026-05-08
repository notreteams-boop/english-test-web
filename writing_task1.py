import streamlit as st
import google.generativeai as genai
import random
import re

# --- 1. API SETUP (Твой блок) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_models = ['models/gemini-1.5-flash', 'models/gemini-pro']
    selected_model = next((t for t in target_models if t in available_models), available_models[0])
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# --- 2. СТИЛИЗАЦИЯ (Экзаменационный бланк) ---
st.markdown("""
<style>
    .exam-paper {
        font-family: 'Times New Roman', serif !important;
        color: #000000 !important;
        line-height: 1.2;
    }
    .announcement-box {
        border: 1px solid #000;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
    }
    .score-banner {
        background-color: #f0f2f6;
        border: 2px solid #000;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 5px;
    }
    .corrected-text {
        background-color: #ffffff;
        border-left: 5px solid #2ecc71;
        padding: 15px;
        font-family: 'Times New Roman', serif;
        white-space: pre-wrap;
    }
    b { color: #d35400; } /* Цвет для выделения исправлений */
</style>
""", unsafe_allow_html=True)

# --- 3. ЛОГИКА ГЕНЕРАЦИИ ТЕМЫ ---
def get_new_task():
    prompt = """Generate an English Exam Task 1 (E-mail). 
    It must include:
    1. A box with an announcement (like LOOKING FOR VOLUNTEERS or SUMMER CAMP).
    2. 3-4 bullet points of what the student must include in the email.
    3. Formal or informal context.
    Return it in a structured way."""
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Error generating task. Please try again."

if 'current_email_task' not in st.session_state:
    st.session_state.current_email_task = None

# --- 4. ИНТЕРФЕЙС ---
st.markdown("<div class='exam-paper'>", unsafe_allow_html=True)
st.write("**Task 1**")
st.write("**E-mail (9 points)**")
st.write("*You should spend about 25 minutes on this task.*")

if st.button("Generate New Task"):
    with st.spinner("Creating task..."):
        st.session_state.current_email_task = get_new_task()
        st.session_state.eval_results = None

if st.session_state.current_email_task:
    # Вывод задания
    st.markdown(f"<div class='announcement-box'>{st.session_state.current_email_task}</div>", unsafe_allow_html=True)
    st.write("**Write between 120–150 words. Texts shorter than 50 words will not be evaluated.**")

    # Поле ввода
    user_email = st.text_area("Type your e-mail here:", height=300, label_visibility="collapsed")
    
    if st.button("CHECK E-MAIL"):
        if len(user_email.split()) < 20:
            st.error("Text too short!")
        else:
            with st.spinner("AI Examiner is grading..."):
                # ПРОМПТ ДЛЯ ПРОВЕРКИ (Твои критерии)
                eval_prompt = f"""
                Act as an official English Examiner. Grade the following email based on a 9-point scale.
                
                Rubric:
                1. Content (Saturs): 0-3 pts (Did they cover all bullet points?)
                2. Organization (Organizācija): 0-3 pts (Structure, linking words)
                3. Language (Valoda): 0-3 pts (Grammar, vocabulary, accuracy)
                Total Max: 9 pts.

                STUDENT TEXT:
                {user_email}

                OUTPUT FORMAT (STRICT):
                TOTAL: [X]/9
                Content: [X]/3
                Organization: [X]/3
                Language: [X]/3
                
                CORRECTED_TEXT:
                [Full student text with all grammar/spelling errors corrected. Put EVERY correction or changed word in **bold**]
                
                DO NOT write anything else. No feedback, no comments.
                """
                
                response = model.generate_content(eval_prompt)
                st.session_state.eval_results = response.text

# --- 5. ВЫВОД РЕЗУЛЬТАТОВ (Окна сверху) ---
if 'eval_results' in st.session_state and st.session_state.eval_results:
    res = st.session_state.eval_results
    
    # Парсим баллы и текст
    try:
        score_part = re.search(r"TOTAL:.*?(?=CORRECTED_TEXT)", res, re.S).group(0)
        text_part = res.split("CORRECTED_TEXT:")[1].strip()
        
        # Большое окно с баллами
        st.markdown(f"""
        <div class="score-banner">
            <h2 style="margin:0; text-align:center;">{score_part.splitlines()[0]}</h2>
            <hr style="border:1px solid #000">
            <p style="text-align:center; font-size:1.1em;">
                {score_part.splitlines()[1]} | {score_part.splitlines()[2]} | {score_part.splitlines()[3]}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Исправленный текст
        st.write("### Corrected Text (Corrections in bold):")
        st.markdown(f"<div class='corrected-text'>{text_part}</div>", unsafe_allow_html=True)
        
    except:
        st.write(res) # Если ИИ выдал не по формату

st.markdown("</div>", unsafe_allow_html=True)
