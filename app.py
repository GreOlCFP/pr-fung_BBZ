import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile

# ===== CONFIG =====
st.set_page_config(page_title="Examens", layout="wide")

# ===== HEADER =====
col_logo, col_lang, col_empty = st.columns([1, 2, 5])

with col_logo:
    st.image("logo.png", width=100)

with col_lang:
    lang = st.selectbox("🌍", ["FR", "DE"], label_visibility="collapsed")

# ===== TRADUCTIONS =====
T = {
    "FR": {
        "title": "📊 Planification des examens",
        "filters": "🔎 Filtres",
        "language": "Langue",
        "class": "Classe",
        "search": "🔎 Recherche",
        "reset": "🔄 Réinitialiser",
        "export": "📄 Export PDF",
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
        "export": "📄 PDF Export",
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
    df.columns = df.columns.str.strip().str.replace("\xa0", "")

    df = df.rename(columns={
        "Prüfung": "Examen",
        "Prüfungsdatum": "Date",
        "Prüfungszeit": "Heure",
        "Lehrperson der Klasse": "Enseignant",
        "Aufsichtsperson": "Surveillance",
        "Sprache": "Langue"
    })

    df["Date_obj"] = pd.to_datetime(df["Date"])
    df["Date"] = df["Date_obj"].dt.strftime("%d.%m.%Y")

    return df

df = load_data()

# ===== SIDEBAR =====
st.sidebar.header(T[lang]["filters"])

if st.sidebar.button(T[lang]["reset"]):
    st.session_state.clear()
    st.rerun()

langues = df["Langue"].dropna().unique()
selected_langue = st.sidebar.multiselect(T[lang]["language"], langues)

classes = df["Klasse"].dropna().unique()
selected_classe = st.sidebar.multiselect(T[lang]["class"], classes)

search = st.sidebar.text_input(T[lang]["search"])

# ===== FILTRAGE =====
filtered_df = df.copy()

if selected_langue:
    filtered_df = filtered_df[filtered_df["Langue"].isin(selected_langue)]

if selected_classe:
    filtered_df = filtered_df[filtered_df["Klasse"].isin(selected_classe)]

if search:
    filtered_df = filtered_df[
        filtered_df.apply(
            lambda row: row.astype(str).str.contains(search, case=False).any(),
            axis=1
        )
    ]

filtered_df = filtered_df.sort_values(by=["Date_obj", "Heure"])

# ===== KPI =====
col1, col2, col3 = st.columns(3)
col1.metric(T[lang]["exams"], len(filtered_df))
col2.metric(T[lang]["classes"], filtered_df["Klasse"].nunique())
col3.metric(T[lang]["languages"], filtered_df["Langue"].nunique())

# ===== PDF EXPORT =====
def generate_pdf(data):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp.name, pagesize=A4)

    y = 800
    for date, group in data.groupby("Date"):
        c.drawString(50, y, f"{date}")
        y -= 20

        for _, row in group.iterrows():
            text = f"{row['Heure']} | {row['Klasse']} | {row['Examen']} | {row['Langue']}"
            c.drawString(70, y, text)
            y -= 15

            if y < 50:
                c.showPage()
                y = 800

        y -= 10

    c.save()
    return tmp.name

if not filtered_df.empty:
    pdf_file = generate_pdf(filtered_df)
    with open(pdf_file, "rb") as f:
        st.download_button(
            label=T[lang]["export"],
            data=f,
            file_name="planning_examens.pdf",
            mime="application/pdf"
        )

st.divider()

# ===== COULEURS =====
def get_color(langue):
    if "fr" in langue.lower():
        return "blue"
    else:
        return "orange"

# ===== AFFICHAGE =====
if filtered_df.empty:
    st.warning(T[lang]["no_results"])
else:
    for date, group in filtered_df.groupby("Date"):
        st.header(f"{T[lang]['date']} : {date}")

        for _, row in group.iterrows():
            color = get_color(row["Langue"])

            with st.container(border=True):
                st.subheader(row["Examen"])
                st.write(f"{T[lang]['time']} : {row['Heure']}")
                st.write(f"{T[lang]['class']} : {row['Klasse']}")
                st.write(f"{T[lang]['teacher']} : {row['Enseignant']}")
                st.write(f"{T[lang]['supervisor']} : {row['Surveillance']}")

                st.markdown(
                    f"<span style='background-color:{color}; color:white; padding:4px 8px; border-radius:6px'>{row['Langue']}</span>",
                    unsafe_allow_html=True
                )
