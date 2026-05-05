import streamlit as st
import google.generativeai as genai

# 1. Твой ключ
API_KEY = "AIzaSyBZqZ58Z7orJTOXU4KrCiBFK1pxu9nokc0"
genai.configure(api_key=API_KEY)

st.title("Проверка связи с ИИ")

# 2. Давай узнаем, какие модели ВООБЩЕ тебе доступны
st.write("Список доступных тебе моделей:")
try:
    available_models = [m.name for m in genai.list_models()]
    st.write(available_models)
    
    # Берем самую первую модель из списка доступных
    first_model = available_models[0]
    st.success(f"Пробуем подключиться к: {first_model}")
    
    model = genai.GenerativeModel(first_model)
    
    user_input = st.text_input("Напиши 'Hello' для проверки:")
    if st.button("Спросить ИИ"):
        response = model.generate_content(user_input)
        st.write("Ответ ИИ:", response.text)

except Exception as e:
    st.error(f"Ошибка: {e}")
