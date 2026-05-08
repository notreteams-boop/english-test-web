import streamlit as st
import google.generativeai as genai
import re

# --- 1. API SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API Error: {e}")
    st.stop()

# --- 2. СТИЛИЗАЦИЯ (Экзаменационный стандарт) ---
st.markdown("""
<style>
    .exam-root { font-family: 'Times New Roman', serif !important; color: #000 !important; }
    .announcement-box { border: 1px solid #000; padding: 10px; margin: 10px 0; text-align: center; }
    .score-table { border: 2px solid #000; padding: 15px; background-color: #f0f0f0; margin-bottom: 20px; }
    .correction-output { border: 1px solid #000; padding: 15px; background-color: #fff; color: #000; line-height: 1.6; }
    div.stButton > button { border: 1px solid #000 !important; border-radius: 0px !important; background-color: #fff !important; color: #000 !important; font-weight: bold; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'task_text' not in st.session_state: st.session_state.task_text = None
if 'eval_res' not in st.session_state: st.session_state.eval_res = None

# --- 4. ИНТЕРФЕЙС ---
st.markdown("<div class='exam-root'>", unsafe_allow_html=True)
st.write("**Task 1: E-mail (9 points)**")

if st.button("GENERATE NEW TASK"):
    prompt = "Create a short Task 1 E-mail prompt: ANNOUNCEMENT: [3 lines max] INSTRUCTIONS: [Situation + 3 bullets]"
    st.session_state.task_text = model.generate_content(prompt).text
    st.session_state.eval_res = None
    st.rerun()

if st.session_state.task_text:
    t_content = st.session_state.task_text
    ann = t_content.split("ANNOUNCEMENT:")[1].split("INSTRUCTIONS:")[0].strip() if "ANNOUNCEMENT:" in t_content else ""
    ins = t_content.split("INSTRUCTIONS:")[1].strip() if "INSTRUCTIONS:" in t_content else t_content
    
    if ann: st.markdown(f"<div class='announcement-box'>{ann}</div>", unsafe_allow_html=True)
    st.write(ins)
    st.write("**Write 120–150 words.**")

    user_input = st.text_area("Input", height=250, label_visibility="collapsed")
    
    # Счётчик слов
    word_count = len(user_input.split())
    st.markdown(f"<p style='text-align:right; font-size:0.8em;'>Word count: <b>{word_count}</b></p>", unsafe_allow_html=True)

    if st.button("CHECK E-MAIL"):
        if word_count < 20:
            st.error("Text too short.")
        else:
            # СТРОГИЙ ПРОМПТ (Чтобы не завышал)
            strict_prompt = f"""
            Act as a CRUEL and STRICT examiner. Be mean. A score of 3 is only for PERFECTION. 
            If there is ONE mistake, the score is 2. If many, the score is 1.
            
            Grade this text (Max 9 pts): {user_input}
            
            FORMAT:
            TOTAL: [X]/9
            Saturs: [X]/3 | Organizācija: [X]/3 | Valoda: [X]/3
            CORRECTED_TEXT: [Full text, errors in **bold**]
            
            NO FEEDBACK. NO COMPLIMENTS. Just numbers and corrected text.
            """
            st.session_state.eval_res = model.generate_content(strict_prompt).text
            st.rerun()

# --- 5. РЕЗУЛЬТАТЫ ---
if st.session_state.eval_res:
    res = st.session_state.eval_res
    try:
        score_h = re.search(r"TOTAL: (.*?)\n", res).group(1)
        scores = re.search(r"(Saturs: .*?)\n", res).group(1)
        corr_txt = res.split("CORRECTED_TEXT:")[1].strip()

        st.markdown(f"<div class='score-table'><h2 style='text-align:center;margin:0;'>{score_h}</h2><p style='text-align:center;'>{scores}</p></div>", unsafe_allow_html=True)
        st.write("**Corrected Version (Corrections in bold):**")
        st.markdown("<div class='correction-output'>", unsafe_allow_html=True)
        st.markdown(corr_txt)
        st.markdown("</div>", unsafe_allow_html=True)
    except:
        st.write(res)

st.markdown("</div>", unsafe_allow_html=True)
