import streamlit as st
import requests
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="TCG Vault", layout="wide")

GAMES = {
    "C - Lorcana JP": "c-lorcana-jp.json",
    "C - Lorcana": "c-lorcana.json",
    "C - Riftbound": "c-riftbound.json",
    "C - Pokemon JP": "c-pokemon-jp.json",
    "P - Lorcana": "p-lorcana.json",
    "P - RIftbound": "p-riftbound.json"
}

BASE_URL = "https://raw.githubusercontent.com/CatusDC/tcg_vault/main/data/"

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_json(file_name):
    url = BASE_URL + file_name
    r = requests.get(url)

    if r.status_code != 200:
        st.error(f"Errore HTTP: {r.status_code}")
        st.stop()

    return r.json()

# =========================
# UI
# =========================

st.title("🎴 TCG Vault")

game = st.sidebar.selectbox("Seleziona gioco", list(GAMES.keys()))
file_name = GAMES[game]

data = load_json(file_name)
cards = data.get("cards", [])

df = pd.DataFrame(cards)

if df.empty:
    st.warning("Nessuna carta trovata")
    st.stop()

st.subheader(game)

# =========================
# FILTRI BASE
# =========================

col1, col2, col3 = st.columns(3)

with col1:
    rarity_filter = "All"
    if "rarity" in df.columns:
        rarity_filter = st.selectbox(
            "Rarità",
            ["All"] + sorted(df["rarity"].dropna().unique().tolist())
        )

with col2:
    set_filter = "All"
    if "set" in df.columns:
        set_filter = st.selectbox(
            "Set",
            ["All"] + sorted(df["set"].dropna().unique().tolist())
        )

with col3:
    search = st.text_input("Ricerca (name / tag)")

# =========================
# FILTRI vX COMPLETION
# =========================

c1, c2, c3 = st.columns(3)

with c1:
    hide_v1_complete = st.checkbox("Nascondi v1 completate")

with c2:
    hide_v2_complete = st.checkbox("Nascondi v2 completate")

with c3:
    hide_v3_complete = st.checkbox("Nascondi v3 completate")

# =========================
# FILTER LOGIC
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
# vX FILTERS
# =========================

if hide_v1_complete:
    filtered = filtered[filtered["v1own"] != filtered["v1max"]]

if hide_v2_complete:
    filtered = filtered[filtered["v2own"] != filtered["v2max"]]

if hide_v3_complete:
    filtered = filtered[filtered["v3own"] != filtered["v3max"]]

# =========================
# COLONNE COMBINATE
# =========================

filtered["v1"] = filtered["v1own"].astype(str) + " / " + filtered["v1max"].astype(str)
filtered["v2"] = filtered["v2own"].astype(str) + " / " + filtered["v2max"].astype(str)
filtered["v3"] = filtered["v3own"].astype(str) + " / " + filtered["v3max"].astype(str)

# =========================
# OUTPUT (SET NASCOSTA MA USATA PER FILTRI)
# =========================

display_df = filtered[[
    "tag",
    "name",
    "rarity",
    "v1",
    "v2",
    "v3"
]].reset_index(drop=True)

st.write(f"Carte trovate: **{len(display_df)}**")

st.dataframe(display_df, use_container_width=True, hide_index=True)
