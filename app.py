import streamlit as st
import google.generativeai as genai

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="AI Exam Prep", page_icon="📝")

# ВСТАВЬ СВОЙ API KEY НИЖЕ (в кавычках)
API_KEY = "AIzaSyBEgXRMal1511eD3H9mq5V7dKBTNPPTuLQ"

# Настройка нейросети
if API_KEY and API_KEY != "ЗДЕСЬ_ТВОЙ_API_КЛЮЧ":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Ошибка: API Key не настроен!")

topics = load_topics()

# --- 3. ИНТЕРФЕЙС САЙТА ---
st.title("🚀 Подготовка к экзаменам с ИИ")
st.subheader("Блок: Английский язык (Сочинение)")

# Выбор темы
selected_topic = st.selectbox("1. Выбери тему для сочинения:", topics)

# Поле для ввода текста
user_text = st.text_area("2. Напиши или вставь сюда свое сочинение:", height=350, placeholder="Start writing here...")

# Кнопка проверки
if st.button("Проверить работу ✅"):
    if not user_text:
        st.warning("Сначала введи текст сочинения!")
    elif API_KEY == "ЗДЕСЬ_ТВОЙ_API_КЛЮЧ":
        st.error("Ошибка: Не указан API Key в настройках сайта.")
    else:
        with st.spinner('Учитель ИИ внимательно проверяет твою работу...'):
            try:
                # Промпт (Инструкция для ИИ)
                prompt = f"""
                Ты профессиональный эксперт по проверке школьных сочинений на английском языке.
                Тема задания: "{selected_topic}"
                Текст ученика: "{user_text}"
                
                Твоя задача — проверить работу по следующим критериям:
                1. Соответствие теме.
                2. Грамматика и орфография (исправь ошибки).
                3. Богатство словарного запаса (предложи синонимы).
                4. Логика и структура (абзацы, связки).
                
                Формат ответа:
                - Поставь оценку от 0 до 10.
                - Список найденных ошибок с исправлениями.
                - 3 совета, как сделать работу лучше.
                
                Отвечай на русском языке. Будь строгим, но справедливым.
                """
                
                # Запрос к нейросети
                response = model.generate_content(prompt)
                
                # Вывод результата
                st.markdown("---")
                st.success("Проверка завершена!")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Произошла ошибка при обращении к ИИ: {e}")

# Подпись внизу
st.info("Это бета-версия сайта. Данные проверяются моделью Gemini 1.5 Flash.")
