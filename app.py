import streamlit as st
import google.generativeai as genai

# --- 1. КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="Examination System", page_icon="📝", layout="centered")

# Применяем "бумажный" дизайн: белый фон, строгие шрифты
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    .main .block-container {
        padding-top: 3rem;
        max-width: 850px;
    }
    h1, h2, h3, p, li {
        color: #000000 !important;
        font-family: 'Times New Roman', serif;
    }
    .stTextArea textarea {
        background-color: #ffffff !important;
        border: 1px solid #000000 !important;
        color: #000000 !important;
        font-size: 16px;
    }
    .exam-header {
        border-bottom: 2px solid #000;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ПОДКЛЮЧЕНИЕ КЛЮЧА (SECRETS) ---
try:
    # Берем ключ из Streamlit Secrets
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-flash-latest')
except Exception as e:
    st.error("Ключ API не найден в Secrets. Пожалуйста, добавь GEMINI_API_KEY в настройки Streamlit.")
    st.stop()

# --- 3. ЗАГРУЗКА ТЕМ ---
def load_topics():
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except:
        return ["Students' time management skills", "Environmental protection", "Impact of technology on youth"]

# --- 4. ИНТЕРФЕЙС ЭКЗАМЕНА ---
st.markdown("<div class='exam-header'><h1>Task 2</h1><h2>Essay (16 points)</h2></div>", unsafe_allow_html=True)
st.write("**You should spend about 55 minutes on this task.**")

topics = load_topics()
selected_topic = st.selectbox("Select examination topic:", topics)

# Описание задания как на фото Screenshot_20260506_170349_Chrome.jpg
st.markdown(f"""
You are participating in an international youth newspaper essay competition on **{selected_topic}**.
Read the information provided and write an essay in which you:
* formulate the problem raised in the sources and explain why it should be addressed;
* propose and support at least two solutions to the problem which address the causes;
* come to a conclusion.

**Write between 250–300 words.** Texts shorter than 100 words will not be evaluated.
""")

# Поле для ввода эссе
user_text = st.text_area("Your Response:", height=450, placeholder="Type your essay here...")

# Динамический счетчик слов
words = user_text.split()
word_count = len(words)
st.write(f"**Word count: {word_count}**")

# --- 5. ОБРАБОТКА РЕЗУЛЬТАТОВ ---
if st.button("SUBMIT FOR EVALUATION"):
    if word_count < 100:
        st.error("❌ Text too short. Minimum 100 words required.")
    elif user_text:
        with st.spinner('Examiner is evaluating your work...'):
            try:
                # Промпт настроен на жесткую проверку по Screenshot_20260505_234937_Chrome.jpg
                prompt = f"""
                Ты — официальный латвийский экзаменатор (VISC). Оцени эссе на тему: "{selected_topic}".
                
                ИНСТРУКЦИЯ ПО ОФОРМЛЕНИЮ:
                1. Сначала выведи текст ученика. В тех местах, где есть ошибки (грамматика, лексика, пунктуация), оставь ошибку, но выдели её **ЖИРНЫМ И В СКОБКАХ** (например: "**I is (I am)**").
                2. После текста сделай раздел "List of Corrections", где кратко объясни каждую ошибку.
                3. В конце выведи таблицу оценок строго по критериям (0-5 баллов):
                   - Sagatavotā runa: [балл]/5 (организация, аргументы)
                   - Mijiedarbība: [балл]/5 (соответствие задаче)
                   - Valodas bagātība: [балл]/5 (лексика)
                   - Valodas lietojuma pareizība: [балл]/5 (грамматика)
                   - Valodas plūdums: [балл]/5 (связность текста)
                
                ИТОГ: Сумма баллов / 25.
                
                Текст ученика: {user_text}
                
                Отвечай на русском языке (кроме названий критериев). Будь предельно строг.
                """
                
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.header("Evaluation Report")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Evaluation error: {e}")
    else:
        st.warning("Please enter your essay before submitting.")st.markdown("### Твоя случайная тема:")
st.info(f"**{st.session_state.current_topic}**")

# Кнопка смены темы
if st.button("🔄 Хочу другую тему"):
    refresh_topic()
    st.rerun()

st.divider()

user_text = st.text_area("Вставь свое сочинение здесь:", height=250, placeholder="Начни писать...")

if st.button("Проверить работу ✅"):
    if user_text:
        with st.spinner('Экзаменатор изучает текст...'):
            try:
                # Промпт для проверки
                check_prompt = f"""
                Ты — официальный экзаменатор. Оцени текст строго по критериям VISC.
                Тема: "{st.session_state.current_topic}"
                Текст: "{user_text}"

                Критерии (по 5 баллов каждый):
                1. Uzdevuma izpilde
                2. Mijiedarbība
                3. Valodas bagātība
                4. Valodas līdzekļu pareizība
                5. Valodas plūdums

                ФОРМАТ ОТВЕТА:
                Название критерия: балл/5. Причина.
                В конце — ИТОГ (сумма баллов).
                Отвечай на русском.
                """
                
                response = model.generate_content(check_prompt)
                st.success("Проверка завершена!")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")
    else:
        st.warning("Поле пустое! Вставь текст сочинения.")
