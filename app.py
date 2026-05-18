import streamlit as st
import pandas as pd

# ===== CONFIG =====
st.set_page_config(
    page_title="Examens",
    page_icon="📚",
    layout="wide"
)

# ===== STYLE CSS =====
st.markdown("""
<style>
.card {
    padding: 15px;
    border-radius: 15px;
    background-color: #f5f7fa;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 10px;
}
.title {
    font-size: 20px;
    font-weight: bold;
}
.subtitle {
    color: gray;
    font-size: 14px;
}
.tag {
    padding: 4px 8px;
    border-radius: 8px;
    font-size: 12px;
    color: white;
    display: inline-block;
}
.fr {
    background-color: #2b8cff;
}
.de {
    background-color: #ff7a00;
}
</style>
""", unsafe_allow_html=True)

# ===== DATA =====
@st.cache_data
def load_data():
    return pd.read_excel("examens.xlsx")

df = load_data()

st.title("📊 Planification des examens")

# ===== SIDEBAR FILTERS =====
st.sidebar.header("🔎 Filtres")

langues = df["Sprache (français/deutsch)"].dropna().unique()
selected_langue = st.sidebar.multiselect(
    "Langue",
    options=langues,
    default=langues
)

classes = df["Klasse"].dropna().unique()
selected_classe = st.sidebar.multiselect(
    "Classe",
    options=classes,
    default=classes
)

# ===== FILTER =====
filtered_df = df[
    (df["Sprache (français/deutsch)"].isin(selected_langue)) &
    (df["Klasse"].isin(selected_classe))
]

filtered_df = filtered_df.sort_values(by=["Prüfungsdatum", "Prüfungszeit"])

# ===== KPIs =====
col1, col2, col3 = st.columns(3)

col1.metric("📋 Examens", len(filtered_df))
col2.metric("🏫 Classes", filtered_df["Klasse"].nunique())
col3.metric("🌍 Langues", filtered_df["Sprache (français/deutsch)"].nunique())

st.divider()

# ===== CARDS DISPLAY =====
for _, row in filtered_df.iterrows():

    langue = row["Sprache (français/deutsch)"]
    tag_class = "fr" if "fr" in langue.lower() else "de"

    st.markdown(f"""
    <div class="card">
        <div class="title">{row['Prüfung']}</div>

        <div class="subtitle">
            📅 {row['Prüfungsdatum']} | ⏰ {row['Prüfungszeit']}
        </div>

        <br>

        🏫 <b>Classe:</b> {row['Klasse']} <br>
        👨‍🏫 <b>Enseignant:</b> {row['Lehrperson der Klasse']} <br>
        👀 <b>Surveillance:</b> {row['Aufsichtsperson']} <br><br>

        <span class="tag {tag_class}">{langue}</span>
    </div>
    """, unsafe_allow_html=True)