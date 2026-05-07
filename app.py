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
    
    # Пытаемся найти любую доступную модель flash или pro
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Приоритетный список имен
    target_models = [
        'models/gemini-1.5-flash', 
        'models/gemini-1.5-flash-latest', 
        'models/gemini-pro'
    ]
    
    selected_model = None
    for target in target_models:
        if target in available_models:
            selected_model = target
            break
            
    if not selected_model:
        # Если ничего из списка не нашли, берем первую доступную
        selected_model = available_models[0]
        
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# --- SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'mode' not in st.session_state: st.session_state.mode = None 
if 'drill_type' not in st.session_state: st.session_state.drill_type = None
if 'current_topic' not in st.session_state: st.session_state.current_topic = None # Изменил на None для словаря
if 'results_data' not in st.session_state: st.session_state.results_data = {}
    
if 'reading_answers' not in st.session_state: st.session_state.reading_answers = {}
if 'current_reading_task' not in st.session_state: st.session_state.current_reading_task = None

# НОВАЯ ФУНКЦИЯ ДЛЯ ВЫБОРА ТЕМ (из topics.py)
def get_topic():
    try:
        from topics import TASKS_2
        return random.choice(TASKS_2)
    except:
        # Заглушка, если файл topics.py не найден
        return {
            "title": "Global Warming",
            "source1": "Temperatures are rising globally...",
            "source2": "Carbon emissions reached a new high..."
        }



    # --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.title("🇬🇧 English Exam Coach")
    st.subheader("Select a section to practice:")
    
    col_writ, col_read = st.columns(2)
    
    with col_writ:
        st.markdown("### ✍️ Writing")
        st.write("Task 1, Task 2 and Drills with AI.")
        if st.button("GO TO WRITING", use_container_width=True):
            st.session_state.page = 'writing_menu' # Теперь ведем сюда
            st.rerun()

    with col_read:
        st.markdown("### 📖 Reading")
        st.write("Text comprehension and tasks (No AI).")
        if st.button("GO TO READING", use_container_width=True):
            st.session_state.page = 'reading' # Задел на будущее
            st.rerun()

# --- PAGE: WRITING_MENU ---
elif st.session_state.page == 'writing_menu':
    st.title("✍️ Writing Practice")
    
    if st.button("⬅️ Back to Home"):
        st.session_state.page = 'home'
        st.rerun()

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

# ========================================================
# ШАГ 3: СТРАНИЦА ТЕСТА (READING)
# ========================================================
elif st.session_state.page == 'reading':
    # 1. Выбираем случайное задание, если оно еще не выбрано
    if st.session_state.current_reading_task is None:
        st.session_state.current_reading_task = random.choice(READING_TASKS)
    
    task = st.session_state.current_reading_task
    
    st.title("📖 Reading Practice")
    
    # Кнопка назад
    if st.button("⬅️ Back to Home"):
        st.session_state.current_reading_task = None
        st.session_state.page = 'home'
        st.rerun()

    st.markdown("### Task 1 (7 points)")
    st.info("Read the comments and answer the questions. Choose the correct letter (A-E).")
    
    # 2. Рисуем таблицу (как на скриншоте)
    cols = st.columns([0.1, 0.7, 0.2])
    cols[0].write("**№**")
    cols[1].write("**Questions**")
    cols[2].write("**Text**")

    # Цикл создает 7 строк с вопросами и полями ввода
    for i, q in enumerate(task["questions"], 1):
        c1, c2, c3 = st.columns([0.1, 0.7, 0.2])
        c1.write(f"{i}.")
        c2.write(q)
        # Сохраняем ввод пользователя
        st.session_state.reading_answers[f"q{i}"] = c3.text_input("", key=f"q{i}_{task['id']}", max_chars=1).upper()

    # Кнопка проверки
    if st.button("CHECK ANSWERS", use_container_width=True):
        st.session_state.page = 'reading_results'
        st.rerun()

    st.write("---")
    st.subheader("TEXTS")
    # Выводим тексты в раскрывающихся списках
    for name, content in task["texts"].items():
        with st.expander(f"**Text {name}**"):
            st.write(content)


# ========================================================
# ШАГ 4: СТРАНИЦА РЕЗУЛЬТАТОВ (READING_RESULTS)
# ========================================================
elif st.session_state.page == 'reading_results':
    st.title("📊 Reading Results")
    task = st.session_state.current_reading_task
    score = 0
    
    # Сверяем ответы пользователя с правильными
    for i in range(1, 8):
        key = f"q{i}"
        user_ans = st.session_state.reading_answers.get(key, "").strip()
        correct = task["correct_data"][key]
        is_correct = user_ans == correct["ans"]
        
        if is_correct: 
            score += 1
        
        # Выбираем цвет фона: зеленый если верно, красный если нет
        bg_color = "#d4edda" if is_correct else "#f8d7da"
        icon = "✅" if is_correct else "❌"
        
        # Рисуем красивую плашку с объяснением
        st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 15px; border-radius: 5px; margin-bottom: 10px; color: #000; border: 1px solid #ccc;">
                <b>Question {i}: {icon}</b><br>
                Your answer: <b>{user_ans if user_ans else 'No answer'}</b> | Correct: <b>{correct['ans']}</b><br>
                <div style="margin-top: 5px; font-size: 0.9em; color: #444;">
                    <i>Why: {correct['exp']}</i>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.subheader(f"Total Score: {score} / 7")
    
    if st.button("Finish & Back to Home"):
        st.session_state.current_reading_task = None
        st.session_state.page = 'home'
        st.rerun()
# --- READING DATA ---
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
            "q1": {"ans": "A", "exp": "Mark had never worked with animals before but learned to care for injured birds[cite: 10, 12]."},
            "q2": {"ans": "C", "exp": "Elena was incredibly shy and terrified of strangers, but her job transformed her confidence[cite: 21, 23]."},
            "q3": {"ans": "E", "exp": "Julian realized how much he missed academic theory after physical labour[cite: 32, 34]."},
            "q4": {"ans": "D", "exp": "Tom warns that without a clear goal or schedule, you achieve nothing[cite: 27, 29]."},
            "q5": {"ans": "B", "exp": "Sarah worked in a bakery and a call centre to afford her trip[cite: 15, 16]."},
            "q6": {"ans": "B", "exp": "Sarah realized she had a natural gift for digital marketing through her vlog[cite: 17, 18]."},
            "q7": {"ans": "A", "exp": "Mark felt like a failure watching his friends start university while he stayed behind[cite: 10, 11]."}
        },
        "texts": {
            "A. Mark": "After high school, I felt like a failure staying behind... I spent six months volunteering at a wildlife rescue centre. I had never worked with animals before... [cite: 10, 12]",
            "B. Sarah": "To afford the trip, I spent the first four months working two jobs... I started a travel vlog... realized I had a natural gift for digital marketing[cite: 15, 17].",
            "C. Elena": "I used to be incredibly shy... I took a part-time job in a busy tourist information office... transformed my confidence[cite: 21, 23].",
            "D. Tom": "I didn't have a plan... I realized too late that without a clear goal, time just slips away[cite: 26, 27].",
            "E. Julian": "I took a year off to work in a carpentry workshop... It made me realize how much I actually missed academic theory[cite: 30, 32]."
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
            "q1": {"ans": "C", "exp": "Maya admitted she only wanted to be a doctor to please her parents[cite: 62, 63]."},
            "q2": {"ans": "D", "exp": "Liam felt like a 'loser' when he saw his classmates moving into dorms[cite: 67]."},
            "q3": {"ans": "B", "exp": "Kevin's physical work made him dream of sitting in a library or lecture hall[cite: 59, 60]."},
            "q4": {"ans": "D", "exp": "Liam started repairing bicycles and turned it into a small business[cite: 68, 69]."},
            "q5": {"ans": "E", "exp": "Rachel learned to budget and live within her means[cite: 75, 76]."},
            "q6": {"ans": "A", "exp": "Sophie knew she wasn't ready for the independence of university[cite: 53]."},
            "q7": {"ans": "A", "exp": "Sophie's fluency in French improved more in six months than in years of school[cite: 54]."}
        },
        "texts": {
            "A. Sophie": "I knew I wasn't ready for the independence of university... my fluency in the language improved more in six months[cite: 53, 54].",
            "B. Kevin": "Working on a construction site... made me realize how much I had taken my education for granted[cite: 57, 59].",
            "C. Maya": "I told everyone I wanted to be a doctor... I finally admitted to myself that I only wanted to please them[cite: 62, 63].",
            "D. Liam": "I felt like a bit of a loser... I started repairing old bicycles... turned into a small business[cite: 67, 69].",
            "E. Rachel": "Learning how to budget my limited savings... taught me how to be responsible with money[cite: 75, 76]."
        }
    },
    {
        "id": 3,
        "questions": [
            "Who realized that their lack of confidence was their main obstacle to succeeding?",
            "Who changed their mind about their future career after gaining some work experience?",
            "Who believes that practical work is the best way to prepare for a university degree?",
            "Who felt that they were initially being too arrogant about their abilities?",
            "Who had to deal with the disappointment of a failed plan at the start of their year?",
            "Who focused on a creative hobby that eventually became their main passion?",
            "Who used their gap year to prove they could be independent from their family?"
        ],
        "correct_data": {
            "q1": {"ans": "E", "exp": "Oliver realized his only real problem was his own self-doubt[cite: 118]."},
            "q2": {"ans": "C", "exp": "Jessica was certain she wanted to be a lawyer until she worked in a school[cite: 105, 106]."},
            "q3": {"ans": "A", "exp": "Chloe believes dealing with customers taught her more than any internship[cite: 96]."},
            "q4": {"ans": "B", "exp": "Sam admits he had a bit of an ego and thought he was superior[cite: 98, 102]."},
            "q5": {"ans": "A", "exp": "Chloe's luxury internship was cancelled two weeks before she was due to leave[cite: 94]."},
            "q6": {"ans": "D", "exp": "Daniel's recording and music production became his main focus[cite: 110, 112]."},
            "q7": {"ans": "E", "exp": "Oliver forced himself to handle problems without calling his parents for help[cite: 117]."}
        },
        "texts": {
            "A. Chloe": "The company cancelled the program... dealing with difficult customers taught me more than any internship[cite: 94, 96].",
            "B. Sam": "I was always the top of my class, and I’ll admit I had a bit of an ego... it was a humbling experience[cite: 98, 102].",
            "C. Jessica": "I was certain I wanted to be a corporate lawyer... seeing the impact a good teacher can have changed everything[cite: 105, 106].",
            "D. Daniel": "What was once just a hobby became my main focus... creative freedom allowed me to understand[cite: 111, 113].",
            "E. Oliver": "I forced myself to handle every problem... without calling my parents for help. My only problem was my own self-doubt[cite: 117, 118]."
        }
    }
]
# --- PAGE: INPUT ---
# --- PAGE: INPUT ---
# --- PAGE: INPUT ---
elif st.session_state.page == 'input':
    # Выбираем случайную тему, если она еще не выбрана
    if not st.session_state.current_topic:
        from topics import TASKS_2
        st.session_state.current_topic = random.choice(TASKS_2)

    topic = st.session_state.current_topic

    # Оформление заголовка как на скриншоте
    # Вывод задания и источников (прижми к левому краю, чтобы не было черного фона!)
    st.markdown(f"""
<div style="font-family: 'Times New Roman', serif; color: #000;">
<p style="margin-bottom:0;"><b>Task 2</b></p>
<p style="margin-bottom:0;"><i>Essay (16 points)</i></p>
<p><b>You should spend about 55 minutes on this task.</b></p>
<p>You are participating in an international youth newspaper essay competition on <b>{topic['title']}</b>. 
Read the information provided and write an essay in which you:</p>
<ul style="margin-top: 10px; margin-bottom: 10px;">
<li>formulate the problem raised in the sources and explain why it should be addressed;</li>
<li>propose and support at least two solutions to the problem which address the causes;</li>
<li>come to a conclusion.</li>
</ul>
<p><b>Write between 250–300 words. Texts shorter than 100 words will not be evaluated.</b></p>
<p>Do not forget to use “quotation marks” if you decide to quote a phrase from the sources.</p>
<div style="margin-top:20px;">
<p style="margin-bottom:5px;"><b>Source 1:</b></p>
<div style="border-left: 3px solid #000; padding-left: 15px; font-style: italic; margin-bottom: 20px;">
{topic['source1']}
</div>
<p style="margin-bottom:5px;"><b>Source 2:</b></p>
<div style="border-left: 3px solid #000; padding-left: 15px; font-style: italic; margin-bottom: 20px;">
{topic['source2']}
</div>
</div>
</div>
""", unsafe_allow_html=True)

    st.write("---") # Просто черта для разделения задания и поля ввода

    # Поле для ввода (оставляй как было)
    user_text = st.text_area("Write your essay here:", height=400, placeholder="Start typing...")
    
    word_count = len(user_text.split())
    st.write(f"**Word count: {word_count}**")

    # Кнопки управления
    col_back, col_sub = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Back"):
            st.session_state.page = 'home'
            st.session_state.current_topic = ""
            st.rerun()
            
    with col_sub:
        if st.button("SUBMIT FOR EVALUATION"):
            if word_count < 100:
                st.error("Text too short! Minimum 100 words required for evaluation.")
            else:
                with st.spinner("Examiner is reading..."):
                    # Здесь остается твой промпт, который мы настраивали (C1-C5)
                    prompt = f"""
                    Analyze this essay based on the provided sources.
                    Topic: {topic['title']}
                    Source 1: {topic['source1']}
                    Source 2: {topic['source2']}
                    
                    Format:
                    C1: [score]
                    C2: [score]
                    C3: [score]
                    C4: [score]
                    C5: [score]
                    TOTAL: [sum]
                    FEEDBACK: [Advice]
                    TEXT: [Corrected text with **bold (fixes)**]
                    
                    Student Text: {user_text}
                    """
                    # ... (дальше твой код вызова model.generate_content как раньше)
                    try:
                        response_obj = model.generate_content(prompt)
                        resp = response_obj.text
                        
                        def get_val(label, text):
                            match = re.search(rf'{label}:\s*(\d+)', text)
                            return match.group(1) if match else "0"

                        st.session_state.results_data = {
                            'c1': get_val('C1', resp),
                            'c2': get_val('C2', resp),
                            'c3': get_val('C3', resp),
                            'c4': get_val('C4', resp),
                            'c5': get_val('C5', resp),
                            'total': get_val('TOTAL', resp),
                            'feedback': resp.split("FEEDBACK:")[1].split("TEXT:")[0].strip() if "FEEDBACK:" in resp else "Done!",
                            'text': resp.split("TEXT:")[1].strip() if "TEXT:" in resp else user_text
                        }
                        st.session_state.page = 'results'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                            
        
                

# --- PAGE: RESULTS ---
elif st.session_state.page == 'results':
    data = st.session_state.results_data
    
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border: 2px solid #000; border-radius: 10px; margin-bottom: 20px;">
            <p style="margin:0; font-weight: bold; color: #000;">TOTAL SCORE</p>
            <h2 style="color: #000; font-size: 36px; margin: 0;">{data.get('total', 0)} / 25</h2>
        </div>
    """, unsafe_allow_html=True)

    # Те самые 5 окошек (критериев)
    st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 20px;">
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white;">
                <small style="color: #666;">Sagatavotība</small><br><b style="font-size: 20px; color: #000;">{data.get('c1')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white;">
                <small style="color: #666;">Mijiedarbība</small><br><b style="font-size: 20px; color: #000;">{data.get('c2')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white;">
                <small style="color: #666;">Bagātība</small><br><b style="font-size: 20px; color: #000;">{data.get('c3')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white;">
                <small style="color: #666;">Gramatika</small><br><b style="font-size: 20px; color: #000;">{data.get('c4')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white;">
                <small style="color: #666;">Plūdums</small><br><b style="font-size: 20px; color: #000;">{data.get('c5')}</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if data.get('feedback'):
        st.subheader("💡 Examiner's Advice")
        st.info(data['feedback'])

    st.subheader("📝 Revised Text (Corrections)")
    st.markdown(data.get('text', ''))
    
    st.write("---")
    if st.button("⬅️ TRY ANOTHER EXERCISE"):
        st.session_state.page = 'home'
        st.session_state.current_topic = ""
        st.rerun()
