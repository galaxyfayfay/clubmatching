import streamlit as st
import anthropic
import json
import random
from data import CLUBS, QUESTIONS

# ── 页面配置 ────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClubMatch · 找到属于你的圈子",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 全局 CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
/* ══ 问卷选项动态特效 ══ */
@keyframes selPop {
    0%   { transform: translateY(0) scale(1); }
    40%  { transform: translateY(-4px) scale(1.06); }
    70%  { transform: translateY(-2px) scale(1.02); }
    100% { transform: translateY(-2px) scale(1.03); }
}
@keyframes glowPulse {
    0%, 100% { box-shadow: 0 0 0 3px rgba(99,102,241,0.35), 0 12px 35px rgba(99,102,241,0.40); }
    50%       { box-shadow: 0 0 0 5px rgba(99,102,241,0.50), 0 16px 45px rgba(99,102,241,0.55); }
}
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────
def init():
    defaults = {
        "page": "home",
        "quiz_step": 0,
        "quiz_answers": {},
        "results": None,
        "ai_reason": None,
        "expand_club": None,
        "cart": [],
        "applications": [],
        "chat_history": [],
        "create_submitted": False,
        "ai_suggestion": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

# ── 工具函数 ──────────────────────────────────────────────
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

# ── 导航栏 ──────────────────────────────────────────────
def render_nav():
    cart_n = len(st.session_state.cart)
    cart_str = f" ({cart_n})" if cart_n else ""
    st.markdown(
        '<div style="display:flex;align-items:center;gap:12px;padding:18px 0 8px 0;margin-bottom:4px;">'
        '<div style="width:38px;height:38px;background:linear-gradient(135deg,#6366F1,#8B5CF6);'
        'border-radius:10px;display:flex;align-items:center;justify-content:center;'
        'color:#fff;font-weight:900;font-size:1rem;">CM</div>'
        '<div style="line-height:1.1;">'
        '<span style="font-weight:900;font-size:1.15rem;color:#1a1a2e;">Club</span>'
        '<span style="font-weight:900;font-size:1.15rem;color:#6366F1;">Match</span>'
        '</div>'
        '<div style="margin-left:auto;font-size:0.78rem;color:#9ca3af;">'
        '每个人都值得找到属于自己的圈子'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    cols = st.columns(6, gap="small")
    tabs = [
        ("🏠", "首页", "home"),
        ("🧠", "匹配测评", "quiz"),
        ("🔍", "发现社团", "browse"),
        ("🤖", "AI 顾问", "chat"),
        ("📋", f"我的申请{cart_str}", "apply"),
        ("✨", "申请创建", "create"),
    ]
    for col, (icon, label, pg) in zip(cols, tabs):
        with col:
            active = st.session_state.page == pg
            if st.button(f"{icon} {label}", key=f"nav_{pg}",
                         type="primary" if active else "secondary",
                         use_container_width=True):
                go(pg)

# ── 分数条 ──────────────────────────────────────────────
def score_bar(score):
    st.markdown(
        f'<div style="margin:8px 0 12px;">'
        f'<div style="display:flex;justify-content:space-between;'
        f'font-size:0.75rem;color:#6b7280;margin-bottom:4px;">'
        f'<span>匹配度</span><span style="color:#6366F1;font-weight:700;">{score}%</span></div>'
        f'<div style="height:6px;background:#f0f0ff;border-radius:99px;overflow:hidden;">'
        f'<div style="width:{score}%;height:100%;'
        f'background:linear-gradient(90deg,#6366F1,#A78BFA);border-radius:99px;"></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

def tags_html(club):
    return "".join(
        f'<span style="display:inline-block;background:rgba(99,102,241,0.08);'
        f'color:#6366F1;border-radius:99px;padding:2px 10px;font-size:0.72rem;'
        f'font-weight:600;margin:2px 3px 2px 0;">{t}</span>'
        for t in club.get("tags", [])
    )

def stat_cell(v, l, bg="rgba(99,102,241,0.05)", border="rgba(99,102,241,0.10)"):
    return (
        f'<div style="background:{bg};border:1px solid {border};'
        f'border-radius:10px;padding:10px 14px;text-align:center;flex:1;">'
        f'<div style="font-weight:800;font-size:1.05rem;color:#1a1a2e;">{v}</div>'
        f'<div style="font-size:0.72rem;color:#9ca3af;margin-top:2px;">{l}</div>'
        f'</div>'
    )

# ── AI 函数 ───────────────────────────────────────────────
CLAUDE_SELF_INTRO = """你是 Claude，由 Anthropic 创造的 AI。
你是 ClubMatch 平台的 AI 顾问，专门帮助大学新生找到最适合自己的社团。
你知道自己是 Claude，可以在对话中自然地提及这一点。
你的性格：温暖、直接、有洞察力，不说废话，给出具体可执行的建议。
你理解大学生活的不确定感，也理解选择社团时的迷茫——用真实的共情回应，而不是套话。
当用户问到你是谁时，告诉他们你是 Claude，ClubMatch 的 AI 顾问，由 Anthropic 训练。"""

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
        ans_lines = "<br />".join(
            f"问题{i+1}「{QUESTIONS[i]['q']}」→ 选择了：{QUESTIONS[i]['opts'][answers.get(i, 0)]['title']}"
            for i in range(len(QUESTIONS))
        )
        club_lines = "<br />".join(
            f"{c['id']}. {c['name']}（{c['type']}）：{c['desc']}"
            for c in CLUBS
        )
        prompt = (
            f"请根据用户测评，为以下 {len(CLUBS)} 个社团打匹配分（0-100 整数）。"
            f"同时给出最高匹配社团的一句话分析（温暖人性化，不超过 40 字）。<br /><br />"
            f"用户测评：<br />{ans_lines}<br /><br />"
            f"社团列表：<br />{club_lines}<br /><br />"
            f"只返回 JSON，格式：{{\"scores\":{{\"1\":85,\"2\":72,...}},\"reason\":\"...\"}}"
        )
        msg = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=600,
            system=CLAUDE_SELF_INTRO,
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
            return (
                "我是 ClubMatch 的 AI 顾问——底层由 Claude（Anthropic）驱动。<br /><br />"
                "目前 API Key 未配置，我暂时无法联网思考，但你可以去「发现社团」页面浏览，"
                "或完成测评获取推荐。配置好 Key 后，我就能实时和你聊啦～"
            )
        client = anthropic.Anthropic(api_key=api_key)
        club_info = "<br />".join(
            f"- {c['name']}（{c['type']}）：{c['desc']} "
            f"| 成员 {c['members']} 人，评分 {c['rating']}，时间投入：{c['time_cost']}，{c['freq']}"
            for c in CLUBS
        )
        system = (
            f"{CLAUDE_SELF_INTRO}<br /><br />"
            f"平台社团数据（共 {len(CLUBS)} 个）：<br />{club_info}<br /><br />"
            f"回复风格：简洁、温暖、真实，给具体可执行的建议。用中文，适当分段，不要用 markdown 标题。"
        )
        history = []
        for t in st.session_state.chat_history:
            if t.get("user"):
                history.append({"role": "user", "content": t["user"]})
            if t.get("ai"):
                history.append({"role": "assistant", "content": t["ai"]})
        history.append({"role": "user", "content": user_msg})
        msg = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=600,
            system=system,
            messages=history
        )
        return msg.content[0].text
    except Exception:
        return "我现在遇到了一点技术问题，稍后再试试吧。如果持续出现，可以去「发现社团」页面直接浏览～"

# ══════════════════════════════════════════════════════════════
# 首页
# ══════════════════════════════════════════════════════════════
def page_home():
    render_nav()
    col_l, col_r = st.columns([1.15, 1], gap="large")
    with col_l:
        st.markdown('<p style="font-size:0.8rem;font-weight:700;letter-spacing:0.12em;'
                    'color:#6366F1;text-transform:uppercase;margin-bottom:12px;">'
                    '✦ 找到你的圈子，从这里开始</p>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:2.8rem;font-weight:900;line-height:1.15;'
            'color:#1a1a2e;margin-bottom:16px;">大学四年，<br>你值得遇见'
            '<span style="color:#6366F1;">志同道合的伙伴</span></div>'
            '<div style="font-size:1rem;color:#6b7280;line-height:1.8;margin-bottom:28px;">'
            '不知道加哪个社团？害怕加了之后发现不合适？<br>'
            '我们用 AI 帮你找到真正适合你的那个圈子——<br>'
            '不靠运气，靠真实的你。'
            '</div>',
            unsafe_allow_html=True
        )
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🎯 开始匹配测评", key="h_start", type="primary", use_container_width=True):
                st.session_state.quiz_step = 0
                st.session_state.quiz_answers = {}
                go("quiz")
        with b2:
            if st.button("🔍 逛逛所有社团", key="h_browse", use_container_width=True):
                go("browse")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        for col, (n, l) in zip([c1, c2, c3, c4], [
            ("16", "入驻社团"), ("3,800+", "在校成员"), ("94%", "匹配满意度"), ("8分钟", "完成测评")
        ]):
            with col:
                st.markdown(
                    f'<div style="text-align:center;padding:16px 8px;background:#f8f8ff;'
                    f'border-radius:14px;">'
                    f'<div style="font-size:1.5rem;font-weight:900;color:#6366F1;">{n}</div>'
                    f'<div style="font-size:0.75rem;color:#9ca3af;margin-top:2px;">{l}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
    with col_r:
        top = CLUBS[0]
        stats = "".join([
            stat_cell(v, l)
            for v, l in [(top["members"], "成员"), (f"⭐{top['rating']}", "评分"), (f"{top['awards']}项", "获奖")]
        ])
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#f8f8ff,#ffffff);'
            f'border:1.5px solid #e8e8f8;border-radius:24px;padding:28px;">'
            f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;">'
            f'<div style="font-size:2.5rem;">{top["emoji"]}</div>'
            f'<div>'
            f'<div style="background:linear-gradient(90deg,#6366F1,#8B5CF6);color:#fff;'
            f'border-radius:99px;padding:3px 12px;font-size:0.72rem;font-weight:700;'
            f'display:inline-block;margin-bottom:4px;">92%</div>'
            f'<div style="font-size:0.65rem;color:#9ca3af;">AI 示例匹配度</div>'
            f'</div></div>'
            f'<div style="font-size:1.3rem;font-weight:800;color:#1a1a2e;margin-bottom:4px;">{top["name"]}</div>'
            f'<div style="font-size:0.82rem;color:#6366F1;margin-bottom:10px;">{top.get("vibe","")}</div>'
            f'<div style="font-size:0.88rem;color:#6b7280;line-height:1.6;margin-bottom:14px;">{top["desc"]}</div>'
            f'<div style="margin-bottom:16px;">{tags_html(top)}'
            f'<span style="display:inline-block;background:#fef3c7;color:#d97706;'
            f'border-radius:99px;padding:2px 10px;font-size:0.72rem;font-weight:600;'
            f'margin:2px 3px 2px 0;">热门</span></div>'
            f'<div style="display:flex;gap:8px;">{stats}</div>'
            f'</div>'
            f'<div style="text-align:center;margin-top:12px;font-size:0.78rem;color:#9ca3af;">'
            f'🟢 本周已有 102 位新生完成匹配</div>',
            unsafe_allow_html=True
        )
    st.markdown('<div style="height:48px;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;margin-bottom:32px;">'
        '<div style="font-size:0.78rem;font-weight:700;letter-spacing:0.12em;'
        'color:#6366F1;text-transform:uppercase;margin-bottom:8px;">我们不一样</div>'
        '<div style="font-size:2rem;font-weight:900;color:#1a1a2e;margin-bottom:8px;">'
        '不是随机，是属于你的那个</div>',
        unsafe_allow_html=True
    )
    features = [
        ("🧬", "真实的你，真实的匹配", "我们问的不是「你有什么爱好」，而是「你周末真的会做什么」——8 道情景题，比你自己更了解你。"),
        ("📊", "社团数据全透明", "成员活跃度、时间投入、历年评价……16 个社团的完整数据，在加入前就让你看清楚。"),
        ("🤝", "AI 顾问随时在线", "底层由 Claude（Anthropic）驱动。问什么都行，它了解每一个社团，也懂大学生的真实处境。"),
    ]
    cols = st.columns(3, gap="medium")
    for col, (icon, title, desc) in zip(cols, features):
        with col:
            st.markdown(
                f'<div style="background:#ffffff;border:1.5px solid #e8e8f8;border-radius:20px;'
                f'padding:28px 22px;text-align:center;height:100%;">'
                f'<div style="font-size:2.2rem;margin-bottom:14px;">{icon}</div>'
                f'<div style="font-size:1rem;font-weight:800;color:#1a1a2e;margin-bottom:10px;">{title}</div>'
                f'<div style="font-size:0.85rem;color:#6b7280;line-height:1.7;">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    st.markdown('<div style="height:48px;"></div>', unsafe_allow_html=True)
    picks = random.sample(CLUBS, 3)
    st.markdown(
        '<div style="text-align:center;margin-bottom:24px;">'
        '<div style="font-size:0.78rem;font-weight:700;letter-spacing:0.12em;'
        'color:#6366F1;text-transform:uppercase;margin-bottom:8px;">✦ 今日精选</div>'
        '<div style="font-size:2rem;font-weight:900;color:#1a1a2e;margin-bottom:8px;">'
        '随便逛逛，说不定就遇上了</div>',
        unsafe_allow_html=True
    )
    cols = st.columns(3, gap="small")
    for col, club in zip(cols, picks):
        with col:
            st.markdown(
                f'<div style="background:#ffffff;border:1.5px solid #e8e8f8;border-radius:20px;'
                f'padding:22px;margin-bottom:12px;">'
                f'<div style="font-size:2rem;margin-bottom:10px;">{club["emoji"]}</div>'
                f'<div style="font-size:1.05rem;font-weight:800;color:#1a1a2e;margin-bottom:4px;">{club["name"]}</div>'
                f'<div style="font-size:0.78rem;color:#6366F1;margin-bottom:10px;">{club.get("vibe","")}</div>'
                f'<div style="font-size:0.85rem;color:#6b7280;line-height:1.6;margin-bottom:12px;">'
                f'{club["desc"][:58]}...</div>'
                f'<div>{tags_html(club)}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button("了解更多", key=f"home_club_{club['id']}", use_container_width=True):
                st.session_state.expand_club = club["id"]
                go("browse")
    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("✨ 还没找到感觉？来做个测评吧 →", key="home_cta2",
                     type="primary", use_container_width=True):
            st.session_state.quiz_step = 0
            st.session_state.quiz_answers = {}
            go("quiz")

# ══════════════════════════════════════════════════════════════
# 测评页 ── 核心修改：用 st.components.v1.html 渲染选项卡片
#           点击后通过 Streamlit 的 setComponentValue 回传
# ══════════════════════════════════════════════════════════════
def page_quiz():
    render_nav()

    step  = st.session_state.quiz_step
    total = len(QUESTIONS)
    q     = QUESTIONS[step]
    pct   = int(step / total * 100)
    cur   = st.session_state.quiz_answers.get(step, -1)

    # ── 进度条 ────────────────────────────────────────────
    st.markdown(
        f'<div style="background:linear-gradient(135deg,#f0f0ff,#f8f0ff);'
        f'border:1.5px solid #e0d8ff;border-radius:16px;padding:16px 22px;'
        f'margin-bottom:28px;display:flex;align-items:center;gap:16px;">'
        f'<span style="font-size:0.82rem;font-weight:700;color:#6366F1;white-space:nowrap;">'
        f'问题 {step+1} / {total}</span>'
        f'<div style="flex:1;height:8px;background:#e0e0f8;border-radius:99px;overflow:hidden;">'
        f'<div style="width:{pct}%;height:100%;'
        f'background:linear-gradient(90deg,#6366F1,#A78BFA);border-radius:99px;"></div>'
        f'</div>'
        f'<span style="font-size:0.82rem;font-weight:800;color:#6366F1;">{pct}%</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    _, mid, _ = st.columns([0.4, 4, 0.4])
    with mid:
        # ── 题目 ──────────────────────────────────────────
        st.markdown(
            f'<div style="font-size:0.75rem;font-weight:800;letter-spacing:0.14em;'
            f'text-transform:uppercase;color:#6366F1;margin-bottom:10px;">第 {step+1} 题</div>'
            f'<div style="font-size:1.55rem;font-weight:900;color:#1a1a2e;'
            f'line-height:1.35;margin-bottom:10px;">{q["q"]}</div>',
            unsafe_allow_html=True
        )
        hint = q.get("hint", "")
        if hint:
            st.markdown(
                f'<div style="font-size:0.85rem;color:#9ca3af;font-style:italic;'
                f'margin-bottom:24px;padding:8px 14px;background:rgba(99,102,241,0.04);'
                f'border-left:3px solid #c4b5fd;border-radius:0 8px 8px 0;">💡 {hint}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

        # ══════════════════════════════════════════════════
        # 核心：用 st.radio 隐藏 + CSS 覆盖 实现动态卡片
        # 真正可靠的方案：每个选项渲染一个 st.button，
        # 在按钮上方用 st.markdown 注入该按钮专属的 <style>
        # 利用 Streamlit 渲染顺序：style 块紧跟在按钮之前，
        # 用 CSS 相邻兄弟/后代选择器命中按钮
        # ══════════════════════════════════════════════════

        row1 = st.columns(2, gap="medium")
        row2 = st.columns(2, gap="medium")
        grid = [row1[0], row1[1], row2[0], row2[1]]

        clicked = None

        for i, (col, opt) in enumerate(zip(grid, q["opts"])):
            is_sel = (cur == i)
            uid = f"qbtn_s{step}_o{i}"  # 唯一 key

            with col:
                # ── 为这个按钮注入专属样式 ──────────────
                # Streamlit 把 st.button 渲染为：
                #   <div data-testid="stButton">
                #     <button kind="secondary" ...>label</button>
                #   </div>
                # 我们在它上方注入 <style>，用 ID 选择器命中
                # 原理：给包裹 div 加一个唯一 id，再用 #id button 命中

                if is_sel:
                    btn_css = f"""
                    <style>
                    div[data-testid="stButton"]:has(button[data-testid="baseButton-secondary"][key="{uid}"]),
                    #wrap_{uid} + div[data-testid="stButton"] {{
                        /* fallback */
                    }}
                    #wrap_{uid} button {{
                        background: linear-gradient(135deg,#6366F1 0%,#8B5CF6 55%,#A78BFA 100%) !important;
                        border: 2px solid transparent !important;
                        border-radius: 20px !important;
                        color: #ffffff !important;
                        font-weight: 700 !important;
                        font-size: 0.93rem !important;
                        min-height: 110px !important;
                        width: 100% !important;
                        text-align: left !important;
                        padding: 18px 20px !important;
                        line-height: 1.55 !important;
                        white-space: pre-line !important;
                        transform: translateY(-2px) scale(1.03) !important;
                        box-shadow:
                            0 0 0 3px rgba(99,102,241,0.40),
                            0 14px 38px rgba(99,102,241,0.42),
                            0 4px 16px rgba(139,92,246,0.28) !important;
                        animation: selPop 0.38s cubic-bezier(0.34,1.56,0.64,1) forwards,
                                   glowPulse 2s ease-in-out 0.4s infinite !important;
                        cursor: pointer !important;
                        transition: all 0.2s ease !important;
                    }}
                    #wrap_{uid} button:hover {{
                        transform: translateY(-3px) scale(1.04) !important;
                        box-shadow:
                            0 0 0 4px rgba(99,102,241,0.55),
                            0 18px 45px rgba(99,102,241,0.55) !important;
                    }}
                    </style>
                    <div id="wrap_{uid}">
                    """
                else:
                    btn_css = f"""
                    <style>
                    #wrap_{uid} button {{
                        background: #ffffff !important;
                        border: 2px solid #e0e0f0 !important;
                        border-radius: 20px !important;
                        color: #1a1a2e !important;
                        font-weight: 600 !important;
                        font-size: 0.93rem !important;
                        min-height: 110px !important;
                        width: 100% !important;
                        text-align: left !important;
                        padding: 18px 20px !important;
                        line-height: 1.55 !important;
                        white-space: pre-line !important;
                        box-shadow: 0 2px 10px rgba(99,102,241,0.07) !important;
                        cursor: pointer !important;
                        transition: all 0.22s cubic-bezier(0.34,1.56,0.64,1) !important;
                    }}
                    #wrap_{uid} button:hover {{
                        border-color: #a5b4fc !important;
                        transform: translateY(-4px) scale(1.025) !important;
                        box-shadow: 0 10px 28px rgba(99,102,241,0.22) !important;
                        background: #fafaff !important;
                    }}
                    #wrap_{uid} button:active {{
                        transform: scale(0.97) !important;
                    }}
                    </style>
                    <div id="wrap_{uid}">
                    """

                st.markdown(btn_css, unsafe_allow_html=True)

                # ── 按钮 label：图标 + 标题(+✓) + 换行 + 副文本 ──
                check = "  ✓" if is_sel else ""
                label = f"{opt['icon']}  {opt['title']}{check}<br />{opt['sub']}"

                if st.button(label, key=uid, use_container_width=True):
                    clicked = i

                st.markdown('</div>', unsafe_allow_html=True)

        # ── 处理点击 ──────────────────────────────────────
        if clicked is not None:
            st.session_state.quiz_answers[step] = clicked
            st.rerun()

        st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

        # ── 导航按钮 ──────────────────────────────────────
        nav_l, nav_r = st.columns(2, gap="small")
        with nav_l:
            back_lbl = "← 返回首页" if step == 0 else "← 上一题"
            if st.button(back_lbl, key="q_back", use_container_width=True):
                if step == 0:
                    go("home")
                else:
                    st.session_state.quiz_step -= 1
                    st.rerun()
        with nav_r:
            done     = step in st.session_state.quiz_answers
            next_lbl = "查看匹配结果 →" if step == total - 1 else "下一题 →"
            if st.button(next_lbl, key="q_next", type="primary",
                         use_container_width=True, disabled=not done):
                if step == total - 1:
                    with st.spinner("🤖 AI 正在分析你的性格与偏好..."):
                        res, reason = ai_match(st.session_state.quiz_answers)
                        st.session_state.results   = res
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
        if st.button("去测评", type="primary"):
            go("quiz")
        return
    reason = st.session_state.get("ai_reason")
    st.markdown(
        '<div style="text-align:center;margin-bottom:8px;">'
        '<span style="font-size:0.78rem;font-weight:700;letter-spacing:0.12em;'
        'color:#6366F1;text-transform:uppercase;">✦ 你的专属匹配报告</span></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="text-align:center;font-size:1rem;color:#9ca3af;margin-bottom:24px;">'
        f'AI 从 {len(CLUBS)} 个社团里，为你挑出了这些</div>',
        unsafe_allow_html=True
    )
    if reason:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#f0f0ff,#f8f0ff);'
            f'border:1.5px solid #c4b5fd;border-radius:16px;padding:16px 20px;'
            f'margin-bottom:24px;text-align:center;color:#5b21b6;font-size:0.95rem;">'
            f'✦ Claude 分析：{reason}'
            f'</div>',
            unsafe_allow_html=True
        )
    badges     = ["🥇 最佳匹配", "🥈 强烈推荐", "🥉 推荐"]
    badge_cls  = ["badge-y", "badge-o", "badge-w"]
    cols = st.columns(3, gap="small")
    for idx, club in enumerate(results):
        with cols[idx % 3]:
            applied = already_applied(club["id"])
            in_c    = in_cart(club["id"])
            bc      = badge_cls[idx] if idx < 3 else "badge-w"
            bl      = badges[idx]    if idx < 3 else f"#{idx+1}"
            applied_badge = (
                '<span style="background:#d1fae5;color:#065f46;border-radius:99px;'
                'padding:2px 10px;font-size:0.72rem;font-weight:600;">✓ 已报名</span>'
            ) if applied else ''
            featured = "box-shadow:0 0 0 3px rgba(99,102,241,0.3);" if idx == 0 else ""
            st.markdown(
                f'<div style="background:#ffffff;border:1.5px solid #e8e8f8;border-radius:20px;'
                f'padding:20px;margin-bottom:8px;{featured}">'
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">'
                f'<div style="font-size:2rem;">{club["emoji"]}</div>'
                f'<div>'
                f'<div style="font-size:0.72rem;font-weight:700;color:#6366F1;">{bl}</div>'
                f'<div style="font-size:1rem;font-weight:800;color:#1a1a2e;">{club["name"]}</div>'
                f'<div style="font-size:0.75rem;color:#9ca3af;">'
                f'{club["type"]} · {club["freq"]}</div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
            score_bar(club["match_score"])
            st.markdown(
                f'<div style="font-size:0.78rem;color:#6366F1;margin-bottom:6px;">'
                f'{club.get("vibe","")}</div>'
                f'<div style="font-size:0.85rem;color:#6b7280;line-height:1.6;margin-bottom:10px;">'
                f'{club["desc"][:58]}...</div>'
                f'<div style="margin-bottom:8px;">{tags_html(club)}{applied_badge}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            b1, b2 = st.columns(2, gap="small")
            with b1:
                if st.button("查看详情", key=f"r_det_{club['id']}_{idx}", use_container_width=True):
                    st.session_state.expand_club = (
                        club["id"] if st.session_state.expand_club != club["id"] else None
                    )
                    st.rerun()
            with b2:
                if applied:
                    st.button("已报名 ✓", key=f"r_app_{club['id']}", disabled=True, use_container_width=True)
                elif in_c:
                    if st.button("移出申请袋", key=f"r_rm_{club['id']}_{idx}", use_container_width=True):
                        toggle_cart(club["id"]); st.rerun()
                else:
                    if st.button("➕ 加入申请袋", key=f"r_add_{club['id']}_{idx}",
                                 type="primary", use_container_width=True):
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
            if st.button(f"📋 提交申请 ({cart_n})", key="r_apply",
                         type="primary", use_container_width=True):
                go("apply")
        else:
            st.button("📋 申请袋是空的", key="r_apply_e", disabled=True, use_container_width=True)

def render_club_detail(club):
    applied  = already_applied(club["id"])
    req_rows = "".join(
        f'<div style="display:flex;gap:8px;margin-bottom:6px;">'
        f'<span style="color:#6366F1;font-weight:700;">·</span>'
        f'<span style="font-size:0.85rem;color:#374151;">{r}</span></div>'
        for r in club.get("requirements", [])
    )
    act_rows = "".join(
        f'<div style="display:flex;gap:8px;margin-bottom:6px;">'
        f'<span style="color:#6366F1;font-weight:700;">·</span>'
        f'<span style="font-size:0.85rem;color:#374151;">{a}</span></div>'
        for a in club.get("activities", [])
    )
    stats = "".join([
        stat_cell(v, l)
        for v, l in [
            (str(club["members"]), "成员"),
            (f"⭐{club['rating']}", "评分"),
            (f"{club['awards']}项", "获奖"),
            (club["time_cost"], "时间投入"),
        ]
    ])
    applied_note = (
        '<div style="background:#d1fae5;border-radius:10px;padding:10px 14px;'
        'color:#065f46;font-size:0.85rem;font-weight:600;margin-top:12px;">'
        '✓ 你已报名这个社团</div>'
    ) if applied else ""
    st.markdown(
        f'<div style="background:#f8f8ff;border:1.5px solid #e0e0f8;'
        f'border-radius:16px;padding:22px;margin:8px 0 16px;">'
        f'<div style="font-size:0.85rem;font-weight:700;color:#6366F1;margin-bottom:8px;">关于我们</div>'
        f'<div style="font-size:0.88rem;color:#374151;line-height:1.7;margin-bottom:16px;">'
        f'{club.get("detail","")}</div>'
        f'<div style="font-size:0.85rem;font-weight:700;color:#6366F1;margin-bottom:6px;">最适合</div>'
        f'<div style="font-size:0.85rem;color:#374151;margin-bottom:16px;">'
        f'→ {club.get("best_for","")}</div>'
        f'<div style="font-size:0.85rem;font-weight:700;color:#6366F1;margin-bottom:8px;">招新要求</div>'
        f'{req_rows}'
        f'<div style="font-size:0.85rem;font-weight:700;color:#6366F1;'
        f'margin:12px 0 8px;">主要活动</div>'
        f'{act_rows}'
        f'<div style="display:flex;gap:8px;margin-top:16px;">{stats}</div>'
        f'{applied_note}'
        f'</div>',
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════
# 发现社团页
# ══════════════════════════════════════════════════════════════
def page_browse():
    render_nav()
    st.markdown(
        '<div style="text-align:center;font-size:2rem;font-weight:900;'
        'color:#1a1a2e;margin-bottom:8px;">发现社团</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="text-align:center;font-size:1rem;color:#9ca3af;margin-bottom:24px;">'
        f'{len(CLUBS)} 个社团，总有一个在等你</div>',
        unsafe_allow_html=True
    )
    col_s, col_f = st.columns([2, 1])
    with col_s:
        search = st.text_input("", placeholder="🔍 搜索名称、类型、标签...",
                               label_visibility="collapsed", key="b_search")
    with col_f:
        types    = ["全部类型"] + sorted({c["type"] for c in CLUBS})
        sel_type = st.selectbox("", types, label_visibility="collapsed", key="b_type")
    filtered = [
        c for c in CLUBS
        if (not search or search in c["name"] or search in c["type"]
            or any(search in t for t in c.get("tags", []))
            or search in c.get("desc", ""))
        and (sel_type == "全部类型" or c["type"] == sel_type)
    ]
    if not filtered:
        st.markdown(
            '<div style="text-align:center;padding:60px 0;color:#9ca3af;">'
            '没找到……换个关键词试试？</div>',
            unsafe_allow_html=True
        )
        return
    cols = st.columns(3, gap="small")
    for idx, club in enumerate(filtered):
        with cols[idx % 3]:
            applied = already_applied(club["id"])
            in_c    = in_cart(club["id"])
            extra   = ""
            if applied:
                extra = ('<span style="background:#d1fae5;color:#065f46;border-radius:99px;'
                         'padding:2px 10px;font-size:0.72rem;font-weight:600;">✓ 已报名</span>')
            elif in_c:
                extra = ('<span style="background:#ede9fe;color:#6d28d9;border-radius:99px;'
                         'padding:2px 10px;font-size:0.72rem;font-weight:600;">在申请袋中</span>')
            stat_row = "".join([
                f'<div style="text-align:center;flex:1;">'
                f'<div style="font-size:0.9rem;font-weight:800;color:#1a1a2e;">{v}</div>'
                f'<div style="font-size:0.68rem;color:#9ca3af;">{l}</div></div>'
                for v, l in [
                    (str(club["members"]), "成员"),
                    (f"⭐{club['rating']}", "评分"),
                    (f"{club['awards']}项", "获奖"),
                ]
            ])
            st.markdown(
                f'<div style="background:#ffffff;border:1.5px solid #e8e8f8;'
                f'border-radius:20px;padding:20px;margin-bottom:8px;">'
                f'<div style="font-size:2rem;margin-bottom:8px;">{club["emoji"]}</div>'
                f'<div style="font-size:1.05rem;font-weight:800;color:#1a1a2e;margin-bottom:2px;">'
                f'{club["name"]}</div>'
                f'<div style="font-size:0.75rem;color:#9ca3af;margin-bottom:6px;">'
                f'{club["type"]} · 成立 {club["founded"]}</div>'
                f'<div style="font-size:0.78rem;color:#6366F1;margin-bottom:8px;">'
                f'{club.get("vibe","")}</div>'
                f'<div style="font-size:0.85rem;color:#6b7280;line-height:1.6;margin-bottom:10px;">'
                f'{club["desc"][:62]}...</div>'
                f'<div style="margin-bottom:12px;">{tags_html(club)}{extra}</div>'
                f'<div style="display:flex;gap:8px;padding-top:10px;'
                f'border-top:1px solid #f0f0f8;">{stat_row}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            b1, b2 = st.columns(2, gap="small")
            with b1:
                exp = st.session_state.expand_club == club["id"]
                if st.button("收起 ↑" if exp else "查看详情",
                             key=f"b_det_{club['id']}_{idx}", use_container_width=True):
                    st.session_state.expand_club = club["id"] if not exp else None
                    st.rerun()
            with b2:
                if applied:
                    st.button("已报名 ✓", key=f"b_app_{club['id']}",
                              disabled=True, use_container_width=True)
                elif in_c:
                    if st.button("移出申请袋", key=f"b_rm_{club['id']}_{idx}",
                                 use_container_width=True):
                        toggle_cart(club["id"]); st.rerun()
                else:
                    if st.button("➕ 加入申请袋", key=f"b_add_{club['id']}_{idx}",
                                 type="primary", use_container_width=True):
                        toggle_cart(club["id"]); st.rerun()
            if st.session_state.expand_club == club["id"]:
                render_club_detail(club)
    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        cart_n = len(st.session_state.cart)
        if cart_n:
            if st.button(f"📋 前往提交申请（已选 {cart_n} 个）",
                         type="primary", use_container_width=True, key="b_go_apply"):
                go("apply")
        if st.button("✨ 没找到合适的？申请创建新社团",
                     use_container_width=True, key="b_create"):
            go("create")

# ══════════════════════════════════════════════════════════════
# AI 顾问页
# ══════════════════════════════════════════════════════════════
def page_chat():
    render_nav()
    st.markdown(
        '<div style="text-align:center;font-size:2rem;font-weight:900;'
        'color:#1a1a2e;margin-bottom:4px;">AI 社团顾问</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="text-align:center;font-size:0.88rem;color:#9ca3af;margin-bottom:24px;">'
        '由 Claude (Anthropic) 驱动 · 随时回答关于社团的任何疑问</div>',
        unsafe_allow_html=True
    )
    if not st.session_state.chat_history:
        st.session_state.chat_history = [{
            "user": None,
            "ai": (
                f"嗨！我是 ClubMatch 的 AI 顾问，底层由 Claude（Anthropic）驱动 👋<br /><br />"
                f"我对平台上所有 {len(CLUBS)} 个社团都了如指掌。你可以问我：<br />"
                f"· 某个社团的具体情况和氛围<br />"
                f"· 根据你的情况给个性化推荐<br />"
                f"· 「内向的人适合哪个」「我时间不多怎么选」……<br /><br />"
                f"随便问吧，没有奇怪的问题。"
            )
        }]
    for turn in st.session_state.chat_history:
        if turn.get("user"):
            st.markdown(
                '<div style="text-align:right;font-size:0.75rem;color:#9ca3af;margin-bottom:4px;">你</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#6366F1,#8B5CF6);color:#fff;'
                f'border-radius:16px 16px 4px 16px;padding:12px 16px;margin-bottom:16px;'
                f'max-width:80%;margin-left:auto;font-size:0.92rem;line-height:1.6;">'
                f'{turn["user"]}</div>',
                unsafe_allow_html=True
            )
        if turn.get("ai"):
            st.markdown(
                '<div style="font-size:0.75rem;color:#9ca3af;margin-bottom:4px;">🤖 Claude AI 顾问</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div style="background:#f8f8ff;border:1.5px solid #e0e0f8;'
                f'border-radius:4px 16px 16px 16px;padding:14px 18px;margin-bottom:16px;'
                f'max-width:85%;font-size:0.92rem;line-height:1.7;color:#1a1a2e;">'
                f'{turn["ai"]}</div>',
                unsafe_allow_html=True
            )
    st.markdown("<br>", unsafe_allow_html=True)
    if len(st.session_state.chat_history) <= 1:
        st.markdown(
            '<div style="font-size:0.8rem;font-weight:700;color:#9ca3af;margin-bottom:10px;">快捷问题</div>',
            unsafe_allow_html=True
        )
        sugg = [
            "内向的人适合哪个社团？", "我时间不多，选哪个好？",
            "摄影社和微电影社有啥区别？", "创业社真的有用吗？",
            "不知道自己喜欢什么怎么办？", "哪个社团最容易交到朋友？",
        ]
        cols = st.columns(3, gap="small")
        for i, s in enumerate(sugg):
            with cols[i % 3]:
                if st.button(s, key=f"sugg_{i}", use_container_width=True):
                    with st.spinner("Claude 思考中..."):
                        rep = chat_ai(s)
                    st.session_state.chat_history.append({"user": s, "ai": rep})
                    st.rerun()
    col_i, col_s = st.columns([5, 1])
    with col_i:
        user_input = st.text_input("", placeholder="问我任何关于社团的事...",
                                   label_visibility="collapsed", key="chat_inp")
    with col_s:
        send = st.button("发送 →", key="chat_send", type="primary", use_container_width=True)
    if send and user_input.strip():
        with st.spinner("Claude 思考中..."):
            rep = chat_ai(user_input.strip())
        st.session_state.chat_history.append({"user": user_input.strip(), "ai": rep})
        st.rerun()
    if len(st.session_state.chat_history) > 1:
        if st.button("🗑 清空对话", key="chat_clear"):
            st.session_state.chat_history = []; st.rerun()

# ══════════════════════════════════════════════════════════════
# 申请提交页
# ══════════════════════════════════════════════════════════════
def page_apply():
    render_nav()
    cart = st.session_state.cart
    if not cart:
        st.markdown(
            '<div style="text-align:center;font-size:1.5rem;font-weight:800;'
            'color:#1a1a2e;margin:40px 0 12px;">申请袋是空的</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div style="text-align:center;color:#9ca3af;margin-bottom:24px;">'
            '先去发现社团，把感兴趣的加进申请袋再来这里～</div>',
            unsafe_allow_html=True
        )
        if st.button("去发现社团", type="primary"): go("browse")
        return
    st.markdown(
        '<div style="text-align:center;font-size:2rem;font-weight:900;'
        'color:#1a1a2e;margin-bottom:8px;">提交申请</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="text-align:center;font-size:1rem;color:#9ca3af;margin-bottom:24px;">'
        f'你选择了 {len(cart)} 个社团，一次填写全搞定</div>',
        unsafe_allow_html=True
    )
    col_l, col_r = st.columns([1.2, 1], gap="large")
    with col_l:
        st.markdown('<div style="font-weight:800;font-size:1rem;color:#1a1a2e;'
                    'margin-bottom:12px;">你的申请袋</div>', unsafe_allow_html=True)
        for cid in list(cart):
            club = club_by_id(cid)
            if not club: continue
            c_l, c_r = st.columns([3, 1])
            with c_l:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;'
                    f'background:#f8f8ff;border-radius:12px;padding:12px 14px;margin-bottom:8px;">'
                    f'<div style="font-size:1.5rem;">{club["emoji"]}</div>'
                    f'<div>'
                    f'<div style="font-weight:700;color:#1a1a2e;">{club["name"]}</div>'
                    f'<div style="font-size:0.75rem;color:#9ca3af;">'
                    f'{club["type"]} · {club["freq"]}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            with c_r:
                if st.button("移除", key=f"apply_rm_{cid}", use_container_width=True):
                    toggle_cart(cid); st.rerun()
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        if st.button("+ 继续添加社团", key="apply_more", use_container_width=True):
            go("browse")
        st.markdown("""
<div style="background:#f8f8ff;border-radius:16px;padding:20px;margin-top:20px;">
  <div style="font-weight:800;color:#1a1a2e;margin-bottom:14px;">提交后，然后呢？</div>
  <div style="display:flex;flex-direction:column;gap:12px;">
    <div style="display:flex;gap:12px;align-items:flex-start;">
      <div style="background:#6366F1;color:#fff;border-radius:50%;width:24px;height:24px;min-width:24px;
           display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;">1</div>
      <div>
        <div style="font-weight:700;color:#1a1a2e;font-size:0.88rem;">社团负责人主动联系你</div>
        <div style="font-size:0.8rem;color:#9ca3af;margin-top:2px;">3 个工作日内，通过你填写的手机号或微信联系，说明面试或见面安排。</div>
      </div>
    </div>
    <div style="display:flex;gap:12px;align-items:flex-start;">
      <div style="background:#8B5CF6;color:#fff;border-radius:50%;width:24px;height:24px;min-width:24px;
           display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;">2</div>
      <div>
        <div style="font-weight:700;color:#1a1a2e;font-size:0.88rem;">参加社团见面或体验活动</div>
        <div style="font-size:0.8rem;color:#9ca3af;margin-top:2px;">大部分社团会邀请你来体验一次活动，感受真实氛围再决定要不要加入。</div>
      </div>
    </div>
    <div style="display:flex;gap:12px;align-items:flex-start;">
      <div style="background:#A78BFA;color:#fff;border-radius:50%;width:24px;height:24px;min-width:24px;
           display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;">3</div>
      <div>
        <div style="font-weight:700;color:#1a1a2e;font-size:0.88rem;">被拉入社团群，正式加入</div>
        <div style="font-size:0.8rem;color:#9ca3af;margin-top:2px;">确认加入后，负责人会把你拉进官方微信群，开始你的社团生活。</div>
      </div>
    </div>
  </div>
</div>
        """, unsafe_allow_html=True)
    with col_r:
        st.markdown('<div style="font-weight:800;font-size:1rem;color:#1a1a2e;'
                    'margin-bottom:12px;">个人信息</div>', unsafe_allow_html=True)
        name       = st.text_input("姓名 *", placeholder="请输入真实姓名", key="f_name")
        student_id = st.text_input("学号 *", placeholder="例：2024XXXXXXXX", key="f_sid")
        major      = st.text_input("专业 *", placeholder="例：国际经济与贸易", key="f_major")
        grade      = st.selectbox("年级 *", ["请选择", "大一", "大二", "大三", "大四", "研究生"], key="f_grade")
        phone      = st.text_input("手机号 *", placeholder="社团负责人会通过此号联系你", key="f_phone")
        wechat     = st.text_input("微信号（选填）", placeholder="方便拉你进群", key="f_wechat")
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:800;font-size:1rem;color:#1a1a2e;'
                    'margin-bottom:12px;">补充信息</div>', unsafe_allow_html=True)
        intro      = st.text_area("自我介绍 *",
                                  placeholder="简单介绍一下自己，为什么对这些社团感兴趣？（100字以内）",
                                  height=100, key="f_intro")
        time_avail = st.multiselect("你通常空闲的时间段",
                                    ["周一至周五 白天", "周一至周五 晚上", "周末全天", "周末上午", "周末下午"],
                                    key="f_time")
        skill      = st.text_input("特长或技能（选填）",
                                   placeholder="例：摄影、吉他、编程、英语……", key="f_skill")
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        all_filled = all([
            name.strip(), student_id.strip(), major.strip(),
            grade != "请选择", phone.strip(), intro.strip()
        ])
        if st.button("🎉 提交所有申请", key="apply_submit", type="primary",
                     use_container_width=True, disabled=not all_filled):
            record = {
                "clubs": list(cart), "name": name, "student_id": student_id,
                "major": major, "grade": grade, "phone": phone, "wechat": wechat,
                "intro": intro, "time_avail": time_avail, "skill": skill,
            }
            st.session_state.applications.append(record)
            st.session_state.cart = []
            go("success")
        if not all_filled:
            st.markdown(
                '<div style="text-align:center;font-size:0.8rem;color:#9ca3af;margin-top:8px;">'
                '请填写所有必填项后提交</div>',
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════
# 成功页
# ══════════════════════════════════════════════════════════════
def page_success():
    render_nav()
    if not st.session_state.applications:
        go("home"); return
    last       = st.session_state.applications[-1]
    club_names = [club_by_id(cid)["name"] for cid in last["clubs"] if club_by_id(cid)]
    club_list  = "".join(
        f'<div style="display:flex;align-items:center;gap:10px;'
        f'background:rgba(255,255,255,0.15);border-radius:10px;'
        f'padding:10px 14px;margin-bottom:8px;">'
        f'<div style="background:rgba(255,255,255,0.3);border-radius:50%;'
        f'width:22px;height:22px;display:flex;align-items:center;'
        f'justify-content:center;font-size:0.75rem;font-weight:700;color:#fff;">✓</div>'
        f'<span style="color:#fff;font-weight:600;">{n}</span></div>'
        for n in club_names
    )
    _, col, _ = st.columns([0.5, 3, 0.5])
    with col:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#6366F1,#8B5CF6);'
            f'border-radius:24px;padding:40px;text-align:center;margin-bottom:24px;">'
            f'<div style="font-size:3rem;margin-bottom:16px;">🎉</div>'
            f'<div style="font-size:1.8rem;font-weight:900;color:#fff;margin-bottom:12px;">'
            f'申请已成功提交！</div>'
            f'<div style="color:rgba(255,255,255,0.85);font-size:0.95rem;'
            f'line-height:1.7;margin-bottom:28px;">'
            f'{last["name"]}，欢迎你迈出这一步。<br>接下来，静静等着被发现吧。</div>'
            f'<div style="background:rgba(255,255,255,0.12);border-radius:16px;padding:20px;">'
            f'<div style="color:rgba(255,255,255,0.7);font-size:0.8rem;'
            f'font-weight:700;margin-bottom:12px;text-transform:uppercase;'
            f'letter-spacing:0.1em;">你申请的社团</div>'
            f'{club_list}</div></div>',
            unsafe_allow_html=True
        )
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;font-size:1.1rem;font-weight:800;'
        'color:#1a1a2e;margin-bottom:20px;">加入社团后，怎么快速融入？</div>',
        unsafe_allow_html=True
    )
    tips = [
        ("💬", "第一次活动前", "主动在群里自我介绍，说说你为什么加入。比你想象的更有用。"),
        ("🤝", "第一个月", "每次活动尽量不缺席。前几次见面之后，陌生感会自然消失。"),
        ("🌱", "稳定下来之后", "尝试承担一个具体的小任务。有责任感的成员更容易获得真实成长。"),
    ]
    tips_cols = st.columns(3, gap="small")
    for col_t, (icon, title, desc) in zip(tips_cols, tips):
        with col_t:
            st.markdown(
                f'<div style="background:#ffffff;border:1.5px solid #e8e8f8;'
                f'border-radius:20px;padding:24px;text-align:center;">'
                f'<div style="font-size:2rem;margin-bottom:10px;">{icon}</div>'
                f'<div style="font-weight:800;color:#1a1a2e;margin-bottom:8px;">{title}</div>'
                f'<div style="font-size:0.85rem;color:#6b7280;line-height:1.6;">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
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
    st.markdown(
        '<p style="font-size:0.8rem;font-weight:700;letter-spacing:0.12em;'
        'color:#6366F1;text-transform:uppercase;margin-bottom:8px;">'
        '✦ 找不到合适的？自己创一个</p>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="font-size:2rem;font-weight:900;color:#1a1a2e;margin-bottom:8px;">'
        '申请创建新社团</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="font-size:0.95rem;color:#6b7280;line-height:1.7;margin-bottom:28px;">'
        '每一个存在的社团，都是某个人第一次说「我想做这件事」。<br>'
        '如果你有个想法，这里是它开始的地方。</div>',
        unsafe_allow_html=True
    )
    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown('<div style="font-weight:800;font-size:1rem;color:#1a1a2e;'
                    'margin-bottom:12px;">社团基本信息</div>', unsafe_allow_html=True)
        club_name = st.text_input("你想创建的社团叫什么？*", placeholder="例：城市骑行与街拍社", key="c_name")
        club_type = st.selectbox("社团类型 *", [
            "请选择", "艺术创作", "音乐表演", "舞台表演", "科技创新", "商业创新",
            "户外运动", "人文学术", "公益服务", "体育竞技", "跨文化交流", "科学探索", "其他"
        ], key="c_type")
        club_desc = st.text_area("用一两句话，说说这个社团是做什么的 *",
                                 placeholder="让别人在 5 秒内听懂这个社团，说具体的事，别用太多形容词。",
                                 height=80, key="c_desc")
        club_why  = st.text_area("为什么这个社团值得存在？你发现了什么需求？*",
                                 placeholder="比如：我发现学校没有专注城市骑行的社团，但身边有很多同学想要这个……",
                                 height=100, key="c_why")
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:800;font-size:1rem;color:#1a1a2e;'
                    'margin-bottom:12px;">你的构想</div>', unsafe_allow_html=True)
        activity_plan = st.text_area("你打算做哪些活动或项目？",
                                     placeholder="大概说说你的活动构想，哪怕很初期的想法也可以",
                                     height=90, key="c_plan")
        st.slider("你预计招募多少初始成员？", 5, 50, 15, key="c_members")
        st.selectbox("计划的活动频率",
                     ["每周一次", "每两周一次", "每月一次", "视项目而定", "还没想好"], key="c_freq")
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
    with col_r:
        st.markdown('<div style="font-weight:800;font-size:1rem;color:#1a1a2e;'
                    'margin-bottom:12px;">发起人信息</div>', unsafe_allow_html=True)
        f_name  = st.text_input("你的姓名 *", key="c_fname")
        f_sid   = st.text_input("学号 *", key="c_fsid")
        f_major = st.text_input("专业 *", key="c_fmajor")
        f_grade = st.selectbox("年级 *",
                               ["请选择", "大一", "大二", "大三", "大四", "研究生"], key="c_fgrade")
        f_phone = st.text_input("联系方式 *", key="c_fphone")
        st.text_area("你有哪些相关经历或能力？（选填）",
                     placeholder="比如：你是这个领域的爱好者？做过类似的组织工作？",
                     height=80, key="c_fexp")
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:800;font-size:1rem;color:#1a1a2e;'
                    'margin-bottom:8px;">Claude AI 帮你完善方案</div>', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.85rem;color:#9ca3af;margin-bottom:12px;">'
            '填完基本信息后，让 Claude 给你的创建方案提几条建议——对写申请书很有帮助。</div>',
            unsafe_allow_html=True
        )
        if st.button("🤖 让 Claude 给我点建议", key="c_ai_suggest", use_container_width=True):
            if club_name and club_desc and club_why:
                with st.spinner("Claude 思考中..."):
                    try:
                        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
                        if api_key:
                            client = anthropic.Anthropic(api_key=api_key)
                            msg = client.messages.create(
                                model="claude-opus-4-5", max_tokens=500,
                                system=CLAUDE_SELF_INTRO,
                                messages=[{"role": "user", "content": (
                                    f"一位大学生想创建社团：<br />"
                                    f"名称：{club_name}<br />类型：{club_type}<br />"
                                    f"描述：{club_desc}<br />创建原因：{club_why}<br />"
                                    f"活动计划：{activity_plan}<br /><br />"
                                    f"请给出3条简短、具体、有用的建议，帮助他完善社团方案。"
                                    f"风格温暖鼓励，直接分点，不用 markdown 标题。"
                                )}]
                            )
                            st.session_state.ai_suggestion = msg.content[0].text
                        else:
                            st.session_state.ai_suggestion = (
                                "1. 把你的核心活动再具体化——「每月一次骑行」比「定期活动」更有说服力。<br />"
                                "2. 考虑一下如何区分于现有社团，你的独特价值是什么？<br />"
                                "3. 找 2-3 个有同样想法的人一起发起，审核委员会会看得更认真。"
                            )
                    except Exception:
                        st.session_state.ai_suggestion = "AI 暂时不可用，但你的想法很棒，继续填写吧！"
            else:
                st.warning("先填写社团名称、描述和创建原因，Claude 才能给出有用的建议～")
        if st.session_state.ai_suggestion:
            st.markdown(
                f'<div style="background:linear-gradient(135deg,#f0f0ff,#f8f0ff);'
                f'border:1.5px solid #c4b5fd;border-radius:16px;padding:16px 18px;'
                f'margin-top:12px;font-size:0.88rem;color:#5b21b6;line-height:1.7;">'
                f'✦ Claude 建议：<br><br>{st.session_state.ai_suggestion}</div>',
                unsafe_allow_html=True
            )
    st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
    st.markdown("""
<div style="background:#f8f8ff;border-radius:16px;padding:24px;margin-bottom:24px;">
  <div style="font-weight:800;color:#1a1a2e;margin-bottom:16px;">提交后的审核流程</div>
  <div style="display:flex;gap:16px;flex-wrap:wrap;">
    <div style="flex:1;min-width:200px;">
      <div style="font-size:0.72rem;font-weight:700;color:#6366F1;margin-bottom:4px;">① 初步审核（1-2 个工作日）</div>
      <div style="font-size:0.82rem;color:#6b7280;">学生活动部确认材料完整，通过后进入答辩环节</div>
    </div>
    <div style="flex:1;min-width:200px;">
      <div style="font-size:0.72rem;font-weight:700;color:#6366F1;margin-bottom:4px;">② 创建人答辩（约 15 分钟）</div>
      <div style="font-size:0.82rem;color:#6b7280;">向评审委员会说明社团定位、活动计划和初始招募方案</div>
    </div>
    <div style="flex:1;min-width:200px;">
      <div style="font-size:0.72rem;font-weight:700;color:#6366F1;margin-bottom:4px;">③ 试运营期（一学期）</div>
      <div style="font-size:0.82rem;color:#6b7280;">完成 3 次以上有记录的活动后，正式注册挂牌，登上 ClubMatch 平台</div>
    </div>
  </div>
</div>
    """, unsafe_allow_html=True)
    all_ok = all([
        club_name, club_type != "请选择", club_desc, club_why,
        f_name, f_sid, f_major, f_grade != "请选择", f_phone
    ])
    if st.button("🚀 提交创建申请", key="c_submit", type="primary",
                 use_container_width=True, disabled=not all_ok):
        st.session_state.create_submitted = True
        st.rerun()
    if st.session_state.get("create_submitted"):
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#6366F1,#8B5CF6);'
            f'border-radius:20px;padding:32px;text-align:center;margin-top:20px;">'
            f'<div style="font-size:2.5rem;margin-bottom:12px;">🌱</div>'
            f'<div style="font-size:1.5rem;font-weight:900;color:#fff;margin-bottom:10px;">'
            f'申请已提交！</div>'
            f'<div style="color:rgba(255,255,255,0.85);font-size:0.92rem;line-height:1.7;">'
            f'学生活动部将在 5 个工作日内审核你的申请。<br>'
            f'{f_name}，期待看到「{club_name}」出现在 ClubMatch 上。</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        if st.button("回到首页", key="c_home", type="primary"):
            st.session_state.create_submitted = False
            st.session_state.ai_suggestion    = ""
            go("home")
    if not all_ok and not st.session_state.get("create_submitted"):
        st.markdown(
            '<div style="text-align:center;font-size:0.8rem;color:#9ca3af;margin-top:8px;">'
            '请填写所有必填项（*）</div>',
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════════════════════
# 路由
# ══════════════════════════════════════════════════════════════
dispatch = {
    "home":    page_home,
    "quiz":    page_quiz,
    "results": page_results,
    "browse":  page_browse,
    "chat":    page_chat,
    "apply":   page_apply,
    "success": page_success,
    "create":  page_create,
}
dispatch.get(st.session_state.page, page_home)()
