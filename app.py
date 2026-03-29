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

# ═══════════════════════════════════════════════════════════════
#  GLOBAL CSS  —  Gold + Glass Theme
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', 'PingFang SC', 'Noto Sans SC', system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 4rem !important;
    max-width: 1180px !important;
}

/* ── BACKGROUND: deep gold aurora ── */
.stApp {
    background:
        radial-gradient(ellipse 80% 60% at 10% 5%,  rgba(212,160,20,0.22) 0%, transparent 55%),
        radial-gradient(ellipse 60% 50% at 90% 90%,  rgba(255,200,50,0.15) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 50%,  rgba(180,140,30,0.10) 0%, transparent 60%),
        linear-gradient(170deg, #0f0c00 0%, #1a1500 45%, #0d0e00 100%);
    color: #fff8e7;
    min-height: 100vh;
}

/* ── LIQUID GLASS CARD ── */
.g {
    background: rgba(255,215,0,0.06);
    backdrop-filter: blur(28px) saturate(200%);
    -webkit-backdrop-filter: blur(28px) saturate(200%);
    border: 1px solid rgba(255,215,0,0.18);
    border-radius: 22px;
    padding: 26px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
    transition: transform 0.28s cubic-bezier(.4,0,.2,1),
                box-shadow 0.28s cubic-bezier(.4,0,.2,1),
                border-color 0.28s;
}
.g::before {
    content: '';
    position: absolute; inset: 0;
    border-radius: 22px;
    background: linear-gradient(135deg,
        rgba(255,215,0,0.10) 0%,
        rgba(255,215,0,0.02) 50%,
        rgba(255,215,0,0.05) 100%);
    pointer-events: none;
}
.g::after {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,215,0,0.40), transparent);
}
.g:hover {
    transform: translateY(-4px);
    border-color: rgba(255,215,0,0.32);
    box-shadow: 0 24px 60px rgba(0,0,0,0.40), 0 0 40px rgba(212,160,20,0.12);
}
.g.pin {
    border-color: rgba(255,200,50,0.55);
    background: rgba(255,200,50,0.09);
    box-shadow: 0 0 0 1px rgba(255,200,50,0.25), 0 8px 32px rgba(212,160,20,0.20);
}

/* ── NAV ── */
.nav {
    position: sticky; top: 0; z-index: 999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 0 16px;
    border-bottom: 1px solid rgba(255,215,0,0.10);
    margin-bottom: 40px;
    background: rgba(15,12,0,0.80);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
}
.logo {
    display: flex; align-items: center; gap: 10px;
    font-size: 20px; font-weight: 900; letter-spacing: -0.5px; color: #fff8e7;
}
.logo-badge {
    background: linear-gradient(135deg, #b8860b, #ffd700);
    border-radius: 10px; padding: 5px 10px;
    font-size: 13px; font-weight: 900; color: #1a1000;
    box-shadow: 0 0 20px rgba(212,160,20,0.55);
}
.logo em { color: #ffd700; font-style: normal; }

/* ── BADGE PILLS ── */
.pill {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600; margin: 2px 3px 2px 0;
}
.pill-v { background: rgba(255,200,50,0.15); color: #ffd700; border: 1px solid rgba(255,200,50,0.35); }
.pill-o { background: rgba(255,160,20,0.18); color: #ffbb33; border: 1px solid rgba(255,160,20,0.35); }
.pill-g { background: rgba(100,200,100,0.15); color: #88e088; border: 1px solid rgba(100,200,100,0.30); }
.pill-b { background: rgba(255,215,0,0.12); color: #ffe066; border: 1px solid rgba(255,215,0,0.28); }

/* ── VIBE TAG ── */
.vibe {
    display: inline-block;
    background: rgba(255,200,50,0.10);
    border: 1px solid rgba(255,200,50,0.25);
    color: #ffd700; border-radius: 8px; padding: 3px 10px;
    font-size: 11px; font-weight: 500; margin-bottom: 12px; font-style: italic;
}

/* ── HERO ── */
.h1 {
    font-size: clamp(40px,6vw,72px);
    font-weight: 900; line-height: 1.04; letter-spacing: -2.5px;
    color: #fff8e7; margin-bottom: 18px;
}
.h1 .g1 {
    background: linear-gradient(135deg, #ffd700 0%, #ffaa00 40%, #ff8c00 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sub {
    font-size: 17px; color: rgba(255,240,180,0.50);
    line-height: 1.75; margin-bottom: 32px; font-weight: 400;
}
.eyebrow {
    display: inline-block;
    background: rgba(255,200,50,0.12);
    border: 1px solid rgba(255,200,50,0.30);
    color: #ffd700; border-radius: 20px; padding: 5px 14px;
    font-size: 11px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 20px;
}

/* ── SCORE BAR ── */
.srow { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.strk { flex:1; height:3px; background:rgba(255,215,0,0.10); border-radius:2px; overflow:hidden; }
.sfil { height:100%; border-radius:2px; background:linear-gradient(90deg,#b8860b,#ffd700); }
.spct { font-size:13px; font-weight:800; color:#ffd700; min-width:38px; text-align:right; }

/* ── STATS ── */
.snum { font-size:30px; font-weight:900; color:#ffd700; letter-spacing:-1.5px; line-height:1; }
.slbl { font-size:11px; color:rgba(255,240,180,0.35); margin-top:4px; font-weight:500; }

/* ── PROGRESS BAR ── */
.prog-wrap { margin-bottom:28px; }
.prog-meta {
    display:flex; justify-content:space-between;
    font-size:12px; color:rgba(255,240,180,0.35); margin-bottom:8px; font-weight:500;
}
.prog-meta b { color:#ffd700; font-weight:700; }
.prog-track { height:3px; background:rgba(255,215,0,0.08); border-radius:2px; overflow:hidden; }
.prog-fill {
    height:100%; border-radius:2px;
    background:linear-gradient(90deg,#b8860b,#ffd700,#ffaa00);
    transition:width 0.5s cubic-bezier(.4,0,.2,1);
}

/* ── STREAMLIT BUTTON OVERRIDES ── */
.stButton > button {
    border-radius: 50px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    border: 1px solid rgba(255,215,0,0.20) !important;
    background: rgba(255,215,0,0.07) !important;
    color: rgba(255,240,180,0.82) !important;
    transition: all 0.22s !important;
    padding: 0.45rem 1.1rem !important;
}
.stButton > button:hover {
    background: rgba(255,215,0,0.14) !important;
    border-color: rgba(255,215,0,0.38) !important;
    color: #ffd700 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 0 20px rgba(212,160,20,0.25) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,#b8860b,#d4a017) !important;
    color: #fff8e7 !important; border: none !important;
    box-shadow: 0 4px 20px rgba(212,160,20,0.45) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg,#d4a017,#ffd700) !important;
    box-shadow: 0 0 30px rgba(255,200,50,0.65), 0 8px 28px rgba(212,160,20,0.40) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:disabled { opacity:0.28 !important; transform:none !important; cursor:not-allowed !important; }

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: rgba(255,215,0,0.05) !important;
    border: 1px solid rgba(255,215,0,0.15) !important;
    border-radius: 14px !important;
    color: #fff8e7 !important;
    font-family: 'Inter','PingFang SC',sans-serif !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #ffd700 !important;
    box-shadow: 0 0 0 3px rgba(255,215,0,0.18), 0 0 16px rgba(212,160,20,0.18) !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder { color:rgba(255,240,180,0.28) !important; }
label, .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label {
    color:rgba(255,240,180,0.52) !important; font-size:13px !important; font-weight:500 !important;
}
.stSelectbox div[data-baseweb="select"] span { color:rgba(255,240,180,0.78) !important; }
.stMultiSelect > div { background:rgba(255,215,0,0.05) !important; border-radius:14px !important; }
.stMultiSelect span[data-baseweb="tag"] { background:rgba(212,160,20,0.22) !important; color:#ffd700 !important; }

/* ── CHAT BUBBLES ── */
.bai {
    background: rgba(255,215,0,0.06);
    border: 1px solid rgba(255,215,0,0.12);
    border-radius: 18px 18px 18px 4px;
    padding: 13px 17px; font-size: 14px; line-height: 1.75;
    margin: 6px 0 6px 44px; color: rgba(255,240,180,0.88);
    white-space: pre-wrap;
}
.buser {
    background: linear-gradient(135deg,#b8860b,#d4a017);
    border-radius: 18px 18px 4px 18px;
    padding: 13px 17px; font-size: 14px; line-height: 1.75;
    margin: 6px 44px 6px 0; color: #fff8e7; text-align: right;
    box-shadow: 0 2px 16px rgba(212,160,20,0.35);
}
.clbl { font-size:11px; color:rgba(255,240,180,0.30); font-weight:600; margin-bottom:3px; }

/* ── MISC ── */
.divider { border:none; border-top:1px solid rgba(255,215,0,0.08); margin:32px 0; }
.det {
    background:rgba(0,0,0,0.30); border:1px solid rgba(255,215,0,0.10);
    border-radius:16px; padding:20px; margin-top:8px;
    backdrop-filter:blur(12px);
}
.dsec {
    font-size:10px; font-weight:700; color:rgba(255,215,0,0.40);
    letter-spacing:1px; text-transform:uppercase; margin-bottom:10px; margin-top:16px;
}
.dsec:first-child { margin-top:0; }
.rr { display:flex; gap:8px; font-size:13px; color:rgba(255,240,180,0.62); margin-bottom:7px; line-height:1.5; }
.ok-glass { background:rgba(255,200,50,0.06); border:1px solid rgba(255,200,50,0.22); border-radius:22px; padding:40px; text-align:center; }
.fs { background:rgba(255,215,0,0.04); border:1px solid rgba(255,215,0,0.10); border-radius:16px; padding:20px 22px; margin-bottom:14px; }
.ft { font-size:11px; font-weight:700; color:rgba(255,215,0,0.38); letter-spacing:0.8px; text-transform:uppercase; margin-bottom:14px; }
.sc { background:rgba(255,215,0,0.04); border:1px solid rgba(255,215,0,0.08); border-radius:12px; padding:10px; text-align:center; }

::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-thumb { background:rgba(255,215,0,0.15); border-radius:2px; }
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
        "quiz_msg": "",
        "pending_quiz_choice": None,
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
    return (f'<div class="sc"><div style="font-size:14px;font-weight:800;color:#fff8e7;">{v}</div>'
            f'<div style="font-size:10px;color:rgba(255,240,180,0.32);margin-top:2px;">{l}</div></div>')

def sbar(s):
    st.markdown(
        f'<div class="srow">'
        f'<span style="font-size:11px;color:rgba(255,240,180,0.32);min-width:36px;">匹配</span>'
        f'<div class="strk"><div class="sfil" style="width:{s}%;"></div></div>'
        f'<span class="spct">{s}%</span></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  AI  (Claude backbone)
# ═══════════════════════════════════════════════════════════════
SYS = """你是 Claude，由 Anthropic 创造。你现在是 ClubMatch 平台的 AI 顾问。
风格：温暖、直接、真实，给具体可行的建议。用中文，适当分段，不用 markdown 标题。
你了解平台所有社团，也理解大学新生选社团时的迷茫与期待。"""

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
        res.append({**c,"match_score":min(96,s)})
    return sorted(res,key=lambda x:-x["match_score"])

def ai_match(ans):
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY","")
        if not key: return local_score(ans), None
        cl = anthropic.Anthropic(api_key=key)
        alines = "<br />".join(
            f"Q{i+1}「{QUESTIONS[i]['q']}」→ {QUESTIONS[i]['opts'][ans.get(i,0)]['title']}"
            for i in range(len(QUESTIONS)))
        clines = "<br />".join(f"{c['id']}. {c['name']}（{c['type']}）" for c in CLUBS)
        prompt = (f"根据用户测评，为{len(CLUBS)}个社团打匹配分（0-100整数），"
                  f"给出最高匹配社团一句话原因（温暖，≤40字）。<br />"
                  f"测评：<br />{alines}<br /><br />社团：<br />{clines}<br /><br />"
                  f"只返回JSON：{{\"scores\":{{\"1\":85,...}},\"reason\":\"...\"}}")
        msg = cl.messages.create(model="claude-opus-4-5", max_tokens=600,
                                  system=SYS, messages=[{"role":"user","content":prompt}])
        t = msg.content[0].text.strip().replace("```json","").replace("```","").strip()
        p = json.loads(t)
        sc = p.get("scores",{})
        res = [{**c,"match_score":min(96,int(sc.get(str(c["id"]),c["score_base"])))} for c in CLUBS]
        return sorted(res,key=lambda x:-x["match_score"]), p.get("reason")
    except Exception:
        return local_score(ans), None

def chat_ai(msg):
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY","")
        if not key:
            return ("我是 ClubMatch AI 顾问，由 Claude（Anthropic）驱动。<br />"
                    "API Key 未配置，暂时无法联网——但你可以去「发现社团」浏览，或完成测评获取推荐。")
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
        return "AI 暂时不可用，稍后再试～"


# ═══════════════════════════════════════════════════════════════
#  NAV
# ═══════════════════════════════════════════════════════════════
def nav():
    cn = len(st.session_state.cart)
    cs = f" ({cn})" if cn else ""
    st.markdown(
        '<div class="nav">'
        '<div class="logo"><span class="logo-badge">CM</span>Club<em>Match</em></div>'
        '<div style="font-size:12px;color:rgba(255,240,180,0.28);font-weight:500;">每个人都值得找到属于自己的圈子</div>'
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
#  QUIZ  ← 纯 HTML 选项，无 Streamlit 备用按钮
#          通过 URL query_params 传递选择结果
# ═══════════════════════════════════════════════════════════════
def page_quiz():
    nav()

    # ── 读取 query_params 中是否有新选择 ──────────────────────
    qp = st.query_params
    raw_step   = qp.get("qstep",  None)
    raw_choice = qp.get("qchoice", None)

    if raw_step is not None and raw_choice is not None:
        try:
            ps = int(raw_step)
            pc = int(raw_choice)
            if ps == st.session_state.quiz_step:
                st.session_state.quiz_answers[ps] = pc
                # 清掉 query_params，避免刷新时重复触发
                st.query_params.clear()
                st.rerun()
        except Exception:
            pass

    step  = st.session_state.quiz_step
    total = len(QUESTIONS)
    q     = QUESTIONS[step]
    pct   = int(step / total * 100)
    cur   = st.session_state.quiz_answers.get(step)

    # ── 进度条 ────────────────────────────────────────────────
    st.markdown(
        f'<div class="prog-wrap">'
        f'<div class="prog-meta"><span>问题 {step+1} / {total}</span><b>{pct}%</b></div>'
        f'<div class="prog-track"><div class="prog-fill" style="width:{pct}%;"></div></div>'
        f'</div>', unsafe_allow_html=True)

    # ── 题目文字 ──────────────────────────────────────────────
    _,mid,_ = st.columns([0.3, 4, 0.3])
    with mid:
        st.markdown(
            f'<div style="font-size:11px;font-weight:700;color:#ffd700;letter-spacing:1px;'
            f'text-transform:uppercase;margin-bottom:10px;">第 {step+1} 题</div>'
            f'<div style="font-size:clamp(20px,3vw,30px);font-weight:900;letter-spacing:-0.8px;'
            f'line-height:1.2;margin-bottom:6px;color:#fff8e7;">{q["q"]}</div>',
            unsafe_allow_html=True)
        hint = q.get("hint","")
        if hint:
            st.markdown(
                f'<div style="font-size:13px;color:rgba(255,240,180,0.30);'
                f'margin-bottom:22px;font-style:italic;">{hint}</div>',
                unsafe_allow_html=True)
        else:
            st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

        # ── 纯 HTML 选项卡片（点击后通过 URL 参数回传） ──────
        opts   = q["opts"]
        sel    = cur if cur is not None else -1

        cards_html = ""
        for i, o in enumerate(opts):
            is_sel = "sel" if i == sel else ""
            cards_html += f"""
            <div class="opt {is_sel}" data-idx="{i}" onclick="pick({i})">
                <div class="opt-icon">{o['icon']}</div>
                <div class="opt-body">
                    <div class="opt-title">{o['title']}</div>
                    <div class="opt-sub">{o['sub']}</div>
                </div>
                <div class="opt-check">✓</div>
            </div>"""

        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:transparent;font-family:'Inter','PingFang SC',system-ui,sans-serif;padding:0;}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;}}
.opt{{
    display:flex;align-items:center;gap:14px;
    padding:18px 20px;border-radius:18px;
    border:1.5px solid rgba(255,215,0,0.18);
    background:rgba(255,215,0,0.05);
    cursor:pointer;
    transition:border-color .22s,background .22s,box-shadow .22s,transform .18s;
    position:relative;user-select:none;-webkit-user-select:none;
}}
.opt:hover{{
    border-color:rgba(255,215,0,0.50);
    background:rgba(255,215,0,0.10);
    transform:translateY(-2px);
    box-shadow:0 6px 24px rgba(212,160,20,0.22);
}}
.opt.sel{{
    border-color:#ffd700;
    background:rgba(255,215,0,0.14);
    box-shadow:
        0 0 0 3px rgba(255,215,0,0.20),
        0 0 24px rgba(255,200,50,0.50),
        0 0 48px rgba(212,160,20,0.22),
        0 8px 28px rgba(212,160,20,0.30);
    transform:translateY(-2px);
}}
.opt::after{{
    content:'';position:absolute;inset:0;border-radius:18px;
    background:radial-gradient(circle at center,rgba(255,215,0,0.30) 0%,transparent 70%);
    opacity:0;transform:scale(0.6);
    transition:opacity .4s,transform .4s;pointer-events:none;
}}
.opt.ripple::after{{opacity:1;transform:scale(1.2);}}
.opt-icon{{
    font-size:28px;flex-shrink:0;
    filter:drop-shadow(0 0 8px rgba(255,200,50,0.35));
    transition:filter .22s,transform .22s;
}}
.opt.sel .opt-icon{{
    filter:drop-shadow(0 0 14px rgba(255,200,50,0.72));
    transform:scale(1.08);
}}
.opt-body{{flex:1;}}
.opt-title{{
    font-size:15px;font-weight:700;
    color:rgba(255,248,231,0.90);margin-bottom:4px;transition:color .22s;
}}
.opt.sel .opt-title{{color:#fff8e7;}}
.opt-sub{{
    font-size:12px;color:rgba(255,240,180,0.40);
    line-height:1.45;transition:color .22s;
}}
.opt.sel .opt-sub{{color:rgba(255,230,130,0.70);}}
.opt-check{{
    width:22px;height:22px;border-radius:50%;
    border:1.5px solid rgba(255,215,0,0.25);
    color:transparent;font-size:11px;font-weight:700;
    display:flex;align-items:center;justify-content:center;
    flex-shrink:0;transition:all .22s;
}}
.opt.sel .opt-check{{
    background:linear-gradient(135deg,#b8860b,#ffd700);
    border-color:transparent;color:#1a1000;
    box-shadow:0 0 12px rgba(255,200,50,0.65);
}}
@media(max-width:560px){{.grid{{grid-template-columns:1fr;}}}}
</style>
</head>
<body>
<div class="grid" id="g">{cards_html}</div>
<script>
function pick(idx){{
    document.querySelectorAll('.opt').forEach(function(o){{o.classList.remove('sel');}});
    var el=document.querySelectorAll('.opt')[idx];
    el.classList.add('sel');
    el.classList.add('ripple');
    setTimeout(function(){{el.classList.remove('ripple');}},420);
    // 通过修改父窗口 URL query 参数回传选择
    var url=new URL(window.parent.location.href);
    url.searchParams.set('qstep','{step}');
    url.searchParams.set('qchoice',idx);
    window.parent.history.replaceState(null,'',url.toString());
    // 用 postMessage 通知 Streamlit 重新运行
    window.parent.postMessage({{isStreamlitMessage:true,type:'streamlit:setComponentValue',value:idx}}, '*');
    // 备用：延迟后触发隐藏按钮点击（最可靠方案）
    setTimeout(function(){{
        var btn=window.parent.document.querySelector('[data-quiz-confirm="true"] button');
        if(btn)btn.click();
    }},120);
}}
</script>
</body>
</html>"""

        components.html(html, height=230, scrolling=False)

        # ── 隐藏的"确认"按钮，由 JS 触发 ───────────────────
        st.markdown(
            '<div data-quiz-confirm="true" style="position:absolute;opacity:0;pointer-events:none;height:0;overflow:hidden;">',
            unsafe_allow_html=True)
        confirm_clicked = st.button("confirm", key=f"qconfirm_{step}")
        st.markdown('</div>', unsafe_allow_html=True)

        if confirm_clicked:
            # 从 query_params 读取选择
            qp2 = st.query_params
            raw_c = qp2.get("qchoice", None)
            raw_s = qp2.get("qstep",   None)
            if raw_c is not None and raw_s is not None:
                try:
                    if int(raw_s) == step:
                        st.session_state.quiz_answers[step] = int(raw_c)
                        st.query_params.clear()
                        st.rerun()
                except Exception:
                    pass

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 导航按钮（上一题 / 下一题） ────────────────────
        done = step in st.session_state.quiz_answers
        nl, nr = st.columns(2, gap="small")

        with nl:
            if st.button("← 返回" if step == 0 else "← 上一题",
                         key="qbk", use_container_width=True):
                if step == 0:
                    go("home")
                else:
                    st.session_state.quiz_step -= 1
                    st.rerun()

        with nr:
            lbl = "查看匹配结果 →" if step == total - 1 else "下一题 →"
            if st.button(lbl, key="qnx", type="primary",
                         use_container_width=True, disabled=not done):
                if step == total - 1:
                    with st.spinner("🤖 Claude AI 分析中..."):
                        res, reason = ai_match(st.session_state.quiz_answers)
                        st.session_state.results  = res
                        st.session_state.ai_reason = reason
                    go("results")
                else:
                    st.session_state.quiz_step += 1
                    st.rerun()


# ═══════════════════════════════════════════════════════════════
#  PAGE: HOME
# ═══════════════════════════════════════════════════════════════
def page_home():
    nav()
    cl, cr = st.columns([1.15, 1], gap="large")
    with cl:
        st.markdown('<div class="eyebrow">✦ AI 驱动的社团匹配平台</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="h1">大学四年<br>你值得遇见<span class="g1">真正的同类</span></div>'
            '<div class="sub">不知道加哪个？害怕加了发现不合适？<br>'
            '8 道情景题，Claude AI 分析你的真实性格，<br>从 16 个社团里找到最适合你的那个。</div>',
            unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🎯  开始匹配测评", key="hs", type="primary", use_container_width=True):
                st.session_state.quiz_step=0; st.session_state.quiz_answers={}; go("quiz")
        with b2:
            if st.button("🔍  逛逛所有社团", key="hb", use_container_width=True):
                go("browse")
        st.markdown("<br>", unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        for col,(n,l) in zip([c1,c2,c3,c4],[("16","入驻社团"),("3,800+","在校成员"),("94%","匹配满意度"),("8题","完成测评")]):
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
            f'<div style="font-size:44px;filter:drop-shadow(0 0 16px rgba(255,200,50,0.55));">{top["emoji"]}</div>'
            f'<div style="text-align:right;">'
            f'<div style="font-size:42px;font-weight:900;background:linear-gradient(135deg,#ffd700,#ffaa00);'
            f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;'
            f'letter-spacing:-2px;line-height:1;">92%</div>'
            f'<div style="font-size:10px;color:rgba(255,240,180,0.32);margin-top:2px;">AI 示例匹配度</div>'
            f'</div></div>'
            f'<div style="font-size:18px;font-weight:800;margin-bottom:4px;color:#fff8e7;">{top["name"]}</div>'
            f'<div class="vibe">{top.get("vibe","")}</div>'
            f'<div style="font-size:13px;color:rgba(255,240,180,0.47);line-height:1.65;margin-bottom:14px;">{top["desc"]}</div>'
            f'<div style="margin-bottom:14px;">{tags(top)}<span class="pill pill-o">热门</span></div>'
            f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">'
            + scell(top["members"],"成员") + scell(f"⭐{top['rating']}","评分") + scell(f"{top['awards']}项","获奖") +
            f'</div></div>'
            f'<div style="text-align:center;font-size:12px;color:rgba(255,240,180,0.20);margin-top:8px;">'
            f'🟡  本周已有 102 位新生完成匹配</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;margin-bottom:28px;">'
        '<div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#ffd700;'
        'text-transform:uppercase;margin-bottom:10px;">为什么选 ClubMatch</div>'
        '<div style="font-size:26px;font-weight:900;letter-spacing:-0.8px;color:#fff8e7;">'
        '不是随机推荐，是真正了解你</div></div>', unsafe_allow_html=True)
    feats = [
        ("🧬","情景化测评，读懂真实的你","不问「有什么爱好」，问「你周末真的会做什么」——8 道题挖掘你的性格底色，Claude AI 实时分析。"),
        ("📊","16 个社团，数据全透明","成员数、评分、时间投入、活动频率……加入前就把所有信息摆在你面前。"),
        ("🤖","Claude AI 顾问随时在线","底层由 Claude（Anthropic）驱动，问任何问题都行——它懂社团，也懂大学生的迷茫。"),
    ]
    cols = st.columns(3, gap="medium")
    for col,(icon,title,desc) in zip(cols,feats):
        with col:
            st.markdown(
                f'<div class="g" style="min-height:165px;">'
                f'<div style="font-size:28px;margin-bottom:14px;">{icon}</div>'
                f'<div style="font-size:15px;font-weight:800;margin-bottom:8px;color:#fff8e7;">{title}</div>'
                f'<div style="font-size:13px;color:rgba(255,240,180,0.44);line-height:1.65;">{desc}</div>'
                f'</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    picks = random.sample(CLUBS, 3)
    st.markdown(
        '<div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#ffd700;'
        'text-transform:uppercase;margin-bottom:10px;">✦ 今日精选</div>'
        '<div style="font-size:22px;font-weight:900;letter-spacing:-0.6px;margin-bottom:20px;color:#fff8e7;">'
        '随便逛逛，说不定就遇上了</div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    for col,club in zip(cols,picks):
        with col:
            st.markdown(
                f'<div class="g">'
                f'<div style="font-size:36px;margin-bottom:10px;">{club["emoji"]}</div>'
                f'<div style="font-size:16px;font-weight:800;margin-bottom:3px;color:#fff8e7;">{club["name"]}</div>'
                f'<div class="vibe">{club.get("vibe","")}</div>'
                f'<div style="font-size:13px;color:rgba(255,240,180,0.44);line-height:1.55;margin-bottom:12px;">'
                f'{club["desc"][:55]}...</div><div>{tags(club)}</div></div>', unsafe_allow_html=True)
            if st.button("了解更多", key=f"hc_{club['id']}", use_container_width=True):
                st.session_state.expand_club = club["id"]; go("browse")

    st.markdown("<br>", unsafe_allow_html=True)
    _,mid,_ = st.columns([1,2,1])
    with mid:
        if st.button("✨  还没找到感觉？来做个测评 →", key="hcta2", type="primary", use_container_width=True):
            st.session_state.quiz_step=0; st.session_state.quiz_answers={}; go("quiz")


# ═══════════════════════════════════════════════════════════════
#  PAGE: RESULTS
# ═══════════════════════════════════════════════════════════════
def page_results():
    nav()
    res = st.session_state.results
    if not res:
        st.warning("还没有结果，先完成测评吧～")
        if st.button("去测评", type="primary"): go("quiz")
        return
    reason = st.session_state.get("ai_reason")
    st.markdown(
        '<div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#ffd700;'
        'text-transform:uppercase;margin-bottom:10px;">✦ 你的专属匹配报告</div>'
        f'<div style="font-size:clamp(22px,4vw,36px);font-weight:900;letter-spacing:-1.2px;'
        f'margin-bottom:10px;color:#fff8e7;">Claude 从 {len(CLUBS)} 个社团里，为你找到了这些</div>',
        unsafe_allow_html=True)
    if reason:
        st.markdown(
            f'<div style="background:rgba(255,200,50,0.07);border:1px solid rgba(255,200,50,0.22);'
            f'border-radius:14px;padding:14px 18px;font-size:14px;color:rgba(255,240,180,0.72);'
            f'line-height:1.65;margin-bottom:24px;">'
            f'<span style="color:#ffd700;font-weight:700;">✦ Claude 分析：</span>{reason}</div>',
            unsafe_allow_html=True)

    bnames=["🥇 最佳匹配","🥈 强烈推荐","🥉 推荐"]; bcls=["pill-o","pill-v","pill-b"]
    cols=st.columns(3,gap="small")
    for idx,club in enumerate(res):
        with cols[idx%3]:
            app=applied(club["id"]); inc=incart(club["id"])
            bc=bcls[idx] if idx<3 else "pill-b"; bl=bnames[idx] if idx<3 else f"#{idx+1}"
            ab='<span class="pill pill-g">✓ 已报名</span>' if app else ""
            feat="pin" if idx==0 else ""
            st.markdown(
                f'<div class="g {feat}">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">'
                f'<div style="font-size:36px;filter:drop-shadow(0 0 10px rgba(255,200,50,0.45));">{club["emoji"]}</div>'
                f'<span class="pill {bc}">{bl}</span></div>'
                f'<div style="font-size:16px;font-weight:800;margin-bottom:2px;color:#fff8e7;">{club["name"]}</div>'
                f'<div style="font-size:11px;color:rgba(255,240,180,0.32);margin-bottom:10px;">{club["type"]} · {club["freq"]}</div>',
                unsafe_allow_html=True)
            sbar(club["match_score"])
            st.markdown(
                f'<div class="vibe">{club.get("vibe","")}</div>'
                f'<div style="font-size:13px;color:rgba(255,240,180,0.47);line-height:1.55;margin-bottom:12px;">{club["desc"][:58]}...</div>'
                f'<div style="margin-bottom:14px;">{tags(club)}{ab}</div></div>',
                unsafe_allow_html=True)
            b1,b2=st.columns(2,gap="small")
            with b1:
                if st.button("查看详情",key=f"rd_{club['id']}_{idx}",use_container_width=True):
                    st.session_state.expand_club=(club["id"] if st.session_state.expand_club!=club["id"] else None)
                    st.rerun()
            with b2:
                if app: st.button("已报名 ✓",key=f"ra_{club['id']}",disabled=True,use_container_width=True)
                elif inc:
                    if st.button("移出申请袋",key=f"rr_{club['id']}_{idx}",use_container_width=True):
                        toggle(club["id"]); st.rerun()
                else:
                    if st.button("➕ 加入申请袋",key=f"radd_{club['id']}_{idx}",type="primary",use_container_width=True):
                        toggle(club["id"]); st.rerun()
            if st.session_state.expand_club==club["id"]:
                club_detail(club)

    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4,gap="small")
    with c1:
        if st.button("🔄 重新测评",key="rr",use_container_width=True):
            st.session_state.quiz_step=0; st.session_state.quiz_answers={}; go("quiz")
    with c2:
        if st.button("🔍 发现更多",key="rb",use_container_width=True): go("browse")
    with c3:
        if st.button("🤖 AI 顾问",key="rc",use_container_width=True): go("chat")
    with c4:
        cn=len(st.session_state.cart)
        if cn:
            if st.button(f"📋 提交申请({cn})",key="rapp",type="primary",use_container_width=True): go("apply")
        else:
            st.button("📋 申请袋为空",key="rape",disabled=True,use_container_width=True)


def club_detail(club):
    app=applied(club["id"])
    rr="".join(f'<div class="rr"><span style="color:#ffd700;flex-shrink:0;">·</span><span>{r}</span></div>' for r in club.get("requirements",[]))
    ar="".join(f'<div class="rr"><span style="color:#ffaa00;flex-shrink:0;">·</span><span>{a}</span></div>' for a in club.get("activities",[]))
    st4="".join(scell(v,l) for v,l in [(str(club["members"]),"成员"),(f"⭐{club['rating']}","评分"),(f"{club['awards']}项","获奖"),(club["time_cost"],"时间")])
    an=('<div style="margin-top:12px;padding:10px 14px;background:rgba(100,200,100,0.08);'
        'border:1px solid rgba(100,200,100,0.22);border-radius:10px;font-size:12px;'
        'color:#88e088;text-align:center;">✓ 你已报名这个社团</div>') if app else ""
    st.markdown(
        f'<div class="det">'
        f'<div class="dsec">关于我们</div>'
        f'<div style="font-size:13px;color:rgba(255,240,180,0.62);line-height:1.7;">{club.get("detail","")}</div>'
        f'<div class="dsec">最适合谁</div>'
        f'<div style="font-size:13px;color:rgba(255,240,180,0.62);">→ {club.get("best_for","")}</div>'
        f'<div class="dsec">招新要求</div>{rr}'
        f'<div class="dsec">主要活动</div>{ar}'
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:14px;">{st4}</div>'
        f'{an}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE: BROWSE
# ═══════════════════════════════════════════════════════════════
def page_browse():
    nav()
    st.markdown(
        '<div style="font-size:26px;font-weight:900;letter-spacing:-0.8px;margin-bottom:4px;color:#fff8e7;">发现社团</div>',
        unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:14px;color:rgba(255,240,180,0.34);margin-bottom:20px;">{len(CLUBS)} 个社团，总有一个在等你</div>',
        unsafe_allow_html=True)
    cs,cf = st.columns([2,1])
    with cs: search=st.text_input("",placeholder="🔍  搜索名称、类型、标签...",label_visibility="collapsed",key="bs")
    with cf:
        types=["全部类型"]+sorted({c["type"] for c in CLUBS})
        selt=st.selectbox("",types,label_visibility="collapsed",key="bt")
    filtered=[c for c in CLUBS
               if (not search or search in c["name"] or search in c["type"]
                   or any(search in t for t in c.get("tags",[])) or search in c.get("desc",""))
               and (selt=="全部类型" or c["type"]==selt)]
    if not filtered:
        st.markdown(
            '<div style="text-align:center;padding:60px;color:rgba(255,240,180,0.22);">没找到……换个关键词？</div>',
            unsafe_allow_html=True); return
    cols=st.columns(3,gap="small")
    for idx,club in enumerate(filtered):
        with cols[idx%3]:
            app=applied(club["id"]); inc=incart(club["id"])
            ex=('<span class="pill pill-g">✓ 已报名</span>' if app
                else ('<span class="pill pill-v">已加入申请袋</span>' if inc else ""))
            sr="".join(
                f'<div style="text-align:center;">'
                f'<div style="font-size:13px;font-weight:800;color:#fff8e7;">{v}</div>'
                f'<div style="font-size:10px;color:rgba(255,240,180,0.30);margin-top:2px;">{l}</div></div>'
                for v,l in [(str(club["members"]),"成员"),(f"⭐{club['rating']}","评分"),(f"{club['awards']}项","获奖")])
            st.markdown(
                f'<div class="g">'
                f'<div style="font-size:36px;margin-bottom:10px;">{club["emoji"]}</div>'
                f'<div style="font-size:16px;font-weight:800;margin-bottom:2px;color:#fff8e7;">{club["name"]}</div>'
                f'<div style="font-size:11px;color:rgba(255,240,180,0.30);margin-bottom:8px;">{club["type"]} · 成立 {club["founded"]}</div>'
                f'<div class="vibe">{club.get("vibe","")}</div>'
                f'<div style="font-size:13px;color:rgba(255,240,180,0.44);line-height:1.55;margin-bottom:12px;">{club["desc"][:62]}...</div>'
                f'<div style="margin-bottom:12px;">{tags(club)}{ex}</div>'
                f'<div style="display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid rgba(255,215,0,0.08);padding-top:12px;">{sr}</div>'
                f'</div>', unsafe_allow_html=True)
            b1,b2=st.columns(2,gap="small")
            with b1:
                exp=st.session_state.expand_club==club["id"]
                if st.button("收起 ↑" if exp else "查看详情",key=f"bd_{club['id']}_{idx}",use_container_width=True):
                    st.session_state.expand_club=club["id"] if not exp else None; st.rerun()
            with b2:
                if app: st.button("已报名 ✓",key=f"ba_{club['id']}",disabled=True,use_container_width=True)
                elif inc:
                    if st.button("移出申请袋",key=f"br_{club['id']}_{idx}",use_container_width=True):
                        toggle(club["id"]); st.rerun()
                else:
                    if st.button("➕ 加入申请袋",key=f"badd_{club['id']}_{idx}",type="primary",use_container_width=True):
                        toggle(club["id"]); st.rerun()
            if st.session_state.expand_club==club["id"]:
                club_detail(club)
    st.markdown("<br>", unsafe_allow_html=True)
    _,mid,_=st.columns([1,2,1])
    with mid:
        cn=len(st.session_state.cart)
        if cn:
            if st.button(f"📋  前往提交申请（已选 {cn} 个）",type="primary",use_container_width=True,key="bgo"): go("apply")
        if st.button("✨  没找到合适的？申请创建新社团",use_container_width=True,key="bcr"): go("create")


# ═══════════════════════════════════════════════════════════════
#  PAGE: CHAT
# ═══════════════════════════════════════════════════════════════
def page_chat():
    nav()
    st.markdown(
        '<div style="font-size:24px;font-weight:900;letter-spacing:-0.6px;margin-bottom:4px;color:#fff8e7;">AI 社团顾问</div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:13px;color:rgba(255,240,180,0.32);margin-bottom:24px;">由 Claude (Anthropic) 驱动 · 随时回答关于社团的任何问题</div>',
        unsafe_allow_html=True)
    if not st.session_state.chat_history:
        st.session_state.chat_history=[{"user":None,"ai":(
            f"嗨！我是 ClubMatch AI 顾问，底层由 Claude（Anthropic）驱动 👋<br /><br />"
            f"我对平台上全部 {len(CLUBS)} 个社团都了如指掌。你可以问我：<br />"
            f"· 某个社团的具体情况和氛围<br />· 根据你的情况给个性化推荐<br />"
            f"· 「内向的人适合哪个」「我时间不多怎么选」……<br /><br />随便问，没有奇怪的问题。")}]
    for t in st.session_state.chat_history:
        if t.get("user"):
            st.markdown(
                '<div style="text-align:right;font-size:11px;color:rgba(255,240,180,0.30);font-weight:600;margin-bottom:3px;">你</div>',
                unsafe_allow_html=True)
            st.markdown(f'<div class="buser">{t["user"]}</div>',unsafe_allow_html=True)
        if t.get("ai"):
            st.markdown('<div class="clbl">🤖  Claude AI 顾问</div>',unsafe_allow_html=True)
            st.markdown(f'<div class="bai">{t["ai"]}</div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    if len(st.session_state.chat_history)<=1:
        st.markdown(
            '<div style="font-size:12px;color:rgba(255,240,180,0.24);margin-bottom:8px;">快捷问题</div>',
            unsafe_allow_html=True)
        sugg=["内向的人适合哪个？","时间不多选哪个？","摄影社和微电影社区别？","创业社真的有用吗？","不知道自己喜欢什么？","哪个最容易交朋友？"]
        cols=st.columns(3,gap="small")
        for i,s in enumerate(sugg):
            with cols[i%3]:
                if st.button(s,key=f"sg_{i}",use_container_width=True):
                    with st.spinner("Claude 思考中..."): rep=chat_ai(s)
                    st.session_state.chat_history.append({"user":s,"ai":rep}); st.rerun()
    ci,cs=st.columns([5,1])
    with ci: ui=st.text_input("",placeholder="问我任何关于社团的事...",label_visibility="collapsed",key="ci")
    with cs: send=st.button("发送 →",key="cs",type="primary",use_container_width=True)
    if send and ui.strip():
        with st.spinner("Claude 思考中..."): rep=chat_ai(ui.strip())
        st.session_state.chat_history.append({"user":ui.strip(),"ai":rep}); st.rerun()
    if len(st.session_state.chat_history)>1:
        if st.button("🗑  清空对话",key="cc"): st.session_state.chat_history=[]; st.rerun()


# ═══════════════════════════════════════════════════════════════
#  PAGE: APPLY
# ═══════════════════════════════════════════════════════════════
def page_apply():
    nav()
    cart=st.session_state.cart
    if not cart:
        st.markdown(
            '<div style="font-size:22px;font-weight:800;color:#fff8e7;margin-bottom:8px;">申请袋是空的</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div style="color:rgba(255,240,180,0.40);margin-bottom:24px;font-size:14px;">先去发现社团，把感兴趣的加进来～</div>',
            unsafe_allow_html=True)
        if st.button("去发现社团",type="primary"): go("browse")
        return
    st.markdown(
        f'<div style="font-size:26px;font-weight:900;letter-spacing:-0.8px;margin-bottom:4px;color:#fff8e7;">提交申请</div>',
        unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:14px;color:rgba(255,240,180,0.37);margin-bottom:24px;">你选择了 {len(cart)} 个社团，一次填写全搞定</div>',
        unsafe_allow_html=True)
    cl,cr=st.columns([1.2,1],gap="large")
    with cl:
        st.markdown('<div class="fs"><div class="ft">你的申请袋</div>',unsafe_allow_html=True)
        for cid in list(cart):
            club=cbyid(cid)
            if not club: continue
            cL,cR=st.columns([3,1])
            with cL:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;padding:10px 0;'
                    f'border-bottom:1px solid rgba(255,215,0,0.07);">'
                    f'<span style="font-size:22px;">{club["emoji"]}</span>'
                    f'<div><div style="font-size:14px;font-weight:700;color:#fff8e7;">{club["name"]}</div>'
                    f'<div style="font-size:11px;color:rgba(255,240,180,0.32);">{club["type"]} · {club["freq"]}</div>'
                    f'</div></div>', unsafe_allow_html=True)
            with cR:
                if st.button("移除",key=f"arm_{cid}",use_container_width=True): toggle(cid); st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
        if st.button("+ 继续添加",key="am",use_container_width=True): go("browse")
        st.markdown("""
        <div class="fs" style="margin-top:14px;">
            <div class="ft">提交后会发生什么</div>
            <div style="display:flex;flex-direction:column;gap:14px;">
                <div style="display:flex;gap:12px;">
                    <div style="width:26px;height:26px;border-radius:50%;background:rgba(212,160,20,0.18);color:#ffd700;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;">1</div>
                    <div><div style="font-size:13px;font-weight:700;color:#fff8e7;margin-bottom:2px;">社团负责人主动联系你</div><div style="font-size:12px;color:rgba(255,240,180,0.40);line-height:1.5;">3 个工作日内通过手机号或微信联系，说明面试安排。</div></div>
                </div>
                <div style="display:flex;gap:12px;">
                    <div style="width:26px;height:26px;border-radius:50%;background:rgba(212,160,20,0.18);color:#ffd700;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;">2</div>
                    <div><div style="font-size:13px;font-weight:700;color:#fff8e7;margin-bottom:2px;">体验一次活动，再决定</div><div style="font-size:12px;color:rgba(255,240,180,0.40);line-height:1.5;">大部分社团会邀请你先来体验，感受真实氛围后再确认加入。</div></div>
                </div>
                <div style="display:flex;gap:12px;">
                    <div style="width:26px;height:26px;border-radius:50%;background:rgba(212,160,20,0.18);color:#ffd700;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;">3</div>
                    <div><div style="font-size:13px;font-weight:700;color:#fff8e7;margin-bottom:2px;">进群，正式开始</div><div style="font-size:12px;color:rgba(255,240,180,0.40);line-height:1.5;">确认加入后被拉进官方微信群，社团生活从这里开始。</div></div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    with cr:
        st.markdown('<div class="fs"><div class="ft">个人信息</div>',unsafe_allow_html=True)
        name=st.text_input("姓名 *",placeholder="请输入真实姓名",key="fn")
        sid=st.text_input("学号 *",placeholder="例：2024XXXXXXXX",key="fs")
        major=st.text_input("专业 *",placeholder="例：国际经济与贸易",key="fm")
        grade=st.selectbox("年级 *",["请选择","大一","大二","大三","大四","研究生"],key="fg")
        phone=st.text_input("手机号 *",placeholder="社团负责人会通过此号联系你",key="fp")
        wechat=st.text_input("微信号（选填）",placeholder="方便拉你进群",key="fw")
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<div class="fs" style="margin-top:10px;"><div class="ft">补充信息</div>',unsafe_allow_html=True)
        intro=st.text_area("自我介绍 *",placeholder="简单说说自己，为什么对这些社团感兴趣？（100字以内）",height=100,key="fi")
        ta=st.multiselect("空闲时间段",["周一至周五 白天","周一至周五 晚上","周末全天","周末上午","周末下午"],key="ft2")
        sk=st.text_input("特长技能（选填）",placeholder="例：摄影、吉他、编程……",key="fsk")
        st.markdown('</div>',unsafe_allow_html=True)
        ok=all([name.strip(),sid.strip(),major.strip(),grade!="请选择",phone.strip(),intro.strip()])
        if st.button("🎉  提交所有申请",key="asub",type="primary",use_container_width=True,disabled=not ok):
            st.session_state.applications.append({
                "clubs":list(cart),"name":name,"student_id":sid,"major":major,
                "grade":grade,"phone":phone,"wechat":wechat,"intro":intro,
                "time_avail":ta,"skill":sk})
            st.session_state.cart=[]; go("success")
        if not ok:
            st.markdown(
                '<div style="font-size:12px;color:rgba(255,240,180,0.27);text-align:center;margin-top:6px;">请填写所有必填项后提交</div>',
                unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PAGE: SUCCESS
# ═══════════════════════════════════════════════════════════════
def page_success():
    nav()
    if not st.session_state.applications: go("home"); return
    last=st.session_state.applications[-1]
    cnames=[cbyid(cid)["name"] for cid in last["clubs"] if cbyid(cid)]
    cl="".join(
        f'<div style="display:flex;align-items:center;gap:8px;font-size:14px;'
        f'color:rgba(255,240,180,0.72);margin-bottom:8px;">'
        f'<span style="color:#88e088;">✓</span>{n}</div>'
        for n in cnames)
    _,col,_=st.columns([0.5,3,0.5])
    with col:
        st.markdown(
            f'<div class="ok-glass">'
            f'<div style="font-size:56px;margin-bottom:16px;">🎉</div>'
            f'<div style="font-size:28px;font-weight:900;letter-spacing:-1px;margin-bottom:10px;color:#fff8e7;">申请已成功提交！</div>'
            f'<div style="font-size:15px;color:rgba(255,240,180,0.52);line-height:1.75;margin-bottom:24px;">'
            f'{last["name"]}，欢迎你迈出这一步。<br>接下来，静静等着被发现吧。</div>'
            f'<div style="background:rgba(255,215,0,0.04);border:1px solid rgba(255,215,0,0.10);'
            f'border-radius:14px;padding:18px;text-align:left;margin-bottom:20px;">'
            f'<div style="font-size:11px;color:rgba(255,215,0,0.35);font-weight:700;'
            f'letter-spacing:0.8px;text-transform:uppercase;margin-bottom:12px;">你申请的社团</div>'
            f'{cl}</div></div>', unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        b1,b2=st.columns(2)
        with b1:
            if st.button("继续发现社团",key="sb",use_container_width=True): go("browse")
        with b2:
            if st.button("回到首页",key="sh",type="primary",use_container_width=True): go("home")


# ═══════════════════════════════════════════════════════════════
#  PAGE: CREATE
# ═══════════════════════════════════════════════════════════════
def page_create():
    nav()
    st.markdown('<div class="eyebrow">✦ 找不到合适的？自己创一个</div>',unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:28px;font-weight:900;letter-spacing:-0.8px;margin-bottom:8px;color:#fff8e7;">申请创建新社团</div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:15px;color:rgba(255,240,180,0.42);line-height:1.7;margin-bottom:28px;">'
        '每一个存在的社团，都是某个人第一次说「我想做这件事」。<br>'
        '如果你有个想法，这里是它开始的地方。</div>',
        unsafe_allow_html=True)
    cl,cr=st.columns([1,1],gap="large")
    with cl:
        st.markdown('<div class="fs"><div class="ft">社团基本信息</div>',unsafe_allow_html=True)
        cn=st.text_input("社团名称 *",placeholder="例：城市骑行与街拍社",key="cc")
        ct=st.selectbox("社团类型 *",["请选择","艺术创作","音乐表演","舞台表演","科技创新","商业创新","户外运动","人文学术","公益服务","体育竞技","跨文化交流","科学探索","其他"],key="cct")
        cd=st.text_area("社团是做什么的 *",placeholder="让人 5 秒内听懂，说具体的事，少用形容词。",height=80,key="ccd")
        cw=st.text_area("为什么它值得存在？*",placeholder="比如：我发现学校没有专注城市骑行的社团，但身边有很多同学想要这个……",height=100,key="ccw")
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<div class="fs" style="margin-top:10px;"><div class="ft">活动构想</div>',unsafe_allow_html=True)
        cap=st.text_area("你打算做哪些活动？",placeholder="哪怕很初期的想法也可以",height=90,key="cap")
        st.slider("预计初始成员数",5,50,15,key="cm")
        st.selectbox("活动频率",["每周一次","每两周一次","每月一次","视项目而定","还没想好"],key="cf")
        st.markdown('</div>',unsafe_allow_html=True)
    with cr:
        st.markdown('<div class="fs"><div class="ft">发起人信息</div>',unsafe_allow_html=True)
        fn=st.text_input("姓名 *",key="cfn"); fs=st.text_input("学号 *",key="cfs")
        fm=st.text_input("专业 *",key="cfm")
        fg=st.selectbox("年级 *",["请选择","大一","大二","大三","大四","研究生"],key="cfg")
        fp=st.text_input("联系方式 *",key="cfp")
        st.text_area("相关经历（选填）",placeholder="做过类似的组织工作？是这个领域的爱好者？",height=80,key="cfe")
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('<div class="fs" style="margin-top:10px;"><div class="ft">Claude AI 帮你完善方案</div>',unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:13px;color:rgba(255,240,180,0.40);line-height:1.6;margin-bottom:14px;">'
            '填完基本信息后，让 Claude 给你的方案提几条建议。</div>',
            unsafe_allow_html=True)
        if st.button("🤖  让 Claude 给我建议",key="cai",use_container_width=True):
            if cn and cd and cw:
                with st.spinner("Claude 思考中..."):
                    try:
                        key=st.secrets.get("ANTHROPIC_API_KEY","")
                        if key:
                            cl2=anthropic.Anthropic(api_key=key)
                            msg=cl2.messages.create(
                                model="claude-opus-4-5",max_tokens=500,system=SYS,
                                messages=[{"role":"user","content":
                                    f"一位大学生想创建社团：<br />名称：{cn}<br />类型：{ct}<br />描述：{cd}<br />原因：{cw}<br />活动：{cap}<br /><br />"
                                    f"给出3条简短具体有用的建议，帮助完善方案。风格温暖鼓励，直接分点。"}])
                            st.session_state.ai_suggestion=msg.content[0].text
                        else:
                            st.session_state.ai_suggestion=(
                                "1. 把核心活动具体化——「每月一次骑行」比「定期活动」更有说服力。<br />"
                                "2. 说清楚你如何区别于现有社团。<br />"
                                "3. 找 2-3 个志同道合的人一起联署发起。")
                    except Exception:
                        st.session_state.ai_suggestion="AI 暂时不可用，但你的想法很棒，继续填写吧！"
            else:
                st.warning("先填写名称、描述和创建原因～")
        if st.session_state.ai_suggestion:
            st.markdown(
                f'<div class="bai">✦ Claude 建议：<br /><br />{st.session_state.ai_suggestion}</div>',
                unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
        aok=all([cn,ct!="请选择",cd,cw,fn,fs,fm,fg!="请选择",fp])
        if st.button("🚀  提交创建申请",key="csub",type="primary",use_container_width=True,disabled=not aok):
            st.session_state.create_submitted=True; st.rerun()
        if st.session_state.get("create_submitted"):
            st.markdown(
                f'<div style="margin-top:14px;background:rgba(100,200,100,0.07);'
                f'border:1px solid rgba(100,200,100,0.22);border-radius:14px;padding:16px;text-align:center;">'
                f'<div style="font-size:22px;margin-bottom:8px;">🌱</div>'
                f'<div style="font-size:15px;font-weight:700;margin-bottom:6px;color:#fff8e7;">申请已提交！</div>'
                f'<div style="font-size:13px;color:rgba(255,240,180,0.47);line-height:1.6;">'
                f'学生活动部将在 5 个工作日内审核。<br>{fn}，期待看到「{cn}」出现在 ClubMatch 上。</div></div>',
                unsafe_allow_html=True)
            if st.button("回到首页",key="ch",type="primary"):
                st.session_state.create_submitted=False
                st.session_state.ai_suggestion=""
                go("home")
        if not aok and not st.session_state.get("create_submitted"):
            st.markdown(
                '<div style="font-size:12px;color:rgba(255,240,180,0.24);text-align:center;margin-top:6px;">请填写所有必填项（*）</div>',
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
