import streamlit as st
import pandas as pd

# ===== CONFIG =====
st.set_page_config(page_title="Examens", layout="wide")

# ===== LANGUE =====
lang = st.sidebar.selectbox(
    "🌍 Lang / Sprache",
    ["FR", "DE"]
)

# ===== TRADUCTIONS =====
T = {
    "FR": {
        "title": "📊 Planification des examens",
        "filters": "🔎 Filtres",
        "language": "Langue",
        "class": "Classe",
        "exams": "📋 Examens",
        "classes": "🏫 Classes",
        "languages": "🌍 Langues",
        "teacher": "👨‍🏫 Enseignant",
        "supervisor": "👀 Surveillance",
        "date": "📅 Date",
        "time": "⏰ Heure",
        "no_results": "Aucun résultat"
    },
    "DE": {
        "title": "📊 Prüfungsplanung",
        "filters": "🔎 Filter",
        "language": "Sprache",
        "class": "Klasse",
        "exams": "📋 Prüfungen",
        "classes": "🏫 Klassen",
        "languages": "🌍 Sprachen",
        "teacher": "👨‍🏫 Lehrperson",
        "supervisor": "👀 Aufsicht",
        "date": "📅 Datum",
        "time": "⏰ Zeit",
        "no_results": "Keine Ergebnisse"
    }
}

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    df = pd.read_excel("examens.xlsx")
    df.columns = df.columns.str.strip()
    return df

df = df["Prüfungsdatum"] = pd.to_datetime(df["Prüfungsdatum"]).dt.strftime("%d.%m.%Y")

# ===== TITLE =====
st.title(T[lang]["title"])

# ===== SIDEBAR FILTERS =====
st.sidebar.header(T[lang]["filters"])

# Filtre langue
langues = df["Sprache"].dropna().unique()
selected_langue = st.sidebar.multiselect(
    T[lang]["language"],
    options=langues,
    default=langues
)

# Filtre classe
classes = df["Klasse"].dropna().unique()
selected_classe = st.sidebar.multiselect(
    T[lang]["class"],
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
col1.metric(T[lang]["exams"], len(filtered_df))
col2.metric(T[lang]["classes"], filtered_df["Klasse"].nunique())
col3.metric(T[lang]["languages"], filtered_df["Sprache"].nunique())

st.divider()

# ===== AFFICHAGE VERTICAL =====
if filtered_df.empty:
    st.warning(T[lang]["no_results"])
else:
    for date, group in filtered_df.groupby("Prüfungsdatum"):

        st.header(f"{T[lang]['date']} : {date}")

        for _, row in group.iterrows():
            with st.container(border=True):
                st.subheader(row["Prüfung"])
                st.write(f"{T[lang]['time']} : {row['Prüfungszeit']}")
                st.write(f"{T[lang]['class']} : {row['Klasse']}")
                st.write(f"{T[lang]['teacher']} : {row['Lehrperson der Klasse']}")
                st.write(f"{T[lang]['supervisor']} : {row['Aufsichtsperson']}")
                
                st.badge(row["Sprache"])
