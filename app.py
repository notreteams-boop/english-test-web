import streamlit as st

# 1. Настройка страницы (ТОЛЬКО ЗДЕСЬ ОДИН РАЗ)
st.set_page_config(page_title="English Exam Coach", page_icon="🎓", layout="centered")

# 2. Тот самый дизайн, который тебе нравится (из Writing)
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, li, span, label, div { 
        color: #000000 !important; 
        font-family: 'Times New Roman', serif; 
    }
    /* Стиль кнопок, чтобы они не были синими */
    div.stButton > button { 
        background-color: #fff !important; 
        color: #000 !important; 
        border: 1px solid #000 !important; 
        font-weight: bold; 
    }
    div.stButton > button:hover { 
        background-color: #000 !important; 
        color: #fff !important; 
    }
</style>
""", unsafe_allow_html=True)

# --- ДАЛЬШЕ ТВОЯ ЛОГИКА ПЕРЕКЛЮЧЕНИЯ (Choice) ---
if 'choice' not in st.session_state:
    st.session_state.choice = 'main'

# ... и так далее (import writing_app и т.д.)'

def go_to_writing():
    st.session_state.choice = 'writing'

def go_to_reading():
    st.session_state.choice = 'reading'

def go_to_menu():
    st.session_state.choice = 'main'

# --- ЛОГИКА ПЕРЕКЛЮЧЕНИЯ ---

if st.session_state.choice == 'main':
    st.title("🎓 English Exam Coach")
    st.write("### Выберите раздел для подготовки:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✍️ Writing Section", use_container_width=True):
            go_to_writing()
            st.rerun()
    with col2:
        if st.button("📖 Reading Section", use_container_width=True):
            go_to_reading()
            st.rerun()

elif st.session_state.choice == 'writing':
    # Добавляем кнопку "Назад" в боковую панель, чтобы не мешала твоему дизайну
    if st.sidebar.button("⬅️ Назад в меню"):
        go_to_menu()
        st.rerun()
    
    # ЗАПУСКАЕМ ТВОЙ СТАРЫЙ КОД
    import writing_app 

elif st.session_state.choice == 'reading':
    if st.sidebar.button("⬅️ Назад в меню"):
        go_to_menu()
        st.rerun()
    
    # ЗАПУСКАЕМ НОВЫЙ КОД ЧТЕНИЯ
    import reading_app
