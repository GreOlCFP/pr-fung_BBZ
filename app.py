import streamlit as st
import pandas as pd

# ===== CONFIG =====
st.set_page_config(page_title="Examens", layout="wide")

# ===== HEADER =====
col_logo, col_lang, col_empty = st.columns([1, 2, 5])

with col_logo:
    st.image("logo.png", width=100)

# ✅ Selectbox largeur adaptée
with col_lang:
    lang = st.selectbox(
        "🌍",
        ["FR", "DE"],
        label_visibility="collapsed"
    )

# ===== TRADUCTIONS =====
T = {
    "FR": {
        "title": "📊 Planification des examens",
        "filters": "🔎 Filtres",
        "language": "Langue",
        "class": "Classe",
        "search": "🔎 Recherche",
        "reset": "🔄 Réinitialiser",
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
        "search": "🔎 Suche",
        "reset": "🔄 Zurücksetzen",
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

st.title(T[lang]["title"])

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    df = pd.read_excel("examens.xlsx")
    df.columns = df.columns.str.strip()
    df["Prüfungsdatum"] = pd.to_datetime(df["Prüfungsdatum"]).dt.strftime("%d.%m.%Y")
    return df

df = load_data()

# ===== SIDEBAR =====
st.sidebar.header(T[lang]["filters"])

# ✅ Reset bouton
if st.sidebar.button(T[lang]["reset"]):
    st.session_state.clear()
    st.rerun()

# ===== FILTRES =====
langues = df["Sprache"].dropna().unique()
selected_langue = st.sidebar.multiselect(
    T[lang]["language"],
    options=langues,
    key="lang_filter"
)

classes = df["Klasse"].dropna().unique()
selected_classe = st.sidebar.multiselect(
    T[lang]["class"],
    options=classes,
    key="class_filter"
)

# ✅ Recherche rapide
search = st.sidebar.text_input(T[lang]["search"])

# ===== FILTRAGE =====
filtered_df = df.copy()

if selected_langue:
    filtered_df = filtered_df[filtered_df["Sprache"].isin(selected_langue)]

if selected_classe:
    filtered_df = filtered_df[filtered_df["Klasse"].isin(selected_classe)]

# ✅ Recherche globale
if search:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(),
            axis=1
        )
    ]

# ✅ TRI
filtered_df = filtered_df.sort_values(by=["Prüfungsdatum", "Prüfungszeit"])

# ===== KPI =====
col1, col2, col3 = st.columns(3)
col1.metric(T[lang]["exams"], len(filtered_df))
col2.metric(T[lang]["classes"], filtered_df["Klasse"].nunique())
col3.metric(T[lang]["languages"], filtered_df["Sprache"].nunique())

st.divider()

# ===== AFFICHAGE =====
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
