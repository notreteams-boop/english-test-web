import streamlit as st

# 1. Настройка страницы (Один раз на всё приложение)
st.set_page_config(page_title="English Exam Coach", page_icon="🎓", layout="centered")

# 2. ГЛОБАЛЬНЫЙ ДИЗАЙН (Чтобы ничего не прыгало)
st.markdown("""
<style>
    /* Жестко фиксируем белый фон для ВСЕХ страниц */
    .stApp { 
        background-color: #ffffff !important; 
    }
    
    /* Жестко фиксируем черный текст для ВСЕХ элементов */
    h1, h2, h3, p, li, span, label, div, .stMarkdown { 
        color: #000000 !important; 
        font-family: 'Times New Roman', serif !important; 
    }

    /* Красивые кнопки в стиле экзамена */
    div.stButton > button { 
        background-color: #fff !important; 
        color: #000 !important; 
        border: 1px solid #000 !important; 
        font-weight: bold; 
        height: 3em;
        transition: 0.3s;
    }
    div.stButton > button:hover { 
        background-color: #000 !important; 
        color: #fff !important; 
    }

    /* Скрываем стандартное меню Streamlit сверху для чистоты */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. ЛОГИКА ПЕРЕКЛЮЧЕНИЯ ---

if 'choice' not in st.session_state:
    st.session_state.choice = 'main'

def go_to_writing():
    st.session_state.choice = 'writing'

def go_to_reading():
    st.session_state.choice = 'reading'

def go_to_menu():
    st.session_state.choice = 'main'

# --- ГЛАВНОЕ МЕНЮ ---
if st.session_state.choice == 'main':
    st.markdown("<h1 style='text-align: center;'>🎓 English Exam Coach</h1>", unsafe_allow_html=True)
    st.write("### Select your preparation section:")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Practice Writing")
        st.write("Full essays, emails, and targeted drills with AI feedback.")
        if st.button("✍️ Writing Section", use_container_width=True):
            go_to_writing()
            st.rerun()
            
    with col2:
        st.markdown("#### Practice Reading")
        st.write("Exam-style reading tasks with instant score and explanations.")
        if st.button("📖 Reading Section", use_container_width=True):
            go_to_reading()
            st.rerun()

# --- РАЗДЕЛ WRITING ---
elif st.session_state.choice == 'writing':
    if st.sidebar.button("⬅️ Back to Menu"):
        go_to_menu()
        st.rerun()
    
    # Импортируем твой код writing_app
    import writing_app 

# --- РАЗДЕЛ READING ---
elif st.session_state.choice == 'reading':
    if st.sidebar.button("⬅️ Back to Menu"):
        go_to_menu()
        st.rerun()
    
    # Импортируем твой код reading_app
    import reading_app
