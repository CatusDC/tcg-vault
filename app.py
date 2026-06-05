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
        st.error(f"Errore JSON: {r.status_code}")
        st.stop()
    return r.json()

data = load_data()
df = pd.DataFrame(data.get("cards", []))

games = sorted(df["game"].dropna().unique().tolist())

# =========================
# SESSION STATE
# =========================

if "game" not in st.session_state:
    st.session_state.game = None

def select_game(game):
    st.session_state.game = game

# =========================
# FILTER DATA
# =========================

def get_game_df():
    if not st.session_state.game:
        return None
    return df[df["game"] == st.session_state.game].copy()

df_game = get_game_df()

# =========================
# TABS
# =========================

home_tab, col_tab, recap_tab, set_tab = st.tabs(
    ["🏠 Home", "📋 Collection", "📊 Recap", "📦 Set Tracker"]
)

# =========================================================
# 🏠 HOME HUB (LIGHT VERSION)
# =========================================================

with home_tab:

    st.title("🎴 TCG Vault")
    st.subheader("Seleziona un gioco")

    stats = df.groupby("game").agg(
        owned=("v1own", "sum"),
        total=("v1max", "sum")
    ).reset_index()

    cols = st.columns(3)

    for i, row in stats.iterrows():

        pct = 0 if row["total"] == 0 else row["owned"] / row["total"]

        with cols[i % 3]:

            st.markdown(f"### {row['game']}")

            st.progress(pct)

            st.caption(f"{pct*100:05.2f}% completato")

            st.button(
                "Apri",
                use_container_width=True,
                on_click=select_game,
                args=(row["game"],)
            )

        if (i + 1) % 3 == 0:
            cols = st.columns(3)

    if st.session_state.game:
        st.success(f"Gioco selezionato: {st.session_state.game}")

# =========================================================
# 📋 COLLECTION
# =========================================================

with col_tab:

    st.title("📋 Collection")

    if df_game is None:
        st.warning("Seleziona un gioco dalla Home")
        st.stop()

    col1, col2, col3 = st.columns(3)

    with col1:
        rarity_filter = st.selectbox(
            "Rarità",
            ["All"] + sorted(df_game["rarity"].dropna().unique().tolist())
        )

    with col2:
        set_filter = st.selectbox(
            "Set",
            ["All"] + sorted(df_game["set"].dropna().unique().tolist())
        )

    with col3:
        search = st.text_input("Ricerca")

    filtered = df_game.copy()

    if rarity_filter != "All":
        filtered = filtered[filtered["rarity"] == rarity_filter]

    if set_filter != "All":
        filtered = filtered[filtered["set"] == set_filter]

    if search:
        filtered = filtered[
            filtered["name"].str.contains(search, case=False, na=False) |
            filtered["tag"].str.contains(search, case=False, na=False)
        ]

    filtered["v1"] = filtered["v1own"].astype(str) + " / " + filtered["v1max"].astype(str)
    filtered["v2"] = filtered["v2own"].astype(str) + " / " + filtered["v2max"].astype(str)
    filtered["v3"] = filtered["v3own"].astype(str) + " / " + filtered["v3max"].astype(str)

    st.dataframe(
        filtered[["set", "tag", "name", "rarity", "v1", "v2", "v3"]],
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# 📊 RECAP
# =========================================================

with recap_tab:

    st.title("📊 Recap Rarità")

    if df_game is None:
        st.warning("Seleziona un gioco dalla Home")
        st.stop()

    recap = df_game.groupby("rarity").agg(
        v1_owned=("v1own", "sum"),
        v1_max=("v1max", "sum"),
        v2_owned=("v2own", "sum"),
        v2_max=("v2max", "sum"),
        v3_owned=("v3own", "sum"),
        v3_max=("v3max", "sum"),
    ).reset_index()

    recap["v1"] = recap["v1_owned"].astype(str) + " / " + recap["v1_max"].astype(str)
    recap["v2"] = recap["v2_owned"].astype(str) + " / " + recap["v2_max"].astype(str)
    recap["v3"] = recap["v3_owned"].astype(str) + " / " + recap["v3_max"].astype(str)

    st.dataframe(
        recap[["rarity", "v1", "v2", "v3"]],
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# 📦 SET TRACKER
# =========================================================

with set_tab:

    st.title("📦 Set Tracker")

    if df_game is None:
        st.warning("Seleziona un gioco dalla Home")
        st.stop()

    set_stats = df_game.groupby("set").agg(
        owned=("v1own", "sum"),
        total=("v1max", "sum")
    ).reset_index()

    set_stats["pct"] = set_stats["owned"] / set_stats["total"].replace(0, 1) * 100

    set_stats = set_stats.sort_values("pct", ascending=False)

    st.dataframe(
        set_stats[["set", "owned", "total", "pct"]],
        use_container_width=True,
        hide_index=True
    )
