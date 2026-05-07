import streamlit as st
import google.generativeai as genai
import random
import re
from google.generativeai.types import RequestOptions

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
</style>
""", unsafe_allow_html=True)

# --- 2. READING DATA (ВЫНЕСЛИ НАВЕРХ, ЧТОБЫ НЕ ЛОМАТЬ ЦЕПОЧКУ) ---
READING_TASKS = [
    {
        "id": 1,
        "questions": [
            "Who decided to gain practical skills in a field they knew nothing about?",
            "Who mentions that their gap year helped them overcome social anxieties?",
            "Who found that their time away from studies made them more focused on their future degree?",
            "Who warns that a gap year can be a waste of time if not planned properly?",
            "Who had to work to fund their travels during the year?",
            "Who discovered a hidden talent that changed their career path?",
            "Who felt pressured by their peers' success before starting their gap year?"
        ],
        "correct_data": {
            "q1": {"ans": "A", "exp": "Mark had never worked with animals before but learned to care for injured birds."},
            "q2": {"ans": "C", "exp": "Elena was incredibly shy and terrified of strangers, but her job transformed her confidence."},
            "q3": {"ans": "E", "exp": "Julian realized how much he missed academic theory after physical labour."},
            "q4": {"ans": "D", "exp": "Tom warns that without a clear goal or schedule, you achieve nothing."},
            "q5": {"ans": "B", "exp": "Sarah worked in a bakery and a call centre to afford her trip."},
            "q6": {"ans": "B", "exp": "Sarah realized she had a natural gift for digital marketing through her vlog."},
            "q7": {"ans": "A", "exp": "Mark felt like a failure watching his friends start university while he stayed behind."}
        },
        "texts": {
            "A. Mark": "After high school, I felt like a failure staying behind... I spent volunteering at a wildlife rescue centre...",
            "B. Sarah": "To afford the trip, I spent the first four months working two jobs... I started a travel vlog...",
            "C. Elena": "I used to be incredibly shy... I took a part-time job... transformed my confidence.",
            "D. Tom": "I didn't have a plan... without a clear goal, time just slips away.",
            "E. Julian": "I took a year off to work in a carpentry workshop... missed academic theory."
        }
    },
    {
        "id": 2,
        "questions": [
            "Who realized that their original career choice was based on other people's expectations?",
            "Who mentions that they initially felt ashamed of not going straight to university?",
            "Who found that a period of physical work made them appreciate mental work more?",
            "Who managed to turn a hobby into a source of income during their year off?",
            "Who emphasizes that a gap year is a good time to learn how to manage finances?",
            "Who took a gap year because they felt they weren't mature enough for college life?",
            "Who used their gap year to improve their skills in a foreign language?"
        ],
        "correct_data": {
            "q1": {"ans": "C", "exp": "Maya admitted she only wanted to be a doctor to please her parents."},
            "q2": {"ans": "D", "exp": "Liam felt like a 'loser' when he saw his classmates moving into dorms."},
            "q3": {"ans": "B", "exp": "Kevin's physical work made him dream of sitting in a library or lecture hall."},
            "q4": {"ans": "D", "exp": "Liam started repairing bicycles and turned it into a small business."},
            "q5": {"ans": "E", "exp": "Rachel learned to budget and live within her means."},
            "q6": {"ans": "A", "exp": "Sophie knew she wasn't ready for the independence of university."},
            "q7": {"ans": "A", "exp": "Sophie's fluency in French improved more in six months than in school."}
        },
        "texts": {
            "A. Sophie": "I knew I wasn't ready for independence... my fluency improved more in six months.",
            "B. Kevin": "Working on a construction site... made me realize how much I had taken education for granted.",
            "C. Maya": "I told everyone I wanted to be a doctor... I finally admitted I only wanted to please my parents.",
            "D. Liam": "I felt like a bit of a loser... I started repairing old bicycles... turned into a small business.",
            "E. Rachel": "Learning how to budget my limited savings... taught me responsibility with money."
        }
    }
]

# --- 3. API SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Расширенный список для Европы
    AVAILABLE_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
except Exception as e:
    st.error(f"API Configuration Error: {e}")
    st.stop()

# --- 4. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'mode' not in st.session_state: st.session_state.mode = None 
if 'drill_type' not in st.session_state: st.session_state.drill_type = None
if 'current_topic' not in st.session_state: st.session_state.current_topic = None
if 'results_data' not in st.session_state: st.session_state.results_data = {}
if 'reading_answers' not in st.session_state: st.session_state.reading_answers = {}
if 'current_reading_task' not in st.session_state: st.session_state.current_reading_task = None

# --- 5. PAGE LOGIC (ЦЕЛЬНАЯ ЦЕПОЧКА IF/ELIF) ---

# PAGE: HOME
if st.session_state.page == 'home':
    st.title("🇬🇧 English Exam Coach")
    st.subheader("Select a section to practice:")
    col_writ, col_read = st.columns(2)  
    with col_writ:
        st.markdown("### ✍️ Writing")
        if st.button("GO TO WRITING", use_container_width=True):
            st.session_state.page = 'writing_menu'
            st.rerun()
    with col_read:
        st.markdown("### 📖 Reading")
        if st.button("GO TO READING", use_container_width=True):
            st.session_state.page = 'reading'
            st.rerun()

# PAGE: WRITING_MENU
elif st.session_state.page == 'writing_menu':
    st.title("✍️ Writing Practice")
    if st.button("⬅️ Back to Home"):
        st.session_state.page = 'home'
        st.rerun()
    
    st.subheader("🏁 Full Task Simulation")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Task 1: E-mail"):
            st.session_state.mode, st.session_state.drill_type, st.session_state.page = 'full', "Task 1 Email", 'input'
            st.rerun()
    with c2:
        if st.button("Task 2: Full Essay"):
            st.session_state.mode, st.session_state.drill_type, st.session_state.page = 'full', "Task 2 Essay", 'input'
            st.rerun()

# PAGE: READING
elif st.session_state.page == 'reading':
    if st.session_state.current_reading_task is None:
        st.session_state.current_reading_task = random.choice(READING_TASKS)
    task = st.session_state.current_reading_task
    
    st.title("📖 Reading Practice")
    if st.button("⬅️ Back to Home"):
        st.session_state.current_reading_task = None
        st.session_state.page = 'home'
        st.rerun()

    st.markdown("### Task 1 (7 points)")
    st.info("Read the comments and answer the questions. Choose the correct letter (A-E).")
    
    for i, q in enumerate(task["questions"], 1):
        c1, c2, c3 = st.columns([0.1, 0.7, 0.2])
        c1.write(f"{i}.")
        c2.write(q)
        st.session_state.reading_answers[f"q{i}"] = c3.text_input("", key=f"q{i}_{task['id']}", max_chars=1).upper()

    if st.button("CHECK ANSWERS", use_container_width=True):
        st.session_state.page = 'reading_results'
        st.rerun()
    
    st.write("---")
    for name, content in task["texts"].items():
        with st.expander(f"**Text {name}**"):
            st.write(content)

# PAGE: READING_RESULTS
elif st.session_state.page == 'reading_results':
    st.title("📊 Reading Results")
    task = st.session_state.current_reading_task
    score = 0
    for i in range(1, 8):
        key = f"q{i}"
        user_ans = st.session_state.reading_answers.get(key, "").strip()
        correct = task["correct_data"][key]
        is_correct = user_ans == correct["ans"]
        if is_correct: score += 1
        bg = "#d4edda" if is_correct else "#f8d7da"
        st.markdown(f'<div style="background-color: {bg}; padding: 10px; border-radius: 5px; color: #000; margin-bottom: 5px;"><b>Q{i}:</b> {user_ans} (Correct: {correct["ans"]})<br><small>{correct["exp"]}</small></div>', unsafe_allow_html=True)
    
    st.subheader(f"Total: {score} / 7")
    if st.button("Finish & Back to Home"):
        st.session_state.current_reading_task = None
        st.session_state.page = 'home'
        st.rerun()

# --- PAGE: INPUT ---
elif st.session_state.page == 'input':
    # 1. Выбор темы
    if not st.session_state.current_topic:
        from topics import TASKS_2
        st.session_state.current_topic = random.choice(TASKS_2)
    topic = st.session_state.current_topic

    st.title(f"✍️ Practice: {st.session_state.drill_type}")
    
    # 2. Поле ввода текста
    user_text = st.text_area("Your text:", height=350)
    word_count = len(user_text.split())
    st.write(f"Words: {word_count}")

    # 3. КНОПКА ПРОВЕРКИ (ТОТ САМЫЙ ШАГ 2)
    if st.button("SUBMIT FOR EVALUATION", use_container_width=True):
        if word_count < 100:
            st.error("Text too short!")
        else:
            # Создаем инструкции (промпт)
            prompt = f"Grade this English text: {user_text}" 

            with st.spinner("Connecting to AI (Stable V1)..."):
                response_text = None
                errors = []
                
                for model_name in AVAILABLE_MODELS:
                    try:
                        # Создаем модель
                        model_instance = genai.GenerativeModel(model_name)
                        
                        # ПРИНУДИТЕЛЬНО указываем версию API v1 для Латвии
                        from google.generativeai.types import RequestOptions
                        res = model_instance.generate_content(
                            prompt,
                            request_options=RequestOptions(api_version='v1')
                        )
                        
                        if res and res.text:
                            response_text = res.text
                            break
                    except Exception as e:
                        errors.append(f"{model_name}: {str(e)}")
                        continue 

                # Если получили ответ от ИИ
                if response_text:
                    try:
                        import json
                        # Очистка и сохранение
                        clean_content = response_text.replace('```json', '').replace('```', '').strip()
                        st.session_state.results_data = json.loads(clean_content)
                        st.session_state.page = 'results'
                        st.rerun()
                    except:
                        st.error("AI responded but format is bad. Try again.")
                else:
                    st.error("All models failed. Errors:")
                    for err in errors:
                        st.write(f"❌ {err}")
# PAGE: RESULTS
elif st.session_state.page == 'results':
    st.title("Results")
    st.write(f"Score: {st.session_state.results_data.get('total')}")
    if st.button("Back"):
        st.session_state.page = 'home'
        st.rerun()
