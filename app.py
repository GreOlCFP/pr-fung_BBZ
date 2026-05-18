import streamlit as st
import pandas as pd

st.set_page_config(page_title="Examens", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("examens.xlsx")

df = load_data()

st.title("📊 Planification des examens")

# ===== FILTRES =====
st.sidebar.header("🔎 Filtres")

langues = df["Sprache (français/deutsch)"].dropna().unique()
selected_langue = st.sidebar.multiselect("Langue", langues, default=langues)

classes = df["Klasse"].dropna().unique()
selected_classe = st.sidebar.multiselect("Classe", classes, default=classes)

# ===== FILTRE =====
filtered_df = df[
    (df["Sprache (français/deutsch)"].isin(selected_langue)) &
    (df["Klasse"].isin(selected_classe))
].sort_values(by=["Prüfungsdatum", "Prüfungszeit"])

# ===== KPIs =====
col1, col2, col3 = st.columns(3)
col1.metric("📋 Examens", len(filtered_df))
col2.metric("🏫 Classes", filtered_df["Klasse"].nunique())
col3.metric("🌍 Langues", filtered_df["Sprache (français/deutsch)"].nunique())

st.divider()

# ===== AFFICHAGE TYPE CARTE (SAFE) =====
cols = st.columns(2)

for i, (_, row) in enumerate(filtered_df.iterrows()):
    with cols[i % 2]:
        with st.container():
            st.subheader(row["Prüfung"])
            st.write(f"📅 {row['Prüfungsdatum']} | ⏰ {row['Prüfungszeit']}")
            st.write(f"🏫 Classe : {row['Klasse']}")
            st.write(f"👨‍🏫 Enseignant : {row['Lehrperson der Klasse']}")
            st.write(f"👀 Surveillance : {row['Aufsichtsperson']}")
            st.badge(row["Sprache (français/deutsch)"])
            st.divider()
