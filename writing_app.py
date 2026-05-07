import streamlit as st
import google.generativeai as genai
import random
import re

# --- 1. API SETUP (Твой код без изменений) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro']
    selected_model = next((t for t in target_models if t in available_models), available_models[0] if available_models else None)
    if not selected_model:
        st.error("No available models found.")
        st.stop()
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# --- 2. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'drill_type' not in st.session_state: st.session_state.drill_type = None
if 'current_task' not in st.session_state: st.session_state.current_task = None
if 'results_data' not in st.session_state: st.session_state.results_data = {}

# --- 3. ВРЕМЕННЫЕ ДАННЫЕ (Если нет в topics.py) ---
# Добавь это в topics.py или оставь здесь для проверки
TASKS_1_EMAIL = [
    {"title": "Job Application", "prompt": "Write an email to a company applying for a summer internship."},
    {"title": "Complaint", "prompt": "Write an email to a hotel manager complaining about the noise levels."}
]

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.title("🇬🇧 English Exam Coach")
    
    st.subheader("🏁 Full Task Simulation")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Task 1: E-mail"):
            st.session_state.drill_type = "Task 1 Email"
            st.session_state.page = 'input'
            st.session_state.current_task = random.choice(TASKS_1_EMAIL)
            st.rerun()
    with c2:
        if st.button("Task 2: Full Essay"):
            st.session_state.drill_type = "Task 2 Essay"
            st.session_state.page = 'input'
            from topics import TASKS_2
            st.session_state.current_task = random.choice(TASKS_2)
            st.rerun()

    st.write("---")
    st.subheader("🎯 Section Drills (Task 2 Focus)")
    d1, d2, d3 = st.columns(3)
    # Для дриллов тоже берем данные из Task 2
    for label in ["Introduction", "Solutions", "Conclusion"]:
        if st.button(label):
            st.session_state.drill_type = label
            st.session_state.page = 'input'
            from topics import TASKS_2
            st.session_state.current_task = random.choice(TASKS_2)
            st.rerun()

# --- PAGE: INPUT ---
elif st.session_state.page == 'input':
    task = st.session_state.current_task
    drill = st.session_state.drill_type

    # --- ЛОГИКА ОТОБРАЖЕНИЯ (Разделяем Письмо и Эссе) ---
    
    if drill == "Task 1 Email":
        # ИНТЕРФЕЙС ДЛЯ ПИСЬМА
        st.markdown(f"### {drill}: {task['title']}")
        st.info(f"**Instructions:** {task['prompt']}")
        st.write("Write between 120-150 words.")
        
    elif drill == "Task 2 Essay":
        # ИНТЕРФЕЙС ДЛЯ ПОЛНОГО ЭССЕ (Твой дизайн)
        st.markdown(f"### {drill}: {task['title']}")
        st.markdown(f"""
        <div style="border-left: 5px solid #000; padding: 10px; background: #f9f9f9; color: #000;">
        <b>Source 1:</b> {task['source1']}<br><br>
        <b>Source 2:</b> {task['source2']}
        </div>
        """, unsafe_allow_html=True)
        st.write("Write between 250-300 words.")

    else:
        # ИНТЕРФЕЙС ДЛЯ ТРЕНИРОВКИ (Introduction/Solutions/Conclusion)
        st.markdown(f"### Drill: {drill}")
        st.write(f"**Topic:** {task['title']}")
        st.markdown(f"*Focus only on writing the {drill.lower()} for this topic.*")

    user_text = st.text_area("Type your response here:", height=350)
    word_count = len(user_text.split())
    st.write(f"Word Count: {word_count}")

    col_back, col_sub = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Back"):
            st.session_state.page = 'home'
            st.session_state.current_task = None
            st.rerun()
            
    with col_sub:
        if st.button("SUBMIT FOR EVALUATION"):
            with st.spinner("AI Examiner is checking..."):
                # Настраиваем промпт в зависимости от типа задачи
                prompt = f"""
                Act as an English Exam Examiner. 
                Task Type: {drill}
                Task Title: {task.get('title', '')}
                Content/Prompt: {task.get('prompt', task.get('source1', ''))}
                
                Analyze this student text: {user_text}
                
                Provide:
                1. Scores (C1-C5)
                2. Feedback
                3. Corrected version (TEXT: ...)
                """
                
                try:
                    response_obj = model.generate_content(prompt)
                    resp = response_obj.text
                    # (Здесь твоя логика парсинга C1-C5 как в прошлом коде)
                    st.session_state.results_data = {'text': resp} # Для примера
                    st.session_state.page = 'results'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# --- PAGE: RESULTS ---
elif st.session_state.page == 'results':
    st.subheader("Exam Results")
    st.write(st.session_state.results_data.get('text', 'No data available'))
    if st.sidebar.button("New Task"):
        st.session_state.page = 'home'
        st.session_state.current_task = None
        st.rerun()
