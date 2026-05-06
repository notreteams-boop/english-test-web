import streamlit as st
import google.generativeai as genai
import random
import re

# --- 1. CONFIG & STYLES ---
st.set_page_config(page_title="English Exam Coach", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3, p, li, span, label, div { color: #000000 !important; font-family: 'Times New Roman', serif; }
    .overall-box { background-color: #f8f9fa; padding: 20px; text-align: center; border: 2px solid #000; border-radius: 10px; margin-bottom: 20px; }
    .overall-box h2 { color: #000 !important; font-size: 36px; margin: 0; }
    .announcement-box { border: 2px solid #000; padding: 15px; margin: 15px 0; background-color: #fff; }
    div.stButton > button { background-color: #fff !important; color: #000 !important; border: 1px solid #000 !important; font-weight: bold; width: 100%; transition: 0.3s; }
    div.stButton > button:hover { background-color: #000 !important; color: #fff !important; }
    .drill-label { background-color: #000; color: #fff; padding: 2px 8px; border-radius: 3px; font-size: 12px; margin-bottom: 10px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- 2. API SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Пытаемся найти любую доступную модель flash или pro
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Приоритетный список имен
    target_models = [
        'models/gemini-1.5-flash', 
        'models/gemini-1.5-flash-latest', 
        'models/gemini-pro'
    ]
    
    selected_model = None
    for target in target_models:
        if target in available_models:
            selected_model = target
            break
            
    if not selected_model:
        # Если ничего из списка не нашли, берем первую доступную
        selected_model = available_models[0]
        
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# --- 3. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'mode' not in st.session_state: st.session_state.mode = None # 'full' or 'drill'
if 'drill_type' not in st.session_state: st.session_state.drill_type = None
if 'current_topic' not in st.session_state: st.session_state.current_topic = ""
if 'results_data' not in st.session_state: st.session_state.results_data = {}

def get_topic():
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            return random.choice([l.strip() for l in f.readlines() if l.strip()])
    except: return "Global Warming and its impact."

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.title("🇬🇧 English Exam Coach")
    
    st.subheader("🏁 Full Task Simulation")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Task 1: E-mail"):
            st.session_state.mode = 'full'
            st.session_state.drill_type = "Task 1 Email"
            st.session_state.page = 'input'
            st.rerun()
    with c2:
        if st.button("Task 2: Full Essay"):
            st.session_state.mode = 'full'
            st.session_state.drill_type = "Task 2 Essay"
            st.session_state.page = 'input'
            st.rerun()

    st.write("---")
    st.subheader("🎯 Section Drills (Task 2 Focus)")
    d1, d2, d3 = st.columns(3)
    with d1:
        if st.button("Introduction"):
            st.session_state.mode = 'drill'
            st.session_state.drill_type = "Introduction"
            st.session_state.page = 'input'
            st.rerun()
    with d2:
        if st.button("Solutions"):
            st.session_state.mode = 'drill'
            st.session_state.drill_type = "Solutions"
            st.session_state.page = 'input'
            st.rerun()
    with d3:
        if st.button("Conclusion"):
            st.session_state.mode = 'drill'
            st.session_state.drill_type = "Conclusion"
            st.session_state.page = 'input'
            st.rerun()

# --- PAGE: INPUT ---
# --- PAGE: INPUT ---
elif st.session_state.page == 'input':
    if not st.session_state.current_topic: 
        st.session_state.current_topic = get_topic()

    st.markdown(f"<span style='background-color: #000; color: #fff; padding: 2px 8px; border-radius: 3px; font-size: 12px;'>{st.session_state.drill_type.upper()} MODE</span>", unsafe_allow_html=True)
    
    if st.button("New Topic 🎲"):
        st.session_state.current_topic = get_topic()
        st.rerun()

    st.subheader(f"Topic: {st.session_state.current_topic}")
    
    # Инструкции в зависимости от выбранного режима
    instructions = {
        "Introduction": "Write only the introduction. Paraphrase the topic and clearly state the problem.",
        "Solutions": "Write the body paragraphs. Propose 2 solutions with examples and consequences.",
        "Conclusion": "Write only the conclusion. Summarize your points and give a final thought.",
        "Task 2 Essay": "Write a full essay (250-300 words).",
        "Task 1 Email": "Write a formal/neutral email (120-150 words) based on the announcement."
    }
    st.info(instructions.get(st.session_state.drill_type, ""))

    user_text = st.text_area("Type your text here:", height=350, placeholder="Start writing...")
    word_count = len(user_text.split())
    st.write(f"**Word count: {word_count}**")
    
    col_back, col_sub = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ Back"): 
            st.session_state.page = 'home'
            st.session_state.current_topic = ""
            st.rerun()
            
    with col_sub:
        if st.button("SUBMIT FOR EVALUATION"):
            if word_count < 10:
                st.error("Please write a longer text before submitting.")
            else:
                with st.spinner("The examiner is checking your work..."):
                    prompt = f"""
                    You are a professional English examiner. Analyze this {st.session_state.drill_type}.
                    Topic: {st.session_state.current_topic}
                    
                    Evaluate the text strictly based on these 5 criteria (0-5 points each):
                    1. Task Achievement (Sagatavotība)
                    2. Coherence and Cohesion (Mijiedarbība)
                    3. Lexical Resource (Bagātība)
                    4. Grammatical Range and Accuracy (Gramatika)
                    5. Fluency (Plūdums)

                    Format your response EXACTLY like this:
                    C1: [score]
                    C2: [score]
                    C3: [score]
                    C4: [score]
                    C5: [score]
                    TOTAL: [sum of scores]
                    FEEDBACK: [Short advice for improvement]
                    TEXT: [Rewritten text. Use **bold (correction)** for every mistake found. Example: I **goed (went)** to school.]

                    Student's text: {user_text}
                    """
                    
                    try:
                        response_obj = model.generate_content(prompt)
                        resp = response_obj.text
                        
                        def get_val(label, text):
                            match = re.search(rf'{label}:\s*(\d+)', text)
                            return match.group(1) if match else "0"

                        # Сохраняем все данные для страницы результатов
                        st.session_state.results_data = {
                            'c1': get_val('C1', resp),
                            'c2': get_val('C2', resp),
                            'c3': get_val('C3', resp),
                            'c4': get_val('C4', resp),
                            'c5': get_val('C5', resp),
                            'total': get_val('TOTAL', resp),
                            'feedback': resp.split("FEEDBACK:")[1].split("TEXT:")[0].strip() if "FEEDBACK:" in resp else "Good effort!",
                            'text': resp.split("TEXT:")[1].strip() if "TEXT:" in resp else user_text
                        }
                        st.session_state.page = 'results'
                        st.rerun()
                    except Exception as e:
                        st.error(f"API Error: {e}")
        
                

# --- PAGE: RESULTS ---
elif st.session_state.page == 'results':
    data = st.session_state.results_data
    
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border: 2px solid #000; border-radius: 10px; margin-bottom: 20px;">
            <p style="margin:0; font-weight: bold; color: #000;">TOTAL SCORE</p>
            <h2 style="color: #000; font-size: 36px; margin: 0;">{data.get('total', 0)} / 25</h2>
        </div>
    """, unsafe_allow_html=True)

    # Те самые 5 окошек (критериев)
    st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 20px;">
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white;">
                <small style="color: #666;">Sagatavotība</small><br><b style="font-size: 20px; color: #000;">{data.get('c1')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white;">
                <small style="color: #666;">Mijiedarbība</small><br><b style="font-size: 20px; color: #000;">{data.get('c2')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white;">
                <small style="color: #666;">Bagātība</small><br><b style="font-size: 20px; color: #000;">{data.get('c3')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white;">
                <small style="color: #666;">Gramatika</small><br><b style="font-size: 20px; color: #000;">{data.get('c4')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white;">
                <small style="color: #666;">Plūdums</small><br><b style="font-size: 20px; color: #000;">{data.get('c5')}</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if data.get('feedback'):
        st.subheader("💡 Examiner's Advice")
        st.info(data['feedback'])

    st.subheader("📝 Revised Text (Corrections)")
    st.markdown(data.get('text', ''))
    
    st.write("---")
    if st.button("⬅️ TRY ANOTHER EXERCISE"):
        st.session_state.page = 'home'
        st.session_state.current_topic = ""
        st.rerun()
