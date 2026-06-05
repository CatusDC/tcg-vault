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
    rarity_filter = "All"
    if "rarity" in df.columns:
        rarity_list = ["All"] + sorted(df["rarity"].dropna().unique().tolist())
        rarity_filter = st.selectbox("Rarità", rarity_list)

with col2:
    set_filter = "All"
    if "set" in df.columns:
        set_list = ["All"] + sorted(df["set"].dropna().unique().tolist())
        set_filter = st.selectbox("Set", set_list)

with col3:
    search = st.text_input("Ricerca (name / tag)")

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
        filtered["name"].str.contains(search, case=False, na=False)
        | filtered["tag"].str.contains(search, case=False, na=False)
    ]

# =========================
# TRANSFORM UI (QUI LA PARTE IMPORTANTE)
# =========================

def combine(v_own, v_max):
    return f"{v_own} / {v_max}"

filtered["v1"] = filtered.apply(lambda x: combine(x["v1own"], x["v1max"]), axis=1)
filtered["v2"] = filtered.apply(lambda x: combine(x["v2own"], x["v2max"]), axis=1)
filtered["v3"] = filtered.apply(lambda x: combine(x["v3own"], x["v3max"]), axis=1)

# colonne finali pulite
columns_to_show = ["set", "tag", "name", "rarity", "v1", "v2", "v3"]

# reset indice (rimuove colonna 0)
filtered = filtered.reset_index(drop=True)

st.write(f"Carte trovate: **{len(filtered)}**")

st.dataframe(
    filtered[columns_to_show],
    use_container_width=True,
    hide_index=True
)
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
