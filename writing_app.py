import streamlit as st
import google.generativeai as genai
import random
import re

# --- 1. API SETUP (Ваш блок) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro']
    selected_model = next((t for t in target_models if t in available_models), available_models[0] if available_models else None)
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# --- 2. ДАННЫЕ (Важно: проверяем наличие тем) ---
# Если файла topics.py нет, создаем базовые темы прямо здесь, чтобы не было TypeError
try:
    from topics import TASKS_2
except ImportError:
    TASKS_2 = [{"title": "Environment", "source1": "Text about pollution...", "source2": "Text about recycling..."}]

TASKS_1_EMAIL = [
    {"title": "Formal Inquiry", "prompt": "Write an email to a university admissions office asking about the requirements for the English program."},
    {"title": "Informal Invitation", "prompt": "Write an email to a friend inviting them to spend a gap year traveling with you."}
]

# --- 3. SESSION STATE ---
# Используем ключи с префиксом 'wr_', чтобы они не конфликтовали с другими частями приложения
if 'wr_page' not in st.session_state: st.session_state.wr_page = 'home'
if 'wr_drill_type' not in st.session_state: st.session_state.wr_drill_type = None
if 'wr_current_task' not in st.session_state: st.session_state.wr_current_task = None
if 'wr_results' not in st.session_state: st.session_state.wr_results = {}

# --- ПРИНУДИТЕЛЬНЫЙ СТИЛЬ ДЛЯ ЧЕРНОГО ТЕКСТА ---
st.markdown("""<style> 
    .stMarkdown, p, div, label, h3 { color: #000000 !important; } 
    div.stButton > button { border: 2px solid #000 !important; }
</style>""", unsafe_allow_html=True)

# --- PAGE: HOME ---
if st.session_state.wr_page == 'home':
    st.title("✍️ Writing Section")
    
    st.subheader("🏁 Full Task Simulation")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Task 1: E-mail", use_container_width=True):
            st.session_state.wr_drill_type = "Task 1 Email"
            st.session_state.wr_current_task = random.choice(TASKS_1_EMAIL)
            st.session_state.wr_page = 'input'
            st.rerun()
    with c2:
        if st.button("Task 2: Full Essay", use_container_width=True):
            st.session_state.wr_drill_type = "Task 2 Essay"
            st.session_state.wr_current_task = random.choice(TASKS_2)
            st.session_state.wr_page = 'input'
            st.rerun()

    st.write("---")
    st.subheader("🎯 Section Drills (Task 2 Focus)")
    d1, d2, d3 = st.columns(3)
    drills = ["Introduction", "Solutions", "Conclusion"]
    for i, label in enumerate([d1, d2, d3]):
        with label:
            if st.button(drills[i], key=f"dr_{i}", use_container_width=True):
                st.session_state.wr_drill_type = drills[i]
                st.session_state.wr_current_task = random.choice(TASKS_2)
                st.session_state.wr_page = 'input'
                st.rerun()

# --- PAGE: INPUT ---
elif st.session_state.wr_page == 'input':
    task = st.session_state.wr_current_task
    drill = st.session_state.wr_drill_type

    st.subheader(f"Type: {drill}")
    
    # Разделяем отображение
    if drill == "Task 1 Email":
        st.info(f"**Prompt:** {task['prompt']}")
    elif drill == "Task 2 Essay":
        st.markdown(f"**Topic:** {task['title']}")
        st.markdown(f"""
        <div style="background: #f0f2f6; padding: 15px; border-radius: 5px; border: 1px solid #000; color: #000;">
        <b>Source 1:</b> {task['source1']}<br><br>
        <b>Source 2:</b> {task['source2']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.write(f"**Focus:** Write only the **{drill}** for the topic: *{task['title']}*")

    user_text = st.text_area("Your response:", height=300)
    
    col_back, col_sub = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Back"):
            st.session_state.wr_page = 'home'
            st.rerun()
    with col_sub:
        if st.button("SUBMIT FOR EVALUATION", use_container_width=True):
            if len(user_text.split()) < 10:
                st.error("Please write more text.")
            else:
                with st.spinner("AI Examiner is checking..."):
                    try:
                        prompt = f"Level: C1 English. Analyze this {drill}. Topic: {task.get('title', 'Email')}. Text: {user_text}"
                        response = model.generate_content(prompt)
                        st.session_state.wr_results = {"feedback": response.text}
                        st.session_state.wr_page = 'results'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

# --- PAGE: RESULTS ---
elif st.session_state.wr_page == 'results':
    st.title("📝 Results")
    st.write(st.session_state.wr_results.get("feedback", "No feedback available."))
    if st.button("Try Another Task"):
        st.session_state.wr_page = 'home'
        st.rerun()
