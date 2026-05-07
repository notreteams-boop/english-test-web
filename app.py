import streamlit as st

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
</style>
""", unsafe_allow_html=True)
# Используем session_state, чтобы сайт запомнил, какую кнопку нажал пользователь
if 'choice' not in st.session_state:
    st.session_state.choice = 'main'

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
