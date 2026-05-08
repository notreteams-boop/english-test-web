import streamlit as st
import google.generativeai as genai
import json
import random
import re

# ─────────────────────────────────────────
# PAGE CONFIG  (call only if this is the entry point;
# when used as a sub-page inside app.py the parent already called it)
# ─────────────────────────────────────────
try:
    st.set_page_config(page_title="Writing Task 2 – Essay", layout="wide")
except Exception:
    pass  # already set by parent

# ─────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:wght@400;500;600&display=swap');

/* ── root ── */
:root {
    --bg:        #f5f3ef;
    --card:      #ffffff;
    --border:    #d6d0c4;
    --accent:    #1a3a5c;
    --accent2:   #c0392b;
    --text:      #1c1c1c;
    --muted:     #6b6560;
    --tag-bg:    #eaf0f8;
    --good:      #1a7a4a;
    --warn:      #b35900;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

/* hide default streamlit header */
[data-testid="stHeader"] { display: none !important; }

/* ── custom header ── */
.w2-header {
    background: var(--accent);
    color: #fff;
    padding: 18px 32px;
    border-radius: 10px 10px 0 0;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 0;
}
.w2-header .badge {
    background: var(--accent2);
    color: #fff;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
}
.w2-header h1 {
    font-family: 'Crimson Pro', serif;
    font-size: 24px;
    margin: 0;
    font-weight: 700;
    color: #fff;
}
.w2-header .meta {
    margin-left: auto;
    font-size: 13px;
    opacity: 0.75;
    text-align: right;
}

/* ── task card ── */
.task-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 28px 32px 24px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.task-title {
    font-family: 'Crimson Pro', serif;
    font-size: 19px;
    font-weight: 700;
    margin-bottom: 6px;
}
.task-body {
    font-size: 14.5px;
    line-height: 1.65;
    margin-bottom: 12px;
}
.task-bullets {
    font-size: 14px;
    line-height: 1.8;
    padding-left: 18px;
    margin-bottom: 12px;
}
.task-note {
    font-family: 'Crimson Pro', serif;
    font-style: italic;
    font-size: 14.5px;
    font-weight: 600;
    margin: 10px 0 6px;
    color: var(--accent);
}

/* ── source boxes ── */
.source-block {
    background: #f9f8f5;
    border-left: 4px solid var(--accent);
    border-radius: 0 6px 6px 0;
    padding: 14px 18px 10px;
    margin: 14px 0;
}
.source-label {
    font-weight: 700;
    font-size: 13.5px;
    letter-spacing: .3px;
    margin-bottom: 6px;
    color: var(--accent);
}
.source-text {
    font-size: 14px;
    line-height: 1.65;
}
.source-credit {
    text-align: right;
    font-family: 'Crimson Pro', serif;
    font-style: italic;
    font-size: 13px;
    color: var(--muted);
    margin-top: 8px;
}

/* ── score overlay ── */
.score-overlay {
    background: var(--card);
    border: 2px solid var(--accent);
    border-radius: 10px;
    padding: 28px 32px;
    margin-bottom: 28px;
    box-shadow: 0 4px 20px rgba(26,58,92,0.10);
}
.score-total {
    font-family: 'Crimson Pro', serif;
    font-size: 42px;
    font-weight: 700;
    color: var(--accent);
    text-align: center;
    margin-bottom: 4px;
}
.score-sub {
    text-align: center;
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 22px;
}
.criteria-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}
.criteria-item {
    background: var(--tag-bg);
    border-radius: 8px;
    padding: 12px 16px;
}
.criteria-name {
    font-size: 12px;
    font-weight: 600;
    color: var(--accent);
    letter-spacing: .3px;
    margin-bottom: 6px;
    text-transform: uppercase;
}
.criteria-score {
    font-family: 'Crimson Pro', serif;
    font-size: 26px;
    font-weight: 700;
    color: var(--text);
}
.criteria-score span {
    font-size: 14px;
    color: var(--muted);
    font-family: 'DM Sans', sans-serif;
}
.bar-track {
    background: #dde4ed;
    border-radius: 4px;
    height: 6px;
    margin-top: 6px;
}
.bar-fill {
    height: 6px;
    border-radius: 4px;
    background: var(--accent);
}

/* corrected essay */
.corrected-box {
    background: #fffdf7;
    border: 1px solid #e8e0cc;
    border-radius: 8px;
    padding: 20px 24px;
    font-size: 14.5px;
    line-height: 1.75;
    margin-top: 16px;
}
.corrected-box .err {
    background: #ffeaea;
    color: #a00;
    text-decoration: underline wavy #c0392b;
    border-radius: 2px;
    padding: 0 2px;
}
.corrected-box .fix {
    background: #eafaf1;
    color: #145a32;
    border-radius: 2px;
    padding: 0 2px;
    font-weight: 500;
}

/* buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 28px !important;
    cursor: pointer !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .85 !important; }

.stTextArea textarea {
    font-family: 'Crimson Pro', serif !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    background: var(--card) !important;
    padding: 14px !important;
}

.word-counter {
    font-size: 12.5px;
    color: var(--muted);
    text-align: right;
    margin-top: -12px;
    margin-bottom: 16px;
}
.word-counter.ok   { color: var(--good); }
.word-counter.warn { color: var(--warn); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# GEMINI SETUP  (reuse key from st.secrets)
# ─────────────────────────────────────────
@st.cache_resource
def get_model():
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    available = [m.name for m in genai.list_models()
                 if 'generateContent' in m.supported_generation_methods]
    targets = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest',
               'models/gemini-pro']
    chosen = next((t for t in targets if t in available), available[0])
    return genai.GenerativeModel(chosen)

model = get_model()


# ─────────────────────────────────────────
# TOPIC POOL (AI picks one randomly, but we
# also keep a fallback list so the page
# doesn't break if the API is slow)
# ─────────────────────────────────────────
FALLBACK_TOPICS = [
    "students' screen time and digital wellbeing",
    "the impact of social media on teenage mental health",
    "gap year benefits and drawbacks for students",
    "why students struggle with healthy eating habits",
    "balancing academics and extracurricular activities",
]

SYSTEM_PROMPT_GENERATE = """You are an English language exam content creator.
Generate a Task 2 Essay prompt for a youth newspaper competition.
Return ONLY a valid JSON object with these exact keys:
{
  "topic_title": "short topic phrase (5-8 words)",
  "intro": "2-sentence task introduction mentioning the youth newspaper essay competition and the topic",
  "source1_text": "3-4 sentences about the problem/background from an educational perspective",
  "source1_credit": "www.[realistic-edu-domain].edu or org",
  "source2_bullets": ["bullet 1 cause with stat or detail", "bullet 2 cause", "bullet 3 cause", "bullet 4 cause"],
  "source2_credit": "www.[realistic-domain].com"
}
Do NOT include any markdown, code fences, or extra text. Return raw JSON only."""


def generate_topic() -> dict:
    """Call Gemini to produce a fresh essay task."""
    seed_topic = random.choice(FALLBACK_TOPICS)
    prompt = f"{SYSTEM_PROMPT_GENERATE}\nThe topic should be about: {seed_topic}"
    try:
        resp = model.generate_content(prompt)
        raw = resp.text.strip()
        # strip possible markdown fences
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'```$', '', raw).strip()
        return json.loads(raw)
    except Exception as e:
        # graceful fallback
        return {
            "topic_title": seed_topic,
            "intro": (
                f"You are participating in an international youth newspaper essay competition "
                f"on {seed_topic}. Read the information provided and write an essay."
            ),
            "source1_text": (
                "This issue is widely discussed among educators and researchers. "
                "Many students face challenges related to this topic in their daily lives. "
                "Addressing it early can significantly improve student wellbeing and academic outcomes. "
                "However, solutions remain underexplored in school curricula."
            ),
            "source1_credit": "www.educationresearch.org",
            "source2_bullets": [
                "lack of awareness — many students are unaware of the long-term consequences",
                "peer pressure — social environments reinforce negative habits",
                "poor institutional support — schools rarely address this systematically",
                "digital distractions — technology exacerbates the problem for today's students",
            ],
            "source2_credit": "www.youthwellbeing.com",
        }


RUBRIC_PROMPT = """You are a strict English language examiner using the following 4-criterion rubric (0–4 pts each, total 16):

1. CONTENT & TASK COMPLETION (Saturs un uzdevuma izpilde):
   4 = Fully addresses all task requirements; formulates problem, supports opinion with arguments and examples.
   3 = Mostly addresses task; summarises sources, gives opinion with some arguments/examples.
   2 = Partially addresses task; retells content, adds personal experience.
   1 = General statements loosely related to topic.
   0 = Does not meet task requirements or under 100 words.

2. ORGANISATION & TEXT STRUCTURE (Organizācija un tekstveide):
   4 = Logically structured; connectives and paragraphs fully match organisation requirements.
   3 = Structured and cohesive; connectives mostly match.
   2 = Connectives and paragraphs partially match organisation.
   1 = Partially cohesive; flow sometimes unclear.
   0 = Does not meet task requirements or under 100 words.

3. LANGUAGE VARIETY (Valodas līdzekļu daudzveidība):
   4 = Rich vocabulary; predominantly complex grammatical structures.
   3 = Sufficient vocabulary; complex structures used frequently.
   2 = Limited vocabulary for simple expression; simple structures, often repeated.
   1 = Very limited; only basic structures and short phrases.
   0 = Does not meet task requirements or under 100 words.

4. LANGUAGE ACCURACY (Valodas lietojuma pareizība un precizitāte):
   4 = High accuracy; isolated non-systematic errors in complex structures only.
   3 = Mostly correct; minor errors do not impede understanding.
   2 = Systematic elementary errors; sometimes impedes understanding.
   1 = Mostly erroneous; barely comprehensible.
   0 = Does not meet task requirements or under 100 words.

TASK TOPIC: {topic}

STUDENT ESSAY:
{essay}

Return ONLY a valid JSON object with these exact keys:
{{
  "content_score": <0-4>,
  "content_comment": "<one short sentence>",
  "organisation_score": <0-4>,
  "organisation_comment": "<one short sentence>",
  "variety_score": <0-4>,
  "variety_comment": "<one short sentence>",
  "accuracy_score": <0-4>,
  "accuracy_comment": "<one short sentence>",
  "corrected_essay": "<full essay text; wrap each error like: ~~wrong~~(correction) — use this exact format for every mistake you find>"
}}
Do NOT include markdown, code fences, or any extra text. Return raw JSON only."""


def check_essay(topic_title: str, essay_text: str) -> dict:
    prompt = RUBRIC_PROMPT.format(topic=topic_title, essay=essay_text)
    try:
        resp = model.generate_content(prompt)
        raw = resp.text.strip()
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'```$', '', raw).strip()
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}


def render_corrected(text: str) -> str:
    """Convert ~~wrong~~(fix) markers to HTML spans."""
    # pattern: ~~wrong~~(fix)
    def replacer(m):
        wrong = m.group(1)
        fix   = m.group(2)
        return (f'<span class="err">{wrong}</span>'
                f' <span class="fix">→ {fix}</span>')
    out = re.sub(r'~~(.+?)~~\((.+?)\)', replacer, text)
    # also handle plain ~~wrong~~ with no correction
    out = re.sub(r'~~(.+?)~~', lambda m: f'<span class="err">{m.group(1)}</span>', out)
    return out.replace('\n', '<br>')


# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
if 'task_data'    not in st.session_state: st.session_state.task_data    = None
if 'essay_text'   not in st.session_state: st.session_state.essay_text   = ""
if 'result'       not in st.session_state: st.session_state.result       = None
if 'generating'   not in st.session_state: st.session_state.generating   = False


# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="w2-header">
  <div class="badge">Task 2</div>
  <h1>Essay Practice</h1>
  <div class="meta">16 points &nbsp;·&nbsp; ~55 minutes<br>250–300 words</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# GENERATE / REGENERATE BUTTON
# ─────────────────────────────────────────
col_btn, col_info = st.columns([1, 4])
with col_btn:
    gen_label = "🎲 New Topic" if st.session_state.task_data else "🎲 Generate Topic"
    if st.button(gen_label, key="gen_btn"):
        st.session_state.result = None
        st.session_state.essay_text = ""
        with st.spinner("Generating topic…"):
            st.session_state.task_data = generate_topic()
with col_info:
    if not st.session_state.task_data:
        st.info("Click **Generate Topic** to receive a random essay task with sources.")


# ─────────────────────────────────────────
# TASK CARD
# ─────────────────────────────────────────
if st.session_state.task_data:
    d = st.session_state.task_data
    bullets_html = "".join(f"<li>{b}</li>" for b in d.get("source2_bullets", []))

    st.markdown(f"""
<div class="task-card">
  <div class="task-title">Essay &nbsp;<em style="font-weight:400;font-size:16px">(16 points)</em></div>
  <div class="task-note">You should spend about 55 minutes on this task.</div>
  <div class="task-body">{d['intro']}</div>
  <ul class="task-bullets">
    <li>formulate the problem raised in the sources and explain why it should be addressed;</li>
    <li>propose and support <strong>at least two solutions</strong> to the problem which address the causes;</li>
    <li>come to a conclusion.</li>
  </ul>
  <div class="task-note">Write between 250–300 words. Texts shorter than 100 words will not be evaluated.</div>
  <div class="task-note">Do not forget to use "quotation marks" if you decide to quote a phrase from the sources.</div>

  <div class="source-block">
    <div class="source-label">Source 1:</div>
    <div class="source-text">{d['source1_text']}</div>
    <div class="source-credit">Adapted from {d['source1_credit']}</div>
  </div>

  <div class="source-block">
    <div class="source-label">Source 2:</div>
    <div class="source-text">There are several reasons students struggle with this, including:</div>
    <ul class="source-text" style="margin-top:6px">{bullets_html}</ul>
    <div class="source-credit">Adapted from {d['source2_credit']}</div>
  </div>
</div>
""", unsafe_allow_html=True)


    # ─────────────────────────────────────
    # SCORE RESULT (shown ABOVE text area)
    # ─────────────────────────────────────
    if st.session_state.result and 'error' not in st.session_state.result:
        r = st.session_state.result
        total = (r.get('content_score', 0) + r.get('organisation_score', 0)
                 + r.get('variety_score', 0) + r.get('accuracy_score', 0))

        criteria = [
            ("Content & Task", "content",      r.get('content_score', 0),      r.get('content_comment', '')),
            ("Organisation",   "organisation", r.get('organisation_score', 0), r.get('organisation_comment', '')),
            ("Lang. Variety",  "variety",       r.get('variety_score', 0),      r.get('variety_comment', '')),
            ("Accuracy",       "accuracy",      r.get('accuracy_score', 0),     r.get('accuracy_comment', '')),
        ]

        criteria_html = ""
        for name, _, score, comment in criteria:
            pct = int(score / 4 * 100)
            criteria_html += f"""
<div class="criteria-item">
  <div class="criteria-name">{name}</div>
  <div class="criteria-score">{score}<span> / 4</span></div>
  <div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div></div>
  <div style="font-size:12px;color:var(--muted);margin-top:5px">{comment}</div>
</div>"""

        st.markdown(f"""
<div class="score-overlay">
  <div class="score-total">{total} <span style="font-size:22px;color:var(--muted)">/ 16</span></div>
  <div class="score-sub">Total Score</div>
  <div class="criteria-grid">{criteria_html}</div>

  <div style="font-weight:600;font-size:14px;margin-bottom:8px;color:var(--accent)">
    ✏️ Your essay with corrections:
  </div>
  <div class="corrected-box">{render_corrected(r.get('corrected_essay',''))}</div>
</div>
""", unsafe_allow_html=True)

    elif st.session_state.result and 'error' in st.session_state.result:
        st.error(f"Grading error: {st.session_state.result['error']}")


    # ─────────────────────────────────────
    # ESSAY TEXT AREA
    # ─────────────────────────────────────
    st.markdown("#### ✍️ Write your essay below")

    essay = st.text_area(
        label="essay_input",
        value=st.session_state.essay_text,
        height=320,
        placeholder="Start writing your essay here…",
        label_visibility="collapsed",
        key="essay_area",
    )
    st.session_state.essay_text = essay

    # live word counter
    wcount = len(essay.split()) if essay.strip() else 0
    if wcount == 0:
        wclass, wlabel = "", f"{wcount} words"
    elif wcount < 100:
        wclass, wlabel = "warn", f"⚠️ {wcount} words — too short (min 100)"
    elif wcount < 250:
        wclass, wlabel = "warn", f"⚠️ {wcount} words — aim for 250–300"
    elif wcount <= 300:
        wclass, wlabel = "ok", f"✓ {wcount} words"
    else:
        wclass, wlabel = "warn", f"⚠️ {wcount} words — over 300!"
    st.markdown(f'<div class="word-counter {wclass}">{wlabel}</div>', unsafe_allow_html=True)


    # ─────────────────────────────────────
    # CHECK BUTTON
    # ─────────────────────────────────────
    col_check, _ = st.columns([1, 3])
    with col_check:
        if st.button("✅ Check Essay", key="check_btn"):
            if wcount < 50:
                st.warning("Please write at least a few sentences before checking.")
            else:
                with st.spinner("Grading your essay…"):
                    st.session_state.result = check_essay(
                        d.get('topic_title', 'essay topic'),
                        essay
                    )
                st.rerun()
