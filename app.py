import streamlit as st
import google.generativeai as genai

# --- 1. НАСТРОЙКИ ---
st.set_page_config(page_title="AI Exam Prep", page_icon="📝")

# Твой ключ
API_KEY = "AIzaSyBsETc7a3v_z98gmhDQPgKWo2WWUM7bzFg"
genai.configure(api_key=API_KEY)

# Используем "умное" имя модели, которое само подстроится под систему
MODEL_NAME = 'models/gemini-flash-latest'

try:
    model = genai.GenerativeModel(MODEL_NAME)
except:
    # Запасной вариант, если первый не сработал
    model = genai.GenerativeModel('models/gemini-2.0-flash')

# --- 2. ТЕМЫ ---
def load_topics():
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except:
        return ["Education", "Technology", "Environment"]

topics = load_topics()

# --- 3. ИНТЕРФЕЙС ---
st.title("🚀 Проверка сочинений")

selected_topic = st.selectbox("Выбери тему:", topics)
user_text = st.text_area("Вставь текст сочинения:", height=250)

if st.button("Проверить ✅"):
    if user_text:
        with st.spinner('Связываюсь с ИИ...'):
            try:
                # Специальная инструкция для ИИ
                prompt = f"Ты учитель. Проверь сочинение на тему '{selected_topic}': {user_text}. Оцени от 0 до 10 и исправь ошибки. Ответь на русском."
                
                response = model.generate_content(prompt)
                st.success("Готово!")
                st.write(response.text)
                
            except Exception as e:
                # Если опять лимит (429) или 404, выводим понятное сообщение
                if "429" in str(e):
                    st.warning("Google занят. Подожди ровно 1 минуту и нажми кнопку еще раз.")
                else:
                    st.error(f"Техническая заминка: {e}")
    else:
        st.info("Напиши что-нибудь в поле выше!")
