import streamlit as st

# 1. Настройка страницы (ЕДИНСТВЕННАЯ на всё приложение)
st.set_page_config(page_title="English Exam Coach", page_icon="🎓", layout="centered")

# 2. БРОНЕБОЙНЫЙ СТИЛЬ
# Мы добавляем стили не только для .stApp, но и для всех контейнеров
st.markdown("""
<style>
    /* 1. Фон для всего, включая подложки */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
        background-color: #ffffff !important;
    }

    /* 2. Текст (черный везде) */
    h1, h2, h3, p, li, span, label, div, .stMarkdown, [data-testid="stText"] { 
        color: #000000 !important; 
        font-family: 'Times New Roman', serif !important; 
    }

    /* 3. Боковая панель (Sidebar) - тоже делаем белой, чтобы не было контраста */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #eee;
    }

    /* 4. Кнопки (Экзаменационный стиль) */
    div.stButton > button { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        border: 2px solid #000000 !important; 
        border-radius: 0px !important;
        font-weight: bold !important;
    }
    div.stButton > button:hover { 
        background-color: #000000 !important; 
        color: #ffffff !important; 
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ЛОГИКА ---
if 'choice' not in st.session_state:
    st.session_state.choice = 'main'

if st.session_state.choice == 'main':
    st.markdown("<h1 style='text-align: center;'>🎓 English Exam Coach</h1>", unsafe_allow_html=True)
    st.write("---")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✍️ Writing Section", use_container_width=True):
            st.session_state.choice = 'writing'
            st.rerun()
    with c2:
        if st.button("📖 Reading Section", use_container_width=True):
            st.session_state.choice = 'reading'
            st.rerun()

elif st.session_state.choice == 'writing':
    if st.sidebar.button("⬅️ Menu"):
        st.session_state.choice = 'main'
        st.rerun()
    import writing_app 

elif st.session_state.choice == 'reading':
    if st.sidebar.button("⬅️ Menu"):
        st.session_state.choice = 'main'
        st.rerun()
    import reading_app
