import streamlit as st
import google.generativeai as genai
import random
import re

# --- 1. API SETUP (Твой блок) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro']
    selected_model = next((t for t in target_models if t in available_models), available_models[0])
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# --- 2. ГЛОБАЛЬНЫЙ СТИЛЬ (Экзаменационный стандарт) ---
st.markdown("""
<style>
    /* Весь текст в Times New Roman, строго черный */
    .exam-root {
        font-family: 'Times New Roman', Times, serif !important;
        color: #000000 !important;
    }
    
    /* Рамка объявления */
    .announcement-container {
        border: 1px solid #000000;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
        background-color: #ffffff;
    }

    /* Блок результатов (баллы) */
    .score-table {
        border: 2px solid #000000;
        padding: 15px;
        margin-bottom: 25px;
        background-color: #f9f9f9;
    }

    /* Исправленный текст */
    .correction-box {
        border: 1px solid #000000;
        padding: 15px;
        background-color: #ffffff;
        white-space: pre-wrap;
        line-height: 1.6;
    }

    /* Кнопки в строгом стиле */
    div.stButton > button {
        border: 1px solid #000 !important;
        border-radius: 0px !important;
        background-color: #fff !important;
        color: #000 !important;
        font-family: 'Times New Roman', serif !important;
        text-transform: uppercase;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ЛОГИКА ГЕНЕРАЦИИ ТЕМЫ ---
def generate_exam_task():
    prompt = """
    Create a Task 1 E-mail exam prompt. 
    1. It must have an 'Announcement' section inside a box.
    2. It must have 3 bullet points for the student to follow.
    3. The context must be formal or semi-formal (job, volunteer, inquiry).
    Format the response as:
    ANNOUNCEMENT: [Text of the ad]
    INSTRUCTIONS: [Text of the situation and bullets]
    """
    response = model.generate_content(prompt)
    return response.text

if 'current_task_text' not in st.session_state:
    st.session_state.current_task_text = None
if 'grading_result' not in st.session_state:
    st.session_state.grading_result = None

# --- 4. ОТОБРАЖЕНИЕ ---
st.markdown("<div class='exam-root'>", unsafe_allow_html=True)

st.write("**Task 1**")
st.write("**E-mail (9 points)**")
st.write("*You should spend about 25 minutes on this task.*")

if st.button("Generate New Task"):
    st.session_state.current_task_text = generate_exam_task()
    st.session_state.grading_result = None
    st.rerun()

if st.session_state.current_task_text:
    # Отрисовка задания
    task_content = st.session_state.current_task_text
    announcement = ""
    instructions = ""
    
    if "ANNOUNCEMENT:" in task_content and "INSTRUCTIONS:" in task_content:
        announcement = task_content.split("ANNOUNCEMENT:")[1].split("INSTRUCTIONS:")[0].strip()
        instructions = task_content.split("INSTRUCTIONS:")[1].strip()
    else:
        instructions = task_content

    if announcement:
        st.markdown(f"<div class='announcement-container'>{announcement}</div>", unsafe_allow_html=True)
    
    st.markdown(f"<div style='margin-bottom:15px;'>{instructions}</div>", unsafe_allow_html=True)
    st.write("**Write between 120–150 words. Texts shorter than 50 words will not be evaluated.**")

    # Поле ввода (как на скрине - рамка)
    user_input = st.text_area("Input", height=350, label_visibility="collapsed")

    if st.button("Check E-mail"):
        if len(user_input.split()) < 20:
            st.error("Text is too short to be evaluated.")
        else:
            with st.spinner("Checking..."):
                eval_prompt = f"""
                You are an official English Exam Examiner. Grade this email strictly using the 9-point criteria:
                1. Saturs un uzdevuma izpilde (Content): 0-3 points.
                2. Organizācija un tekstveide (Organization): 0-3 points.
                3. Valodas līdzekļi (Language): 0-3 points.
                
                Student's text: {user_input}
                
                RESPONSE FORMAT (STRICTLY FOLLOW):
                TOTAL: [X]/9
                Saturs: [X]/3
                Organizācija: [X]/3
                Valoda: [X]/3
                CORRECTED_TEXT: [The whole student's text but every correction/improvement must be in **bold**]
                
                NO OTHER TEXT OR FEEDBACK.
                """
                res = model.generate_content(eval_prompt).text
                st.session_state.grading_result = res
                st.rerun()

# --- 5. ВЫВОД РЕЗУЛЬТАТОВ (Окна сверху) ---
if st.session_state.grading_result:
    res = st.session_state.grading_result
    
    try:
        # Извлекаем баллы и текст
        scores = re.search(r"TOTAL: (.*?)CORRECTED_TEXT:", res, re.S).group(1).strip()
        corrected = res.split("CORRECTED_TEXT:")[1].strip()

        # Блок с баллами
        st.markdown(f"""
        <div class="score-table">
            <h2 style="text-align:center; margin-top:0;">{scores.splitlines()[0]}</h2>
            <p style="text-align:center; font-size:1.2em;">
                { " | ".join(scores.splitlines()[1:]) }
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Блок с правками
        st.write("**Corrected Version (Changes in bold):**")
        st.markdown(f"<div class='correction-box'>{corrected}</div>", unsafe_allow_html=True)
    except:
        st.write(res)

st.markdown("</div>", unsafe_allow_html=True)
