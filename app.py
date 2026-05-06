import streamlit as st
import google.generativeai as genai

# --- 1. НАСТРОЙКИ ---
st.set_page_config(page_title="AI Exam Prep", page_icon="📝")

# Твой ключ
API_KEY = "AIzaSyBsETc7a3v_z98gmhDQPgKWo2WWUM7bzFg"
genai.configure(api_key=API_KEY)

MODEL_NAME = 'models/gemini-flash-latest'
model = genai.GenerativeModel(MODEL_NAME)

# --- 2. ФУНКЦИЯ ГЕНЕРАЦИИ ТЕМЫ ---
def get_ai_topic():
    """Запрашивает у ИИ новую тему для сочинения"""
    prompt = "Придумай одну актуальную тему для экзаменационного сочинения (уровень средней школы, формат VISC). Тема должна быть на русском языке. Напиши только саму тему, без кавычек и лишних слов."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return "Влияние искусственного интеллекта на выбор профессии"

# --- 3. ЛОГИКА СОСТОЯНИЯ ---
# Если темы еще нет в памяти — генерируем её
if 'current_topic' not in st.session_state:
    with st.spinner('ИИ придумывает тему...'):
        st.session_state.current_topic = get_ai_topic()

def refresh_topic():
    with st.spinner('Генерирую новую тему...'):
        st.session_state.current_topic = get_ai_topic()

# --- 4. ИНТЕРФЕЙС ---
st.title("🚀 Экзаменатор на базе ИИ")

st.markdown("### Твоя случайная тема:")
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
