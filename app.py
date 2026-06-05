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
# LOAD JSON
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

st.subheader(game)

if df.empty:
    st.warning("Nessuna carta trovata")
    st.stop()

# =========================
# FILTRI BASE
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
# FILTRI COMPLETAMENTO (NUOVI)
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
        filtered["name"].str.contains(search, case=False, na=False)
        | filtered["tag"].str.contains(search, case=False, na=False)
    ]

# =========================
# COMBINAZIONE COLONNE
# =========================

def combine(own, maxv):
    return f"{own} / {maxv}"

filtered["v1"] = filtered.apply(lambda x: combine(x["v1own"], x["v1max"]), axis=1)
filtered["v2"] = filtered.apply(lambda x: combine(x["v2own"], x["v2max"]), axis=1)
filtered["v3"] = filtered.apply(lambda x: combine(x["v3own"], x["v3max"]), axis=1)

# =========================
# LOGIC FILTRI COMPLETAMENTO
# =========================

if hide_v1_complete:
    filtered = filtered[filtered["v1own"] != filtered["v1max"]]

if hide_v2_complete:
    filtered = filtered[filtered["v2own"] != filtered["v2max"]]

if hide_v3_complete:
    filtered = filtered[filtered["v3own"] != filtered["v3max"]]

# reset index (niente colonna 0)
filtered = filtered.reset_index(drop=True)

# =========================
# STYLING CONDIZIONALE
# =========================

def highlight(row):
    styles = []

    # v1
    if row["v1own"] == row["v1max"]:
        styles.append("background-color: #d4f8d4")
    else:
        styles.append("background-color: #ffe5cc")

    # v2
    if row["v2own"] == row["v2max"]:
        styles.append("background-color: #d4f8d4")
    else:
        styles.append("background-color: #ffe5cc")

    # v3
    if row["v3own"] == row["v3max"]:
        styles.append("background-color: #d4f8d4")
    else:
        styles.append("background-color: #ffe5cc")

    # colonne extra senza stile
    extra_cols = len(row) - 3
    return [""] * extra_cols + styles

# =========================
# OUTPUT
# =========================

st.write(f"Carte trovate: **{len(filtered)}**")

# mantieni DF completo per styling
styled_df = filtered.style.apply(highlight, axis=1)

# poi selezioni solo le colonne da mostrare
columns_to_show = ["set", "tag", "name", "rarity", "v1", "v2", "v3"]
styled_df = styled_df.format()

styled_df = filtered[columns_to_show].style.apply(highlight, axis=1)

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True
)
