import streamlit as st
from datetime import date, timedelta
from utils import load_config, save_config, fetch_articles
import math

# Zúžená šířka stránky
PAGE_WIDTH = 1024
st.set_page_config(page_title="Můj AI Digest", layout="wide")

cfg = load_config()
today = date.today()
defaults = {
    "sources": cfg.get("sources", "www.zive.cz ; www.cnews.cz ; www.root.cz"),
    "keywords": cfg.get("keywords", "pojišťovnictví ; pojišťovna ; pojišťovny"),
    "blacklist": cfg.get("blacklist", "zdravotní pojištění ; sociální pojištění"),
    "newest_date": cfg.get("newest_date", str(today)),
    "oldest_date": cfg.get("oldest_date", str(today - timedelta(days=365))),
    "page_size": int(cfg.get("page_size", "10")),
}

# ----------------------------
# Hlavní záhlaví
# ----------------------------
st.markdown(
    f"""
    <div style="text-align:center; max-width:{PAGE_WIDTH}px; margin:auto;">
        <h1><b>Můj AI Digest</b></h1>
        <p>Aplikace pro výběr článků ze zadaných zdrojů podle klíčových slov a blacklistu.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Konfigurační pole
# ----------------------------
with st.container():
    sources = st.text_area("Zdroje", value=defaults["sources"], height=150)
    keywords = st.text_input("Klíčová slova", value=defaults["keywords"])
    blacklist = st.text_input("Blacklist slova", value=defaults["blacklist"])

    col1, col2 = st.columns(2)
    with col1:
        newest_date = st.date_input(
            "Datum nejnovějšího článku", value=date.fromisoformat(defaults["newest_date"])
        )
    with col2:
        oldest_date = st.date_input(
            "Datum nejstaršího článku", value=date.fromisoformat(defaults["oldest_date"])
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Načíst konfiguraci"):
            st.rerun()
    with col2:
        if st.button("Uložit konfiguraci"):
            save_config({
                "sources": sources,
                "keywords": keywords,
                "blacklist": blacklist,
                "newest_date": str(newest_date),
                "oldest_date": str(oldest_date),
                "page_size": str(defaults["page_size"]),
                "page_width": str(PAGE_WIDTH),
            })
            st.success("Konfigurace uložena.")

# ----------------------------
# Načtení článků a stránkovač
# ----------------------------
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
if st.button("Načíst články"):
    urls = [u.strip() for u in sources.split(";") if u.strip()]
    kws = [k.strip() for k in keywords.split(";") if k.strip()]
    bls = [b.strip() for b in blacklist.split(";") if b.strip()]

    articles = fetch_articles(
        urls, kws, bls, newest_date, oldest_date, max_articles=100
    )
    st.session_state["articles"] = articles
st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Výpis článků s stránkováním
# ----------------------------
articles = st.session_state.get("articles", [])
page_size = defaults["page_size"]
total_pages = math.ceil(len(articles) / page_size)
current_page = st.session_state.get("current_page", 1)

if total_pages > 0:
    current_page = st.number_input(
        "Stránka",
        min_value=1,
        max_value=total_pages,
        value=current_page,
        step=1,
        key="page_selector"
    )
    st.session_state["current_page"] = current_page

    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    for art in articles[start_idx:end_idx]:
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            st.image(art["image"] or "https://via.placeholder.com/150", use_container_width=True)
        with col2:
            st.markdown(f"<span style='background-color:red; color:white; padding:2px 6px;'>{art['source']}</span>", unsafe_allow_html=True)
            st.markdown(f"### **{art['title']}**")
            st.markdown(f"**{art['perex']}**")
            st.markdown(f"*{art['url']}*")

    st.markdown("---")
    st.markdown(f"Zobrazuji články {start_idx+1}-{min(end_idx,len(articles))} z {len(articles)}")
