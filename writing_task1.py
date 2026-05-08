import streamlit as st
import google.generativeai as genai
import re

# --- 1. API SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_models = ['models/gemini-1.5-flash', 'models/gemini-pro']
    selected_model = next((t for t in target_models if t in available_models), available_models[0])
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# --- 2. СТИЛИЗАЦИЯ (Строгий экзамен) ---
st.markdown("""
<style>
    .exam-root {
        font-family: 'Times New Roman', serif !important;
        color: #000000 !important;
    }
    .announcement-container {
        border: 1px solid #000;
        padding: 10px;
        margin: 10px 0;
        text-align: center;
        font-size: 0.9em;
    }
    .score-table {
        border: 2px solid #000;
        padding: 10px;
        background-color: #f0f0f0;
        margin-bottom: 20px;
    }
    /* Стиль для исправленного текста, чтобы Markdown работал */
    .correction-output {
        border: 1px solid #000;
        padding: 15px;
        background-color: #fff;
        color: #000;
    }
    div.stButton > button {
        border: 1px solid #000 !important;
        border-radius: 0px !important;
        background-color: #fff !important;
        color: #000 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ЛОГИКА ---
def generate_short_task():
    # Запрос на укороченное задание
    prompt = """
    Create a VERY CONCISE Task 1 E-mail prompt. 
    1. Short announcement (max 3 lines).
    2. Exactly 3 short bullet points.
    ANNOUNCEMENT: [Ad text]
    INSTRUCTIONS: [Situation and bullets]
    """
    response = model.generate_content(prompt)
    return response.text

if 'current_task_text' not in st.session_state:
    st.session_state.current_task_text = None
if 'grading_result' not in st.session_state:
    st.session_state.grading_result = None

# --- 4. ИНТЕРФЕЙС ---
st.markdown("<div class='exam-root'>", unsafe_allow_html=True)

st.write("**Task 1: E-mail (9 points)**")
st.write("*Time: 25 minutes*")

if st.button("Generate New Task"):
    st.session_state.current_task_text = generate_short_task()
    st.session_state.grading_result = None
    st.rerun()

if st.session_state.current_task_text:
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
    
    st.markdown(f"<div>{instructions}</div>", unsafe_allow_html=True)
    st.write("**Write 120–150 words.**")

    # Поле ввода и счетчик слов
    user_input = st.text_area("Input", height=300, label_visibility="collapsed")
    
    # СЧЕТЧИК СЛОВ
    words = len(user_input.split())
    st.markdown(f"<p style='text-align: right; font-size: 0.8em;'>Word count: <b>{words}</b></p>", unsafe_allow_html=True)

    if st.button("Check E-mail"):
        if words < 20:
            st.error("Text is too short.")
        else:
            with st.spinner("Grading..."):
                # --- ОБНОВЛЕННЫЙ СТРОГИЙ ПРОМПТ ---
eval_prompt = f"""
Act as a VERY STRICT and SKEPTICAL English Exam Examiner. Your goal is to find errors and deduct points. 
Do not be nice. A score of 3/3 is ONLY for perfect, native-level work.

Grade this email based on these STRICT criteria:

1. Saturs (Content) [0-3]:
   - 3: All points covered in detail, perfect tone.
   - 2: One point is slightly missed or tone is inconsistent.
   - 1: Only half of the info is there.
   - 0: Task not fulfilled.

2. Organizācija (Organization) [0-3]:
   - 3: Perfect paragraphs, logical flow, sophisticated linking words (not just 'and', 'but').
   - 2: Standard structure, simple linking words.
   - 1: Messy structure, difficult to follow.
   - 0: Random sentences.

3. Valoda (Language) [0-3]:
   - 3: ZERO grammar/spelling mistakes. Advanced vocabulary.
   - 2: 1-3 minor mistakes, simple vocabulary.
   - 1: Many mistakes that hinder understanding.
   - 0: Total mess.

Student's text: 
{user_input}

FORMAT (STRICT):
TOTAL: [X]/9
Saturs: [X]/3 | Organizācija: [X]/3 | Valoda: [X]/3
CORRECTED_TEXT: [Full text, errors in **bold**]

No positive feedback. No "Good job". Just the numbers and the corrected text.
"""
st.session_state.grading_result = model.generate_content(eval_prompt).text
                st.rerun()

# --- 5. РЕЗУЛЬТАТЫ ---
if st.session_state.grading_result:
    res = st.session_state.grading_result
    try:
        # Парсим баллы
        score_header = re.search(r"TOTAL: (.*?)\n", res).group(1)
        sub_scores = re.search(r"(Saturs: .*?)\n", res).group(1)
        corrected = res.split("CORRECTED_TEXT:")[1].strip()

        # Блок баллов
        st.markdown(f"""
        <div class="score-table">
            <h2 style="text-align:center; margin:0;">TOTAL: {score_header}</h2>
            <p style="text-align:center; margin:5px 0 0 0;">{sub_scores}</p>
        </div>
        """, unsafe_allow_html=True)

        # Блок исправлений (используем st.markdown для работы жирного шрифта)
        st.write("**Corrected Version (Corrections in bold):**")
        st.markdown(f"<div class='correction-output'>", unsafe_allow_html=True)
        st.markdown(corrected) # Markdown внутри блока
        st.markdown("</div>", unsafe_allow_html=True)
    except:
        st.write(res)

st.markdown("</div>", unsafe_allow_html=True)
