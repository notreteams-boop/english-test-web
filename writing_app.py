import streamlit as st
import google.generativeai as genai
import random
import re

# --- 1. CONFIG & STYLES (Исправлено для стабильности фона) ---
# st.set_page_config удален, так как он теперь в главном файле app.py

st.markdown("""
<style>
    /* Принудительный белый фон для раздела Writing */
    .stApp { background-color: #ffffff !important; }
    
    /* Принудительный черный текст */
    h1, h2, h3, p, li, span, label, div, .stMarkdown { 
        color: #000000 !important; 
        font-family: 'Times New Roman', serif !important; 
    }
    
    .overall-box { background-color: #f8f9fa; padding: 20px; text-align: center; border: 2px solid #000; border-radius: 10px; margin-bottom: 20px; }
    .overall-box h2 { color: #000 !important; font-size: 36px; margin: 0; }
    .announcement-box { border: 2px solid #000; padding: 15px; margin: 15px 0; background-color: #fff; }
    
    /* Кнопки в стиле экзамена */
    div.stButton > button { 
        background-color: #fff !important; 
        color: #000 !important; 
        border: 1px solid #000 !important; 
        font-weight: bold; 
        width: 100%; 
        transition: 0.3s; 
    }
    div.stButton > button:hover { 
        background-color: #000 !important; 
        color: #fff !important; 
    }
    .drill-label { background-color: #000; color: #fff; padding: 2px 8px; border-radius: 3px; font-size: 12px; margin-bottom: 10px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- 2. API SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro']
    
    selected_model = next((target for target in target_models if target in available_models), available_models[0])
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# --- 3. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'mode' not in st.session_state: st.session_state.mode = None 
if 'drill_type' not in st.session_state: st.session_state.drill_type = None
if 'current_topic' not in st.session_state: st.session_state.current_topic = ""
if 'results_data' not in st.session_state: st.session_state.results_data = {}

# --- PAGE: HOME ---
if st.session_state.page == 'home':
    st.title("✍️ Writing Section")
    
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
elif st.session_state.page == 'input':
    if not st.session_state.current_topic:
        from topics import TASKS_2
        st.session_state.current_topic = random.choice(TASKS_2)

    topic = st.session_state.current_topic

    st.markdown(f"""
<div style="font-family: 'Times New Roman', serif; color: #000;">
<p style="margin-bottom:0;"><b>Task 2</b></p>
<p style="margin-bottom:0;"><i>Essay (16 points)</i></p>
<p><b>You should spend about 55 minutes on this task.</b></p>
<p>You are participating in an international youth newspaper essay competition on <b>{topic['title']}</b>. 
Read the information provided and write an essay in which you:</p>
<ul style="margin-top: 10px; margin-bottom: 10px;">
<li>formulate the problem raised in the sources and explain why it should be addressed;</li>
<li>propose and support at least two solutions to the problem which address the causes;</li>
<li>come to a conclusion.</li>
</ul>
<p><b>Write between 250–300 words.</b></p>
<div style="margin-top:20px;">
<p style="margin-bottom:5px;"><b>Source 1:</b></p>
<div style="border-left: 3px solid #000; padding-left: 15px; font-style: italic; margin-bottom: 20px;">{topic['source1']}</div>
<p style="margin-bottom:5px;"><b>Source 2:</b></p>
<div style="border-left: 3px solid #000; padding-left: 15px; font-style: italic; margin-bottom: 20px;">{topic['source2']}</div>
</div>
</div>
""", unsafe_allow_html=True)

    user_text = st.text_area("Write your essay here:", height=400, placeholder="Start typing...")
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
            if word_count < 100:
                st.error("Text too short! Minimum 100 words required.")
            else:
                with st.spinner("Examiner is evaluating..."):
                    prompt = f"""
                    Analyze this essay:
                    Topic: {topic['title']}
                    Sources: {topic['source1']} | {topic['source2']}
                    
                    Structure:
                    C1: [score/5] - Content
                    C2: [score/5] - Organization
                    C3: [score/5] - Vocabulary
                    C4: [score/5] - Grammar
                    C5: [score/5] - Style
                    TOTAL: [sum/25]
                    FEEDBACK: [Brief advice]
                    TEXT: [Corrected version with **bold** fixes]
                    
                    Student Text: {user_text}
                    """
                    try:
                        response_obj = model.generate_content(prompt)
                        resp = response_obj.text
                        
                        def get_val(label, text):
                            match = re.search(rf'{label}:\s*(\d+)', text)
                            return match.group(1) if match else "0"

                        st.session_state.results_data = {
                            'c1': get_val('C1', resp),
                            'c2': get_val('C2', resp),
                            'c3': get_val('C3', resp),
                            'c4': get_val('C4', resp),
                            'c5': get_val('C5', resp),
                            'total': get_val('TOTAL', resp),
                            'feedback': resp.split("FEEDBACK:")[1].split("TEXT:")[0].strip() if "FEEDBACK:" in resp else "Great job!",
                            'text': resp.split("TEXT:")[1].strip() if "TEXT:" in resp else user_text
                        }
                        st.session_state.page = 'results'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error during evaluation: {e}")

# --- PAGE: RESULTS ---
elif st.session_state.page == 'results':
    data = st.session_state.results_data
    
    st.markdown(f"""
        <div class="overall-box">
            <p style="margin:0; font-weight: bold; color: #000;">TOTAL SCORE</p>
            <h2>{data.get('total', 0)} / 25</h2>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 10px; margin-bottom: 20px;">
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white; color: black;">
                <small>Content</small><br><b>{data.get('c1')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white; color: black;">
                <small>Org.</small><br><b>{data.get('c2')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white; color: black;">
                <small>Vocab.</small><br><b>{data.get('c3')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white; color: black;">
                <small>Grammar</small><br><b>{data.get('c4')}</b>
            </div>
            <div style="border: 1px solid #000; padding: 10px; text-align: center; border-radius: 5px; background: white; color: black;">
                <small>Style</small><br><b>{data.get('c5')}</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if data.get('feedback'):
        st.subheader("💡 Examiner's Advice")
        st.info(data['feedback'])

    st.subheader("📝 Revised Text")
    st.markdown(data.get('text', ''))
    
    if st.button("⬅️ TRY ANOTHER EXERCISE"):
        st.session_state.page = 'home'
        st.session_state.current_topic = ""
        st.rerun()
