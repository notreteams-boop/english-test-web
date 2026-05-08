import streamlit as st

# ─── 1. Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="English Exam Coach",
    page_icon="🎓",
    layout="centered",
)

# ─── 2. Global style ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; }
    .main-title { text-align: center; color: #000000; font-family: 'Times New Roman', serif; }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
        border-right: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# ─── 3. Navigation state ──────────────────────────────────────────────────────
if "choice" not in st.session_state:
    st.session_state.choice = "main"

# ─── 4. MAIN MENU ─────────────────────────────────────────────────────────────
if st.session_state.choice == "main":
    st.markdown("<h1 class='main-title'>🎓 English Exam Coach</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✍️ Writing Section", use_container_width=True):
            st.session_state.choice = "writing"
            st.rerun()
    with col2:
        if st.button("📖 Reading Section", use_container_width=True):
            st.session_state.choice = "reading"
            st.rerun()

# ─── 5. WRITING SECTION ───────────────────────────────────────────────────────
elif st.session_state.choice == "writing":
    if st.sidebar.button("⬅️ Back to Menu"):
        st.session_state.choice = "main"
        st.rerun()

    writing_mode = st.sidebar.radio("Select Task:", ["Task 1: E-mail", "Task 2: Essay"])

    if writing_mode == "Task 1: E-mail":
        try:
            from writing1 import writing1_page   # ← импортируем функцию
            writing1_page()                       # ← вызываем её
        except ImportError:
            st.error("Файл writing1.py не найден. Убедись, что он лежит рядом с app.py.")
        except Exception as e:
            st.error(f"Ошибка в writing1.py: {e}")

    elif writing_mode == "Task 2: Essay":
        try:
            from writing2 import writing2_page
            writing2_page()
        except ImportError:
            st.error("Файл writing2.py не найден.")
        except Exception as e:
            st.error(f"Ошибка в writing2.py: {e}")

# ─── 6. READING SECTION ───────────────────────────────────────────────────────
elif st.session_state.choice == "reading":
    if st.sidebar.button("⬅️ Back to Menu"):
        st.session_state.choice = "main"
        st.rerun()

    try:
        from reading_app import reading_page
        reading_page()
    except ImportError:
        st.error("Файл reading_app.py не найден.")
    except Exception as e:
        st.error(f"Ошибка в reading_app.py: {e}")
