import streamlit as st
import google.generativeai as genai
import json
import random
import re

# ─────────────────────────────────────────────
# TOPIC POOL  (AI fills in the specific details)
# ─────────────────────────────────────────────
TOPIC_POOL = [
    {"org": "City Arts Centre",        "theme": "art gallery / creative workshops",        "contact": "Ms Longman",   "email": "volunteer@cityartcentre.ie"},
    {"org": "Green Valley Animal Shelter", "theme": "animal care / dog walking / vet support", "contact": "Mr O'Brien",  "email": "volunteers@greenvalley.ie"},
    {"org": "Dublin Science Museum",   "theme": "science demonstrations / school tours",   "contact": "Ms Carter",    "email": "volunteer@sciencemuseum.ie"},
    {"org": "Community Sports Centre", "theme": "youth coaching / event setup / reception", "contact": "Mr Walsh",     "email": "help@communitysports.ie"},
    {"org": "City Public Library",     "theme": "children's reading / shelf management / IT help", "contact": "Ms Brennan", "email": "volunteer@citylibrary.ie"},
    {"org": "Riverside Food Bank",     "theme": "food sorting / delivery / client support", "contact": "Mr Doyle",    "email": "join@riversideFB.ie"},
    {"org": "Heritage History Museum", "theme": "tour guiding / archive cataloguing / gift shop", "contact": "Ms Flynn", "email": "volunteer@heritagemuseum.ie"},
    {"org": "Greenpark Environmental Trust", "theme": "park maintenance / wildlife surveys / education", "contact": "Mr Kelly", "email": "eco@greenpark.ie"},
    {"org": "Youth Theatre Dublin",    "theme": "stage crew / costume design / front-of-house", "contact": "Ms Murphy", "email": "volunteer@youththeatre.ie"},
    {"org": "City Hospital Wellbeing Unit", "theme": "reading to patients / activity sessions / admin", "contact": "Mr Byrne", "email": "volunteer@cityhospital.ie"},
]


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def get_model():
    """Return a configured Gemini model (cached in session state)."""
    if "gemini_model" not in st.session_state:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        available = [m.name for m in genai.list_models()
                     if "generateContent" in m.supported_generation_methods]
        preferred = [
            "models/gemini-1.5-flash",
            "models/gemini-1.5-flash-latest",
            "models/gemini-pro",
        ]
        chosen = next((m for m in preferred if m in available), available[0])
        st.session_state.gemini_model = genai.GenerativeModel(chosen)
    return st.session_state.gemini_model


def count_words(text: str) -> int:
    return len(text.split()) if text.strip() else 0


def word_count_badge(n: int) -> str:
    if n >= 120:
        colour = "green"
    elif n >= 50:
        colour = "orange"
    else:
        colour = "red"
    return f":{colour}[**{n} words**]"


def highlight_errors(text: str) -> str:
    """Convert [ERROR: old → new] markers to styled HTML spans."""
    pattern = r"\[ERROR:\s*(.+?)\s*→\s*(.+?)\]"
    result = re.sub(
        pattern,
        lambda m: (
            f'<span style="background:#ffe4e4;color:#c0392b;'
            f'text-decoration:line-through;border-radius:3px;padding:0 3px">'
            f'{m.group(1)}</span>'
            f'<span style="background:#e4ffe4;color:#1a7a2e;font-weight:600;'
            f'border-radius:3px;padding:0 3px;margin-left:2px">'
            f'{m.group(2)}</span>'
        ),
        text,
    )
    return result.replace("\n", "<br>")


# ─────────────────────────────────────────────
# ANNOUNCEMENT GENERATOR
# ─────────────────────────────────────────────
ANNOUNCEMENT_PROMPT = """Generate a volunteer recruitment announcement for: {org} ({theme}).

Rules:
- Title line: LOOKING FOR VOLUNTEERS
- Second line: {org}
- Short opening paragraph (1-2 sentences) about joining
- Exactly 3 bullet-point positions with concrete shift info in brackets
- Benefits paragraph: training, travel allowance, pocket money, free entry
- Positions available from July 1, 2025 to August 31, 2025
- Contact: {contact} at {email}

Return ONLY the plain announcement text — no markdown headers, no asterisks."""

# ─────────────────────────────────────────────
# CHECKER PROMPT
# ─────────────────────────────────────────────
CHECKER_PROMPT = """You are a strict but fair English exam grader.

TASK the student was given:
Write an e-mail to apply for a volunteer position. Cover:
1) Which role they want and their availability
2) Their relevant experience/skills and how they contribute
3) Ask about terms and conditions of work

STUDENT EMAIL:
{email_text}

Grade using THREE criteria, each 0–3 points (total max 9):

CONTENT & TASK COMPLETION (0-3)
0 – missing / off-topic
1 – partially meets task, some repetition or omission
2 – covers all points but lacks detail somewhere
3 – fully covers all points with elaboration

ORGANIZATION & TEXT TYPE (0-3)
0 – not an email format, or <50 words
1 – some sentences linked, basic email elements
2 – mostly correct email structure and coherence
3 – fully correct email format, smooth cohesion

LANGUAGE DIVERSITY & ACCURACY (0-3)
0 – incomprehensible or <50 words
1 – very limited vocabulary, systematic errors block understanding
2 – adequate vocabulary, mostly clear, errors don't block understanding
3 – varied vocabulary, mostly accurate, minor errors only

Also return the student's email with every error marked as:
[ERROR: wrong_word → correction]
Fix only real grammar/spelling/vocabulary mistakes. Do NOT rewrite style.

Return ONLY valid JSON — no markdown fences, no extra keys:
{{
  "content_score": <int 0-3>,
  "content_feedback": "<one sentence in English>",
  "organization_score": <int 0-3>,
  "organization_feedback": "<one sentence in English>",
  "language_score": <int 0-3>,
  "language_feedback": "<one sentence in English>",
  "corrected_text": "<full email with [ERROR: x → y] markers>"
}}"""


# ─────────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────────
def writing1_page():
    # ── CSS ──────────────────────────────────
    st.markdown("""
    <style>
    .task-header {
        font-size: 0.85rem; color: #555; margin-bottom: 0.5rem;
    }
    .announcement-box {
        border: 1px solid #bbb; border-radius: 6px;
        padding: 1rem 1.25rem; background: #fafafa;
        font-size: 0.92rem; line-height: 1.6;
        margin-bottom: 1rem;
    }
    .announcement-title {
        font-weight: 700; text-align: center; font-size: 1rem; margin-bottom: 0.2rem;
    }
    .score-panel {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: white; border-radius: 10px; padding: 1.5rem;
        margin: 1rem 0; text-align: center;
    }
    .score-total {font-size: 2.5rem; font-weight: 800; color: #f0c040;}
    .score-label {font-size: 0.9rem; opacity: 0.75; margin-top: -0.3rem;}
    .criteria-card {
        background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
        padding: 0.75rem 1rem; text-align: center;
    }
    .criteria-score {font-size: 1.5rem; font-weight: 700;}
    .criteria-name {font-size: 0.75rem; color: #666; margin-top: 2px;}
    .criteria-fb {font-size: 0.8rem; color: #444; margin-top: 6px; font-style: italic;}
    .corrected-box {
        border: 1px solid #ddd; border-radius: 8px; padding: 1rem 1.25rem;
        background: #fff; line-height: 1.9; font-size: 0.93rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Session state init ────────────────────
    for key, val in [
        ("w1_topic", None),
        ("w1_announcement", None),
        ("w1_result", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = val

    # ── Header row ───────────────────────────
    col_title, col_btn = st.columns([5, 1])
    with col_title:
        st.markdown("## ✉️ Writing — Task 1: E-mail")
        st.markdown('<p class="task-header">9 points &nbsp;|&nbsp; ~25 minutes &nbsp;|&nbsp; 120–150 words</p>',
                    unsafe_allow_html=True)
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎲 New topic", use_container_width=True):
            st.session_state.w1_topic = None
            st.session_state.w1_announcement = None
            st.session_state.w1_result = None
            st.rerun()

    # ── Pick topic ───────────────────────────
    if st.session_state.w1_topic is None:
        st.session_state.w1_topic = random.choice(TOPIC_POOL)
        st.session_state.w1_announcement = None

    topic = st.session_state.w1_topic

    # ── Generate announcement ─────────────────
    if st.session_state.w1_announcement is None:
        with st.spinner("Generating task…"):
            try:
                model = get_model()
                prompt = ANNOUNCEMENT_PROMPT.format(**topic)
                resp = model.generate_content(prompt)
                st.session_state.w1_announcement = resp.text.strip()
            except Exception as e:
                st.error(f"Generation error: {e}")
                return

    # ── Display announcement ──────────────────
    ann = st.session_state.w1_announcement
    # Make first two lines bold (title + org)
    lines = ann.split("\n")
    formatted = ""
    for i, ln in enumerate(lines):
        if i < 2 and ln.strip():
            formatted += f"<div class='announcement-title'>{ln.strip()}</div>"
        else:
            formatted += f"{ln}<br>"

    st.markdown(
        f'<div class="announcement-box">{formatted}</div>',
        unsafe_allow_html=True,
    )

    # ── Instructions ─────────────────────────
    st.markdown("""
You see the following announcement on the school website.  
Write an **e-mail** to apply for one of these positions. In your e-mail:

- explain which role you're interested in the most and your availability;
- describe your relevant experience and skills and explain how you can contribute to the centre;
- ask for more information about the terms and conditions of work.
""")

    # ── Text area ────────────────────────────
    user_text = st.text_area(
        "Write your e-mail here:",
        height=280,
        key="w1_user_text",
        placeholder="Dear Ms …,\n\nI am writing to apply for the position of…",
    )

    wc = count_words(user_text)
    st.markdown(f"Word count: {word_count_badge(wc)} / target 120–150")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Check button ─────────────────────────
    check_clicked = st.button("✅ Check my e-mail", type="primary", use_container_width=True)

    if check_clicked:
        if wc < 50:
            st.warning("⚠️ Text is too short (fewer than 50 words). Please write more.")
        elif not user_text.strip():
            st.warning("Please write your e-mail first.")
        else:
            with st.spinner("Grading your e-mail…"):
                try:
                    model = get_model()
                    prompt = CHECKER_PROMPT.format(email_text=user_text)
                    resp = model.generate_content(prompt)
                    raw = resp.text.strip()
                    # Strip possible ```json fences
                    raw = re.sub(r"^```json?\s*", "", raw)
                    raw = re.sub(r"\s*```$", "", raw)
                    result = json.loads(raw)
                    st.session_state.w1_result = result
                except json.JSONDecodeError:
                    st.error("Couldn't parse the AI response. Please try again.")
                except Exception as e:
                    st.error(f"Checking error: {e}")

    # ── Results panel ─────────────────────────
    if st.session_state.w1_result:
        r = st.session_state.w1_result
        total = r.get("content_score", 0) + r.get("organization_score", 0) + r.get("language_score", 0)

        st.markdown("---")

        # Total score
        st.markdown(
            f'<div class="score-panel">'
            f'<div class="score-total">{total} / 9</div>'
            f'<div class="score-label">Total score</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Per-criterion cards
        c1, c2, c3 = st.columns(3)
        criteria = [
            (c1, "Content & Task", "content_score", "content_feedback", "#e74c3c"),
            (c2, "Organization",   "organization_score", "organization_feedback", "#2980b9"),
            (c3, "Language",       "language_score", "language_feedback", "#27ae60"),
        ]
        for col, name, score_key, fb_key, colour in criteria:
            with col:
                score = r.get(score_key, 0)
                fb    = r.get(fb_key, "")
                st.markdown(
                    f'<div class="criteria-card">'
                    f'<div class="criteria-score" style="color:{colour}">{score}/3</div>'
                    f'<div class="criteria-name">{name}</div>'
                    f'<div class="criteria-fb">{fb}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # Corrected text
        st.markdown("### ✏️ Corrected e-mail")
        st.caption("Errors are shown as ~~wrong~~ **correct**")
        corrected_html = highlight_errors(r.get("corrected_text", ""))
        st.markdown(
            f'<div class="corrected-box">{corrected_html}</div>',
            unsafe_allow_html=True,
        )
