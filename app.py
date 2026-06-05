import streamlit as st
import requests
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="TCG Vault", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/CatusDC/tcg_vault/main/data/collection.json"

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    r = requests.get(DATA_URL)

    if r.status_code != 200:
        st.error(f"Errore caricamento JSON: {r.status_code}")
        st.stop()

    try:
        return r.json()
    except Exception:
        st.error("JSON non valido o corrotto")
        st.stop()


data = load_data()
cards = data.get("cards", [])

df = pd.DataFrame(cards)

if df.empty:
    st.warning("Nessuna carta trovata")
    st.stop()

# =========================
# GAME SELECTION
# =========================

games = sorted(df["game"].dropna().unique().tolist())
selected_game = st.sidebar.selectbox("🎮 Gioco", games)

df = df[df["game"] == selected_game].copy()

st.title(f"🎴 TCG Vault - {selected_game}")

# =========================
# TABS DASHBOARD
# =========================

tab1, tab2 = st.tabs(["📋 Collezione", "📊 Recap"])

# =========================
# TAB 1 - COLLECTION
# =========================

with tab1:

    # -------------------------
    # FILTERS
    # -------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        rarity_filter = st.selectbox(
            "Rarità",
            ["All"] + sorted(df["rarity"].dropna().unique().tolist())
        )

    with col2:
        set_filter = st.selectbox(
            "Set",
            ["All"] + sorted(df["set"].dropna().unique().tolist())
        )

    with col3:
        search = st.text_input("Ricerca (name / tag)")

    c1, c2, c3 = st.columns(3)

    with c1:
        hide_v1 = st.checkbox("Nascondi v1 completate")

    with c2:
        hide_v2 = st.checkbox("Nascondi v2 completate")

    with c3:
        hide_v3 = st.checkbox("Nascondi v3 completate")

    # -------------------------
    # FILTER LOGIC
    # -------------------------

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

    # safe completion filters (gestisce vmax=0)
    if hide_v1:
        filtered = filtered[~((filtered["v1max"] > 0) & (filtered["v1own"] == filtered["v1max"]))]

    if hide_v2:
        filtered = filtered[~((filtered["v2max"] > 0) & (filtered["v2own"] == filtered["v2max"]))]

    if hide_v3:
        filtered = filtered[~((filtered["v3max"] > 0) & (filtered["v3own"] == filtered["v3max"]))]

    # -------------------------
    # DISPLAY COLUMNS
    # -------------------------

    filtered["v1"] = filtered["v1own"].astype(str) + " / " + filtered["v1max"].astype(str)
    filtered["v2"] = filtered["v2own"].astype(str) + " / " + filtered["v2max"].astype(str)
    filtered["v3"] = filtered["v3own"].astype(str) + " / " + filtered["v3max"].astype(str)

    display_df = filtered[[
        "set",
        "tag",
        "name",
        "rarity",
        "v1",
        "v2",
        "v3"
    ]].reset_index(drop=True)

    st.write(f"Carte trovate: **{len(display_df)}**")

    st.dataframe(display_df, use_container_width=True, hide_index=True)

# =========================
# TAB 2 - RECAP
# =========================

with tab2:

    st.subheader("📊 Recap per rarità")

    recap = df.copy()

    summary = recap.groupby("rarity").agg(
        total_v1=("v1own", "sum"),
        max_v1=("v1max", "sum"),
        total_v2=("v2own", "sum"),
        max_v2=("v2max", "sum"),
        total_v3=("v3own", "sum"),
        max_v3=("v3max", "sum"),
    ).reset_index()

    summary["v1"] = summary["total_v1"].astype(str) + " / " + summary["max_v1"].astype(str)
    summary["v2"] = summary["total_v2"].astype(str) + " / " + summary["max_v2"].astype(str)
    summary["v3"] = summary["total_v3"].astype(str) + " / " + summary["max_v3"].astype(str)

    st.dataframe(
        summary[["rarity", "v1", "v2", "v3"]],
        use_container_width=True,
        hide_index=True
    )
