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

# ─── 液态玻璃 + 全局样式 ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'PingFang SC', 'Noto Sans SC', sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* ── 隐藏 Streamlit 杂物 ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1200px; }
[data-testid="stSidebar"] { display: none; }

/* ── 背景：深蓝紫渐变，带光晕 ── */
.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(99,102,241,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(245,197,24,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 70% 60% at 50% 50%, rgba(139,92,246,0.08) 0%, transparent 70%),
        linear-gradient(160deg, #0a0a14 0%, #0d0d1a 40%, #0a0f0a 100%);
    color: #FFFFFF;
    min-height: 100vh;
}

/* ── 液态玻璃卡片 ── */
.glass {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(20px) saturate(160%);
    -webkit-backdrop-filter: blur(20px) saturate(160%);
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 16px;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    position: relative;
    overflow: hidden;
}
.glass::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
}
.glass:hover {
    background: rgba(255,255,255,0.09);
    border-color: rgba(255,255,255,0.22);
    transform: translateY(-3px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.35), 0 0 40px rgba(99,102,241,0.08);
}
.glass.featured {
    border-color: rgba(245,197,24,0.35);
    background: rgba(245,197,24,0.06);
    box-shadow: 0 0 40px rgba(245,197,24,0.06);
}
.glass.featured::before {
    background: linear-gradient(90deg, transparent, rgba(245,197,24,0.4), transparent);
}

/* ── 导航栏 ── */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0 22px 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 36px;
}
.logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 21px;
    font-weight: 900;
    letter-spacing: -0.5px;
}
.logo-badge {
    background: linear-gradient(135deg, #F5C518, #FF8C00);
    color: #0a0a14;
    border-radius: 10px;
    padding: 5px 10px;
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 0.3px;
}
.logo-accent { color: #F5C518; }

/* ── 徽章 ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 4px;
    margin-bottom: 4px;
}
.badge-y { background: rgba(245,197,24,0.18); color: #F5C518; border: 1px solid rgba(245,197,24,0.25); }
.badge-o { background: rgba(255,107,53,0.18); color: #FF8C61; border: 1px solid rgba(255,107,53,0.25); }
.badge-w { background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.7); border: 1px solid rgba(255,255,255,0.15); }
.badge-g { background: rgba(74,222,128,0.15); color: #4ADE80; border: 1px solid rgba(74,222,128,0.25); }

/* ── 进度条 ── */
.prog-wrap { margin-bottom: 28px; }
.prog-meta {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: rgba(255,255,255,0.4);
    margin-bottom: 8px;
    font-weight: 500;
}
.prog-meta span:last-child { color: #F5C518; font-weight: 700; }
.prog-track {
    height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 2px;
    overflow: hidden;
}
.prog-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #6366F1, #F5C518, #FF6B35);
    transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
}

/* ── 测评选项 ── */
.opt {
    background: rgba(255,255,255,0.05);
    border: 1.5px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 16px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 13px;
    transition: all 0.2s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.opt::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
}
.opt:hover {
    border-color: rgba(245,197,24,0.45);
    background: rgba(245,197,24,0.06);
}
.opt.sel {
    border-color: #F5C518;
    background: rgba(245,197,24,0.1);
    box-shadow: 0 0 20px rgba(245,197,24,0.1);
}
.opt-icon { font-size: 22px; margin-top: 1px; flex-shrink: 0; }
.opt-title { font-size: 14px; font-weight: 700; color: #fff; margin-bottom: 3px; }
.opt-sub { font-size: 12px; color: rgba(255,255,255,0.45); line-height: 1.4; }

/* ── 分数条 ── */
.score-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
}
.score-track {
    flex: 1;
    height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 2px;
    overflow: hidden;
}
.score-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #6366F1, #F5C518);
}
.score-pct { font-size: 13px; font-weight: 800; color: #F5C518; min-width: 38px; text-align: right; }

/* ── 统计数字 ── */
.stat-num { font-size: 28px; font-weight: 900; color: #F5C518; letter-spacing: -1.5px; line-height: 1; }
.stat-lbl { font-size: 11px; color: rgba(255,255,255,0.35); margin-top: 4px; font-weight: 500; }

/* ── 大标题 ── */
.hero-title {
    font-size: clamp(36px, 5vw, 60px);
    font-weight: 900;
    line-height: 1.06;
    letter-spacing: -2px;
    margin-bottom: 16px;
}
.hl {
    background: linear-gradient(135deg, #F5C518 0%, #FF6B35 60%, #A78BFA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 16px;
    color: rgba(255,255,255,0.52);
    line-height: 1.75;
    margin-bottom: 30px;
}
.eyebrow {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    color: #A5B4FC;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 18px;
}

/* ── Streamlit 按钮覆写 ── */
.stButton > button {
    border-radius: 50px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    transition: all 0.22s !important;
    letter-spacing: -0.1px !important;
    border: 1.5px solid rgba(255,255,255,0.2) !important;
    background: rgba(255,255,255,0.1) !important;
    color: #ffffff !important;
    padding: 0.45rem 1.1rem !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.18) !important;
    border-color: rgba(255,255,255,0.35) !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #F5C518, #FF8C00) !important;
    color: #0a0a14 !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(245,197,24,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #FFD700, #F5C518) !important;
    color: #0a0a14 !important;
    box-shadow: 0 8px 30px rgba(245,197,24,0.4) !important;
    transform: translateY(-2px) !important;
}

/* 禁用态按钮 */
.stButton > button:disabled {
    opacity: 0.35 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* ── 输入框 ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: rgba(255,255,255,0.07) !important;
    border: 1.5px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    font-family: 'Inter', 'PingFang SC', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(245,197,24,0.5) !important;
    box-shadow: 0 0 0 3px rgba(245,197,24,0.1) !important;
}

/* ── Checkbox ── */
.stCheckbox > label { color: rgba(255,255,255,0.8) !important; font-size: 14px !important; }

/* ── Radio ── */
.stRadio > label { color: rgba(255,255,255,0.7) !important; }

/* ── 多选框 ── */
.stMultiSelect > div { background: rgba(255,255,255,0.06) !important; border-radius: 14px !important; }

/* ── 对话气泡 ── */
.bubble-ai {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px 18px 18px 4px;
    padding: 13px 17px;
    font-size: 14px;
    line-height: 1.7;
    margin: 6px 0 6px 44px;
    color: rgba(255,255,255,0.88);
    white-space: pre-wrap;
    backdrop-filter: blur(10px);
}
.bubble-user {
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 18px 18px 4px 18px;
    padding: 13px 17px;
    font-size: 14px;
    line-height: 1.7;
    margin: 6px 44px 6px 0;
    color: rgba(255,255,255,0.88);
    text-align: right;
}
.chat-label {
    font-size: 11px;
    color: rgba(255,255,255,0.3);
    font-weight: 600;
    margin-bottom: 3px;
}

/* ── 分割线 ── */
.divider { border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 28px 0; }

/* ── 详情展开区 ── */
.detail-box {
    background: rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 6px;
    backdrop-filter: blur(10px);
}
.detail-section-title {
    font-size: 10px;
    font-weight: 700;
    color: rgba(255,255,255,0.3);
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
    color: rgba(255,255,255,0.65);
    margin-bottom: 7px;
    line-height: 1.5;
}

/* ── Vibe 标签 ── */
.vibe-tag {
    display: inline-block;
    background: rgba(163,117,255,0.12);
    border: 1px solid rgba(163,117,255,0.2);
    color: #C084FC;
    border-radius: 8px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 12px;
    font-style: italic;
}

/* ── 成功页 ── */
.success-glass {
    background: rgba(74,222,128,0.06);
    border: 1px solid rgba(74,222,128,0.2);
    border-radius: 24px;
    padding: 40px;
    text-align: center;
    backdrop-filter: blur(20px);
}

/* ── 申请表单 ── */
.form-section {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 20px 22px;
    margin-bottom: 14px;
    backdrop-filter: blur(10px);
}
.form-section-title {
    font-size: 12px;
    font-weight: 700;
    color: rgba(255,255,255,0.35);
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 14px;
}

/* 滚动条 */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 2px; }

/* selectbox 文字颜色 */
.stSelectbox div[data-baseweb="select"] span { color: rgba(255,255,255,0.8) !important; }
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
        # 报名相关
        "cart": [],            # 加入购物车的社团 id 列表
        "applications": [],    # 已提交的报名记录
        "apply_form": {},      # 当前填写的表单
        # 对话
        "chat_history": [],
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()


# ─── 工具 ───────────────────────────────────────────────────
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


# ─── 导航栏 ─────────────────────────────────────────────────
def render_nav():
    cart_count = len(st.session_state.cart)
    cart_str = f" ({cart_count})" if cart_count else ""
    st.markdown(f"""
    <div class="navbar">
        <div class="logo">
            <span class="logo-badge">CM</span>
            Club<span class="logo-accent">Match</span>
        </div>
        <div style="font-size:12px; color:rgba(255,255,255,0.28); font-weight:500; letter-spacing:0.3px;">
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
        (f"📋", f"我的申请{cart_str}", "apply"),
        ("✨", "申请创建", "create"),
    ]
    for col, (icon, label, pg) in zip(tab_cols, labels):
        with col:
            is_active = st.session_state.page == pg
            if st.button(f"{icon} {label}", key=f"nav_{pg}",
                         type="primary" if is_active else "secondary",
                         use_container_width=True):
                go(pg)


# ─── 分数条 ─────────────────────────────────────────────────
def score_bar(score):
    st.markdown(f"""
    <div class="score-row">
        <span style="font-size:11px; color:rgba(255,255,255,0.35); min-width:36px;">匹配度</span>
        <div class="score-track"><div class="score-fill" style="width:{score}%;"></div></div>
        <span class="score-pct">{score}%</span>
    </div>
    """, unsafe_allow_html=True)

def tags_html(club):
    h = ""
    for t in club["tags"]:
        h += f'<span class="badge badge-y">{t}</span>'
    return h


# ─── AI 匹配 ────────────────────────────────────────────────
def local_score(answers):
    result = []
    for c in CLUBS:
        s = c["score_base"]
        a0 = answers.get(0)
        if a0 == 0 and c["id"] in [1,2,10]: s += 12
        if a0 == 1 and c["id"] in [4,11]:   s += 12
        if a0 == 2 and c["id"] in [3,10,12]: s += 10
        if a0 == 3 and c["id"] in [6,12]:   s += 12
        a1 = answers.get(1)
        if a1 == 0 and c["id"] in [5,8]:    s += 10
        if a1 == 1 and c["id"] in [4,11]:   s += 12
        if a1 == 2 and c["id"] in [1,2,8]:  s += 8
        if a1 == 3 and c["id"] in [6,7]:    s += 8
        a2 = answers.get(2)
        if a2 == 0 and c["id"] in [1,2]:    s += 12
        if a2 == 1 and c["id"] in [4,5,8]:  s += 10
        if a2 == 2 and c["id"] in [3,9]:    s += 12
        if a2 == 3 and c["id"] in [6,12]:   s += 12
        a3 = answers.get(3)
        if a3 == 0 and c["id"] in [1,2,8]:  s += 8
        if a3 == 1 and c["id"] in [5,8]:    s += 8
        if a3 == 2 and c["id"] in [7,11]:   s += 8
        if a3 == 3 and c["id"] in [4,9]:    s += 8
        a4 = answers.get(4)
        low  = ["低","中等"]
        mid  = ["中等"]
        high = ["较高","高"]
        all_ = ["低","中等","较高","高"]
        pref = {0:low, 1:mid, 2:high, 3:all_}
        if c["time_cost"] in pref.get(a4, []): s += 6
        a5 = answers.get(5)
        if a5 == 0 and c["id"] in [1,2,8]:  s += 6
        if a5 == 1 and c["id"] in [6,7,11]: s += 6
        if a5 == 2 and c["id"] in [5,8,10]: s += 6
        if a5 == 3 and c["id"] in [3,9,4]:  s += 6
        result.append({**c, "match_score": min(96, s)})
    return sorted(result, key=lambda x: -x["match_score"])

def ai_match(answers):
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return local_score(answers), None
        client = anthropic.Anthropic(api_key=api_key)
        ans_desc = "\n".join([
            f"问题{i+1}「{QUESTIONS[i]['q']}」→ {QUESTIONS[i]['opts'][answers.get(i,0)]['title']}"
            for i in range(len(QUESTIONS))
        ])
        prompt = f"""你是大学社团匹配顾问。根据用户测评，为12个社团打匹配分（0-100整数），给出最高匹配社团的一句话原因（温暖人性化，不超过40字）。

用户测评：
{ans_desc}

社团：
{chr(10).join([f"{c['id']}. {c['name']}（{c['type']}）" for c in CLUBS])}

只返回JSON：{{"scores":{{"1":85,...,"12":60}},"reason":"..."}}"""
        msg = client.messages.create(
            model="claude-opus-4-5", max_tokens=400,
            messages=[{"role":"user","content":prompt}]
        )
        text = msg.content[0].text.strip().replace("```json","").replace("```","").strip()
        parsed = json.loads(text)
        scores = parsed.get("scores", {})
        result = [{**c, "match_score": min(96, int(scores.get(str(c["id"]), c["score_base"])))} for c in CLUBS]
        return sorted(result, key=lambda x: -x["match_score"]), parsed.get("reason")
    except Exception:
        return local_score(answers), None

def chat_ai(user_msg):
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "（需要配置 API Key 才能使用 AI 顾问，不过你可以直接去「发现社团」页面浏览，或者完成测评获取推荐～）"
        client = anthropic.Anthropic(api_key=api_key)
        system = f"""你是 ClubMatch 平台的 AI 社团顾问，帮助大学新生找到适合的社团。
风格：简洁、温暖、真实，给具体有用的建议，不废话，用中文，适当换行。

社团数据（共12个）：
{chr(10).join([f"- {c['name']}（{c['type']}）：{c['desc']} | 成员{c['members']}人，评分{c['rating']}，时间投入：{c['time_cost']}" for c in CLUBS])}"""
        history = []
        for t in st.session_state.chat_history:
            if t.get("user"): history.append({"role":"user","content":t["user"]})
            if t.get("ai"):   history.append({"role":"assistant","content":t["ai"]})
        history.append({"role":"user","content":user_msg})
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
            if st.button("🎯  开始 3 分钟测评", key="h_start", type="primary", use_container_width=True):
                st.session_state.quiz_step = 0
                st.session_state.quiz_answers = {}
                go("quiz")
        with b2:
            if st.button("🔍  逛逛所有社团", key="h_browse", use_container_width=True):
                go("browse")

        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        for col,(n,l) in zip([c1,c2,c3,c4],[("12","入驻社团"),("3,200+","在校成员"),("94%","匹配满意度"),("3分钟","完成测评")]):
            with col:
                st.markdown(f'<div style="text-align:center;"><div class="stat-num">{n}</div><div class="stat-lbl">{l}</div></div>', unsafe_allow_html=True)

    with col_r:
        # 英雄卡片
        top = CLUBS[0]
        st.markdown(f"""
        <div class="glass featured" style="margin-top:4px;">
            <div style="position:absolute;top:-30px;right:-30px;width:120px;height:120px;
                background:radial-gradient(circle,rgba(245,197,24,0.15),transparent 70%);
                border-radius:50%;pointer-events:none;"></div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
                <div style="font-size:44px;">{top['emoji']}</div>
                <div style="text-align:right;">
                    <div style="font-size:40px;font-weight:900;color:#F5C518;letter-spacing:-2px;line-height:1;">92%</div>
                    <div style="font-size:10px;color:rgba(255,255,255,0.3);margin-top:2px;">AI 示例匹配度</div>
                </div>
            </div>
            <div style="font-size:18px;font-weight:800;letter-spacing:-0.4px;margin-bottom:4px;">{top['name']}</div>
            <div class="vibe-tag">{top['vibe']}</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.5);line-height:1.6;margin-bottom:14px;">{top['desc']}</div>
            <div style="margin-bottom:14px;">{tags_html(top)}<span class="badge badge-o">热门</span></div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
                {''.join([f'<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:10px;text-align:center;"><div style="font-size:14px;font-weight:800;">{v}</div><div style="font-size:10px;color:rgba(255,255,255,0.3);margin-top:2px;">{l}</div></div>' for v,l in [(top['members'],'成员'),('⭐'+str(top['rating']),'评分'),(str(top['awards'])+'项','获奖')]])}
            </div>
        </div>
        <div style="text-align:center;font-size:12px;color:rgba(255,255,255,0.2);margin-top:8px;">
            🟢 &nbsp;本周已有 86 位新生完成匹配
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # 为什么要用 ClubMatch
    st.markdown('<div style="text-align:center;margin-bottom:28px;"><div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#A5B4FC;text-transform:uppercase;margin-bottom:10px;">我们不一样</div><div style="font-size:26px;font-weight:900;letter-spacing:-0.8px;">不是随机，是属于你的那个</div></div>', unsafe_allow_html=True)

    cols = st.columns(3, gap="medium")
    features = [
        ("🧬", "真实的你，真实的匹配", "我们问的不是「你有什么爱好」，而是「你周末真的会做什么」——6 道情景题，比你自己更了解你适合哪种氛围。"),
        ("📊", "社团数据全透明", "成员活跃度、时间投入、历年评价……在你加入之前，我们让数据替你把关。"),
        ("🤝", "不合适？可以创建新的", "如果你有个想法、找不到对应的社团，直接在这里申请创建——也许你就是下一个领头人。"),
    ]
    for col,(icon,title,desc) in zip(cols,features):
        with col:
            st.markdown(f"""
            <div class="glass" style="min-height:160px;">
                <div style="font-size:28px;margin-bottom:14px;">{icon}</div>
                <div style="font-size:15px;font-weight:800;letter-spacing:-0.3px;margin-bottom:8px;">{title}</div>
                <div style="font-size:13px;color:rgba(255,255,255,0.45);line-height:1.65;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # 今日精选社团（随机展示3个）
    import random
    picks = random.sample(CLUBS, 3)
    st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#A5B4FC;text-transform:uppercase;margin-bottom:10px;">✦ 今日精选</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:22px;font-weight:900;letter-spacing:-0.6px;margin-bottom:20px;">随便逛逛，说不定就遇上了</div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    for col,club in zip(cols,picks):
        with col:
            st.markdown(f"""
            <div class="glass">
                <div style="font-size:36px;margin-bottom:10px;">{club['emoji']}</div>
                <div style="font-size:16px;font-weight:800;letter-spacing:-0.3px;margin-bottom:3px;">{club['name']}</div>
                <div class="vibe-tag">{club['vibe']}</div>
                <div style="font-size:13px;color:rgba(255,255,255,0.45);line-height:1.55;margin-bottom:12px;">{club['desc'][:55]}...</div>
                <div>{tags_html(club)}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("了解更多", key=f"home_club_{club['id']}", use_container_width=True):
                st.session_state.expand_club = club["id"]
                go("browse")

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1,2,1])
    with mid:
        if st.button("✨  还没找到感觉？来做个测评吧 →", key="home_cta2", type="primary", use_container_width=True):
            st.session_state.quiz_step = 0
            st.session_state.quiz_answers = {}
            go("quiz")


# ══════════════════════════════════════════════════════════════
# 测评页
# ══════════════════════════════════════════════════════════════
def page_quiz():
    render_nav()

    step = st.session_state.quiz_step
    total = len(QUESTIONS)
    q = QUESTIONS[step]
    pct = int(step / total * 100)

    st.markdown(f"""
    <div class="prog-wrap">
        <div class="prog-meta">
            <span>问题 {step+1} / {total}</span>
            <span>{pct}%</span>
        </div>
        <div class="prog-track"><div class="prog-fill" style="width:{pct}%;"></div></div>
    </div>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([0.5, 4, 0.5])
    with mid:
        st.markdown(f'<div style="font-size:11px;font-weight:700;color:#A5B4FC;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:10px;">第 {step+1} 题</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:clamp(20px,3vw,28px);font-weight:900;letter-spacing:-0.8px;line-height:1.25;margin-bottom:6px;">{q["q"]}</div>', unsafe_allow_html=True)
        if q["hint"]:
            st.markdown(f'<div style="font-size:13px;color:rgba(255,255,255,0.32);margin-bottom:22px;font-style:italic;">{q["hint"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)

        cur = st.session_state.quiz_answers.get(step)
        row1 = st.columns(2, gap="small")
        row2 = st.columns(2, gap="small")
        all_cols = list(row1) + list(row2)

        for i, (col, opt) in enumerate(zip(all_cols, q["opts"])):
            with col:
                is_sel = cur == i
                sel_style = "border: 1.5px solid #F5C518; background: rgba(245,197,24,0.1);" if is_sel else ""
                st.markdown(f"""
                <div class="opt {'sel' if is_sel else ''}" style="{sel_style}">
                    <div class="opt-icon">{opt['icon']}</div>
                    <div>
                        <div class="opt-title">{opt['title']}</div>
                        <div class="opt-sub">{opt['sub']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"{'✓ ' if is_sel else ''}{opt['title']}", key=f"q{step}_o{i}", use_container_width=True,
                             type="primary" if is_sel else "secondary"):
                    st.session_state.quiz_answers[step] = i
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        nav_l, nav_r = st.columns(2, gap="small")
        with nav_l:
            if st.button("← " + ("返回首页" if step == 0 else "上一题"), key="q_back", use_container_width=True):
                if step == 0: go("home")
                else:
                    st.session_state.quiz_step -= 1
                    st.rerun()
        with nav_r:
            done = step in st.session_state.quiz_answers
            label = "查看我的匹配结果 →" if step == total-1 else "下一题 →"
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

    st.markdown('<div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#F5C518;text-transform:uppercase;margin-bottom:10px;">✦ 你的专属匹配报告</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:clamp(24px,4vw,38px);font-weight:900;letter-spacing:-1.2px;margin-bottom:10px;">AI 从 12 个社团里，为你挑出了这些</div>', unsafe_allow_html=True)

    if reason:
        st.markdown(f"""
        <div style="background:rgba(245,197,24,0.06);border:1px solid rgba(245,197,24,0.2);border-radius:14px;padding:14px 18px;font-size:14px;color:rgba(255,255,255,0.75);line-height:1.65;margin-bottom:24px;">
            <span style="color:#F5C518;font-weight:700;">✦ AI 分析：</span>{reason}
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

            st.markdown(f"""
            <div class="glass {'featured' if idx==0 else ''}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                    <div style="font-size:36px;">{club['emoji']}</div>
                    <span class="badge {bc}">{bl}</span>
                </div>
                <div style="font-size:16px;font-weight:800;letter-spacing:-0.3px;margin-bottom:2px;">{club['name']}</div>
                <div style="font-size:11px;color:rgba(255,255,255,0.35);margin-bottom:10px;">{club['type']} · {club['freq']}</div>
            """, unsafe_allow_html=True)
            score_bar(club["match_score"])
            st.markdown(f"""
                <div class="vibe-tag">{club['vibe']}</div>
                <div style="font-size:13px;color:rgba(255,255,255,0.5);line-height:1.55;margin-bottom:12px;">{club['desc'][:58]}...</div>
                <div style="margin-bottom:14px;">{tags_html(club)}{('<span class="badge badge-g">✓ 已报名</span>' if applied else '')}</div>
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
    st.markdown(f"""
    <div class="detail-box">
        <div class="detail-section-title">关于我们</div>
        <div style="font-size:13px;color:rgba(255,255,255,0.65);line-height:1.7;margin-bottom:4px;">{club['detail']}</div>
        <div class="detail-section-title">这个社团最适合</div>
        <div style="font-size:13px;color:rgba(255,255,255,0.65);margin-bottom:4px;">→ {club['best_for']}</div>
        <div class="detail-section-title">招新要求</div>
        {''.join([f'<div class="req-row"><span style="color:#F5C518;margin-top:2px;flex-shrink:0;">·</span><span>{r}</span></div>' for r in club['requirements']])}
        <div class="detail-section-title">主要活动</div>
        {''.join([f'<div class="req-row"><span style="color:#FF6B35;margin-top:2px;flex-shrink:0;">·</span><span>{a}</span></div>' for a in club['activities']])}
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:14px;">
            {''.join([f'<div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:10px;text-align:center;"><div style="font-size:14px;font-weight:800;">{v}</div><div style="font-size:10px;color:rgba(255,255,255,0.3);margin-top:2px;">{l}</div></div>' for v,l in [(str(club['members']),'成员'),('⭐'+str(club['rating']),'评分'),(str(club['awards'])+'项','获奖'),(club['time_cost'],'时间投入')]])}
        </div>
        {'<div style="margin-top:12px;padding:10px 14px;background:rgba(74,222,128,0.08);border:1px solid rgba(74,222,128,0.2);border-radius:10px;font-size:12px;color:#4ADE80;text-align:center;">✓ 你已报名这个社团</div>' if applied else ''}
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 发现社团页
# ══════════════════════════════════════════════════════════════
def page_browse():
    render_nav()

    st.markdown('<div style="font-size:26px;font-weight:900;letter-spacing:-0.8px;margin-bottom:4px;">发现社团</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px;color:rgba(255,255,255,0.4);margin-bottom:20px;">12 个社团，总有一个在等你</div>', unsafe_allow_html=True)

    col_s, col_f = st.columns([2,1])
    with col_s:
        search = st.text_input("", placeholder="🔍  搜索名称、类型、标签...", label_visibility="collapsed", key="b_search")
    with col_f:
        types = ["全部类型"] + sorted(list({c["type"] for c in CLUBS}))
        sel_type = st.selectbox("", types, label_visibility="collapsed", key="b_type")

    filtered = [
        c for c in CLUBS
        if (not search or search in c["name"] or search in c["type"] or any(search in t for t in c["tags"]) or search in c["desc"])
        and (sel_type == "全部类型" or c["type"] == sel_type)
    ]

    if not filtered:
        st.markdown('<div style="text-align:center;padding:60px;color:rgba(255,255,255,0.25);">没找到……换个关键词试试？</div>', unsafe_allow_html=True)
        return

    cols = st.columns(3, gap="small")
    for idx, club in enumerate(filtered):
        with cols[idx % 3]:
            applied = already_applied(club["id"])
            in_c = in_cart(club["id"])
            st.markdown(f"""
            <div class="glass">
                <div style="font-size:36px;margin-bottom:10px;">{club['emoji']}</div>
                <div style="font-size:16px;font-weight:800;letter-spacing:-0.3px;margin-bottom:2px;">{club['name']}</div>
                <div style="font-size:11px;color:rgba(255,255,255,0.35);margin-bottom:8px;">{club['type']} · 成立 {club['founded']}</div>
                <div class="vibe-tag">{club.get('vibe', '暂无标签')}</div>
                <div style="font-size:13px;color:rgba(255,255,255,0.5);line-height:1.55;margin-bottom:12px;">{club['desc'][:62]}...</div>
                <div style="margin-bottom:12px;">{tags_html(club)}{('<span class="badge badge-g">✓ 已报名</span>' if applied else '')}{('<span class="badge badge-y">在申请袋中</span>' if in_c and not applied else '')}</div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid rgba(255,255,255,0.07);padding-top:12px;">
                    {''.join([f'<div style="text-align:center;"><div style="font-size:13px;font-weight:800;">{v}</div><div style="font-size:10px;color:rgba(255,255,255,0.3);margin-top:2px;">{l}</div></div>' for v,l in [(str(club['members']),'成员'),('⭐'+str(club['rating']),'评分'),(str(club['awards'])+'项','获奖')]])}
                </div>
            </div>
            """, unsafe_allow_html=True)

            b1, b2 = st.columns(2, gap="small")
            with b1:
                exp = st.session_state.expand_club == club["id"]
                if st.button("收起 ↑" if exp else "查看详情", key=f"b_det_{club['id']}_{idx}", use_container_width=True):
                    st.session_state.expand_club = club["id"] if not exp else None; st.rerun()
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
    _, mid, _ = st.columns([1,2,1])
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
    st.markdown('<div style="font-size:24px;font-weight:900;letter-spacing:-0.6px;margin-bottom:4px;">AI 社团顾问</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px;color:rgba(255,255,255,0.35);margin-bottom:24px;">由 Claude AI 驱动 · 随时回答关于社团的任何疑问</div>', unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.session_state.chat_history = [{"user": None, "ai": "嗨！我是 ClubMatch AI 顾问 👋\n\n我对平台上所有 12 个社团都了如指掌。你可以问我：\n· 某个社团的具体情况和氛围\n· 根据你的情况给个性化推荐\n· 「内向的人适合哪个」「我时间不多怎么选」……\n\n随便问吧，没有奇怪的问题。"}]

    for turn in st.session_state.chat_history:
        if turn.get("user"):
            st.markdown(f'<div style="text-align:right;" class="chat-label">你</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bubble-user">{turn["user"]}</div>', unsafe_allow_html=True)
        if turn.get("ai"):
            st.markdown(f'<div class="chat-label">🤖  AI 顾问</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bubble-ai">{turn["ai"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if len(st.session_state.chat_history) <= 1:
        st.markdown('<div style="font-size:12px;color:rgba(255,255,255,0.28);margin-bottom:8px;">快捷问题，点一下就能问</div>', unsafe_allow_html=True)
        sugg = ["内向的人适合哪个社团？","我时间不多，选哪个好？","摄影社和电影社有啥区别？","创业社真的有用吗？","不知道自己喜欢什么怎么办？","哪个社团竞争最激烈？"]
        cols = st.columns(3, gap="small")
        for i, s in enumerate(sugg):
            with cols[i % 3]:
                if st.button(s, key=f"sugg_{i}", use_container_width=True):
                    with st.spinner("思考中..."):
                        rep = chat_ai(s)
                    st.session_state.chat_history.append({"user": s, "ai": rep}); st.rerun()

    col_i, col_s = st.columns([5,1])
    with col_i:
        user_input = st.text_input("", placeholder="问我任何关于社团的事...", label_visibility="collapsed", key="chat_inp")
    with col_s:
        send = st.button("发送 →", key="chat_send", type="primary", use_container_width=True)

    if send and user_input.strip():
        with st.spinner("AI 思考中..."):
            rep = chat_ai(user_input.strip())
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
        st.markdown('<div style="text-align:center;padding:80px 40px;">', unsafe_allow_html=True)
        st.markdown("### 申请袋是空的")
        st.markdown('<div style="color:rgba(255,255,255,0.4);margin-bottom:24px;">先去发现社团，把感兴趣的加进申请袋再来这里～</div>', unsafe_allow_html=True)
        if st.button("去发现社团", type="primary"): go("browse")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown('<div style="font-size:26px;font-weight:900;letter-spacing:-0.8px;margin-bottom:4px;">提交申请</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:14px;color:rgba(255,255,255,0.4);margin-bottom:24px;">你选择了 {len(cart)} 个社团，一次提交全搞定</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1.2, 1], gap="large")

    with col_l:
        # 已选社团展示
        st.markdown('<div class="form-section"><div class="form-section-title">你的申请袋</div>', unsafe_allow_html=True)
        for cid in cart:
            club = club_by_id(cid)
            if club:
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="font-size:22px;">{club['emoji']}</span>
                        <div>
                            <div style="font-size:14px;font-weight:700;">{club['name']}</div>
                            <div style="font-size:11px;color:rgba(255,255,255,0.35);">{club['type']} · {club['freq']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"移除", key=f"apply_rm_{cid}"):
                    toggle_cart(cid); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # 可以继续添加
        st.markdown('<div style="margin-top:8px;">', unsafe_allow_html=True)
        if st.button("+ 继续添加社团", key="apply_more", use_container_width=True):
            go("browse")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="form-section"><div class="form-section-title">个人信息</div>', unsafe_allow_html=True)

        name = st.text_input("你的姓名 *", placeholder="请输入真实姓名", key="form_name")
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

        # 提交
        all_filled = all([name.strip(), student_id.strip(), major.strip(), grade != "请选择", phone.strip(), intro.strip()])

        if st.button("🎉  提交所有申请", key="apply_submit", type="primary", use_container_width=True, disabled=not all_filled):
            record = {
                "clubs": list(cart),
                "name": name, "student_id": student_id,
                "major": major, "grade": grade,
                "phone": phone, "wechat": wechat,
                "intro": intro, "time_avail": time_avail, "skill": skill,
            }
            st.session_state.applications.append(record)
            st.session_state.cart = []
            go("success")

        if not all_filled:
            st.markdown('<div style="font-size:12px;color:rgba(255,255,255,0.3);text-align:center;margin-top:6px;">请填写所有必填项后提交</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 成功页
# ══════════════════════════════════════════════════════════════
def page_success():
    render_nav()
    # 取最近一次申请
    if not st.session_state.applications:
        go("home"); return

    last = st.session_state.applications[-1]
    club_names = [club_by_id(cid)["name"] for cid in last["clubs"] if club_by_id(cid)]

    _, col, _ = st.columns([0.5, 3, 0.5])
    with col:
        st.markdown(f"""
        <div class="success-glass">
            <div style="font-size:56px;margin-bottom:16px;">🎉</div>
            <div style="font-size:30px;font-weight:900;letter-spacing:-1px;margin-bottom:10px;">申请已成功提交！</div>
            <div style="font-size:15px;color:rgba(255,255,255,0.55);line-height:1.75;margin-bottom:24px;">
                {last['name']}，欢迎你迈出这一步。<br>
                接下来，等着被发现吧。
            </div>
            <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:14px;padding:18px;text-align:left;margin-bottom:24px;">
                <div style="font-size:11px;color:rgba(255,255,255,0.3);font-weight:700;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:12px;">你申请的社团</div>
                {''.join([f'<div style="display:flex;align-items:center;gap:8px;font-size:14px;color:rgba(255,255,255,0.75);margin-bottom:8px;"><span style="color:#4ADE80;">✓</span>{n}</div>' for n in club_names])}
            </div>
            <div style="background:rgba(255,255,255,0.04);border-radius:12px;padding:16px;text-align:left;">
                <div style="font-size:11px;color:rgba(255,255,255,0.3);font-weight:700;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:10px;">接下来</div>
                {''.join([f'<div style="display:flex;align-items:center;gap:10px;font-size:13px;color:rgba(255,255,255,0.6);margin-bottom:8px;"><div style="width:20px;height:20px;border-radius:50%;background:rgba(245,197,24,0.15);color:#F5C518;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;">{i+1}</div><span>{s}</span></div>' for i,s in enumerate(['社团负责人将在 3 个工作日内通过你留的手机号联系你','注意查收短信或微信','提前想想自我介绍，见面第一印象很重要 😊'])])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
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
    st.markdown('<div style="font-size:28px;font-weight:900;letter-spacing:-0.8px;margin-bottom:8px;">申请创建新社团</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:15px;color:rgba(255,255,255,0.45);line-height:1.7;margin-bottom:28px;">每一个存在的社团，都是某个人第一次说「我想做这件事」。<br>如果你有个想法，这里是它开始的地方。</div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1,1], gap="large")

    with col_l:
        st.markdown('<div class="form-section"><div class="form-section-title">社团基本信息</div>', unsafe_allow_html=True)
        club_name = st.text_input("你想创建的社团叫什么？*", placeholder="例：城市骑行与街拍社", key="c_name")
        club_type = st.selectbox("社团类型 *", ["请选择", "艺术创作", "音乐表演", "舞台表演", "科技创新", "商业创新", "户外运动", "人文学术", "公益服务", "体育竞技", "跨文化交流", "科学探索", "其他"], key="c_type")
        club_desc = st.text_area("用一两句话，说说这个社团是做什么的 *", placeholder="让别人在 5 秒内听懂这个社团，别用太多形容词，说具体的事。", height=80, key="c_desc")
        club_why = st.text_area("为什么这个社团值得存在？你发现了什么需求？*", placeholder="比如：我发现学校没有专注城市骑行的社团，但身边有很多同学想要这个……", height=100, key="c_why")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-section" style="margin-top:10px;"><div class="form-section-title">你的构想</div>', unsafe_allow_html=True)
        activity_plan = st.text_area("你打算做哪些活动或项目？", placeholder="大概说说你的活动构想，哪怕很初期的想法也可以", height=90, key="c_plan")
        target_members = st.slider("你预计招募多少初始成员？", 5, 50, 15, key="c_members")
        freq_plan = st.selectbox("计划的活动频率", ["每周一次", "每两周一次", "每月一次", "视项目而定", "还没想好"], key="c_freq")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="form-section"><div class="form-section-title">发起人信息</div>', unsafe_allow_html=True)
        f_name = st.text_input("你的姓名 *", key="c_fname")
        f_sid = st.text_input("学号 *", key="c_fsid")
        f_major = st.text_input("专业 *", key="c_fmajor")
        f_grade = st.selectbox("年级 *", ["请选择","大一","大二","大三","大四","研究生"], key="c_fgrade")
        f_phone = st.text_input("联系方式 *", key="c_fphone")
        f_exp = st.text_area("你有哪些相关经历或能力？（选填）", placeholder="比如：你本身就是这个领域的爱好者？做过类似的组织工作？", height=80, key="c_fexp")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-section" style="margin-top:10px;"><div class="form-section-title">AI 帮你完善方案</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px;color:rgba(255,255,255,0.45);line-height:1.6;margin-bottom:14px;">填完上面的基本信息后，可以点这里让 AI 给你的创建方案提一些建议——可能对你写申请书很有帮助。</div>', unsafe_allow_html=True)

        if st.button("🤖  让 AI 给我点建议", key="c_ai_suggest", use_container_width=True):
            if club_name and club_desc and club_why:
                with st.spinner("AI 思考中..."):
                    try:
                        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
                        if api_key:
                            client = anthropic.Anthropic(api_key=api_key)
                            msg = client.messages.create(
                                model="claude-opus-4-5", max_tokens=500,
                                messages=[{"role":"user","content":f"""一位大学生想创建社团：
名称：{club_name}
类型：{club_type}
描述：{club_desc}
创建原因：{club_why}
活动计划：{activity_plan}

请给出3条简短、具体、有用的建议，帮助他完善社团方案。风格温暖鼓励，不用markdown标题，直接分点。"""}]
                            )
                            suggestion = msg.content[0].text
                        else:
                            suggestion = "1. 把你的核心活动再具体化——「每月一次骑行」比「定期活动」更有说服力。\n2. 考虑一下如何区分于现有社团，你的独特价值是什么？\n3. 找 2-3 个有同样想法的人一起发起，审核委员会会看得更认真。"
                        st.markdown(f'<div class="bubble-ai">✦ AI 建议：\n\n{suggestion}</div>', unsafe_allow_html=True)
                    except Exception:
                        st.info("AI 暂时不可用，但你的想法很棒，继续填写吧！")
            else:
                st.warning("先填写社团名称、描述和创建原因，AI 才能给出有用的建议～")
        st.markdown('</div>', unsafe_allow_html=True)

        # 提交
        all_ok = all([club_name, club_type != "请选择", club_desc, club_why, f_name, f_sid, f_major, f_grade != "请选择", f_phone])
        if st.button("🚀  提交创建申请", key="c_submit", type="primary", use_container_width=True, disabled=not all_ok):
            st.session_state.create_submitted = True
            st.rerun()

        if st.session_state.get("create_submitted"):
            st.markdown(f"""
            <div style="margin-top:14px;background:rgba(74,222,128,0.08);border:1px solid rgba(74,222,128,0.2);border-radius:14px;padding:16px;text-align:center;">
                <div style="font-size:22px;margin-bottom:8px;">🌱</div>
                <div style="font-size:15px;font-weight:700;margin-bottom:6px;">申请已提交！</div>
                <div style="font-size:13px;color:rgba(255,255,255,0.5);line-height:1.6;">
                    学生活动部将在 5 个工作日内审核你的申请。<br>
                    {f_name}，期待看到「{club_name}」出现在 ClubMatch 上。
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("回到首页", key="c_home", type="primary"):
                st.session_state.create_submitted = False
                go("home")

        if not all_ok and not st.session_state.get("create_submitted"):
            st.markdown('<div style="font-size:12px;color:rgba(255,255,255,0.25);text-align:center;margin-top:6px;">请填写所有必填项（*）</div>', unsafe_allow_html=True)


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