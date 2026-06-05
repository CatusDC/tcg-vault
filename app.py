import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="TCG Vault", layout="wide")

st.title("🎴 TCG Vault")

# =========================
# GIOCHI
# =========================

GAMES = {
    "C - Lorcana JP": "https://raw.githubusercontent.com/CatusDC/TCG_vault/main/data/lorcana_jp.json",
    "C - Lorcana": "https://raw.githubusercontent.com/CatusDC/TCG_vault/main/data/lorcana.json",
    "C - Riftbound": "https://raw.githubusercontent.com/CatusDC/TCG_vault/main/data/riftbound.json",
    "C - Pokemon JP": "https://raw.githubusercontent.com/CatusDC/TCG_vault/main/data/pokemon_jp.json",
    "P - Lorcana": "https://raw.githubusercontent.com/CatusDC/TCG_vault/main/P - Lorcana.json",
    "P - RIftbound": "https://raw.githubusercontent.com/CatusDC/TCG_vault/main/data/p_riftbound.json"
}

# =========================
# LOAD
# =========================

@st.cache_data
def load_json(url):
    r = requests.get(url)
    return r.json()

game = st.sidebar.selectbox("Seleziona gioco", list(GAMES.keys()))

data = load_json(GAMES[game])
cards = data.get("cards", [])

df = pd.DataFrame(cards)

st.subheader(game)

if df.empty:
    st.warning("Nessuna carta trovata")
    st.stop()

# =========================
# FILTRI
# =========================

col1, col2, col3 = st.columns(3)

with col1:
    rarity = st.selectbox("Rarità", ["All"] + sorted(df["rarity"].dropna().unique()))

with col2:
    sets = st.selectbox("Set", ["All"] + sorted(df["set"].dropna().unique()))

with col3:
    search = st.text_input("Ricerca")

filtered = df.copy()

if rarity != "All":
    filtered = filtered[filtered["rarity"] == rarity]

if sets != "All":
    filtered = filtered[filtered["set"] == sets]

if search:
    filtered = filtered[
        filtered["name"].str.contains(search, case=False, na=False) |
        filtered["tag"].str.contains(search, case=False, na=False)
    ]

st.write(f"Carte: {len(filtered)}")

st.dataframe(
    filtered[
        ["set", "tag", "name", "rarity", "v1own", "v1max", "v2own", "v2max", "v3own", "v3max"]
    ],
    use_container_width=True
)
