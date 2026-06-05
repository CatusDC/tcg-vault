import streamlit as st
import requests
import pandas as pd

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="TCG Vault Dashboard", layout="wide")

BASE_URL = "https://raw.githubusercontent.com/CatusDC/tcg_vault/main/data/"

GAMES = {
    "C - Lorcana JP": "c-lorcana-jp.json",
    "C - Lorcana": "c-lorcana.json",
    "C - Riftbound": "c-riftbound.json",
    "C - Pokemon JP": "c-pokemon-jp.json",
    "P - Lorcana": "p-lorcana.json",
    "P - RIftbound": "p-riftbound.json"
}

# =========================
# LOAD
# =========================

@st.cache_data
def load_json(file_name):
    url = BASE_URL + file_name
    r = requests.get(url)

    if r.status_code != 200:
        return None

    return r.json()

def to_df(game_file):
    data = load_json(game_file)
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data.get("cards", []))

# =========================
# STATS
# =========================

def compute_stats(df):
    if df.empty:
        return 0, 0, 0

    total_max = df["v1max"].sum() + df["v2max"].sum() + df["v3max"].sum()
    total_own = df["v1own"].sum() + df["v2own"].sum() + df["v3own"].sum()

    pct = (total_own / total_max * 100) if total_max > 0 else 0
    return total_own, total_max, pct

# =========================
# RECAP RARITY
# =========================

def build_recap(df):
    recap = df.groupby("rarity").agg({
        "v1own": "sum",
        "v1max": "sum",
        "v2own": "sum",
        "v2max": "sum",
        "v3own": "sum",
        "v3max": "sum",
    }).reset_index()

    recap["v1"] = recap["v1own"].astype(int).astype(str) + " / " + recap["v1max"].astype(int).astype(str)
    recap["v2"] = recap["v2own"].astype(int).astype(str) + " / " + recap["v2max"].astype(int).astype(str)
    recap["v3"] = recap["v3own"].astype(int).astype(str) + " / " + recap["v3max"].astype(int).astype(str)

    return recap

# =========================
# SESSION STATE
# =========================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_game" not in st.session_state:
    st.session_state.selected_game = None

# =========================
# NAV HELPERS
# =========================

def go_home():
    st.session_state.page = "home"
    st.session_state.selected_game = None

def open_game(game_name):
    st.session_state.page = "game"
    st.session_state.selected_game = game_name

# =========================
# HOME DASHBOARD
# =========================

def render_home():
    st.title("🎴 TCG Vault Dashboard")

    cols = st.columns(3)

    for i, (game_name, file_name) in enumerate(GAMES.items()):
        df = to_df(file_name)

        own, total, pct = compute_stats(df)

        with cols[i % 3]:
            st.metric(
                label=game_name,
                value=f"{pct:.1f}% completato",
                delta=f"{own}/{total}"
            )

            st.progress(pct / 100 if total > 0 else 0)

            if st.button(f"Apri {game_name}", key=game_name):
                open_game(game_name)

# =========================
# GAME PAGE
# =========================

def render_game():
    game_name = st.session_state.selected_game
    file_name = GAMES[game_name]

    df = to_df(file_name)

    st.title(f"🎮 {game_name}")

    colA, colB = st.columns([1, 3])

    with colA:
        if st.button("⬅ Torna indietro"):
            go_home()

        view = st.radio(
            "Vista",
            ["Dettaglio", "Recap rarità"]
        )

    if df.empty:
        st.warning("Nessun dato")
        return

    # =========================
    # RECAP MODE
    # =========================

    if view == "Recap rarità":
        recap = build_recap(df)

        st.subheader("📊 Progress per rarità")

        st.dataframe(
            recap[["rarity", "v1", "v2", "v3"]],
            use_container_width=True,
            hide_index=True
        )
        return

    # =========================
    # DETAIL MODE FILTERS
    # =========================

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
        search = st.text_input("Search")

    c1, c2, c3 = st.columns(3)

    with c1:
        hide_v1 = st.checkbox("Hide v1 complete")

    with c2:
        hide_v2 = st.checkbox("Hide v2 complete")

    with c3:
        hide_v3 = st.checkbox("Hide v3 complete")

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

    # FIX vX filters
    if hide_v1:
        filtered = filtered[~((filtered["v1max"] > 0) & (filtered["v1own"] == filtered["v1max"]))]

    if hide_v2:
        filtered = filtered[~((filtered["v2max"] > 0) & (filtered["v2own"] == filtered["v2max"]))]

    if hide_v3:
        filtered = filtered[~((filtered["v3max"] > 0) & (filtered["v3own"] == filtered["v3max"]))]

    # =========================
    # DISPLAY
    # =========================

    filtered["v1"] = filtered["v1own"].astype(str) + " / " + filtered["v1max"].astype(str)
    filtered["v2"] = filtered["v2own"].astype(str) + " / " + filtered["v2max"].astype(str)
    filtered["v3"] = filtered["v3own"].astype(str) + " / " + filtered["v3max"].astype(str)

    st.subheader(f"Carte trovate: {len(filtered)}")

    st.dataframe(
        filtered[["tag", "name", "rarity", "v1", "v2", "v3"]],
        use_container_width=True,
        hide_index=True
    )

# =========================
# ROUTER
# =========================

if st.session_state.page == "home":
    render_home()
else:
    render_game()
