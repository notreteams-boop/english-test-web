import streamlit as st
import google.generativeai as genai

# --- 1. НАСТРОЙКИ И КЛЮЧ ---
st.set_page_config(page_title="AI Exam Prep", page_icon="📝")

# Твой рабочий ключ
API_KEY = "AIzaSyBsETc7a3v_z98gmhDQPgKWo2WWUM7bzFg"
genai.configure(api_key=API_KEY)

# Указываем конкретную рабочую модель из твоего списка
# Мы выбрали gemini-2.0-flash, так как она самая надежная
MODEL_NAME = 'models/gemini-1.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

# --- 2. ЗАГРУЗКА ТЕМ ---
def load_topics():
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        return ["Future of AI", "Global Warming", "Benefits of Reading"]

topics = load_topics()

# --- 3. ИНТЕРФЕЙС ---
st.title("🚀 Подготовка к экзаменам")
st.subheader("Блок: Английский язык")

selected_topic = st.selectbox("1. Выбери тему:", topics)
user_text = st.text_area("2. Напиши сочинение:", height=300)

if st.button("Проверить работу ✅"):
    if user_text:
        with st.spinner('ИИ анализирует текст...'):
            try:
                prompt = f"""
                Ты строгий учитель английского. Проверь сочинение на тему: "{selected_topic}".
                Текст ученика: "{user_text}"
                
                Дай ответ по пунктам:
                1. Оценка (0-10).
                2. Список ошибок и как их исправить.
                3. Рекомендации по лексике.
                Отвечай на русском языке.
                """
                
                response = model.generate_content(prompt)
                st.markdown("---")
                st.success("Разбор готов:")
                st.write(response.text)
                
            except Exception as e:
                if "429" in str(e):
                    st.error("Слишком много запросов! Подожди 60 секунд и попробуй снова.")
                else:
                    st.error(f"Произошла ошибка: {e}")
    else:
        st.warning("Сначала введи текст!")

# Маленькая плашка внизу для красоты
st.caption(f"Используемая модель: {MODEL_NAME}")
