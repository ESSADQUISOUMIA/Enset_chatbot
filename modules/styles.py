"""Thème sobre de l'interface ENSET Chatbot (sans emojis)."""
import streamlit as st


def apply_styles():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#17233b; --muted:#718096; --accent:#4f46e5; --canvas:#f7f8fc; --line:#e8eaf2; }
html, body, [class*="css"], [data-testid="stAppViewContainer"] { font-family:'DM Sans',sans-serif; }
[data-testid="stAppViewContainer"] { background:var(--canvas); }
[data-testid="stHeader"] { background:transparent; }
.block-container { max-width:960px; padding-top:2.1rem; padding-bottom:7rem; }
h1,h2,h3 {font-family:'Manrope',sans-serif; letter-spacing:-.035em; color:var(--ink);}
[data-testid="stSidebar"] {background:#fff; border-right:1px solid var(--line);}
[data-testid="stSidebar"] .block-container {padding-top:1.6rem;}
[data-testid="stSidebar"] h3 {font-size:0.85rem; color:#7b8498; letter-spacing:.07em; text-transform:uppercase; margin-top:1.2rem;}
[data-testid="stSidebar"] button {border-radius:11px; min-height:39px;}
.stButton > button {border:1px solid var(--line); background:#fff; color:var(--ink); font-weight:600;}
.stButton > button:hover {border-color:#9d96f7; color:var(--accent); background:#f6f5ff;}
.stButton > button[kind="primary"] {background:var(--accent); border-color:var(--accent); color:white;}
.stButton > button[kind="primary"]:hover {background:#4338ca; color:white;}
[data-testid="stChatMessage"] {background:#fff; border:1px solid var(--line); border-radius:17px; padding:1rem 1.15rem; margin-bottom:.85rem; box-shadow:0 3px 16px rgba(28,38,65,.025);}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {line-height:1.72;}
[data-testid="stChatInput"] {border-radius:17px; box-shadow:0 8px 30px rgba(30,40,65,.07);}
[data-testid="stChatInput"] textarea {font-family:'DM Sans',sans-serif;}
[data-testid="stDownloadButton"] button {border-radius:10px;}
[data-testid="stSelectbox"] > div > div {border-radius:10px;}
[data-testid="stSlider"] {padding-bottom:.2rem;}
hr {border-color:var(--line);}
.enset-kicker {color:var(--accent); font-size:.73rem; text-transform:uppercase; letter-spacing:.17em; font-weight:800; margin-bottom:.55rem;}
.enset-heading {font:800 clamp(1.6rem,3.5vw,2.25rem) 'Manrope',sans-serif; color:var(--ink); letter-spacing:-.055em; margin:0;}
.enset-subtitle {color:#7b8498; font-size:.94rem; margin-top:.5rem; margin-bottom:1.9rem;}
.enset-empty {background:#fff; border:1px solid var(--line); border-radius:22px; padding:3.8rem 2.2rem; text-align:center; margin-top:2rem;}
.enset-empty-title {font:800 1.35rem 'Manrope',sans-serif; color:var(--ink); margin-bottom:.5rem;}
.enset-empty-desc {color:#80899b; max-width:380px; margin:auto; line-height:1.7;}
.enset-brand {font:800 1.28rem 'Manrope',sans-serif; color:var(--ink); letter-spacing:-.055em; padding:.2rem 0 .4rem;}
.enset-brand span {color:var(--accent);}
.enset-meta {color:#8590a2; font-size:.8rem; margin-bottom:1rem;}
@media (max-width:700px) {.block-container {padding-top:1rem;} .enset-empty {padding:2.2rem 1.1rem;}}
</style>
""", unsafe_allow_html=True)
