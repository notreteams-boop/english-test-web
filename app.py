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
                # --- НОВЫЙ ЖЕСТКИЙ ПРОМПТ ---
                prompt = f"""
                Ты — официальный экзаменатор. Твоя задача — оценить текст строго по критериям VISC (латвийский госстандарт).
                Тема: "{selected_topic}"
                Текст ученика: "{user_text}"

                Оценивай по следующим критериям с картинки:
                1. Uzdevuma izpilde (Sagatavotā runa) — до 5 пунктов.
                2. Mijiedarbība (Atbildes uz jautājumiem) — до 5 пунктов.
                3. Valodas bagātība (Leksika/Diapazons) — до 5 пунктов.
                4. Valodas līdzekļu lietojuma pareizība (Gramatika) — до 5 пунктов.
                5. Valodas plūdums un izruna — до 5 пунктов.

                ФОРМАТ ОТВЕТА (строго):
                Напиши только название критерия, количество баллов и краткую причину (почему не максимум). 
                Без приветствий и лишних слов.

                Пример:
                - Sagatavotā runa: 3/5. Причина: Использовано мало аргументов из источников.
                - Valodas bagātība: 2/5. Причина: Ограниченный словарный запас, много повторов.
                И так далее по всем пунктам. В конце — ИТОГ (сумма баллов).
                Отвечай на русском языке.
                """
                
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
