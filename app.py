import streamlit as st
from datetime import date, timedelta
from utils import load_config, save_config

st.set_page_config(page_title="Můj AI Digest", layout="wide")

# Načíst config
cfg = load_config()

# Výchozí hodnoty
today = date.today()
defaults = {
    "sources": cfg.get("sources", "www.zive.cz ; www.cnews.cz ; www.root.cz"),
    "keywords": cfg.get("keywords", "pojišťovnictví ; pojišťovna ; pojišťovny"),
    "blacklist": cfg.get("blacklist", "zdravotní pojištění ; sociální pojištění"),
    "newest_date": cfg.get("newest_date", str(today)),
    "oldest_date": cfg.get("oldest_date", str(today - timedelta(days=365))),
    "page_size": cfg.get("page_size", "10"),
    "page_width": cfg.get("page_width", "1280"),
}

# ----------------------------
# Hlavní záhlaví
# ----------------------------
st.markdown(
    f"""
    <div style="text-align:center; max-width:{defaults['page_width']}px; margin:auto;">
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
                "page_size": defaults["page_size"],
                "page_width": defaults["page_width"],
            })
            st.success("Konfigurace uložena.")

# ----------------------------
# Tlačítko načítání článků
# ----------------------------
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
if st.button("Načíst články"):
    st.info("Načítám články... (zatím mock data)")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ----------------------------
# Mock data pro články
# ----------------------------
articles = [
    {
        "source": "www.zive.cz",
        "title": "Pojišťovnictví a technologie",
        "perex": "Nové trendy v pojišťovnictví mění trh...",
        "url": "https://www.zive.cz/clanek/123",
        "image": None,
    },
    {
        "source": "www.root.cz",
        "title": "Pojišťovna online",
        "perex": "Digitální transformace pojišťoven v praxi...",
        "url": "https://www.root.cz/clanek/456",
        "image": None,
    },
]

# ----------------------------
# Výpis článků
# ----------------------------
for art in articles:
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.image(art["image"] or "https://via.placeholder.com/150", use_container_width=True)
    with col2:
        st.markdown(f"<span style='background-color:red; color:white; padding:2px 6px;'>{art['source']}</span>", unsafe_allow_html=True)
        st.markdown(f"### **{art['title']}**")
        st.markdown(f"**{art['perex']}**")
        st.markdown(f"*{art['url']}*")

st.markdown("---")
st.write("Stránkovač (zatím mock)")
