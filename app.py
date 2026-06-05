import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

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

if df.empty:
    st.warning("Nessun dato disponibile")
    st.stop()

games = sorted(df["game"].dropna().unique().tolist())

# =========================
# GLOBAL GAME SELECTOR (UNICO)
# =========================

selected_game = st.sidebar.selectbox(
    "🎮 Gioco",
    games
)

df_game = df[df["game"] == selected_game].copy()

# =========================
# PROGRESS CIRCLE
# =========================

def progress_circle(title, value, total):
    pct = 0 if total == 0 else value / total * 100

    fig = go.Figure(go.Pie(
        values=[pct, 100 - pct],
        hole=0.72,
        marker_colors=["#4cd97b", "#2a2a2a"],
        textinfo="none"
    ))

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        annotations=[
            dict(
                text=f"{title}<br><b>{pct:06.2f}%</b>",
                x=0.5,
                y=0.5,
                font_size=13,
                showarrow=False,
                align="center"
            )
        ],
        height=200,
        width=200
    )

    return fig

# =========================
# TABS
# =========================

home_tab, col_tab, recap_tab, set_tab = st.tabs(
    ["🏠 Home", "📋 Collection", "📊 Recap", "📦 Set Tracker"]
)

# =========================================================
# 🏠 HOME (ALL GAMES - 6 CIRCOLI IN GRID 3x2)
# =========================================================

with home_tab:

    st.title("🎴 TCG Vault Dashboard")
    st.subheader("Panoramica collezioni")

    stats = df.groupby("game").agg(
        owned=("v1own", "sum"),
        total=("v1max", "sum")
    ).reset_index()

    cols = st.columns(3)

    for i, row in stats.iterrows():

        with cols[i % 3]:

            fig = progress_circle(
                row["game"],
                row["owned"],
                row["total"]
            )

            st.plotly_chart(fig, use_container_width=True)

        # nuova riga ogni 3 elementi
        if (i + 1) % 3 == 0 and i != len(stats) - 1:
            cols = st.columns(3)

# =========================================================
# 📋 COLLECTION
# =========================================================

with col_tab:

    st.title(f"📋 Collection - {selected_game}")

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

    c1, c2, c3 = st.columns(3)

    with c1:
        hide_v1 = st.checkbox("Nascondi v1 completate")

    with c2:
        hide_v2 = st.checkbox("Nascondi v2 completate")

    with c3:
        hide_v3 = st.checkbox("Nascondi v3 completate")

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

    if hide_v1:
        filtered = filtered[~((filtered["v1max"] > 0) & (filtered["v1own"] == filtered["v1max"]))]

    if hide_v2:
        filtered = filtered[~((filtered["v2max"] > 0) & (filtered["v2own"] == filtered["v2max"]))]

    if hide_v3:
        filtered = filtered[~((filtered["v3max"] > 0) & (filtered["v3own"] == filtered["v3max"]))]

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

    st.title("📦 Set Completion Tracker")

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
