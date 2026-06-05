import streamlit as st
import requests
import json
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="TCG Vault", layout="wide")

GAMES = {
    "C - Lorcana JP": "p-lorcana.json",
    "C - Lorcana": "p-lorcana.json",
    "C - Riftbound": "p-lorcana.json",
    "C - Pokemon JP": "p-lorcana.json",
    "P - Lorcana": "p-lorcana.json",
    "P - RIftbound": "p-lorcana.json"
}

BASE_URL = "https://raw.githubusercontent.com/CatusDC/tcg_vault/main/data/"

# =========================
# LOAD JSON (RAW)
# =========================

@st.cache_data
def load_json(file_name):
    url = BASE_URL + file_name

    r = requests.get(url)

    if r.status_code != 200:
        st.error(f"Errore HTTP: {r.status_code}")
        st.stop()

    try:
        return r.json()
    except Exception as e:
        st.error("JSON non valido o non parsabile")
        st.write("Debug raw response (prime 300 char):")
        st.code(r.text[:300])
        st.stop()

# =========================
# UI
# =========================

st.title("🎴 TCG Vault")

game = st.sidebar.selectbox("Seleziona gioco", list(GAMES.keys()))

file_name = GAMES[game]

data = load_json(file_name)

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
    if "rarity" in df.columns:
        rarity_list = ["All"] + sorted(df["rarity"].dropna().unique().tolist())
        rarity_filter = st.selectbox("Rarità", rarity_list)
    else:
        rarity_filter = "All"

with col2:
    if "set" in df.columns:
        set_list = ["All"] + sorted(df["set"].dropna().unique().tolist())
        set_filter = st.selectbox("Set", set_list)
    else:
        set_filter = "All"

with col3:
    search = st.text_input("Ricerca (name / tag)")

# =========================
# FILTER LOGIC
# =========================

filtered = df.copy()

if rarity_filter != "All" and "rarity" in df.columns:
    filtered = filtered[filtered["rarity"] == rarity_filter]

if set_filter != "All" and "set" in df.columns:
    filtered = filtered[filtered["set"] == set_filter]

if search:
    if "name" in df.columns:
        filtered = filtered[
            df["name"].str.contains(search, case=False, na=False)
            | df["tag"].str.contains(search, case=False, na=False)
        ]

# =========================
# OUTPUT
# =========================

st.write(f"Carte trovate: **{len(filtered)}**")

columns_to_show = [
    "set", "tag", "name", "rarity",
    "v1own", "v1max",
    "v2own", "v2max",
    "v3own", "v3max"
]

existing_cols = [c for c in columns_to_show if c in filtered.columns]

st.dataframe(filtered[existing_cols], use_container_width=True)
