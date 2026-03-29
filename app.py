import streamlit as st
import streamlit.components.v1 as components
import anthropic
import json
import random
from data import CLUBS, QUESTIONS

st.set_page_config(
    page_title="ClubMatch",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', 'PingFang SC', 'Noto Sans SC', system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 4rem !important;
    max-width: 1180px !important;
}

/* ── BACKGROUND ── */
.stApp {
    background:
        radial-gradient(ellipse 90% 60% at 10% 0%,   rgba(255,200,50,0.20) 0%, transparent 55%),
        radial-gradient(ellipse 70% 50% at 95% 95%,  rgba(255,160,20,0.15) 0%, transparent 55%),
        radial-gradient(ellipse 60% 40% at 50% 50%,  rgba(255,220,100,0.10) 0%, transparent 60%),
        linear-gradient(160deg, #fffdf5 0%, #fff9e6 40%, #fffcf0 75%, #fff8e0 100%);
    color: #2d2000;
    min-height: 100vh;
}

/* ── GLASS CARD ── */
.g {
    background: rgba(255,255,255,0.55);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid rgba(255,200,50,0.28);
    border-radius: 22px;
    padding: 26px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: transform 0.28s cubic-bezier(.4,0,.2,1),
                box-shadow 0.28s cubic-bezier(.4,0,.2,1),
                border-color 0.28s;
    box-shadow: 0 4px 24px rgba(200,150,0,0.08), 0 1px 4px rgba(200,150,0,0.06);
}
.g::before {
    content: '';
    position: absolute; inset: 0;
    border-radius: 22px;
    background: linear-gradient(135deg,
        rgba(255,220,80,0.10) 0%,
        rgba(255,255,255,0.35) 50%,
        rgba(255,200,50,0.06) 100%);
    pointer-events: none;
}
.g::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,210,60,0.55), transparent);
}
.g:hover {
    transform: translateY(-4px);
    border-color: rgba(245,158,11,0.45);
    box-shadow: 0 20px 50px rgba(200,140,0,0.14), 0 0 0 1px rgba(245,158,11,0.12);
}
.g.pin {
    border-color: rgba(245,158,11,0.60);
    background: rgba(255,250,230,0.75);
    box-shadow: 0 0 0 2px rgba(245,158,11,0.22), 0 8px 40px rgba(200,140,0,0.16);
}

/* ── NAV — 完全透明 ── */
.nav {
    position: sticky; top: 0; z-index: 999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 0;
    border-bottom: 1px solid rgba(200,150,0,0.10);
    margin-bottom: 40px;
    background: transparent;
}
.logo {
    display: flex; align-items: center; gap: 10px;
    font-size: 20px; font-weight: 900; letter-spacing: -0.5px; color: #1a1000;
}
.logo-badge {
    background: linear-gradient(135deg, #f59e0b, #fbbf24, #f97316);
    border-radius: 10px; padding: 5px 10px;
    font-size: 13px; font-weight: 900; color: #fff;
    box-shadow: 0 0 20px rgba(245,158,11,0.40), 0 2px 8px rgba(249,115,22,0.25);
}
.logo em { color: #d97706; font-style: normal; }

/* ── PILLS ── */
.pill {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600; margin: 2px 3px 2px 0;
}
.pill-v { background: rgba(245,158,11,0.12); color: #b45309; border: 1px solid rgba(245,158,11,0.32); }
.pill-o { background: rgba(249,115,22,0.12); color: #c2410c; border: 1px solid rgba(249,115,22,0.32); }
.pill-g { background: rgba(16,185,129,0.10); color: #047857; border: 1px solid rgba(16,185,129,0.25); }
.pill-b { background: rgba(245,158,11,0.10); color: #92400e; border: 1px solid rgba(245,158,11,0.22); }

/* ── VIBE ── */
.vibe {
    display: inline-block;
    background: rgba(245,158,11,0.09);
    border: 1px solid rgba(245,158,11,0.26);
    color: #b45309; border-radius: 8px; padding: 3px 10px;
    font-size: 11px; font-weight: 500; margin-bottom: 12px; font-style: italic;
}

/* ── HERO ── */
.h1 {
    font-size: clamp(38px,5.5vw,68px);
    font-weight: 900; line-height: 1.06; letter-spacing: -2px;
    color: #1a1000; margin-bottom: 18px;
}
.h1 .g1 {
    background: linear-gradient(135deg, #f59e0b 0%, #f97316 55%, #ef4444 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sub {
    font-size: 16px; color: rgba(60,35,0,0.52);
    line-height: 1.80; margin-bottom: 32px; font-weight: 400;
}
.eyebrow {
    display: inline-block;
    background: rgba(245,158,11,0.11);
    border: 1px solid rgba(245,158,11,0.30);
    color: #b45309; border-radius: 20px; padding: 5px 14px;
    font-size: 11px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 20px;
}

/* ── SCORE BAR ── */
.srow { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.strk { flex:1; height:4px; background:rgba(200,150,0,0.10); border-radius:2px; overflow:hidden; }
.sfil { height:100%; border-radius:2px;
        background: linear-gradient(90deg, #f59e0b, #fbbf24, #f97316); }
.spct { font-size:13px; font-weight:800; color:#d97706; min-width:38px; text-align:right; }

/* ── STATS ── */
.snum { font-size:30px; font-weight:900;
        background: linear-gradient(135deg,#f59e0b,#f97316);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
        letter-spacing:-1.5px; line-height:1; }
.slbl { font-size:11px; color:rgba(80,50,0,0.38); margin-top:4px; font-weight:500; }

/* ── PROGRESS ── */
.prog-wrap { margin-bottom:28px; }
.prog-meta {
    display:flex; justify-content:space-between;
    font-size:12px; color:rgba(80,50,0,0.42); margin-bottom:8px; font-weight:500;
}
.prog-meta b { color:#d97706; font-weight:700; }
.prog-track { height:4px; background:rgba(200,150,0,0.10); border-radius:2px; overflow:hidden; }
.prog-fill {
    height:100%; border-radius:2px;
    background: linear-gradient(90deg, #f59e0b, #fbbf24, #f97316);
    transition: width 0.5s cubic-bezier(.4,0,.2,1);
    box-shadow: 0 0 8px rgba(245,158,11,0.35);
}

/* ── BUTTONS ── */
.stButton > button {
    border-radius: 50px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border: 1.5px solid rgba(200,150,0,0.22) !important;
    background: rgba(255,255,255,0.65) !important;
    color: rgba(80,50,0,0.78) !important;
    transition: all 0.22s !important;
    padding: 0.45rem 1.1rem !important;
    box-shadow: 0 2px 8px rgba(200,140,0,0.06) !important;
}
.stButton > button:hover {
    background: rgba(255,248,220,0.88) !important;
    border-color: rgba(245,158,11,0.48) !important;
    color: #92400e !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(200,140,0,0.14) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #d97706, #f59e0b, #f97316) !important;
    color: #fff !important; border: none !important;
    box-shadow: 0 4px 20px rgba(217,119,6,0.38), 0 0 0 1px rgba(245,158,11,0.18) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #f59e0b, #fbbf24, #ef4444) !important;
    box-shadow: 0 8px 28px rgba(245,158,11,0.48), 0 0 40px rgba(249,115,22,0.20) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:disabled {
    opacity: 0.32 !important; transform: none !important; cursor: not-allowed !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: rgba(255,255,255,0.75) !important;
    border: 1.5px solid rgba(200,150,0,0.20) !important;
    border-radius: 14px !important;
    color: #1a1000 !important;
    font-family: 'Inter','PingFang SC',sans-serif !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #f59e0b !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.16) !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: rgba(80,50,0,0.32) !important;
}
label, .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label {
    color: rgba(80,50,0,0.58) !important;
    font-size: 13px !important; font-weight: 500 !important;
}
.stSelectbox div[data-baseweb="select"] span { color: rgba(50,30,0,0.80) !important; }
.stMultiSelect > div { background: rgba(255,255,255,0.75) !important; border-radius: 14px !important; }
.stMultiSelect span[data-baseweb="tag"] { background: rgba(245,158,11,0.18) !important; color: #92400e !important; }

/* ── CHAT ── */
.bai {
    background: rgba(255,255,255,0.65);
    border: 1px solid rgba(200,150,0,0.16);
    border-radius: 18px 18px 18px 4px;
    padding: 13px 17px; font-size: 14px; line-height: 1.75;
    margin: 6px 0 6px 44px; color: rgba(50,30,0,0.82);
    white-space: pre-wrap;
    box-shadow: 0 2px 12px rgba(200,140,0,0.06);
}
.buser {
    background: linear-gradient(135deg, #d97706, #f59e0b, #f97316);
    border-radius: 18px 18px 4px 18px;
    padding: 13px 17px; font-size: 14px; line-height: 1.75;
    margin: 6px 44px 6px 0; color: #fff; text-align: right;
    box-shadow: 0 4px 16px rgba(217,119,6,0.32);
}
.clbl { font-size:11px; color:rgba(80,50,0,0.36); font-weight:600; margin-bottom:3px; }

/* ── MISC ── */
.divider { border:none; border-top:1px solid rgba(200,150,0,0.12); margin:32px 0; }
.det {
    background: rgba(255,253,240,0.80);
    border: 1px solid rgba(200,150,0,0.16);
    border-radius: 16px; padding: 20px; margin-top: 8px;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 20px rgba(200,140,0,0.06);
}
.dsec {
    font-size:10px; font-weight:700; color:rgba(180,120,0,0.52);
    letter-spacing:1px; text-transform:uppercase;
    margin-bottom:10px; margin-top:16px;
}
.dsec:first-child { margin-top:0; }
.rr { display:flex; gap:8px; font-size:13px; color:rgba(60,35,0,0.62); margin-bottom:7px; line-height:1.5; }
.ok-glass {
    background: rgba(255,253,240,0.82);
    border: 1.5px solid rgba(245,158,11,0.32);
    border-radius: 22px; padding: 40px; text-align: center;
    box-shadow: 0 8px 40px rgba(200,140,0,0.10);
}
.fs {
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(200,150,0,0.16);
    border-radius: 16px; padding: 20px 22px; margin-bottom: 14px;
    box-shadow: 0 2px 12px rgba(200,140,0,0.05);
}
.ft {
    font-size:11px; font-weight:700; color:rgba(180,120,0,0.52);
    letter-spacing:0.8px; text-transform:uppercase; margin-bottom:14px;
}
.sc {
    background: rgba(255,248,220,0.65);
    border: 1px solid rgba(200,150,0,0.14);
    border-radius: 12px; padding: 10px; text-align: center;
}

::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-thumb { background: rgba(200,150,0,0.20); border-radius:2px; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════
def init():
    for k, v in {
        "page": "home", "quiz_step": 0, "quiz_answers": {},
        "results": None, "ai_reason": None, "expand_club": None,
        "cart": [], "applications": [], "chat_history": [],
        "create_submitted": False, "ai_suggestion": "",
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v
init()


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def go(p): st.session_state.page = p; st.rerun()
def cbyid(cid): return next((c for c in CLUBS if c["id"] == cid), None)
def applied(cid): return any(cid in a["clubs"] for a in st.session_state.applications)
def incart(cid): return cid in st.session_state.cart
def toggle(cid):
    if cid in st.session_state.cart: st.session_state.cart.remove(cid)
    else: st.session_state.cart.append(cid)

def tags(club):
    return "".join(f'<span class="pill pill-b">{t}</span>' for t in club.get("tags", []))

def scell(v, l):
    return (f'<div class="sc">'
            f'<div style="font-size:14px;font-weight:800;color:#1a1000;">{v}</div>'
            f'<div style="font-size:10px;color:rgba(80,50,0,0.38);margin-top:2px;">{l}</div>'
            f'</div>')

def sbar(s):
    st.markdown(
        f'<div class="srow">'
        f'<span style="font-size:11px;color:rgba(80,50,0,0.36);min-width:36px;">匹配</span>'
        f'<div class="strk"><div class="sfil" style="width:{s}%;"></div></div>'
        f'<span class="spct">{s}%</span></div>',
        unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  AI
# ═══════════════════════════════════════════════════════════════
SYS = """你是 ClubMatch 平台的顾问助手。
回答风格：像一个熟悉校园生活的学长/学姐，说话直接、亲切，给实用建议。用中文，适当分段，不用标题。
不要用「当然」「首先」「总的来说」这类套话开头。直接说重点。"""

def local_score(ans):
    res = []
    for c in CLUBS:
        s = c["score_base"]
        a0=ans.get(0); a1=ans.get(1); a2=ans.get(2); a3=ans.get(3)
        a4=ans.get(4); a5=ans.get(5); a6=ans.get(6); a7=ans.get(7)
        if a0==0 and c["id"] in [1,2,10]: s+=12
        if a0==1 and c["id"] in [4,11]:   s+=12
        if a0==2 and c["id"] in [3,10,12,16]: s+=10
        if a0==3 and c["id"] in [6,12,13]: s+=12
        if a1==0 and c["id"] in [5,8]:    s+=10
        if a1==1 and c["id"] in [4,11]:   s+=12
        if a1==2 and c["id"] in [1,2,8]:  s+=8
        if a1==3 and c["id"] in [6,7,15]: s+=8
        if a2==0 and c["id"] in [1,2]:    s+=12
        if a2==1 and c["id"] in [4,5,8]:  s+=10
        if a2==2 and c["id"] in [3,9,14]: s+=12
        if a2==3 and c["id"] in [6,12,13]:s+=12
        if a3==0 and c["id"] in [1,2,8]:  s+=8
        if a3==1 and c["id"] in [5,8,16]: s+=8
        if a3==2 and c["id"] in [7,11,15]:s+=8
        if a3==3 and c["id"] in [4,9,14]: s+=8
        pref={0:["低"],1:["中等"],2:["较高","高"],3:["低","中等","较高","高"]}
        if c["time_cost"] in pref.get(a4,[]): s+=6
        if a5==0 and c["id"] in [1,2,8]:  s+=6
        if a5==1 and c["id"] in [6,7,11,13]: s+=6
        if a5==2 and c["id"] in [5,8,10]: s+=6
        if a5==3 and c["id"] in [3,9,4,14]: s+=6
        if a6==0 and c["id"] in [10,12]:  s+=6
        if a6==1 and c["id"] in [11,13,16]: s+=6
        if a6==2 and c["id"] in [7,15]:   s+=6
        if a6==3 and c["id"] in [5,8,14]: s+=6
        if a7==0 and c["id"] in [10,12,1]: s+=5
        if a7==1 and c["id"] in [11,13,5]: s+=5
        if a7==2 and c["id"] in [7,15,3]:  s+=5
        if a7==3 and c["id"] in [9,14,6]:  s+=5
        res.append({**c, "match_score": min(96, s)})
    return sorted(res, key=lambda x: -x["match_score"])

def ai_match(ans):
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not key: return local_score(ans), None
        cl = anthropic.Anthropic(api_key=key)
        alines = "<br />".join(
            f"Q{i+1}「{QUESTIONS[i]['q']}」→ {QUESTIONS[i]['opts'][ans.get(i,0)]['title']}"
            for i in range(len(QUESTIONS)))
        clines = "<br />".join(f"{c['id']}. {c['name']}（{c['type']}）" for c in CLUBS)
        prompt = (f"根据用户测评，为{len(CLUBS)}个社团打匹配分（0-100整数），"
                  f"给出最高匹配社团一句话原因（口语化，≤30字，不要套话）。<br />"
                  f"测评：<br />{alines}<br /><br />社团：<br />{clines}<br /><br />"
                  f"只返回JSON：{{\"scores\":{{\"1\":85,...}},\"reason\":\"...\"}}")
        msg = cl.messages.create(model="claude-opus-4-5", max_tokens=600,
                                  system=SYS, messages=[{"role":"user","content":prompt}])
        t = msg.content[0].text.strip().replace("```json","").replace("```","").strip()
        p = json.loads(t)
        sc = p.get("scores", {})
        res = [{**c, "match_score": min(96, int(sc.get(str(c["id"]), c["score_base"])))} for c in CLUBS]
        return sorted(res, key=lambda x: -x["match_score"]), p.get("reason")
    except Exception:
        return local_score(ans), None

def chat_ai(msg):
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not key:
            return ("我是 ClubMatch 的 AI 顾问，暂时没有联网。<br />"
                    "你可以去「发现社团」逛逛，或者先做个测评看看推荐结果。")
        cl = anthropic.Anthropic(api_key=key)
        info = "<br />".join(
            f"- {c['name']}（{c['type']}）：{c['desc']} | 成员{c['members']}人，评分{c['rating']}，时间投入{c['time_cost']}"
            for c in CLUBS)
        sys2 = f"{SYS}<br /><br />平台社团（共{len(CLUBS)}个）：<br />{info}"
        hist = []
        for t in st.session_state.chat_history:
            if t.get("user"): hist.append({"role":"user","content":t["user"]})
            if t.get("ai"):   hist.append({"role":"assistant","content":t["ai"]})
        hist.append({"role":"user","content":msg})
        r = cl.messages.create(model="claude-opus-4-5", max_tokens=600, system=sys2, messages=hist)
        return r.content[0].text
    except Exception:
        return "现在连不上，稍后再试～"


# ═══════════════════════════════════════════════════════════════
#  NAV
# ═══════════════════════════════════════════════════════════════
def nav():
    cn = len(st.session_state.cart)
    cs = f" ({cn})" if cn else ""
    st.markdown(
        '<div class="nav">'
        '<div class="logo"><span class="logo-badge">CM</span>Club<em>Match</em></div>'
        '<div style="font-size:12px;color:rgba(80,50,0,0.38);font-weight:500;">每个人都值得找到属于自己的圈子</div>'
        '</div>', unsafe_allow_html=True)
    tabs = [("🏠","首页","home"),("🧠","匹配测评","quiz"),("🔍","发现社团","browse"),
            ("🤖","AI 顾问","chat"),("📋",f"我的申请{cs}","apply"),("✨","申请创建","create")]
    cols = st.columns(6, gap="small")
    for col,(icon,label,pg) in zip(cols,tabs):
        with col:
            if st.button(f"{icon} {label}", key=f"nav_{pg}",
                         type="primary" if st.session_state.page==pg else "secondary",
                         use_container_width=True):
                go(pg)


# ═══════════════════════════════════════════════════════════════
#  PAGE: QUIZ  — 每题只有 4 个 st.button，点哪个选哪个
# ═══════════════════════════════════════════════════════════════
def page_quiz():
    nav()

    step  = st.session_state.quiz_step
    total = len(QUESTIONS)
    q     = QUESTIONS[step]
    pct   = int(step / total * 100)
    cur   = st.session_state.quiz_answers.get(step)

    # 进度条
    st.markdown(
        f'<div class="prog-wrap">'
        f'<div class="prog-meta"><span>第 {step+1} 题 / 共 {total} 题</span><b>{pct}%</b></div>'
        f'<div class="prog-track"><div class="prog-fill" style="width:{pct}%;"></div></div>'
        f'</div>', unsafe_allow_html=True)

    _, mid, _ = st.columns([0.3, 4, 0.3])
    with mid:
        # 题目
        st.markdown(
            f'<div style="font-size:11px;font-weight:700;color:#d97706;letter-spacing:1px;'
            f'text-transform:uppercase;margin-bottom:12px;">Q{step+1}</div>'
            f'<div style="font-size:clamp(20px,3vw,28px);font-weight:900;letter-spacing:-0.6px;'
            f'line-height:1.28;margin-bottom:8px;color:#1a1000;">{q["q"]}</div>',
            unsafe_allow_html=True)
        hint = q.get("hint", "")
        if hint:
            st.markdown(
                f'<div style="font-size:13px;color:rgba(80,50,0,0.38);'
                f'margin-bottom:20px;font-style:italic;">{hint}</div>',
                unsafe_allow_html=True)
        else:
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

        # 4 个选项，2列布局，每个选项只有一个按钮
        opts = q["opts"]
        c1, c2 = st.columns(2, gap="medium")
        cols_map = [c1, c2, c1, c2]

        for i, o in enumerate(opts):
            is_sel = (cur == i)
            with cols_map[i]:
                # 选中时用金色卡片背景
                bg   = "rgba(255,248,220,0.95)" if is_sel else "rgba(255,255,255,0.60)"
                bord = "rgba(245,158,11,0.65)"   if is_sel else "rgba(200,150,0,0.20)"
                shad = ("0 0 0 3px rgba(245,158,11,0.18),0 4px 18px rgba(200,140,0,0.15)"
                        if is_sel else "0 2px 10px rgba(200,140,0,0.07)")
                chk_bg    = "linear-gradient(135deg,#f59e0b,#fbbf24)" if is_sel else "transparent"
                chk_bord  = "transparent" if is_sel else "rgba(200,150,0,0.28)"
                chk_color = "#fff" if is_sel else "transparent"

                st.markdown(f"""
<div style="
    display:flex;align-items:center;gap:12px;
    padding:15px 16px;border-radius:16px;
    border:2px solid {bord};
    background:{bg};
    margin-bottom:2px;
    box-shadow:{shad};
">
    <div style="font-size:26px;flex-shrink:0;">{o['icon']}</div>
    <div style="flex:1;">
        <div style="font-size:14px;font-weight:700;color:#1a1000;margin-bottom:2px;">{o['title']}</div>
        <div style="font-size:12px;color:rgba(80,50,0,0.46);line-height:1.4;">{o['sub']}</div>
    </div>
    <div style="
        width:20px;height:20px;border-radius:50%;
        border:2px solid {chk_bord};
        background:{chk_bg};
        display:flex;align-items:center;justify-content:center;
        font-size:10px;font-weight:800;color:{chk_color};flex-shrink:0;
    ">{'✓' if is_sel else ''}</div>
</div>
""", unsafe_allow_html=True)
                # 唯一的按钮，宽度撑满，选中时 primary 样式
                if st.button(
                    f"{'✓ ' if is_sel else ''}{o['title']}",
                    key=f"qopt_{step}_{i}",
                    type="primary" if is_sel else "secondary",
                    use_container_width=True
                ):
                    st.session_state.quiz_answers[step] = i
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # 导航
        done = step in st.session_state.quiz_answers
        nl, nr = st.columns(2, gap="small")
        with nl:
            if st.button("← 返回" if step == 0 else "← 上一题", key="qbk", use_container_width=True):
                if step == 0: go("home")
                else: st.session_state.quiz_step -= 1; st.rerun()
        with nr:
            lbl = "看看我的结果 →" if step == total - 1 else "下一题 →"
            if st.button(lbl, key="qnx", type="primary", use_container_width=True, disabled=not done):
                if step == total - 1:
                    with st.spinner("分析中，稍等…"):
                        res, reason = ai_match(st.session_state.quiz_answers)
                        st.session_state.results   = res
                        st.session_state.ai_reason = reason
                    go("results")
                else:
                    st.session_state.quiz_step += 1; st.rerun()

        if not done:
            st.markdown(
                '<div style="text-align:center;font-size:12px;color:rgba(150,100,0,0.42);margin-top:10px;">'
                '选一个再继续</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE: HOME
# ═══════════════════════════════════════════════════════════════
def page_home():
    nav()
    cl, cr = st.columns([1.15, 1], gap="large")
    with cl:
        st.markdown('<div class="eyebrow">✦ 找到真正合适你的社团</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="h1">大学四年<br>你值得遇见<br><span class="g1">志同道合的伙伴</span></div>'
            '<div class="sub">选社团不是赌博。8 道真实情景题，<br>'
            '把你的习惯和喜好说清楚，<br>我们帮你从 16 个社团里找那个对的。</div>',
            unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🎯  开始匹配", key="hs", type="primary", use_container_width=True):
                st.session_state.quiz_step=0; st.session_state.quiz_answers={}; go("quiz")
        with b2:
            if st.button("🔍  先逛逛", key="hb", use_container_width=True):
                go("browse")
        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        for col,(n,l) in zip([c1,c2,c3,c4],[("16","个社团"),("3,800+","在校成员"),("94%","觉得匹配准"),("8题","搞定测评")]):
            with col:
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<div class="snum">{n}</div>'
                    f'<div class="slbl">{l}</div></div>',
                    unsafe_allow_html=True)

    with cr:
        top = CLUBS[0]
        st.markdown(
            f'<div class="g pin" style="margin-top:4px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">'
            f'<div style="font-size:44px;">{top["emoji"]}</div>'
            f'<div style="text-align:right;">'
            f'<div style="font-size:42px;font-weight:900;'
            f'background:linear-gradient(135deg,#f59e0b,#f97316);'
            f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;'
            f'letter-spacing:-2px;line-height:1;">92%</div>'
            f'<div style="font-size:10px;color:rgba(80,50,0,0.36);margin-top:2px;">示例匹配度</div>'
            f'</div></div>'
            f'<div style="font-size:18px;font-weight:800;margin-bottom:4px;color:#1a1000;">{top["name"]}</div>'
            f'<div class="vibe">{top.get("vibe","")}</div>'
            f'<div style="font-size:13px;color:rgba(60,35,0,0.50);line-height:1.65;margin-bottom:14px;">{top["desc"]}</div>'
            f'<div style="margin-bottom:14px;">{tags(top)}<span class="pill pill-o">热门</span></div>'
            f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">'
            + scell(top["members"],"成员") + scell(f"⭐{top['rating']}","评分") + scell(f"{top['awards']}项","获奖") +
            f'</div></div>'
            f'<div style="text-align:center;font-size:12px;color:rgba(80,50,0,0.28);margin-top:8px;">'
            f'本周已有 102 位同学完成匹配</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;margin-bottom:28px;">'
        '<div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#d97706;'
        'text-transform:uppercase;margin-bottom:10px;">有什么不一样</div>'
        '<div style="font-size:24px;font-weight:900;letter-spacing:-0.6px;color:#1a1000;">'
        '不靠感觉，靠题目说话</div></div>', unsafe_allow_html=True)
    feats = [
        ("🧬","问的是真实习惯，不是爱好",
         "「你周末会主动找人玩吗」比「你外向吗」靠谱多了。8 道情景题，测的是你平时真正的样子。"),
        ("📊","加入前把数据摆出来",
         "每周要花多少时间、活动频率、成员规模……全透明，不用靠打听。"),
        ("🤖","有问题直接问 AI",
         "「内向的人适合哪个」「我快期末了还能加吗」——随便问，不评判。"),
    ]
    cols = st.columns(3, gap="medium")
    for col,(icon,title,desc) in zip(cols,feats):
        with col:
            st.markdown(
                f'<div class="g" style="min-height:160px;">'
                f'<div style="font-size:26px;margin-bottom:12px;">{icon}</div>'
                f'<div style="font-size:14px;font-weight:800;margin-bottom:8px;color:#1a1000;">{title}</div>'
                f'<div style="font-size:13px;color:rgba(60,35,0,0.50);line-height:1.68;">{desc}</div>'
                f'</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    picks = random.sample(CLUBS, 3)
    st.markdown(
        '<div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#d97706;'
        'text-transform:uppercase;margin-bottom:10px;">今日随机推荐</div>'
        '<div style="font-size:20px;font-weight:900;letter-spacing:-0.4px;margin-bottom:20px;color:#1a1000;">'
        '先看看，也许就看上了</div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    for col,club in zip(cols,picks):
        with col:
            st.markdown(
                f'<div class="g">'
                f'<div style="font-size:34px;margin-bottom:10px;">{club["emoji"]}</div>'
                f'<div style="font-size:15px;font-weight:800;margin-bottom:3px;color:#1a1000;">{club["name"]}</div>'
                f'<div class="vibe">{club.get("vibe","")}</div>'
                f'<div style="font-size:13px;color:rgba(60,35,0,0.50);line-height:1.55;margin-bottom:12px;">'
                f'{club["desc"][:55]}...</div><div>{tags(club)}</div></div>',
                unsafe_allow_html=True)
            if st.button("了解一下", key=f"hc_{club['id']}", use_container_width=True):
                st.session_state.expand_club = club["id"]; go("browse")

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1,2,1])
    with mid:
        if st.button("还没找到感觉？做个测评试试 →", key="hcta2", type="primary", use_container_width=True):
            st.session_state.quiz_step=0; st.session_state.quiz_answers={}; go("quiz")


# ═══════════════════════════════════════════════════════════════
#  PAGE: RESULTS
# ═══════════════════════════════════════════════════════════════
def page_results():
    nav()
    res = st.session_state.results
    if not res:
        st.warning("还没做测评，先去答题吧～")
        if st.button("去测评", type="primary"): go("quiz")
        return
    reason = st.session_state.get("ai_reason")
    st.markdown(
        '<div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#d97706;'
        'text-transform:uppercase;margin-bottom:10px;">你的匹配报告</div>'
        f'<div style="font-size:clamp(20px,4vw,34px);font-weight:900;letter-spacing:-1px;'
        f'margin-bottom:10px;color:#1a1000;">从 {len(CLUBS)} 个里挑出来的，应该挺准</div>',
        unsafe_allow_html=True)
    if reason:
        st.markdown(
            f'<div style="background:rgba(255,248,220,0.82);border:1px solid rgba(245,158,11,0.26);'
            f'border-radius:14px;padding:14px 18px;font-size:14px;color:rgba(60,35,0,0.72);'
            f'line-height:1.68;margin-bottom:24px;">'
            f'<span style="color:#d97706;font-weight:700;">分析结果：</span>{reason}</div>',
            unsafe_allow_html=True)

    bnames=["🥇 最匹配","🥈 推荐","🥉 推荐"]
    bcls=["pill-o","pill-v","pill-b"]
    cols=st.columns(3, gap="small")
    for idx,club in enumerate(res):
        with cols[idx%3]:
            app=applied(club["id"]); inc=incart(club["id"])
            bc=bcls[idx] if idx<3 else "pill-b"
            bl=bnames[idx] if idx<3 else f"#{idx+1}"
            ab='<span class="pill pill-g">✓ 已报名</span>' if app else ""
            feat="pin" if idx==0 else ""
            st.markdown(
                f'<div class="g {feat}">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">'
                f'<div style="font-size:34px;">{club["emoji"]}</div>'
                f'<span class="pill {bc}">{bl}</span></div>'
                f'<div style="font-size:15px;font-weight:800;margin-bottom:2px;color:#1a1000;">{club["name"]}</div>'
                f'<div style="font-size:11px;color:rgba(80,50,0,0.38);margin-bottom:10px;">{club["type"]} · {club["freq"]}</div>',
                unsafe_allow_html=True)
            sbar(club["match_score"])
            st.markdown(
                f'<div class="vibe">{club.get("vibe","")}</div>'
                f'<div style="font-size:13px;color:rgba(60,35,0,0.52);line-height:1.55;margin-bottom:12px;">{club["desc"][:58]}...</div>'
                f'<div style="margin-bottom:14px;">{tags(club)}{ab}</div></div>',
                unsafe_allow_html=True)
            b1,b2=st.columns(2,gap="small")
            with b1:
                if st.button("详情",key=f"rd_{club['id']}_{idx}",use_container_width=True):
                    st.session_state.expand_club=(club["id"] if st.session_state.expand_club!=club["id"] else None)
                    st.rerun()
            with b2:
                if app:
                    st.button("已报名",key=f"ra_{club['id']}",disabled=True,use_container_width=True)
                elif inc:
                    if st.button("取消",key=f"rr_{club['id']}_{idx}",use_container_width=True):
                        toggle(club["id"]); st.rerun()
                else:
                    if st.button("+ 申请袋",key=f"radd_{club['id']}_{idx}",type="primary",use_container_width=True):
                        toggle(club["id"]); st.rerun()
            if st.session_state.expand_club==club["id"]:
                club_detail(club)

    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4,gap="small")
    with c1:
        if st.button("重新测评",key="rr",use_container_width=True):
            st.session_state.quiz_step=0; st.session_state.quiz_answers={}; go("quiz")
    with c2:
        if st.button("发现更多",key="rb",use_container_width=True): go("browse")
    with c3:
        if st.button("问 AI",key="rc",use_container_width=True): go("chat")
    with c4:
        cn=len(st.session_state.cart)
        if cn:
            if st.button(f"提交申请 ({cn})",key="rapp",type="primary",use_container_width=True): go("apply")
        else:
            st.button("申请袋是空的",key="rape",disabled=True,use_container_width=True)


def club_detail(club):
    app=applied(club["id"])
    rr="".join(
        f'<div class="rr"><span style="color:#d97706;flex-shrink:0;">·</span><span>{r}</span></div>'
        for r in club.get("requirements",[]))
    ar="".join(
        f'<div class="rr"><span style="color:#f97316;flex-shrink:0;">·</span><span>{a}</span></div>'
        for a in club.get("activities",[]))
    st4="".join(scell(v,l) for v,l in [
        (str(club["members"]),"成员"),
        (f"⭐{club['rating']}","评分"),
        (f"{club['awards']}项","获奖"),
        (club["time_cost"],"时间投入")])
    an=('<div style="margin-top:12px;padding:10px 14px;background:rgba(16,185,129,0.07);'
        'border:1px solid rgba(16,185,129,0.22);border-radius:10px;font-size:12px;'
        'color:#047857;text-align:center;">✓ 你已报名这个社团</div>') if app else ""
    st.markdown(
        f'<div class="det">'
        f'<div class="dsec">关于我们</div>'
        f'<div style="font-size:13px;color:rgba(60,35,0,0.66);line-height:1.72;">{club.get("detail","")}</div>'
        f'<div class="dsec">适合哪类人</div>'
        f'<div style="font-size:13px;color:rgba(60,35,0,0.66);">→ {club.get("best_for","")}</div>'
        f'<div class="dsec">招新要求</div>{rr}'
        f'<div class="dsec">常规活动</div>{ar}'
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:14px;">{st4}</div>'
        f'{an}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE: BROWSE
# ═══════════════════════════════════════════════════════════════
def page_browse():
    nav()
    st.markdown(
        '<div style="font-size:24px;font-weight:900;letter-spacing:-0.6px;margin-bottom:4px;color:#1a1000;">发现社团</div>',
        unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:14px;color:rgba(80,50,0,0.40);margin-bottom:20px;">{len(CLUBS)} 个社团，随便逛</div>',
        unsafe_allow_html=True)
    cs,cf=st.columns([2,1])
    with cs: search=st.text_input("",placeholder="搜名称、类型、标签…",label_visibility="collapsed",key="bs")
    with cf:
        types=["全部类型"]+sorted({c["type"] for c in CLUBS})
        selt=st.selectbox("",types,label_visibility="collapsed",key="bt")
    filtered=[c for c in CLUBS
               if (not search or search in c["name"] or search in c["type"]
                   or any(search in t for t in c.get("tags",[])) or search in c.get("desc",""))
               and (selt=="全部类型" or c["type"]==selt)]
    if not filtered:
        st.markdown(
            '<div style="text-align:center;padding:60px;color:rgba(80,50,0,0.28);">没找到，换个词试试？</div>',
            unsafe_allow_html=True)
        return
    cols=st.columns(3,gap="small")
    for idx,club in enumerate(filtered):
        with cols[idx%3]:
            app=applied(club["id"]); inc=incart(club["id"])
            ex=('<span class="pill pill-g">✓ 已报名</span>' if app
                else ('<span class="pill pill-v">在申请袋里</span>' if inc else ""))
            sr="".join(
                f'<div style="text-align:center;">'
                f'<div style="font-size:13px;font-weight:800;color:#1a1000;">{v}</div>'
                f'<div style="font-size:10px;color:rgba(80,50,0,0.33);margin-top:2px;">{l}</div></div>'
                for v,l in [(str(club["members"]),"成员"),(f"⭐{club['rating']}","评分"),(f"{club['awards']}项","获奖")])
            st.markdown(
                f'<div class="g">'
                f'<div style="font-size:34px;margin-bottom:10px;">{club["emoji"]}</div>'
                f'<div style="font-size:15px;font-weight:800;margin-bottom:2px;color:#1a1000;">{club["name"]}</div>'
                f'<div style="font-size:11px;color:rgba(80,50,0,0.33);margin-bottom:8px;">{club["type"]} · 成立 {club["founded"]}</div>'
                f'<div class="vibe">{club.get("vibe","")}</div>'
                f'<div style="font-size:13px;color:rgba(60,35,0,0.50);line-height:1.55;margin-bottom:12px;">{club["desc"][:62]}...</div>'
                f'<div style="margin-bottom:12px;">{tags(club)}{ex}</div>'
                f'<div style="display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid rgba(200,150,0,0.10);padding-top:12px;">{sr}</div>'
                f'</div>', unsafe_allow_html=True)
            b1,b2=st.columns(2,gap="small")
            with b1:
                exp=st.session_state.expand_club==club["id"]
                if st.button("收起" if exp else "查看详情",key=f"bd_{club['id']}_{idx}",use_container_width=True):
                    st.session_state.expand_club=club["id"] if not exp else None; st.rerun()
            with b2:
                if app:
                    st.button("已报名",key=f"ba_{club['id']}",disabled=True,use_container_width=True)
                elif inc:
                    if st.button("取消",key=f"br_{club['id']}_{idx}",use_container_width=True):
                        toggle(club["id"]); st.rerun()
                else:
                    if st.button("+ 申请袋",key=f"badd_{club['id']}_{idx}",type="primary",use_container_width=True):
                        toggle(club["id"]); st.rerun()
            if st.session_state.expand_club==club["id"]:
                club_detail(club)
    st.markdown("<br>", unsafe_allow_html=True)
    _,mid,_=st.columns([1,2,1])
    with mid:
        cn=len(st.session_state.cart)
        if cn:
            if st.button(f"去提交申请（已选 {cn} 个）",type="primary",use_container_width=True,key="bgo"):
                go("apply")
        if st.button("没找到合适的？申请创建新社团",use_container_width=True,key="bcr"):
            go("create")


# ═══════════════════════════════════════════════════════════════
#  PAGE: CHAT
# ═══════════════════════════════════════════════════════════════
def page_chat():
    nav()
    st.markdown(
        '<div style="font-size:22px;font-weight:900;letter-spacing:-0.5px;margin-bottom:4px;color:#1a1000;">问 AI 顾问</div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:13px;color:rgba(80,50,0,0.38);margin-bottom:24px;">'
        '由 Claude 驱动 · 16 个社团的情况它都知道</div>',
        unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.session_state.chat_history=[{"user":None,"ai":(
            f"你好！我是 ClubMatch 的 AI 顾问。<br /><br />"
            f"平台上 {len(CLUBS)} 个社团我都了解，你可以问我：<br />"
            f"· 某个社团平时具体做什么、氛围怎么样<br />"
            f"· 根据你的情况帮你推荐<br />"
            f"· 比如「我比较宅，哪个适合我」「大二还能加吗」……<br /><br />"
            f"随便问。")}]
    for t in st.session_state.chat_history:
        if t.get("user"):
            st.markdown(
                '<div style="text-align:right;font-size:11px;color:rgba(80,50,0,0.36);'
                'font-weight:600;margin-bottom:3px;">你</div>',
                unsafe_allow_html=True)
            st.markdown(f'<div class="buser">{t["user"]}</div>', unsafe_allow_html=True)
        if t.get("ai"):
            st.markdown('<div class="clbl">AI 顾问</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bai">{t["ai"]}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if len(st.session_state.chat_history)<=1:
        st.markdown(
            '<div style="font-size:12px;color:rgba(80,50,0,0.33);margin-bottom:8px;">可以这样问</div>',
            unsafe_allow_html=True)
        sugg=["内向的人适合哪个？","时间不多选哪个？","摄影社和微电影社有啥区别？",
              "创业社真的有用吗？","完全不知道自己喜欢什么？","哪个最容易交到朋友？"]
        cols=st.columns(3,gap="small")
        for i,s in enumerate(sugg):
            with cols[i%3]:
                if st.button(s,key=f"sg_{i}",use_container_width=True):
                    with st.spinner("想一下…"): rep=chat_ai(s)
                    st.session_state.chat_history.append({"user":s,"ai":rep}); st.rerun()
    ci,cs=st.columns([5,1])
    with ci:
        ui=st.text_input("",placeholder="问点什么…",label_visibility="collapsed",key="ci")
    with cs:
        send=st.button("发送",key="cs",type="primary",use_container_width=True)
    if send and ui.strip():
        with st.spinner("想一下…"): rep=chat_ai(ui.strip())
        st.session_state.chat_history.append({"user":ui.strip(),"ai":rep}); st.rerun()
    if len(st.session_state.chat_history)>1:
        if st.button("清空对话",key="cc"):
            st.session_state.chat_history=[]; st.rerun()


# ═══════════════════════════════════════════════════════════════
#  PAGE: APPLY
# ═══════════════════════════════════════════════════════════════
def page_apply():
    nav()
    cart=st.session_state.cart
    if not cart:
        st.markdown(
            '<div style="font-size:20px;font-weight:800;color:#1a1000;margin-bottom:8px;">申请袋是空的</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div style="color:rgba(80,50,0,0.44);margin-bottom:24px;font-size:14px;">'
            '去发现社团，把感兴趣的加进来</div>',
            unsafe_allow_html=True)
        if st.button("去逛逛",type="primary"): go("browse")
        return
    st.markdown(
        '<div style="font-size:24px;font-weight:900;letter-spacing:-0.6px;margin-bottom:4px;color:#1a1000;">提交申请</div>',
        unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:14px;color:rgba(80,50,0,0.40);margin-bottom:24px;">'
        f'选了 {len(cart)} 个，填一次就全提交了</div>',
        unsafe_allow_html=True)
    cl,cr=st.columns([1.2,1],gap="large")
    with cl:
        st.markdown('<div class="fs"><div class="ft">申请袋</div>',unsafe_allow_html=True)
        for cid in list(cart):
            club=cbyid(cid)
            if not club: continue
            cL,cR=st.columns([3,1])
            with cL:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;padding:10px 0;'
                    f'border-bottom:1px solid rgba(200,150,0,0.08);">'
                    f'<span style="font-size:22px;">{club["emoji"]}</span>'
                    f'<div><div style="font-size:14px;font-weight:700;color:#1a1000;">{club["name"]}</div>'
                    f'<div style="font-size:11px;color:rgba(80,50,0,0.36);">{club["type"]} · {club["freq"]}</div>'
                    f'</div></div>', unsafe_allow_html=True)
            with cR:
                if st.button("移除",key=f"arm_{cid}",use_container_width=True):
                    toggle(cid); st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
        if st.button("+ 继续添加",key="am",use_container_width=True): go("browse")
        st.markdown("""
        <div class="fs" style="margin-top:14px;">
            <div class="ft">接下来怎么走</div>
            <div style="display:flex;flex-direction:column;gap:14px;">
                <div style="display:flex;gap:12px;">
                    <div style="width:26px;height:26px;border-radius:50%;
                        background:rgba(245,158,11,0.14);color:#d97706;
                        font-size:12px;font-weight:700;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;">1</div>
                    <div>
                        <div style="font-size:13px;font-weight:700;color:#1a1000;margin-bottom:2px;">社团会来联系你</div>
                        <div style="font-size:12px;color:rgba(80,50,0,0.46);line-height:1.5;">3 个工作日内，负责人会用手机或微信联系你，说明下一步安排。</div>
                    </div>
                </div>
                <div style="display:flex;gap:12px;">
                    <div style="width:26px;height:26px;border-radius:50%;
                        background:rgba(245,158,11,0.14);color:#d97706;
                        font-size:12px;font-weight:700;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;">2</div>
                    <div>
                        <div style="font-size:13px;font-weight:700;color:#1a1000;margin-bottom:2px;">先去体验一次活动</div>
                        <div style="font-size:12px;color:rgba(80,50,0,0.46);line-height:1.5;">大部分社团会让你先来旁听，感受真实氛围，不满意不用加。</div>
                    </div>
                </div>
                <div style="display:flex;gap:12px;">
                    <div style="width:26px;height:26px;border-radius:50%;
                        background:rgba(245,158,11,0.14);color:#d97706;
                        font-size:12px;font-weight:700;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;">3</div>
                    <div>
                        <div style="font-size:13px;font-weight:700;color:#1a1000;margin-bottom:2px;">进群，正式开始</div>
                        <div style="font-size:12px;color:rgba(80,50,0,0.46);line-height:1.5;">确认加入就拉进微信群，从这里开始认识新朋友。</div>
                    </div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    with cr:
        st.markdown('<div class="fs"><div class="ft">个人信息</div>',unsafe_allow_html=True)
        name=st.text_input("姓名 *",placeholder="真实姓名",key="fn")
        sid=st.text_input("学号 *",placeholder="例：2024XXXXXXXX",key="fs")
        major=st.text_input("专业 *",placeholder="例：国际经济与贸易",key="fm")
        grade=st.selectbox("年级 *",["请选择","大一","大二","大三","大四","研究生"],key="fg")
        phone=st.text_input("手机号 *",placeholder="社团负责人会用这个联系你",key="fp")
        wechat=st.text_input("微信号（选填）",placeholder="方便拉你进群",key="fw")
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<div class="fs" style="margin-top:10px;"><div class="ft">补充一点</div>',unsafe_allow_html=True)
        intro=st.text_area("自我介绍 *",placeholder="随便说说自己，为啥对这个社团感兴趣（100字以内就行）",height=100,key="fi")
        ta=st.multiselect("空闲时间",["周一至周五 白天","周一至周五 晚上","周末全天","周末上午","周末下午"],key="ft2")
        sk=st.text_input("有什么特长（选填）",placeholder="比如摄影、吉他、编程……",key="fsk")
        st.markdown('</div>',unsafe_allow_html=True)
        ok=all([name.strip(),sid.strip(),major.strip(),grade!="请选择",phone.strip(),intro.strip()])
        if st.button("提交申请",key="asub",type="primary",use_container_width=True,disabled=not ok):
            st.session_state.applications.append({
                "clubs":list(cart),"name":name,"student_id":sid,"major":major,
                "grade":grade,"phone":phone,"wechat":wechat,"intro":intro,
                "time_avail":ta,"skill":sk})
            st.session_state.cart=[]; go("success")
        if not ok:
            st.markdown(
                '<div style="font-size:12px;color:rgba(150,100,0,0.48);text-align:center;margin-top:6px;">'
                '带 * 的都填完才能提交</div>',
                unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE: SUCCESS
# ═══════════════════════════════════════════════════════════════
def page_success():
    nav()
    if not st.session_state.applications: go("home"); return
    last=st.session_state.applications[-1]
    cnames=[cbyid(cid)["name"] for cid in last["clubs"] if cbyid(cid)]
    cl_html="".join(
        f'<div style="display:flex;align-items:center;gap:8px;font-size:14px;'
        f'color:rgba(60,35,0,0.70);margin-bottom:8px;">'
        f'<span style="color:#047857;">✓</span>{n}</div>'
        for n in cnames)
    _,col,_=st.columns([0.5,3,0.5])
    with col:
        st.markdown(
            f'<div class="ok-glass">'
            f'<div style="font-size:52px;margin-bottom:16px;">🎉</div>'
            f'<div style="font-size:26px;font-weight:900;letter-spacing:-0.8px;margin-bottom:10px;color:#1a1000;">提交成功！</div>'
            f'<div style="font-size:15px;color:rgba(80,50,0,0.52);line-height:1.78;margin-bottom:24px;">'
            f'{last["name"]}，稳了。<br>接下来等社团负责人联系你就好。</div>'
            f'<div style="background:rgba(255,248,220,0.65);border:1px solid rgba(200,150,0,0.16);'
            f'border-radius:14px;padding:18px;text-align:left;margin-bottom:20px;">'
            f'<div style="font-size:11px;color:rgba(180,120,0,0.52);font-weight:700;'
            f'letter-spacing:0.8px;text-transform:uppercase;margin-bottom:12px;">你申请的社团</div>'
            f'{cl_html}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        b1,b2=st.columns(2)
        with b1:
            if st.button("继续逛社团",key="sb",use_container_width=True): go("browse")
        with b2:
            if st.button("回首页",key="sh",type="primary",use_container_width=True): go("home")


# ═══════════════════════════════════════════════════════════════
#  PAGE: CREATE
# ═══════════════════════════════════════════════════════════════
def page_create():
    nav()
    st.markdown('<div class="eyebrow">没找到合适的？自己搞一个</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:26px;font-weight:900;letter-spacing:-0.6px;margin-bottom:8px;color:#1a1000;">申请创建新社团</div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:15px;color:rgba(80,50,0,0.46);line-height:1.72;margin-bottom:28px;">'
        '每个存在的社团，都是有人第一次说「我想做这件事」。<br>'
        '如果你有个想法，从这里开始。</div>',
        unsafe_allow_html=True)
    cl,cr=st.columns([1,1],gap="large")
    with cl:
        st.markdown('<div class="fs"><div class="ft">社团基本情况</div>',unsafe_allow_html=True)
        cn=st.text_input("社团名字 *",placeholder="例：城市骑行与街拍社",key="cc")
        ct=st.selectbox("类型 *",["请选择","艺术创作","音乐表演","舞台表演","科技创新","商业创新",
                                       "户外运动","人文学术","公益服务","体育竞技","跨文化交流","科学探索","其他"],key="cct")
        cd=st.text_area("主要做什么 *",placeholder="5 秒内能说清楚最好，别用太多形容词",height=80,key="ccd")
        cw=st.text_area("为什么要创建 *",
                        placeholder="比如：学校没有专注城市骑行的社团，但身边很多人想玩……",
                        height=100,key="ccw")
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<div class="fs" style="margin-top:10px;"><div class="ft">活动构想</div>',unsafe_allow_html=True)
        cap=st.text_area("打算做什么活动",placeholder="初步想法就行，不用完整",height=90,key="cap")
        st.slider("预计初始人数",5,50,15,key="cm")
        st.selectbox("活动频率",["每周一次","每两周一次","每月一次","看项目定","还没想好"],key="cf")
        st.markdown('</div>',unsafe_allow_html=True)
    with cr:
        st.markdown('<div class="fs"><div class="ft">发起人</div>',unsafe_allow_html=True)
        fn=st.text_input("姓名 *",key="cfn")
        fs=st.text_input("学号 *",key="cfs")
        fm=st.text_input("专业 *",key="cfm")
        fg=st.selectbox("年级 *",["请选择","大一","大二","大三","大四","研究生"],key="cfg")
        fp=st.text_input("联系方式 *",key="cfp")
        st.text_area("相关经验（选填）",placeholder="做过类似的组织？或者就是这个领域的爱好者",height=80,key="cfe")
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<div class="fs" style="margin-top:10px;"><div class="ft">让 AI 帮你看看</div>',unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:13px;color:rgba(80,50,0,0.44);line-height:1.6;margin-bottom:14px;">'
            '填完基本信息，让 AI 给几条实用建议。</div>',
            unsafe_allow_html=True)
        if st.button("AI 给我建议",key="cai",use_container_width=True):
            if cn and cd and cw:
                with st.spinner("想一下…"):
                    try:
                        key=st.secrets.get("ANTHROPIC_API_KEY","")
                        if key:
                            cl2=anthropic.Anthropic(api_key=key)
                            msg=cl2.messages.create(
                                model="claude-opus-4-5",max_tokens=500,system=SYS,
                                messages=[{"role":"user","content":
                                    f"一位大学生想创建社团：<br />名称：{cn}<br />类型：{ct}<br />描述：{cd}<br />原因：{cw}<br />活动：{cap}<br /><br />"
                                    f"给3条简短、具体、有用的建议。口语化，不要套话，直接分点说。"}])
                            st.session_state.ai_suggestion=msg.content[0].text
                        else:
                            st.session_state.ai_suggestion=(
                                "1. 把活动说具体——「每月骑行 30km」比「定期活动」更有说服力。<br />"
                                "2. 说清楚你跟现有社团有什么不同。<br />"
                                "3. 先找 2-3 个人一起联署，比一个人申请成功率高很多。")
                    except Exception:
                        st.session_state.ai_suggestion="AI 现在不可用，但你的想法听起来不错，继续填吧！"
            else:
                st.warning("先把名字、描述和创建原因填一下")
        if st.session_state.ai_suggestion:
            st.markdown(
                f'<div class="bai">{st.session_state.ai_suggestion}</div>',
                unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
        aok=all([cn,ct!="请选择",cd,cw,fn,fs,fm,fg!="请选择",fp])
        if st.button("提交创建申请",key="csub",type="primary",use_container_width=True,disabled=not aok):
            st.session_state.create_submitted=True; st.rerun()
        if st.session_state.get("create_submitted"):
            st.markdown(
                f'<div style="margin-top:14px;background:rgba(16,185,129,0.07);'
                f'border:1px solid rgba(16,185,129,0.22);border-radius:14px;padding:16px;text-align:center;">'
                f'<div style="font-size:22px;margin-bottom:8px;">🌱</div>'
                f'<div style="font-size:15px;font-weight:700;margin-bottom:6px;color:#1a1000;">收到了！</div>'
                f'<div style="font-size:13px;color:rgba(60,35,0,0.52);line-height:1.6;">'
                f'学生活动部会在 5 个工作日内审核。<br>{fn}，期待在平台上看到「{cn}」。</div></div>',
                unsafe_allow_html=True)
            if st.button("回首页",key="ch",type="primary"):
                st.session_state.create_submitted=False
                st.session_state.ai_suggestion=""
                go("home")
        if not aok and not st.session_state.get("create_submitted"):
            st.markdown(
                '<div style="font-size:12px;color:rgba(150,100,0,0.48);text-align:center;margin-top:6px;">'
                '带 * 的都填完才能提交</div>',
                unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  ROUTER
# ═══════════════════════════════════════════════════════════════
{
    "home":    page_home,
    "quiz":    page_quiz,
    "results": page_results,
    "browse":  page_browse,
    "chat":    page_chat,
    "apply":   page_apply,
    "success": page_success,
    "create":  page_create,
}.get(st.session_state.page, page_home)()
