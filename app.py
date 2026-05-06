import streamlit as st
import google.generativeai as genai
import random

# --- 1. CONFIG & STYLES ---
st.set_page_config(page_title="Exam Simulator PRO", page_icon="📝", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main .block-container { padding-top: 2rem; max-width: 850px; }
    
    h1, h2, h3, p, li, span, label, div { 
        color: #000000 !important; 
        font-family: 'Times New Roman', serif; 
    }

    .stTextArea textarea { 
        background-color: #ffffff !important; 
        border: 1px solid #000000 !important; 
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-size: 16px !important;
        font-family: 'Arial', sans-serif !important;
    }

    div.stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #000000;
        border-radius: 4px;
        font-weight: bold;
        width: 100%;
        height: 3em;
    }

    div.stButton > button:hover {
        background-color: #444444 !important;
        color: #ffffff !important;
    }

    .exam-header { 
        border-bottom: 2px solid #000000; 
        margin-bottom: 20px; 
    }
    
    .result-box {
        padding: 20px;
        border: 1px dashed #000000;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. API KEY SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-flash-latest')
except Exception as e:
    st.error("API Key not found in Secrets!")
    st.stop()

# --- 3. SESSION STATE ИНИЦИАЛИЗАЦИЯ ---
if 'page' not in st.session_state:
    st.session_state.page = 'input'  # Начальная страница — ввод текста
if 'evaluation' not in st.session_state:
    st.session_state.evaluation = ""
if 'current_topic' not in st.session_state:
    # Загрузка тем
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f.readlines() if line.strip()]
            st.session_state.current_topic = random.choice(topics) if topics else "Standard Exam Topic"
    except:
        st.session_state.current_topic = "Education in the 21st Century"

# --- 4. СТРАНИЦА ПРОВЕРКИ (РЕЗУЛЬТАТЫ) ---
if st.session_state.page == 'results':
    st.markdown("<div class='exam-header'><h1>Evaluation Report</h1></div>", unsafe_allow_html=True)
    st.subheader(f"Topic: {st.session_state.current_topic}")
    
    st.markdown("---")
    st.markdown(st.session_state.evaluation)
    st.markdown("---")
    
    if st.button("⬅️ WRITE ANOTHER ESSAY"):
        st.session_state.page = 'input'
        st.session_state.evaluation = ""
        # Выбираем новую тему для следующего раза
        try:
            with open("topics.txt", "r", encoding="utf-8") as f:
                topics = [line.strip() for line in f.readlines() if line.strip()]
                st.session_state.current_topic = random.choice(topics)
        except:
            pass
        st.rerun()

# --- 5. ГЛАВНАЯ СТРАНИЦА (ВВОД ТЕКСТА) ---
else:
    st.markdown("<div class='exam-header'><h1>Task 2</h1><h2>Essay (16 points)</h2></div>", unsafe_allow_html=True)

    if st.button("GET NEW TOPIC 🎲"):
        try:
            with open("topics.txt", "r", encoding="utf-8") as f:
                topics = [line.strip() for line in f.readlines() if line.strip()]
                st.session_state.current_topic = random.choice(topics)
                st.rerun()
        except:
            pass

    st.subheader(f"Topic: {st.session_state.current_topic}")
    st.write("Write an essay in which you formulate the problem, propose two solutions, and conclude.")
    st.write("**Target: 250-300 words.**")

    user_text = st.text_area("Your Response:", height=400, placeholder="Start writing here...")

    word_count = len(user_text.split())
    st.write(f"Word count: {word_count}")

    if st.button("SUBMIT FOR EVALUATION"):
        if word_count < 100:
            st.error("Text is too short (min 100 words).")
        elif user_text:
            with st.spinner('Examiner is evaluating...'):
                try:
                    prompt = f"""
                    Ты строгий экзаменатор VISC. Оцени эссе на тему '{st.session_state.current_topic}'.
                    1. Выведи текст ученика, выделяя ошибки жирным и в скобках исправленный вариант: **error (correction)**.
                    2. Сделай краткий разбор "List of Corrections".
                    3. Поставь баллы (0-5) по критериям: Sagatavota runa, Mijiedarbiba, Valodas bagatiba, Gramatika, Pludums.
                    Текст ученика: {user_text}
                    Отвечай на русском.
                    """
                    response = model.generate_content(prompt)
                    # Сохраняем результат и переключаем страницу
                    st.session_state.evaluation = response.text
                    st.session_state.page = 'results'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error during evaluation: {str(e)}")
