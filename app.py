import streamlit as st

# 1. Настройка страницы
st.set_page_config(page_title="English Exam Coach", page_icon="🎓", layout="centered")

# 2. МИНИМАЛЬНЫЙ СТИЛЬ (Убираем "пелену")
st.markdown("""
<style>
    /* Красим только фон самого приложения, не трогая контентные блоки */
    .stApp { 
        background-color: #ffffff !important; 
    }
    /* Цвет текста для меню */
    .main-title { text-align: center; color: #000000; font-family: 'Times New Roman', serif; }
    
    /* Делаем боковую панель видимой */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        border-right: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# 3. ЛОГИКА НАВИГАЦИИ
if 'choice' not in st.session_state:
    st.session_state.choice = 'main'

def go_to_menu():
    st.session_state.choice = 'main'
    st.rerun()

# --- ЭКРАН МЕНЮ ---
if st.session_state.choice == 'main':
    st.markdown("<h1 class='main-title'>🎓 English Exam Coach</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✍️ Writing Section", use_container_width=True):
            st.session_state.choice = 'writing'
            st.rerun()
    with col2:
        if st.button("📖 Reading Section", use_container_width=True):
            st.session_state.choice = 'reading'
            st.rerun()

# --- ЭКРАН WRITING ---
elif st.session_state.choice == 'writing':
    if st.sidebar.button("⬅️ Back to Menu"):
        st.session_state.choice = 'main'
        st.rerun()
    
    # Выбор конкретного задания в боковой панели
    writing_mode = st.sidebar.radio("Select Task:", ["Task 1: E-mail", "Task 2: Essay"])
    
    if writing_mode == "Task 1: E-mail":
        try:
            with open("writing_task1.py", encoding="utf-8") as f:
                exec(f.read())
        except FileNotFoundError:
            st.error("Файл writing_task1.py не найден. Убедись, что ты его создал.")
            
    elif writing_mode == "Task 2: Essay":
        try:
            with open("writing_task2.py", encoding="utf-8") as f:
                exec(f.read())
        except FileNotFoundError:
            st.error("Файл writing_task2.py не найден.")

# --- ЭКРАН READING ---
elif st.session_state.choice == 'reading':
    if st.sidebar.button("⬅️ Назад в меню"):
        go_to_menu()
    
    with open("reading_app.py", encoding="utf-8") as f:
        exec(f.read())
