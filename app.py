import streamlit as st
import pandas as pd

# ===== CONFIG =====
st.set_page_config(page_title="Examens", layout="wide")

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    df = pd.read_excel("examens.xlsx")
    
    # Nettoyage des colonnes (important !)
    df.columns = df.columns.str.strip()
    
    return df

df = load_data()

# ===== TITLE =====
st.title("📊 Planification des examens")

# ===== SIDEBAR FILTERS =====
st.sidebar.header("🔎 Filtres")

# Filtre langue (corrigé ✅)
langues = df["Sprache"].dropna().unique()
selected_langue = st.sidebar.multiselect(
    "Langue",
    options=langues,
    default=langues
)

# Filtre classe ✅
classes = df["Klasse"].dropna().unique()
selected_classe = st.sidebar.multiselect(
    "Classe",
    options=classes,
    default=classes
)

# ===== FILTER DATA =====
filtered_df = df[
    (df["Sprache"].isin(selected_langue)) &
    (df["Klasse"].isin(selected_classe))
].sort_values(by=["Prüfungsdatum", "Prüfungszeit"])

# ===== KPI =====
col1, col2, col3 = st.columns(3)
col1.metric("📋 Examens", len(filtered_df))
col2.metric("🏫 Classes", filtered_df["Klasse"].nunique())
col3.metric("🌍 Langues", filtered_df["Sprache"].nunique())

st.divider()

# ===== DISPLAY (STYLE CARTE STABLE) =====

for _, row in filtered_df.iterrows():
    with st.container():
        st.subheader(row["Prüfung"])
        st
for i, (_, row) in enumerate(filtered_df.iterrows()):
    with cols[i % 2]:
        with st.container():
            st.subheader(row["Prüfung"])
            st.write(f"📅 {row['Prüfungsdatum']} | ⏰ {row['Prüfungszeit']}")
            st.write(f"🏫 Classe : {row['Klasse']}")
            st.write(f"👨‍🏫 Enseignant : {row['Lehrperson der Klasse']}")
            st.write(f"👀 Surveillance : {row['Aufsichtsperson']}")
            
            # Badge langue (stable ✅)
            st.badge(row["Sprache"])
            
            st.divider()
