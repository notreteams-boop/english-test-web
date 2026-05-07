import streamlit as st
import random

# --- 1. СТИЛИ (Дизайн под экзаменационный лист) ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, li, span, label, div { color: #000000 !important; font-family: 'Times New Roman', serif; }
    .exam-table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
    .exam-table th, .exam-table td { border: 1px solid black; padding: 10px; text-align: left; }
    .source-box { border-left: 3px solid #000; padding-left: 15px; font-style: italic; margin-bottom: 20px; background-color: #fcfcfc; padding-top: 5px; padding-bottom: 5px; }
    .correct { color: #2e7d32 !important; font-weight: bold; }
    .wrong { color: #d32f2f !important; font-weight: bold; }
    .explanation { background-color: #f0f2f6; padding: 15px; border-radius: 5px; border-left: 5px solid #000; margin-top: 10px; font-size: 15px; color: #000 !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. ДАННЫЕ ЗАДАНИЙ (Все 3 варианта) ---
TASKS = [
    {
        "id": 1,
        "title": "Task 1 (7 points)",
        "instruction": "Five people (A–E) share their experiences of taking a gap year. Read their stories and answer the questions. For each question (1–7), choose the correct letter (A, B, C, D or E). Each letter can be used more than once.",
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
            "A": "<b>Mark:</b> After high school, I felt like a failure staying behind while my friends started university. I spent six months volunteering at a wildlife rescue centre. I had never worked with animals before, but it gave me a sense of responsibility. By the time I started my biology degree, I was far more disciplined.",
            "B": "<b>Sarah:</b> I thought I’d be a lawyer, but I took a gap year to travel. To afford the trip, I worked two jobs in a bakery and a call centre. During my travels, I started a travel vlog and realized I had a natural gift for digital marketing and video editing. I’ve now swapped law for media communications.",
            "C": "<b>Elena:</b> My gap year was about stepping out of my comfort zone. I used to be incredibly shy, terrified of speaking to strangers. I took a job in a busy tourist information office. Interacting with hundreds of people every day completely transformed my confidence. University was much easier after that.",
            "D": "<b>Tom:</b> My gap year was a disaster at first. I didn't have a plan and spent months sleeping in and playing video games. I realized too late that without a clear goal, time slips away. Eventually, a coding course saved my year. My advice: have a schedule, or you’ll achieve nothing.",
            "E": "<b>Julian:</b> I worked in a carpentry workshop to do something with my hands. The experience was invaluable because it made me realize how much I actually missed academic theory. After months of physical labour, I was genuinely excited to get back to my books and engineering degree."
        },
        "answers": ["A", "C", "E", "D", "B", "B", "A"],
        "explanations": [
            "Mark mentions he had never worked with animals before and gained new skills at a rescue centre. [cite: 12, 35]",
            "Elena explains how her job helped her overcome her shyness and fear of interacting with people. [cite: 21, 23, 36]",
            "Julian mentions he missed academic work and entered his degree with a clearer vision. [cite: 32, 34, 37]",
            "Tom warns that without a plan or schedule, you can feel like you’ve achieved nothing. [cite: 27, 29, 38]",
            "Sarah says she worked two jobs in a bakery and call centre to afford her trip. [cite: 15, 39]",
            "Sarah discovered she had a natural gift for digital marketing through her travel vlog. [cite: 17, 40]",
            "Mark felt like a 'failure' while watching his friends start their university life. [cite: 10, 41]"
        ]
    },
    {
        "id": 2,
        "title": "Task 1 (7 points)",
        "instruction": "Five people (A–E) discuss their gap year experiences. Read the texts and answer the questions (1–7). Letters may be used more than once.",
        "questions": [
            "Who realized that their original career choice was based on other people's expectations?",
            "Who mentions that they initially felt ashamed of not going straight to university?",
            "Who found that a period of physical work made them appreciate mental work more?",
            "Who managed to turn a hobby into a source of income during their year off?",
            "Who emphasizes that a gap year is a good time to learn how to manage finances?",
            "Who took a gap year because they felt they weren't mature enough for college life?",
            "Who used their gap year to improve their skills in a foreign language?"
        ],
        "texts": {
            "A": "<b>Sophie:</b> I knew I wasn't ready for the independence of university, so I moved to France to work as an au pair. My fluency in the language improved more in six months than in six years of school. It gave me the 'growing up' time I desperately needed.",
            "B": "<b>Kevin:</b> I worked on a construction site. The physical toll made me realize how much I had taken my education for granted. Every morning at 6:00 AM, I found myself dreaming of sitting in a library. It gave me a huge boost of motivation to study harder.",
            "C": "<b>Maya:</b> I told everyone I wanted to be a doctor because my parents are surgeons. However, volunteering at an art centre made me admit I only wanted to please them. My heart wasn't in medicine. I applied for a graphic design degree instead.",
            "D": "<b>Liam:</b> I felt like a bit of a loser when I saw my classmates moving into dorms. To stay busy, I started repairing old bicycles in my garage and selling them online. It turned into a small business. I made a profit and learned about taxes and marketing.",
            "E": "<b>Rachel:</b> I spent the first half of the year working in a supermarket and saving every penny. This allowed me to travel through South America. Learning how to budget my limited savings taught me how to be responsible with money and live within my means."
        },
        "answers": ["C", "D", "B", "D", "E", "A", "A"],
        "explanations": [
            "Maya realized she only chose medicine to please her parents, not because she wanted it. [cite: 62, 77]",
            "Liam says he felt like a 'loser' when he saw his friends moving to university. [cite: 67, 78]",
            "Kevin's hard physical work on a construction site made him dream of being in a library/studying. [cite: 59, 79]",
            "Liam started repairing bikes in his garage and selling them for a profit. [cite: 68, 80]",
            "Rachel explains how she learned to save money and budget while traveling. [cite: 75, 81]",
            "Sophie felt she wasn't ready for the independence of university and needed time to 'grow up'. [cite: 52, 82]",
            "Sophie mentions that her fluency in French improved significantly during her time as an au pair. [cite: 53, 83]"
        ]
    },
    {
        "id": 3,
        "title": "Task 1 (7 points)",
        "instruction": "Five people (A–E) share their stories about taking a gap year. Read the comments and answer the questions (1–7). Each text may be used more than once.",
        "questions": [
            "Who realized that their lack of confidence was their main obstacle to succeeding?",
            "Who changed their mind about their future career after gaining some work experience?",
            "Who believes that practical work is the best way to prepare for a university degree?",
            "Who felt that they were initially being too arrogant about their abilities?",
            "Who had to deal with the disappointment of a failed plan at the start of their year?",
            "Who focused on a creative hobby that eventually became their main passion?",
            "Who used their gap year to prove they could be independent from their family?"
        ],
        "texts": {
            "A": "<b>Chloe:</b> I had a plan for a luxury internship in Milan, but it was cancelled two weeks before I was due to leave. I was devastated but started working as a waitress. Dealing with difficult customers taught me more about human nature than any internship could have.",
            "B": "<b>Sam:</b> In school, I was always the top of my class and I had a bit of an ego. I volunteered at a homeless shelter thinking I’d be 'teaching' them. Instead, I realized how little I knew about the real world. It was a humbling experience.",
            "C": "<b>Jessica:</b> I worked in a primary school as an assistant. Before that, I was certain I wanted to be a corporate lawyer. But seeing the impact a teacher can have changed everything. I withdrew my law applications and applied for Education.",
            "D": "<b>Daniel:</b> My gap year was dedicated to music. I spent every day in my basement recording songs. As I shared them online, I started getting requests to produce music for others. What was once a hobby became my main focus and career path.",
            "E": "<b>Oliver:</b> I was terrified of university and didn't think I was 'smart enough' to survive alone. I worked in a warehouse and traveled solo through Europe, forcing myself to handle every problem without calling my parents. I realized my only problem was self-doubt."
        },
        "answers": ["E", "C", "A", "B", "A", "D", "E"],
        "explanations": [
            "Oliver realized that his only real problem was his own self-doubt. [cite: 118, 120]",
            "Jessica wanted to be an attorney but decided to become a teacher after working in a school. [cite: 105, 121]",
            "Chloe believes her waitress job taught her more than any internship could. [cite: 96, 122]",
            "Sam admits he had 'a bit of an ego' and needed a humbling experience. [cite: 98, 123]",
            "Chloe's Milan internship was cancelled right before she was supposed to leave. [cite: 94, 124]",
            "Daniel recorded music in his basement and it became his main focus. [cite: 111, 125]",
            "Oliver handled all problems solo without calling his parents for help. [cite: 117]"
        ]
    }
]

# --- 3. SESSION STATE (Логика памяти) ---
if 'reading_state' not in st.session_state: 
    st.session_state.reading_state = 'quiz'

if 'current_task' not in st.session_state:
    st.session_state.current_task = random.choice(TASKS)

if 'user_answers' not in st.session_state: 
    st.session_state.user_answers = [""] * 7

task = st.session_state.current_task

# --- 4. ЭКРАН ТЕСТА ---
if st.session_state.reading_state == 'quiz':
    st.markdown("<h1 style='text-align: center;'>READING PRACTICE</h1>", unsafe_allow_html=True)
    st.write(f"### {task['title']}")
    st.write(f"*{task['instruction']}*")

    # Сетка для вопросов и ответов (имитация таблицы)
    st.markdown("""
        <table class="exam-table">
            <tr style="background-color: #eee;">
                <th style="width: 85%;">Questions</th>
                <th style="width: 15%; text-align: center;">Text</th>
            </tr>
        </table>
    """, unsafe_allow_html=True)

    for i, q in enumerate(task['questions']):
        c1, c2 = st.columns([5, 1])
        with c1:
            st.write(f"**{i+1}.** {q}")
        with c2:
            st.session_state.user_answers[i] = st.selectbox(
                f"Q{i+1}", ["", "A", "B", "C", "D", "E"], 
                key=f"task_{task['id']}_q{i}", 
                label_visibility="collapsed"
            )

    st.markdown("---")
    st.subheader("TEXTS")
    for letter, content in task['texts'].items():
        st.markdown(f"### {letter}")
        st.markdown(f"<div class='source-box'>{content}</div>", unsafe_allow_html=True)

    if st.button("SUBMIT FOR EVALUATION", use_container_width=True):
        st.session_state.reading_state = 'results'
        st.rerun()

# --- 5. ЭКРАН РЕЗУЛЬТАТОВ ---
elif st.session_state.reading_state == 'results':
    st.markdown("<h1 style='text-align: center;'>EXAMINATION RESULTS</h1>", unsafe_allow_html=True)
    
    score = sum(1 for i in range(7) if st.session_state.user_answers[i] == task['answers'][i])
    
    st.markdown(f"""
        <div style="background-color: #000; padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 30px;">
            <h2 style="color: #fff !important; margin: 0;">SCORE: {score} / 7</h2>
        </div>
    """, unsafe_allow_html=True)

    for i, q in enumerate(task['questions']):
        u_ans = st.session_state.user_answers[i]
        c_ans = task['answers'][i]
        is_correct = (u_ans == c_ans)
        
        status_icon = "✅" if is_correct else "❌"
        with st.expander(f"Question {i+1}: {u_ans if u_ans else '?'} {status_icon}"):
            st.write(f"**Question:** {q}")
            if is_correct:
                st.markdown(f"Result: <span class='correct'>Correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"Result: <span class='wrong'>Wrong. The correct answer was **{c_ans}**.</span>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='explanation'><b>Explanation:</b> {task['explanations'][i]}</div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 TRY ANOTHER TASK", use_container_width=True):
        # Сброс и выбор новой задачи
        st.session_state.reading_state = 'quiz'
        st.session_state.user_answers = [""] * 7
        st.session_state.current_task = random.choice(TASKS)
        st.rerun()
