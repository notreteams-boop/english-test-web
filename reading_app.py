import streamlit as st
import random

# --- 1. СТИЛИ (Копируем твой дизайн) ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, li, span, label, div { color: #000000 !important; font-family: 'Times New Roman', serif; }
    .exam-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    .exam-table th, .exam-table td { border: 1px solid black; padding: 10px; text-align: left; }
    .source-box { border-left: 3px solid #000; padding-left: 15px; font-style: italic; margin-bottom: 20px; }
    .correct { color: green !important; font-weight: bold; }
    .wrong { color: red !important; font-weight: bold; }
    .explanation { background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 5px; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# --- 2. ДАННЫЕ ЗАДАНИЙ (Из твоего файла) ---
TASKS = [
    {
        "title": "Task 1 (7 points)",
        "instruction": "Five people have shared their experience of having a gap year after high school. Read the comments (A–E) and answer the questions. For each question (1–7), choose one of the texts (A–E).",
        "questions": [
            "Who decided to gain practical skills in a field they knew nothing about?",
            "Who mentions that their gap year helped them overcome social anxieties?",
            "Who found that their time away from studies made them more focused on their future degree?",
            "Who warns that a gap year can be a waste of time if not planned properly?",
            "Who had to work to fund their travels during the year?",
            "Who discovered a hidden talent that changed their career path?",
            "Who felt pressured by their peers' success before starting their gap year?"
        ],
        "texts": {
            "A": "<b>Mark:</b> After high school, I felt completely burnt out. While all my friends were posting photos from their new university campuses, I felt like a failure staying behind. However, I spent six months volunteering at a wildlife rescue centre. I had never worked with animals before, but learning to care for injured birds gave me a sense of responsibility...",
            "B": "<b>Sarah:</b> I always thought I’d be a lawyer, but I took a gap year to travel across South East Asia. To afford the trip, I spent the first four months working two jobs in a local bakery and a call centre. During my travels, I started a travel vlog just for fun, only to realize I had a natural gift for digital marketing...",
            "C": "<b>Elena:</b> My gap year was about stepping out of my comfort zone at home. I used to be incredibly shy, terrified of speaking to strangers or even making phone calls. I took a part-time job in a busy tourist information office. Forcing myself to interact with people every day completely transformed my confidence.",
            "D": "<b>Tom:</b> I’ll be honest: my gap year was a bit of a disaster at first. I didn't have a plan and spent the first three months just sleeping in and playing video games. I realized too late that without a clear goal, time just slips away. Eventually, I took a short intensive coding course, which saved my year.",
            "E": "<b>Julian:</b> I took a year off to work in a carpentry workshop. I wanted to do something with my hands after years of sitting at a desk. It made me realize how much I actually missed academic theory. After eight months of physical labour, I was genuinely excited to get back to my books."
        },
        "answers": ["A", "C", "E", "D", "B", "B", "A"],
        "explanations": [
            "Mark mentions he had never worked with animals before and gained new skills at a rescue centre.",
            "Elena explains how her job helped her overcome her shyness and fear of interacting with people.",
            "Julian mentions he missed academic work and entered his degree with a clearer vision.",
            "Tom warns that without a plan or schedule, you can feel like you’ve achieved nothing.",
            "Sarah says she worked two jobs in a bakery and call centre to afford her trip.",
            "Sarah discovered she had a natural gift for digital marketing through her travel vlog.",
            "Mark felt like a 'failure' while watching his friends start their university life."
        ]
    }
    # Можно добавить еще 2 объекта из файла по такой же структуре
]

# --- 3. SESSION STATE ---
if 'reading_state' not in st.session_state: st.session_state.reading_state = 'quiz'
if 'user_answers' not in st.session_state: st.session_state.user_answers = [""] * 7
if 'current_task' not in st.session_state: st.session_state.current_task = TASKS[0] # Пока берем первое

task = st.session_state.current_task

# --- 4. СТРАНИЦА ТЕСТА ---
if st.session_state.reading_state == 'quiz':
    st.markdown("<h2 style='text-align: center;'>READING</h2>", unsafe_allow_html=True)
    st.write(f"**{task['title']}**")
    st.write(f"*{task['instruction']}*")

    # ТАБЛИЦА С ВОПРОСАМИ И ВВОДОМ
    st.markdown("""
        <table class="exam-table">
            <tr>
                <th style="width: 80%;">Questions</th>
                <th style="width: 20%;">Text (A-E)</th>
            </tr>
        </table>
    """, unsafe_allow_html=True)

    for i, q in enumerate(task['questions']):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"{i+1}. {q}")
        with col2:
            st.session_state.user_answers[i] = st.selectbox(
                f"Ans {i+1}", ["", "A", "B", "C", "D", "E"], 
                label_visibility="collapsed", key=f"q_{i}"
            )

    st.write("---")
    st.subheader("TEXTS")
    for letter, content in task['texts'].items():
        st.markdown(f"**{letter}**")
        st.markdown(f"<div class='source-box'>{content}</div>", unsafe_allow_html=True)

    if st.button("SUBMIT ANSWERS", use_container_width=True):
        st.session_state.reading_state = 'results'
        st.rerun()

# --- 5. СТРАНИЦА РЕЗУЛЬТАТОВ ---
elif st.session_state.reading_state == 'results':
    st.title("Results & Explanations")
    
    score = 0
    for i in range(7):
        u_ans = st.session_state.user_answers[i]
        c_ans = task['answers'][i]
        is_correct = u_ans == c_ans
        if is_correct: score += 1

    st.subheader(f"Your Score: {score} / 7")

    for i, q in enumerate(task['questions']):
        u_ans = st.session_state.user_answers[i]
        c_ans = task['answers'][i]
        
        with st.expander(f"Question {i+1}: {u_ans if u_ans else '?'} {'✅' if u_ans == c_ans else '❌'}"):
            st.write(f"**Question:** {q}")
            if u_ans == c_ans:
                st.markdown(f"Result: <span class='correct'>Correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"Result: <span class='wrong'>Wrong. Correct answer is {c_ans}</span>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='explanation'><b>Why?</b> {task['explanations'][i]}</div>", unsafe_allow_html=True)

    if st.button("Try Again"):
        st.session_state.reading_state = 'quiz'
        st.session_state.user_answers = [""] * 7
        st.rerun()
