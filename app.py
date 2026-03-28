import streamlit as st
import anthropic
import json
from data import CLUBS, QUESTIONS

st.set_page_config(
    page_title="ClubMatch · 找到属于你的圈子",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'PingFang SC', 'Noto Sans SC', sans-serif;
    -webkit-font-smoothing: antialiased;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1200px;
}
[data-testid="stSidebar"] { display: none; }

.stApp {
    background:
        radial-gradient(ellipse 70% 50% at 15% 10%, rgba(199,210,254,0.35) 0%, transparent 60%),
        radial-gradient(ellipse 55% 40% at 85% 85%, rgba(253,230,138,0.25) 0%, transparent 55%),
        radial-gradient(ellipse 60% 55% at 50% 50%, rgba(221,214,254,0.15) 0%, transparent 70%),
        linear-gradient(160deg, #f8f7ff 0%, #fefce8 50%, #f0fdf4 100%);
    color: #1a1a2e;
    min-height: 100vh;
}

.glass {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 16px;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(99,102,241,0.07), 0 1px 4px rgba(0,0,0,0.04);
}
.glass::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.95), transparent);
}
.glass:hover {
    background: rgba(255,255,255,0.88);
    border-color: rgba(255,255,255,1);
    transform: translateY(-3px);
    box-shadow: 0 20px 50px rgba(99,102,241,0.12), 0 4px 12px rgba(0,0,0,0.06);
}
.glass.featured {
    border-color: rgba(99,102,241,0.3);
    background: rgba(245,243,255,0.9);
    box-shadow: 0 8px 32px rgba(99,102,241,0.12);
}
.glass.featured::before {
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.3), transparent);
}

.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0 22px 0;
    border-bottom: 1px solid rgba(99,102,241,0.1);
    margin-bottom: 36px;
}
.logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 21px;
    font-weight: 900;
    letter-spacing: -0.5px;
    color: #1a1a2e;
}
.logo-badge {
    background: linear-gradient(135deg, #6366F1, #818CF8);
    color: #ffffff;
    border-radius: 10px;
    padding: 5px 10px;
    font-size: 13px;
    font-weight: 900;
}
.logo-accent { color: #6366F1; }

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 4px;
    margin-bottom: 4px;
}
.badge-y { background: rgba(245,197,24,0.15); color: #b45309; border: 1px solid rgba(245,197,24,0.3); }
.badge-o { background: rgba(255,107,53,0.12); color: #c2410c; border: 1px solid rgba(255,107,53,0.25); }
.badge-w { background: rgba(99,102,241,0.1); color: #4338ca; border: 1px solid rgba(99,102,241,0.2); }
.badge-g { background: rgba(74,222,128,0.12); color: #15803d; border: 1px solid rgba(74,222,128,0.25); }

.prog-wrap { margin-bottom: 28px; }
.prog-meta {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: rgba(26,26,46,0.4);
    margin-bottom: 8px;
    font-weight: 500;
}
.prog-meta span:last-child { color: #6366F1; font-weight: 700; }
.prog-track {
    height: 4px;
    background: rgba(99,102,241,0.1);
    border-radius: 2px;
    overflow: hidden;
}
.prog-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #6366F1, #818CF8, #a78bfa);
    transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
}

/* 测评选项：未选中的点击按钮 */
.quiz-opt-btn > button {
    border-radius: 12px !important;
    padding: 10px 16px !important;
    height: auto !important;
    min-height: 40px !important;
    text-align: center !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    background: rgba(255,255,255,0.6) !important;
    border: 1.5px solid rgba(99,102,241,0.15) !important;
    color: rgba(26,26,46,0.75) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    width: 100% !important;
    transition: all 0.18s !important;
    box-shadow: none !important;
}
.quiz-opt-btn > button:hover {
    border-color: #6366F1 !important;
    background: rgba(99,102,241,0.06) !important;
    color: #4338ca !important;
    transform: none !important;
    box-shadow: none !important;
}

/* 测评选项：已选中的点击按钮 */
.quiz-opt-btn-sel > button {
    border-radius: 12px !important;
    padding: 10px 16px !important;
    height: auto !important;
    min-height: 40px !important;
    text-align: center !important;
    white-space: nowrap !important;
    background: #6366F1 !important;
    border: none !important;
    color: #ffffff !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.3) !important;
    transition: all 0.18s !important;
}
.quiz-opt-btn-sel > button:hover {
    background: #4F46E5 !important;
    color: #ffffff !important;
    transform: none !important;
}

.score-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}
.score-track {
    flex: 1;
    height: 4px;
    background: rgba(99,102,241,0.1);
    border-radius: 2px;
    overflow: hidden;
}
.score-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #6366F1, #a78bfa);
}
.score-pct { font-size: 13px; font-weight: 800; color: #6366F1; min-width: 38px; text-align: right; }

.stat-num { font-size: 28px; font-weight: 900; color: #6366F1; letter-spacing: -1.5px; line-height: 1; }
.stat-lbl { font-size: 11px; color: rgba(26,26,46,0.4); margin-top: 4px; font-weight: 500; }

.hero-title {
    font-size: clamp(34px, 5vw, 56px);
    font-weight: 900;
    line-height: 1.08;
    letter-spacing: -2px;
    margin-bottom: 16px;
    color: #1a1a2e;
}
.hl {
    background: linear-gradient(135deg, #6366F1 0%, #a78bfa 55%, #818CF8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 16px;
    color: rgba(26,26,46,0.52);
    line-height: 1.75;
    margin-bottom: 30px;
}
.eyebrow {
    display: inline-block;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.18);
    color: #6366F1;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 18px;
}

/* 通用按钮 */
.stButton > button {
    border-radius: 50px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.22s !important;
    border: 1.5px solid rgba(99,102,241,0.18) !important;
    background: rgba(255,255,255,0.75) !important;
    color: #1a1a2e !important;
    padding: 0.45rem 1.1rem !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.07) !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.95) !important;
    border-color: rgba(99,102,241,0.35) !important;
    color: #1a1a2e !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.12) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366F1, #818CF8) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4F46E5, #6366F1) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 28px rgba(99,102,241,0.4) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:disabled {
    opacity: 0.35 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* quiz容器内的按钮覆盖通用圆角 */
.quiz-opt-btn > button,
.quiz-opt-btn-sel > button {
    border-radius: 12px !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.85) !important;
    border: 1.5px solid rgba(99,102,241,0.15) !important;
    border-radius: 14px !important;
    color: #1a1a2e !important;
    font-family: 'Inter', 'PingFang SC', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.08) !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: rgba(26,26,46,0.35) !important;
}
label, .stTextInput label, .stTextArea label, .stSelectbox label {
    color: rgba(26,26,46,0.65) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.85) !important;
    border: 1.5px solid rgba(99,102,241,0.15) !important;
    border-radius: 14px !important;
    color: #1a1a2e !important;
}
.stSelectbox div[data-baseweb="select"] span { color: rgba(26,26,46,0.8) !important; }
.stMultiSelect > div {
    background: rgba(255,255,255,0.85) !important;
    border-radius: 14px !important;
}
.stMultiSelect span[data-baseweb="tag"] {
    background: rgba(99,102,241,0.12) !important;
    color: #4338ca !important;
}

.bubble-ai {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(99,102,241,0.12);
    border-radius: 18px 18px 18px 4px;
    padding: 13px 17px;
    font-size: 14px;
    line-height: 1.7;
    margin: 6px 0 6px 44px;
    color: rgba(26,26,46,0.85);
    white-space: pre-wrap;
    box-shadow: 0 2px 12px rgba(99,102,241,0.07);
}
.bubble-user {
    background: linear-gradient(135deg, #6366F1, #818CF8);
    border-radius: 18px 18px 4px 18px;
    padding: 13px 17px;
    font-size: 14px;
    line-height: 1.7;
    margin: 6px 44px 6px 0;
    color: #ffffff;
    text-align: right;
    box-shadow: 0 2px 12px rgba(99,102,241,0.2);
}
.chat-label {
    font-size: 11px;
    color: rgba(26,26,46,0.35);
    font-weight: 600;
    margin-bottom: 3px;
}

.divider { border: none; border-top: 1px solid rgba(99,102,241,0.08); margin: 28px 0; }

.detail-box {
    background: rgba(248,247,255,0.92);
    border: 1px solid rgba(99,102,241,0.1);
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 6px;
}
.detail-section-title {
    font-size: 10px;
    font-weight: 700;
    color: rgba(26,26,46,0.35);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
    margin-top: 14px;
}
.detail-section-title:first-child { margin-top: 0; }
.req-row {
    display: flex;
    gap: 8px;
    font-size: 13px;
    color: rgba(26,26,46,0.65);
    margin-bottom: 7px;
    line-height: 1.5;
}

.vibe-tag {
    display: inline-block;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.15);
    color: #6366F1;
    border-radius: 8px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 12px;
    font-style: italic;
}

.success-glass {
    background: rgba(240,253,244,0.92);
    border: 1px solid rgba(74,222,128,0.25);
    border-radius: 24px;
    padding: 40px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(74,222,128,0.08);
}

.form-section {
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(99,102,241,0.1);
    border-radius: 16px;
    padding: 20px 22px;
    margin-bottom: 14px;
}
.form-section-title {
    font-size: 12px;
    font-weight: 700;
    color: rgba(26,26,46,0.35);
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 14px;
}

.step-card {
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(99,102,241,0.1);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    transition: all 0.2s;
}
.step-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99,102,241,0.1);
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.2); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ─── Session State ───────────────────────────────────────────
def init():
    defs = {
        "page": "home",
        "quiz_step": 0,
        "quiz_answers": {},
        "results": None,
        "ai_reason": None,
        "expand_club": None,
        "cart": [],
        "applications": [],
        "apply_form": {},
        "chat_history": [],
        "create_submitted": False,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()


def go(page):
    st.session_state.page = page
    st.rerun()

def club_by_id(cid):
    return next((c for c in CLUBS if c["id"] == cid), None)

def already_applied(cid):
    return any(cid in app["clubs"] for app in st.session_state.applications)

def in_cart(cid):
    return cid in st.session_state.cart

def toggle_cart(cid):
    if cid in st.session_state.cart:
        st.session_state.cart.remove(cid)
    else:
        st.session_state.cart.append(cid)


def render_nav():
    cart_count = len(st.session_state.cart)
    cart_str = f" ({cart_count})" if cart_count else ""
    st.markdown(f"""
    <div class="navbar">
        <div class="logo">
            <span class="logo-badge">CM</span>
            Club<span class="logo-accent">Match</span>
        </div>
        <div style="font-size:12px;color:rgba(26,26,46,0.3);font-weight:500;">
            每个人都值得找到属于自己的圈子
        </div>
    </div>
    """, unsafe_allow_html=True)
    tab_cols = st.columns(6, gap="small")
    labels = [
        ("🏠", "首页", "home"),
        ("🧠", "匹配测评", "quiz"),
        ("🔍", "发现社团", "browse"),
        ("🤖", "AI 顾问", "chat"),
        ("📋", f"我的申请{cart_str}", "apply"),
        ("✨", "申请创建", "create"),
    ]
    for col, (icon, label, pg) in zip(tab_cols, labels):
        with col:
            is_active = st.session_state.page == pg
            if st.button(f"{icon} {label}", key=f"nav_{pg}",
                         type="primary" if is_active else "secondary",
                         use_container_width=True):
                go(pg)


def score_bar(score):
    st.markdown(f"""
    <div class="score-row">
        <span style="font-size:11px;color:rgba(26,26,46,0.35);min-width:36px;">匹配度</span>
        <div class="score-track"><div class="score-fill" style="width:{score}%;"></div></div>
        <span class="score-pct">{score}%</span>
    </div>
    """, unsafe_allow_html=True)

def tags_html(club):
    return "".join(f'<span class="badge badge-w">{t}</span>' for t in club.get("tags", []))


def local_score(answers):
    result = []
    for c in CLUBS:
        s = c["score_base"]
        a0 = answers.get(0)
        if a0 == 0 and c["id"] in [1, 2, 10]: s += 12
        if a0 == 1 and c["id"] in [4, 11]: s += 12
        if a0 == 2 and c["id"] in [3, 10, 12, 16]: s += 10
        if a0 == 3 and c["id"] in [6, 12, 13]: s += 12
        a1 = answers.get(1)
        if a1 == 0 and c["id"] in [5, 8]: s += 10
        if a1 == 1 and c["id"] in [4, 11]: s += 12
        if a1 == 2 and c["id"] in [1, 2, 8]: s += 8
        if a1 == 3 and c["id"] in [6, 7, 15]: s += 8
        a2 = answers.get(2)
        if a2 == 0 and c["id"] in [1, 2]: s += 12
        if a2 == 1 and c["id"] in [4, 5, 8]: s += 10
        if a2 == 2 and c["id"] in [3, 9, 14]: s += 12
        if a2 == 3 and c["id"] in [6, 12, 13]: s += 12
        a3 = answers.get(3)
        if a3 == 0 and c["id"] in [1, 2, 8]: s += 8
        if a3 == 1 and c["id"] in [5, 8, 16]: s += 8
        if a3 == 2 and c["id"] in [7, 11, 15]: s += 8
        if a3 == 3 and c["id"] in [4, 9, 14]: s += 8
        a4 = answers.get(4)
        pref = {0: ["低"], 1: ["中等"], 2: ["较高", "高"], 3: ["低", "中等", "较高", "高"]}
        if c["time_cost"] in pref.get(a4, []): s += 6
        a5 = answers.get(5)
        if a5 == 0 and c["id"] in [1, 2, 8]: s += 6
        if a5 == 1 and c["id"] in [6, 7, 11, 13]: s += 6
        if a5 == 2 and c["id"] in [5, 8, 10]: s += 6
        if a5 == 3 and c["id"] in [3, 9, 4, 14]: s += 6
        a6 = answers.get(6)
        if a6 == 0 and c["id"] in [10, 12]: s += 6
        if a6 == 1 and c["id"] in [11, 13, 16]: s += 6
        if a6 == 2 and c["id"] in [7, 15]: s += 6
        if a6 == 3 and c["id"] in [5, 8, 14]: s += 6
        a7 = answers.get(7)
        if a7 == 0 and c["id"] in [10, 12, 1]: s += 5
        if a7 == 1 and c["id"] in [11, 13, 5]: s += 5
        if a7 == 2 and c["id"] in [7, 15, 3]: s += 5
        if a7 == 3 and c["id"] in [9, 14, 6]: s += 5
        result.append({**c, "match_score": min(96, s)})
    return sorted(result, key=lambda x: -x["match_score"])


def ai_match(answers):
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return local_score(answers), None
        client = anthropic.Anthropic(api_key=api_key)
        ans_desc = "<br />".join([
            f"问题{i+1}「{QUESTIONS[i]['q']}」→ {QUESTIONS[i]['opts'][answers.get(i, 0)]['title']}"
            for i in range(len(QUESTIONS))
        ])
        prompt = (
            f"你是大学社团匹配顾问。根据用户测评，为{len(CLUBS)}个社团打匹配分（0-100整数），"
            f"给出最高匹配社团的一句话原因（温暖人性化，不超过40字）。<br /><br />"
            f"用户测评：<br />{ans_desc}<br /><br />"
            f"社团：<br />" +
            "<br />".join([f"{c['id']}. {c['name']}（{c['type']}）" for c in CLUBS]) +
            f"<br /><br />只返回JSON：{{\"scores\":{{\"1\":85,...}},\"reason\":\"...\"}}"
        )
        msg = client.messages.create(
            model="claude-opus-4-5", max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        text = msg.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)
        scores = parsed.get("scores", {})
        result = [
            {**c, "match_score": min(96, int(scores.get(str(c["id"]), c["score_base"])))}
            for c in CLUBS
        ]
        return sorted(result, key=lambda x: -x["match_score"]), parsed.get("reason")
    except Exception:
        return local_score(answers), None


def chat_ai(user_msg):
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "（需要配置 API Key 才能使用 AI 顾问，你可以先去「发现社团」页面浏览，或完成测评获取推荐～）"
        client = anthropic.Anthropic(api_key=api_key)
        system = (
            f"你是 ClubMatch 平台的 AI 社团顾问，帮助大学新生找到适合的社团。<br />"
            f"风格：简洁、温暖、真实，给具体有用的建议，不废话，用中文，适当换行。<br /><br />"
            f"社团数据（共{len(CLUBS)}个）：<br />" +
            "<br />".join([
                f"- {c['name']}（{c['type']}）：{c['desc']} | 成员{c['members']}人，评分{c['rating']}，时间投入：{c['time_cost']}"
                for c in CLUBS
            ])
        )
        history = []
        for t in st.session_state.chat_history:
            if t.get("user"): history.append({"role": "user", "content": t["user"]})
            if t.get("ai"):   history.append({"role": "assistant", "content": t["ai"]})
        history.append({"role": "user", "content": user_msg})
        msg = client.messages.create(
            model="claude-opus-4-5", max_tokens=600, system=system, messages=history
        )
        return msg.content[0].text
    except Exception:
        return "AI 顾问暂时休息中，你可以先去「发现社团」页面逛逛～"


# ══════════════════════════════════════════════════════════════
# 首页
# ══════════════════════════════════════════════════════════════
def page_home():
    render_nav()
    col_l, col_r = st.columns([1.15, 1], gap="large")
    with col_l:
        st.markdown('<div class="eyebrow">✦ 找到你的圈子，从这里开始</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="hero-title">大学四年，<br>你值得遇见<span class="hl">志同道合的伙伴</span></div>
        <div class="hero-sub">
            不知道加哪个社团？害怕加了之后发现不合适？<br>
            我们用 AI 帮你找到真正适合你的那个圈子——<br>
            不靠运气，靠真实的你。
        </div>
        """, unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🎯  开始匹配测评", key="h_start", type="primary", use_container_width=True):
                st.session_state.quiz_step = 0
                st.session_state.quiz_answers = {}
                go("quiz")
        with b2:
            if st.button("🔍  逛逛所有社团", key="h_browse", use_container_width=True):
                go("browse")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        for col, (n, l) in zip([c1, c2, c3, c4], [
            ("16", "入驻社团"), ("3,800+", "在校成员"), ("94%", "匹配满意度"), ("8分钟", "完成测评")
        ]):
            with col:
                st.markdown(
                    f'<div style="text-align:center;"><div class="stat-num">{n}</div>'
                    f'<div class="stat-lbl">{l}</div></div>',
                    unsafe_allow_html=True
                )

    with col_r:
        top = CLUBS[0]
        stats = "".join([
            f'<div style="background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.1);'
            f'border-radius:12px;padding:10px;text-align:center;">'
            f'<div style="font-size:14px;font-weight:800;color:#1a1a2e;">{v}</div>'
            f'<div style="font-size:10px;color:rgba(26,26,46,0.35);margin-top:2px;">{l}</div></div>'
            for v, l in [(top['members'], '成员'), ('⭐'+str(top['rating']), '评分'), (str(top['awards'])+'项', '获奖')]
        ])
        st.markdown(f"""
        <div class="glass featured" style="margin-top:4px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
                <div style="font-size:44px;">{top['emoji']}</div>
                <div style="text-align:right;">
                    <div style="font-size:40px;font-weight:900;color:#6366F1;letter-spacing:-2px;line-height:1;">92%</div>
                    <div style="font-size:10px;color:rgba(26,26,46,0.35);margin-top:2px;">AI 示例匹配度</div>
                </div>
            </div>
            <div style="font-size:18px;font-weight:800;letter-spacing:-0.4px;margin-bottom:4px;color:#1a1a2e;">{top['name']}</div>
            <div class="vibe-tag">{top.get('vibe','')}</div>
            <div style="font-size:13px;color:rgba(26,26,46,0.5);line-height:1.6;margin-bottom:14px;">{top['desc']}</div>
            <div style="margin-bottom:14px;">{tags_html(top)}<span class="badge badge-o">热门</span></div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">{stats}</div>
        </div>
        <div style="text-align:center;font-size:12px;color:rgba(26,26,46,0.25);margin-top:8px;">
            🟢 &nbsp;本周已有 102 位新生完成匹配
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;margin-bottom:28px;">
        <div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#6366F1;text-transform:uppercase;margin-bottom:10px;">我们不一样</div>
        <div style="font-size:26px;font-weight:900;letter-spacing:-0.8px;color:#1a1a2e;">不是随机，是属于你的那个</div>
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(3, gap="medium")
    features = [
        ("🧬", "真实的你，真实的匹配", "我们问的不是「你有什么爱好」，而是「你周末真的会做什么」——8 道情景题，比你自己更了解你适合哪种氛围。"),
        ("📊", "社团数据全透明", "成员活跃度、时间投入、历年评价……在你加入之前，我们让数据替你把关。16 个社团，深度介绍。"),
        ("🤝", "加入后，我们也在", "申请提交只是开始。我们会告诉你接下来发生什么、怎么融入、社团群如何运营——让你不迷茫。"),
    ]
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div class="glass" style="min-height:160px;">
                <div style="font-size:28px;margin-bottom:14px;">{icon}</div>
                <div style="font-size:15px;font-weight:800;letter-spacing:-0.3px;margin-bottom:8px;color:#1a1a2e;">{title}</div>
                <div style="font-size:13px;color:rgba(26,26,46,0.48);line-height:1.65;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    import random
    picks = random.sample(CLUBS, 3)
    st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#6366F1;text-transform:uppercase;margin-bottom:10px;">✦ 今日精选</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:22px;font-weight:900;letter-spacing:-0.6px;margin-bottom:20px;color:#1a1a2e;">随便逛逛，说不定就遇上了</div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    for col, club in zip(cols, picks):
        with col:
            st.markdown(f"""
            <div class="glass">
                <div style="font-size:36px;margin-bottom:10px;">{club['emoji']}</div>
                <div style="font-size:16px;font-weight:800;letter-spacing:-0.3px;margin-bottom:3px;color:#1a1a2e;">{club['name']}</div>
                <div class="vibe-tag">{club.get('vibe','')}</div>
                <div style="font-size:13px;color:rgba(26,26,46,0.48);line-height:1.55;margin-bottom:12px;">{club['desc'][:55]}...</div>
                <div>{tags_html(club)}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("了解更多", key=f"home_club_{club['id']}", use_container_width=True):
                st.session_state.expand_club = club["id"]
                go("browse")

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("✨  还没找到感觉？来做个测评吧 →", key="home_cta2", type="primary", use_container_width=True):
            st.session_state.quiz_step = 0
            st.session_state.quiz_answers = {}
            go("quiz")


# ══════════════════════════════════════════════════════════════
# 测评页 — 核心改动在这里
# ══════════════════════════════════════════════════════════════
def page_quiz():
    render_nav()

    step = st.session_state.quiz_step
    total = len(QUESTIONS)
    q = QUESTIONS[step]
    pct = int(step / total * 100)

    st.markdown(f"""
    <div class="prog-wrap">
        <div class="prog-meta"><span>问题 {step+1} / {total}</span><span>{pct}%</span></div>
        <div class="prog-track"><div class="prog-fill" style="width:{pct}%;"></div></div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([0.5, 4, 0.5])
    with mid:
        st.markdown(
            f'<div style="font-size:11px;font-weight:700;color:#6366F1;letter-spacing:0.8px;'
            f'text-transform:uppercase;margin-bottom:10px;">第 {step+1} 题</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="font-size:clamp(20px,3vw,28px);font-weight:900;letter-spacing:-0.8px;'
            f'line-height:1.25;margin-bottom:6px;color:#1a1a2e;">{q["q"]}</div>',
            unsafe_allow_html=True
        )
        if q.get("hint"):
            st.markdown(
                f'<div style="font-size:13px;color:rgba(26,26,46,0.32);margin-bottom:22px;'
                f'font-style:italic;">{q["hint"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)

        cur = st.session_state.quiz_answers.get(step)
        row1 = st.columns(2, gap="small")
        row2 = st.columns(2, gap="small")
        all_cols = list(row1) + list(row2)

        for i, (col, opt) in enumerate(zip(all_cols, q["opts"])):
            with col:
                is_sel = (cur == i)

                # ── 展示卡片（纯HTML，无乱码风险）──
                card_bg     = "rgba(99,102,241,0.08)"   if is_sel else "rgba(255,255,255,0.75)"
                card_border = "2px solid #6366F1"       if is_sel else "1.5px solid rgba(99,102,241,0.14)"
                card_shadow = "0 0 0 4px rgba(99,102,241,0.08)" if is_sel else "0 2px 8px rgba(99,102,241,0.05)"
                title_color = "#3730a3" if is_sel else "#1a1a2e"
                check_icon  = '<span style="color:#6366F1;font-weight:900;font-size:14px;">✓</span>' if is_sel else ""

                st.markdown(f"""
                <div style="
                    background:{card_bg};
                    border:{card_border};
                    border-radius:16px;
                    padding:14px 16px;
                    box-shadow:{card_shadow};
                    transition:all 0.2s;
                    margin-bottom:6px;
                ">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:5px;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:20px;">{opt['icon']}</span>
                            <span style="font-size:14px;font-weight:700;color:{title_color};">{opt['title']}</span>
                        </div>
                        {check_icon}
                    </div>
                    <div style="font-size:12px;color:rgba(26,26,46,0.45);padding-left:28px;line-height:1.4;">{opt['sub']}</div>
                </div>
                """, unsafe_allow_html=True)

                # ── 点击按钮（文字简短，绝对不会乱码）──
                css_class = "quiz-opt-btn-sel" if is_sel else "quiz-opt-btn"
                btn_label  = "✓ 已选择" if is_sel else "选这个"

                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                if st.button(btn_label, key=f"q{step}_o{i}", use_container_width=True):
                    st.session_state.quiz_answers[step] = i
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        nav_l, nav_r = st.columns(2, gap="small")
        with nav_l:
            back_label = "← 返回首页" if step == 0 else "← 上一题"
            if st.button(back_label, key="q_back", use_container_width=True):
                if step == 0:
                    go("home")
                else:
                    st.session_state.quiz_step -= 1
                    st.rerun()
        with nav_r:
            done = step in st.session_state.quiz_answers
            label = "查看匹配结果 →" if step == total - 1 else "下一题 →"
            if st.button(label, key="q_next", type="primary", use_container_width=True, disabled=not done):
                if step == total - 1:
                    with st.spinner("🤖 AI 正在分析你的性格与偏好..."):
                        res, reason = ai_match(st.session_state.quiz_answers)
                        st.session_state.results = res
                        st.session_state.ai_reason = reason
                    go("results")
                else:
                    st.session_state.quiz_step += 1
                    st.rerun()


# ══════════════════════════════════════════════════════════════
# 匹配结果页
# ══════════════════════════════════════════════════════════════
def page_results():
    render_nav()
    results = st.session_state.results
    if not results:
        st.warning("还没有结果，先完成测评吧～")
        if st.button("去测评", type="primary"): go("quiz")
        return

    reason = st.session_state.get("ai_reason")
    st.markdown(
        '<div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#6366F1;text-transform:uppercase;margin-bottom:10px;">✦ 你的专属匹配报告</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="font-size:clamp(22px,4vw,36px);font-weight:900;letter-spacing:-1.2px;margin-bottom:10px;color:#1a1a2e;">AI 从 {len(CLUBS)} 个社团里，为你挑出了这些</div>',
        unsafe_allow_html=True
    )
    if reason:
        st.markdown(f"""
        <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.15);
            border-radius:14px;padding:14px 18px;font-size:14px;color:rgba(26,26,46,0.75);
            line-height:1.65;margin-bottom:24px;">
            <span style="color:#6366F1;font-weight:700;">✦ AI 分析：</span>{reason}
        </div>
        """, unsafe_allow_html=True)

    cols = st.columns(3, gap="small")
    badges = ["🥇 最佳匹配", "🥈 强烈推荐", "🥉 推荐"]
    badge_cls = ["badge-y", "badge-o", "badge-w"]

    for idx, club in enumerate(results):
        with cols[idx % 3]:
            applied = already_applied(club["id"])
            in_c = in_cart(club["id"])
            bc = badge_cls[idx] if idx < 3 else "badge-w"
            bl = badges[idx] if idx < 3 else f"#{idx+1}"
            applied_badge = '<span class="badge badge-g">✓ 已报名</span>' if applied else ''

            st.markdown(f"""
            <div class="glass {'featured' if idx==0 else ''}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                    <div style="font-size:36px;">{club['emoji']}</div>
                    <span class="badge {bc}">{bl}</span>
                </div>
                <div style="font-size:16px;font-weight:800;letter-spacing:-0.3px;margin-bottom:2px;color:#1a1a2e;">{club['name']}</div>
                <div style="font-size:11px;color:rgba(26,26,46,0.38);margin-bottom:10px;">{club['type']} · {club['freq']}</div>
            """, unsafe_allow_html=True)
            score_bar(club["match_score"])
            st.markdown(f"""
                <div class="vibe-tag">{club.get('vibe','')}</div>
                <div style="font-size:13px;color:rgba(26,26,46,0.5);line-height:1.55;margin-bottom:12px;">{club['desc'][:58]}...</div>
                <div style="margin-bottom:14px;">{tags_html(club)}{applied_badge}</div>
            </div>
            """, unsafe_allow_html=True)

            b1, b2 = st.columns(2, gap="small")
            with b1:
                if st.button("查看详情", key=f"r_detail_{club['id']}_{idx}", use_container_width=True):
                    st.session_state.expand_club = club["id"] if st.session_state.expand_club != club["id"] else None
                    st.rerun()
            with b2:
                if applied:
                    st.button("已报名 ✓", key=f"r_applied_{club['id']}", disabled=True, use_container_width=True)
                elif in_c:
                    if st.button("移出申请袋", key=f"r_rm_{club['id']}_{idx}", use_container_width=True):
                        toggle_cart(club["id"]); st.rerun()
                else:
                    if st.button("➕ 加入申请袋", key=f"r_add_{club['id']}_{idx}", type="primary", use_container_width=True):
                        toggle_cart(club["id"]); st.rerun()

            if st.session_state.expand_club == club["id"]:
                render_club_detail(club)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1:
        if st.button("🔄 重新测评", key="r_retake", use_container_width=True):
            st.session_state.quiz_step = 0; st.session_state.quiz_answers = {}; go("quiz")
    with c2:
        if st.button("🔍 发现更多社团", key="r_browse", use_container_width=True): go("browse")
    with c3:
        if st.button("🤖 咨询 AI 顾问", key="r_chat", use_container_width=True): go("chat")
    with c4:
        cart_n = len(st.session_state.cart)
        if cart_n:
            if st.button(f"📋 提交申请 ({cart_n})", key="r_apply", type="primary", use_container_width=True): go("apply")
        else:
            st.button("📋 申请袋是空的", key="r_apply_empty", disabled=True, use_container_width=True)


def render_club_detail(club):
    applied = already_applied(club["id"])
    req_rows = "".join([
        f'<div class="req-row"><span style="color:#6366F1;margin-top:2px;flex-shrink:0;">·</span><span>{r}</span></div>'
        for r in club.get('requirements', [])
    ])
    act_rows = "".join([
        f'<div class="req-row"><span style="color:#F97316;margin-top:2px;flex-shrink:0;">·</span><span>{a}</span></div>'
        for a in club.get('activities', [])
    ])
    stat_cells = "".join([
        f'<div style="background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.08);'
        f'border-radius:10px;padding:10px;text-align:center;">'
        f'<div style="font-size:14px;font-weight:800;color:#1a1a2e;">{v}</div>'
        f'<div style="font-size:10px;color:rgba(26,26,46,0.35);margin-top:2px;">{l}</div></div>'
        for v, l in [(str(club['members']),'成员'),('⭐'+str(club['rating']),'评分'),(str(club['awards'])+'项','获奖'),(club['time_cost'],'时间投入')]
    ])
    applied_note = (
        '<div style="margin-top:12px;padding:10px 14px;background:rgba(74,222,128,0.08);'
        'border:1px solid rgba(74,222,128,0.2);border-radius:10px;font-size:12px;'
        'color:#15803d;text-align:center;">✓ 你已报名这个社团</div>'
    ) if applied else ''
    st.markdown(f"""
    <div class="detail-box">
        <div class="detail-section-title">关于我们</div>
        <div style="font-size:13px;color:rgba(26,26,46,0.65);line-height:1.7;margin-bottom:4px;">{club.get('detail','')}</div>
        <div class="detail-section-title">这个社团最适合</div>
        <div style="font-size:13px;color:rgba(26,26,46,0.65);margin-bottom:4px;">→ {club.get('best_for','')}</div>
        <div class="detail-section-title">招新要求</div>{req_rows}
        <div class="detail-section-title">主要活动</div>{act_rows}
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:14px;">{stat_cells}</div>
        {applied_note}
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 发现社团页
# ══════════════════════════════════════════════════════════════
def page_browse():
    render_nav()
    st.markdown('<div style="font-size:26px;font-weight:900;letter-spacing:-0.8px;margin-bottom:4px;color:#1a1a2e;">发现社团</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:14px;color:rgba(26,26,46,0.4);margin-bottom:20px;">{len(CLUBS)} 个社团，总有一个在等你</div>', unsafe_allow_html=True)

    col_s, col_f = st.columns([2, 1])
    with col_s:
        search = st.text_input("", placeholder="🔍  搜索名称、类型、标签...", label_visibility="collapsed", key="b_search")
    with col_f:
        types = ["全部类型"] + sorted(list({c["type"] for c in CLUBS}))
        sel_type = st.selectbox("", types, label_visibility="collapsed", key="b_type")

    filtered = [
        c for c in CLUBS
        if (not search or search in c["name"] or search in c["type"]
            or any(search in t for t in c.get("tags", [])) or search in c["desc"])
        and (sel_type == "全部类型" or c["type"] == sel_type)
    ]

    if not filtered:
        st.markdown('<div style="text-align:center;padding:60px;color:rgba(26,26,46,0.25);">没找到……换个关键词试试？</div>', unsafe_allow_html=True)
        return

    cols = st.columns(3, gap="small")
    for idx, club in enumerate(filtered):
        with cols[idx % 3]:
            applied = already_applied(club["id"])
            in_c = in_cart(club["id"])
            applied_badge = '<span class="badge badge-g">✓ 已报名</span>' if applied else ''
            cart_badge = '<span class="badge badge-y">在申请袋中</span>' if (in_c and not applied) else ''
            stat_cells = "".join([
                f'<div style="text-align:center;"><div style="font-size:13px;font-weight:800;color:#1a1a2e;">{v}</div>'
                f'<div style="font-size:10px;color:rgba(26,26,46,0.35);margin-top:2px;">{l}</div></div>'
                for v, l in [(str(club['members']),'成员'),('⭐'+str(club['rating']),'评分'),(str(club['awards'])+'项','获奖')]
            ])
            st.markdown(f"""
            <div class="glass">
                <div style="font-size:36px;margin-bottom:10px;">{club['emoji']}</div>
                <div style="font-size:16px;font-weight:800;letter-spacing:-0.3px;margin-bottom:2px;color:#1a1a2e;">{club['name']}</div>
                <div style="font-size:11px;color:rgba(26,26,46,0.35);margin-bottom:8px;">{club['type']} · 成立 {club['founded']}</div>
                <div class="vibe-tag">{club.get('vibe','')}</div>
                <div style="font-size:13px;color:rgba(26,26,46,0.5);line-height:1.55;margin-bottom:12px;">{club['desc'][:62]}...</div>
                <div style="margin-bottom:12px;">{tags_html(club)}{applied_badge}{cart_badge}</div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid rgba(99,102,241,0.07);padding-top:12px;">
                    {stat_cells}
                </div>
            </div>
            """, unsafe_allow_html=True)

            b1, b2 = st.columns(2, gap="small")
            with b1:
                exp = st.session_state.expand_club == club["id"]
                if st.button("收起 ↑" if exp else "查看详情", key=f"b_det_{club['id']}_{idx}", use_container_width=True):
                    st.session_state.expand_club = club["id"] if not exp else None
                    st.rerun()
            with b2:
                if applied:
                    st.button("已报名 ✓", key=f"b_app_{club['id']}", disabled=True, use_container_width=True)
                elif in_c:
                    if st.button("移出申请袋", key=f"b_rm_{club['id']}_{idx}", use_container_width=True):
                        toggle_cart(club["id"]); st.rerun()
                else:
                    if st.button("➕ 加入申请袋", key=f"b_add_{club['id']}_{idx}", type="primary", use_container_width=True):
                        toggle_cart(club["id"]); st.rerun()

            if st.session_state.expand_club == club["id"]:
                render_club_detail(club)

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        cart_n = len(st.session_state.cart)
        if cart_n:
            if st.button(f"📋  前往提交申请（已选 {cart_n} 个）", type="primary", use_container_width=True, key="b_go_apply"):
                go("apply")
        if st.button("✨  没找到合适的？申请创建新社团", use_container_width=True, key="b_create"):
            go("create")


# ══════════════════════════════════════════════════════════════
# AI 顾问页
# ══════════════════════════════════════════════════════════════
def page_chat():
    render_nav()
    st.markdown('<div style="font-size:24px;font-weight:900;letter-spacing:-0.6px;margin-bottom:4px;color:#1a1a2e;">AI 社团顾问</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;color:rgba(26,26,46,0.38);margin-bottom:24px;">由 Claude AI 驱动 · 随时回答关于社团的任何疑问</div>', unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.session_state.chat_history = [{"user": None, "ai": (
            f"嗨！我是 ClubMatch AI 顾问 👋<br /><br />"
            f"我对平台上所有 {len(CLUBS)} 个社团都了如指掌。你可以问我：<br />"
            f"· 某个社团的具体情况和氛围<br />"
            f"· 根据你的情况给个性化推荐<br />"
            f"· 「内向的人适合哪个」「我时间不多怎么选」……<br /><br />"
            f"随便问吧，没有奇怪的问题。"
        )}]

    for turn in st.session_state.chat_history:
        if turn.get("user"):
            st.markdown('<div style="text-align:right;" class="chat-label">你</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bubble-user">{turn["user"]}</div>', unsafe_allow_html=True)
        if turn.get("ai"):
            st.markdown('<div class="chat-label">🤖  AI 顾问</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bubble-ai">{turn["ai"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if len(st.session_state.chat_history) <= 1:
        st.markdown('<div style="font-size:12px;color:rgba(26,26,46,0.3);margin-bottom:8px;">快捷问题，点一下就能问</div>', unsafe_allow_html=True)
        sugg = ["内向的人适合哪个社团？", "我时间不多，选哪个好？", "摄影社和微电影社有啥区别？", "创业社真的有用吗？", "不知道自己喜欢什么怎么办？", "哪个社团最容易交到朋友？"]
        cols = st.columns(3, gap="small")
        for i, s in enumerate(sugg):
            with cols[i % 3]:
                if st.button(s, key=f"sugg_{i}", use_container_width=True):
                    with st.spinner("思考中..."): rep = chat_ai(s)
                    st.session_state.chat_history.append({"user": s, "ai": rep}); st.rerun()

    col_i, col_s = st.columns([5, 1])
    with col_i:
        user_input = st.text_input("", placeholder="问我任何关于社团的事...", label_visibility="collapsed", key="chat_inp")
    with col_s:
        send = st.button("发送 →", key="chat_send", type="primary", use_container_width=True)
    if send and user_input.strip():
        with st.spinner("AI 思考中..."): rep = chat_ai(user_input.strip())
        st.session_state.chat_history.append({"user": user_input.strip(), "ai": rep}); st.rerun()
    if len(st.session_state.chat_history) > 1:
        if st.button("🗑  清空对话", key="chat_clear"): st.session_state.chat_history = []; st.rerun()


# ══════════════════════════════════════════════════════════════
# 申请提交页
# ══════════════════════════════════════════════════════════════
def page_apply():
    render_nav()
    cart = st.session_state.cart
    if not cart:
        st.markdown('<div style="font-size:22px;font-weight:800;color:#1a1a2e;margin-bottom:8px;">申请袋是空的</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:rgba(26,26,46,0.4);margin-bottom:24px;font-size:14px;">先去发现社团，把感兴趣的加进申请袋再来这里～</div>', unsafe_allow_html=True)
        if st.button("去发现社团", type="primary"): go("browse")
        return

    st.markdown('<div style="font-size:26px;font-weight:900;letter-spacing:-0.8px;margin-bottom:4px;color:#1a1a2e;">提交申请</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:14px;color:rgba(26,26,46,0.4);margin-bottom:24px;">你选择了 {len(cart)} 个社团，一次填写全搞定</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1.2, 1], gap="large")
    with col_l:
        st.markdown('<div class="form-section"><div class="form-section-title">你的申请袋</div>', unsafe_allow_html=True)
        for cid in list(cart):
            club = club_by_id(cid)
            if club:
                c_left, c_right = st.columns([3, 1])
                with c_left:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid rgba(99,102,241,0.06);">
                        <span style="font-size:22px;">{club['emoji']}</span>
                        <div>
                            <div style="font-size:14px;font-weight:700;color:#1a1a2e;">{club['name']}</div>
                            <div style="font-size:11px;color:rgba(26,26,46,0.38);">{club['type']} · {club['freq']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with c_right:
                    if st.button("移除", key=f"apply_rm_{cid}", use_container_width=True):
                        toggle_cart(cid); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("+ 继续添加社团", key="apply_more", use_container_width=True): go("browse")

        st.markdown("""
        <div class="form-section" style="margin-top:14px;">
            <div class="form-section-title">提交后，然后呢？</div>
            <div style="display:flex;flex-direction:column;gap:14px;">
                <div style="display:flex;align-items:flex-start;gap:12px;">
                    <div style="width:28px;height:28px;border-radius:50%;background:rgba(99,102,241,0.1);color:#6366F1;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px;">1</div>
                    <div><div style="font-size:13px;font-weight:700;color:#1a1a2e;margin-bottom:2px;">社团负责人主动联系你</div><div style="font-size:12px;color:rgba(26,26,46,0.45);line-height:1.5;">3 个工作日内，通过你填写的手机号或微信联系，说明面试或见面安排。</div></div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:12px;">
                    <div style="width:28px;height:28px;border-radius:50%;background:rgba(99,102,241,0.1);color:#6366F1;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px;">2</div>
                    <div><div style="font-size:13px;font-weight:700;color:#1a1a2e;margin-bottom:2px;">参加社团见面或体验活动</div><div style="font-size:12px;color:rgba(26,26,46,0.45);line-height:1.5;">大部分社团会邀请你来体验一次活动，感受真实氛围再决定要不要加入。</div></div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:12px;">
                    <div style="width:28px;height:28px;border-radius:50%;background:rgba(99,102,241,0.1);color:#6366F1;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px;">3</div>
                    <div><div style="font-size:13px;font-weight:700;color:#1a1a2e;margin-bottom:2px;">被拉入社团群，正式加入</div><div style="font-size:12px;color:rgba(26,26,46,0.45);line-height:1.5;">确认加入后，负责人会把你拉进官方微信群。群里有活动通知、资源共享和日常闲聊。</div></div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:12px;">
                    <div style="width:28px;height:28px;border-radius:50%;background:rgba(245,197,24,0.15);color:#b45309;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px;">✦</div>
                    <div><div style="font-size:13px;font-weight:700;color:#1a1a2e;margin-bottom:2px;">进群后建议做的事</div><div style="font-size:12px;color:rgba(26,26,46,0.45);line-height:1.5;">自我介绍时说说你为什么感兴趣；主动问新人任务；跟着参加前两次活动，陌生感会很快消失。</div></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="form-section"><div class="form-section-title">个人信息</div>', unsafe_allow_html=True)
        name = st.text_input("姓名 *", placeholder="请输入真实姓名", key="form_name")
        student_id = st.text_input("学号 *", placeholder="例：2024XXXXXXXX", key="form_sid")
        major = st.text_input("专业 *", placeholder="例：国际经济与贸易", key="form_major")
        grade = st.selectbox("年级 *", ["请选择", "大一", "大二", "大三", "大四", "研究生"], key="form_grade")
        phone = st.text_input("手机号 *", placeholder="社团负责人会通过此号联系你", key="form_phone")
        wechat = st.text_input("微信号（选填）", placeholder="方便拉你进群", key="form_wechat")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-section" style="margin-top:10px;"><div class="form-section-title">补充信息</div>', unsafe_allow_html=True)
        intro = st.text_area("自我介绍 *", placeholder="简单介绍一下自己，为什么对这些社团感兴趣？（100字以内）", height=100, key="form_intro")
        time_avail = st.multiselect("你通常空闲的时间段", ["周一至周五 白天", "周一至周五 晚上", "周末全天", "周末上午", "周末下午"], key="form_time")
        skill = st.text_input("你有哪些特长或技能？（选填）", placeholder="例：会摄影、会吉他、做过社区服务...", key="form_skill")
        st.markdown('</div>', unsafe_allow_html=True)

        all_filled = all([name.strip(), student_id.strip(), major.strip(), grade != "请选择", phone.strip(), intro.strip()])
        if st.button("🎉  提交所有申请", key="apply_submit", type="primary", use_container_width=True, disabled=not all_filled):
            record = {"clubs": list(cart), "name": name, "student_id": student_id, "major": major, "grade": grade, "phone": phone, "wechat": wechat, "intro": intro, "time_avail": time_avail, "skill": skill}
            st.session_state.applications.append(record)
            st.session_state.cart = []
            go("success")
        if not all_filled:
            st.markdown('<div style="font-size:12px;color:rgba(26,26,46,0.3);text-align:center;margin-top:6px;">请填写所有必填项后提交</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 成功页
# ══════════════════════════════════════════════════════════════
def page_success():
    render_nav()
    if not st.session_state.applications: go("home"); return
    last = st.session_state.applications[-1]
    club_names = [club_by_id(cid)["name"] for cid in last["clubs"] if club_by_id(cid)]
    club_list_html = "".join([
        f'<div style="display:flex;align-items:center;gap:8px;font-size:14px;color:rgba(26,26,46,0.75);margin-bottom:8px;"><span style="color:#15803d;">✓</span>{n}</div>'
        for n in club_names
    ])

    _, col, _ = st.columns([0.5, 3, 0.5])
    with col:
        st.markdown(f"""
        <div class="success-glass">
            <div style="font-size:56px;margin-bottom:16px;">🎉</div>
            <div style="font-size:28px;font-weight:900;letter-spacing:-1px;margin-bottom:10px;color:#1a1a2e;">申请已成功提交！</div>
            <div style="font-size:15px;color:rgba(26,26,46,0.55);line-height:1.75;margin-bottom:24px;">
                {last['name']}，欢迎你迈出这一步。<br>接下来，静静等着被发现吧。
            </div>
            <div style="background:rgba(255,255,255,0.7);border:1px solid rgba(99,102,241,0.1);border-radius:14px;padding:18px;text-align:left;margin-bottom:20px;">
                <div style="font-size:11px;color:rgba(26,26,46,0.35);font-weight:700;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:12px;">你申请的社团</div>
                {club_list_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:16px;font-weight:800;color:#1a1a2e;margin-bottom:12px;letter-spacing:-0.3px;">加入社团后，怎么快速融入？</div>', unsafe_allow_html=True)
        tips_cols = st.columns(3, gap="small")
        tips = [
            ("💬", "第一次活动前", "主动在群里自我介绍，说说你为什么加入。「你好，我是新来的 xx，对 xxx 特别感兴趣」——比你想象的更有用。"),
            ("🤝", "第一个月", "每次活动尽量不缺席。陌生感主要来自不熟悉，前几次见面之后会好很多。遇到不懂的就问老成员。"),
            ("🌱", "稳定下来之后", "尝试承担一个具体的小任务或职位。有责任感的成员会被记住，也更容易从中获得真实的成长。"),
        ]
        for col_t, (icon, title, desc) in zip(tips_cols, tips):
            with col_t:
                st.markdown(f"""
                <div class="step-card">
                    <div style="font-size:26px;margin-bottom:10px;">{icon}</div>
                    <div style="font-size:14px;font-weight:700;color:#1a1a2e;margin-bottom:6px;">{title}</div>
                    <div style="font-size:12px;color:rgba(26,26,46,0.5);line-height:1.6;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.12);border-radius:14px;padding:16px 20px;margin-bottom:16px;">
            <div style="font-size:12px;font-weight:700;color:#6366F1;letter-spacing:0.6px;margin-bottom:8px;">关于社团群的小提示</div>
            <div style="font-size:13px;color:rgba(26,26,46,0.6);line-height:1.65;">进群后不要设置消息免打扰（至少前一个月）——很多活动通知和临时安排都在群里。不要只是「潜水」，哪怕发个表情包也比完全沉默好。</div>
        </div>
        """, unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("继续发现社团", key="s_browse", use_container_width=True): go("browse")
        with b2:
            if st.button("回到首页", key="s_home", type="primary", use_container_width=True): go("home")


# ══════════════════════════════════════════════════════════════
# 申请创建社团页
# ══════════════════════════════════════════════════════════════
def page_create():
    render_nav()
    st.markdown('<div class="eyebrow">✦ 找不到合适的？自己创一个</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:28px;font-weight:900;letter-spacing:-0.8px;margin-bottom:8px;color:#1a1a2e;">申请创建新社团</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:15px;color:rgba(26,26,46,0.45);line-height:1.7;margin-bottom:28px;">每一个存在的社团，都是某个人第一次说「我想做这件事」。<br>如果你有个想法，这里是它开始的地方。</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown('<div class="form-section"><div class="form-section-title">社团基本信息</div>', unsafe_allow_html=True)
        club_name = st.text_input("你想创建的社团叫什么？*", placeholder="例：城市骑行与街拍社", key="c_name")
        club_type = st.selectbox("社团类型 *", ["请选择","艺术创作","音乐表演","舞台表演","科技创新","商业创新","户外运动","人文学术","公益服务","体育竞技","跨文化交流","科学探索","其他"], key="c_type")
        club_desc = st.text_area("用一两句话，说说这个社团是做什么的 *", placeholder="让别人在 5 秒内听懂这个社团，别用太多形容词，说具体的事。", height=80, key="c_desc")
        club_why  = st.text_area("为什么这个社团值得存在？你发现了什么需求？*", placeholder="比如：我发现学校没有专注城市骑行的社团，但身边有很多同学想要这个……", height=100, key="c_why")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="form-section" style="margin-top:10px;"><div class="form-section-title">你的构想</div>', unsafe_allow_html=True)
        activity_plan = st.text_area("你打算做哪些活动或项目？", placeholder="大概说说你的活动构想，哪怕很初期的想法也可以", height=90, key="c_plan")
        st.slider("你预计招募多少初始成员？", 5, 50, 15, key="c_members")
        st.selectbox("计划的活动频率", ["每周一次","每两周一次","每月一次","视项目而定","还没想好"], key="c_freq")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="form-section"><div class="form-section-title">发起人信息</div>', unsafe_allow_html=True)
        f_name  = st.text_input("你的姓名 *", key="c_fname")
        f_sid   = st.text_input("学号 *", key="c_fsid")
        f_major = st.text_input("专业 *", key="c_fmajor")
        f_grade = st.selectbox("年级 *", ["请选择","大一","大二","大三","大四","研究生"], key="c_fgrade")
        f_phone = st.text_input("联系方式 *", key="c_fphone")
        st.text_area("你有哪些相关经历或能力？（选填）", placeholder="比如：你本身就是这个领域的爱好者？做过类似的组织工作？", height=80, key="c_fexp")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-section" style="margin-top:10px;"><div class="form-section-title">AI 帮你完善方案</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px;color:rgba(26,26,46,0.45);line-height:1.6;margin-bottom:14px;">填完基本信息后，让 AI 给你的创建方案提几条建议——对写申请书很有帮助。</div>', unsafe_allow_html=True)
        if st.button("🤖  让 AI 给我点建议", key="c_ai_suggest", use_container_width=True):
            if club_name and club_desc and club_why:
                with st.spinner("AI 思考中..."):
                    try:
                        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
                        if api_key:
                            client = anthropic.Anthropic(api_key=api_key)
                            msg = client.messages.create(
                                model="claude-opus-4-5", max_tokens=500,
                                messages=[{"role":"user","content":(
                                    f"一位大学生想创建社团：<br />名称：{club_name}<br />类型：{club_type}<br />"
                                    f"描述：{club_desc}<br />创建原因：{club_why}<br />活动计划：{activity_plan}<br /><br />"
                                    f"请给出3条简短、具体、有用的建议，帮助他完善社团方案。风格温暖鼓励，直接分点，不用markdown标题。"
                                )}]
                            )
                            suggestion = msg.content[0].text
                        else:
                            suggestion = "1. 把你的核心活动再具体化——「每月一次骑行」比「定期活动」更有说服力。<br />2. 考虑一下如何区分于现有社团，你的独特价值是什么？<br />3. 找 2-3 个有同样想法的人一起发起，审核委员会会看得更认真。"
                        st.markdown(f'<div class="bubble-ai">✦ AI 建议：<br /><br />{suggestion}</div>', unsafe_allow_html=True)
                    except Exception:
                        st.info("AI 暂时不可用，但你的想法很棒，继续填写吧！")
            else:
                st.warning("先填写社团名称、描述和创建原因，AI 才能给出有用的建议～")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="form-section" style="margin-top:10px;">
            <div class="form-section-title">提交后的审核流程</div>
            <div style="font-size:13px;color:rgba(26,26,46,0.6);line-height:1.8;">
                <div style="margin-bottom:4px;"><span style="color:#6366F1;font-weight:700;">① 初步审核</span>（1-2 个工作日）</div>
                <div style="margin-bottom:10px;color:rgba(26,26,46,0.45);font-size:12px;padding-left:14px;">学生活动部确认材料完整，通过后进入答辩环节</div>
                <div style="margin-bottom:4px;"><span style="color:#6366F1;font-weight:700;">② 创建人答辩</span>（约 15 分钟）</div>
                <div style="margin-bottom:10px;color:rgba(26,26,46,0.45);font-size:12px;padding-left:14px;">向评审委员会说明社团定位、活动计划和初始招募方案</div>
                <div style="margin-bottom:4px;"><span style="color:#6366F1;font-weight:700;">③ 试运营期</span>（一学期）</div>
                <div style="color:rgba(26,26,46,0.45);font-size:12px;padding-left:14px;">完成 3 次以上有记录的活动后，正式注册挂牌，登上 ClubMatch 平台</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        all_ok = all([club_name, club_type != "请选择", club_desc, club_why, f_name, f_sid, f_major, f_grade != "请选择", f_phone])
        if st.button("🚀  提交创建申请", key="c_submit", type="primary", use_container_width=True, disabled=not all_ok):
            st.session_state.create_submitted = True
            st.rerun()

        if st.session_state.get("create_submitted"):
            st.markdown(f"""
            <div style="margin-top:14px;background:rgba(240,253,244,0.9);border:1px solid rgba(74,222,128,0.25);border-radius:14px;padding:16px;text-align:center;">
                <div style="font-size:22px;margin-bottom:8px;">🌱</div>
                <div style="font-size:15px;font-weight:700;margin-bottom:6px;color:#1a1a2e;">申请已提交！</div>
                <div style="font-size:13px;color:rgba(26,26,46,0.5);line-height:1.6;">
                    学生活动部将在 5 个工作日内审核你的申请。<br>{f_name}，期待看到「{club_name}」出现在 ClubMatch 上。
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("回到首页", key="c_home", type="primary"):
                st.session_state.create_submitted = False
                go("home")

        if not all_ok and not st.session_state.get("create_submitted"):
            st.markdown('<div style="font-size:12px;color:rgba(26,26,46,0.28);text-align:center;margin-top:6px;">请填写所有必填项（*）</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 路由
# ══════════════════════════════════════════════════════════════
page = st.session_state.page
dispatch = {
    "home": page_home,
    "quiz": page_quiz,
    "results": page_results,
    "browse": page_browse,
    "chat": page_chat,
    "apply": page_apply,
    "success": page_success,
    "create": page_create,
}
dispatch.get(page, page_home)()
