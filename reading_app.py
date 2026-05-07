import streamlit as st

st.header("📖 Раздел Reading (в разработке)")
st.write("Здесь будут твои задания без ИИ.")

# Пример простого теста
st.subheader("Task 1: Matching")
st.write("Read the text and choose the correct answer.")

answer = st.selectbox("What is the author's tone?", ["Neutral", "Aggressive", "Optimistic"])

if st.button("Check"):
    if answer == "Neutral":
        st.success("Правильно!")
    else:
        st.error("Неверно, попробуй еще раз.")
