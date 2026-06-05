import streamlit as st
import requests
import base64
import json
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="TCG Vault", layout="wide")

GAMES = {
    "C - Lorcana JP": "p-lorcana.json",
    "C - Lorcana": "lorcana.json",
    "C - Riftbound": "riftbound.json",
    "C - Pokemon JP": "pokemon_jp.json",
    "P - Lorcana": "p-lorcana.json",
    "P - RIftbound": "p-riftbound.json"
}

REPO = "tcg_vault"
BASE_PATH = "main"   # <-- come richiesto

# =========================
# GITHUB AUTH
# =========================

TOKEN = st.secrets["GITHUB_TOKEN"]

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# =========================
# LOAD JSON FROM PRIVATE REPO
# =========================

@st.cache_data
def load_json(file_name):
    url = f"https://raw.githubusercontent.com/CatusDC/tcg_vault/{file_name}"

    r = requests.get(
        url,
        headers={"Authorization": f"token {TOKEN}"}
    )

    if r.status_code != 200:
        st.error(r.text)
        st.stop()

    data = r.json()

    if "content" not in data:
        st.error("File non valido o vuoto")
        st.stop()

    decoded = base64.b64decode(data["content"]).decode("utf-8")

    return json.loads(decoded)

# =========================
# UI - HOME
# =========================

st.title("🎴 TCG Vault")

game = st.sidebar.selectbox("Seleziona gioco", list(GAMES.keys()))

file_path = GAMES[game]

data = load_json(file_path)

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
            filtered["name"].str.contains(search, case=False, na=False)
            | filtered["tag"].str.contains(search, case=False, na=False)
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
