import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="TCG Vault", layout="wide")

st.title("🎴 TCG Vault")

# =========================
# CONFIG (MODIFICA QUI)
# =========================

JSON_FILES = {
    "Pokemon": "https://1drv.ms/u/c/506c16037a998404/IQDsiy_Tc6zyRJ7KXo-WFslFAYgu2DGG97DH-px3soh0NpM?e=gvflk6",
    "One Piece": "https://1drv.ms/u/c/506c16037a998404/IQDsiy_Tc6zyRJ7KXo-WFslFAYgu2DGG97DH-px3soh0NpM?e=gvflk6",
    "Yu-Gi-Oh": "https://1drv.ms/u/c/506c16037a998404/IQDsiy_Tc6zyRJ7KXo-WFslFAYgu2DGG97DH-px3soh0NpM?e=gvflk6"
}

# =========================
# LOAD JSON
# =========================
@st.cache_data
def load_data(url):
    try:
        r = requests.get(url)
        return r.json()
    except:
        return {"cards": []}

# =========================
# HOME
# =========================

game = st.sidebar.selectbox("Seleziona gioco", list(JSON_FILES.keys()))

data = load_data(JSON_FILES[game])
cards = data.get("cards", [])

df = pd.DataFrame(cards)

st.subheader(f"📦 {game}")

if df.empty:
    st.warning("Nessun dato trovato")
    st.stop()

# =========================
# FILTRI
# =========================

col1, col2, col3 = st.columns(3)

with col1:
    rarities = ["All"] + sorted(df["rarity"].dropna().unique().tolist())
    rarity_filter = st.selectbox("Rarità", rarities)

with col2:
    sets = ["All"] + sorted(df["set"].dropna().unique().tolist())
    set_filter = st.selectbox("Set", sets)

with col3:
    search = st.text_input("Ricerca (nome / tag)")

# =========================
# APPLY FILTERS
# =========================

filtered = df.copy()

if rarity_filter != "All":
    filtered = filtered[filtered["rarity"] == rarity_filter]

if set_filter != "All":
    filtered = filtered[filtered["set"] == set_filter]

if search:
    filtered = filtered[
        filtered["name"].str.contains(search, case=False, na=False) |
        filtered["tag"].str.contains(search, case=False, na=False)
    ]

# =========================
# DISPLAY
# =========================

st.write(f"Carte trovate: {len(filtered)}")

st.dataframe(
    filtered[
        ["set", "tag", "name", "rarity", "v1own", "v1max", "v2own", "v2max", "v3own", "v3max"]
    ],
    use_container_width=True
)
