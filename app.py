import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import tempfile

# ===== CONFIG =====
st.set_page_config(page_title="Examens", layout="wide")

# ===== HEADER =====
col_logo, col_lang, col_empty = st.columns([1,2,5])

with col_logo:
    st.image("logo.png", width=100)

with col_lang:
    lang = st.selectbox("🌍", ["FR","DE"], label_visibility="collapsed")

# ===== TRAD =====
T = {
"FR":{
"title":"📊 Planification des examens",
"filters":"🔎 Filtres",
"language":"Langue",
"class":"Classe",
"search":"🔎 Recherche",
"reset":"🔄 Réinitialiser",
"export":"📄 Export PDF",
"date":"📅 Date",
"time":"⏰ Heure",
"type":"Type d’examen",
"no_results":"Aucun résultat",
"exams":"📋 Examens",
"classes":"🏫 Classes",
"languages":"🌍 Langues"
},
"DE":{
"title":"📊 Prüfungsplanung",
"filters":"🔎 Filter",
"language":"Sprache",
"class":"Klasse",
"search":"🔎 Suche",
"reset":"🔄 Zurücksetzen",
"export":"📄 PDF Export",
"date":"📅 Datum",
"time":"⏰ Beginn",
"type":"Prüfungsart",
"no_results":"Keine Ergebnisse",
"exams":"📋 Prüfungen",
"classes":"🏫 Klassen",
"languages":"🌍 Sprachen"
}}

st.title(T[lang]["title"])

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    df = pd.read_excel("examens.xlsx")
    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "Prüfung":"Examen",
        "Prüfungsdatum":"Date",
        "Prüfungszeit":"Startzeit",
        "Art der Prüfung":"Typ",
        "Sprache":"Langue"
    })

    df["Date_obj"] = pd.to_datetime(df["Date"])

    return df

df = load_data()

# ===== SIDEBAR =====
st.sidebar.header(T[lang]["filters"])

if st.sidebar.button(T[lang]["reset"]):
    st.session_state.clear()
    st.rerun()

selected_langue = st.sidebar.multiselect(T[lang]["language"], df["Langue"].unique())
selected_classe = st.sidebar.multiselect(T[lang]["class"], df["Klasse"].unique())
search = st.sidebar.text_input(T[lang]["search"])

# ===== FILTER =====
filtered_df = df.copy()

if selected_langue:
    filtered_df = filtered_df[filtered_df["Langue"].isin(selected_langue)]

if selected_classe:
    filtered_df = filtered_df[filtered_df["Klasse"].isin(selected_classe)]

if search:
    filtered_df = filtered_df[
        filtered_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
    ]

filtered_df = filtered_df.sort_values(by=["Date_obj","Startzeit"])

# ===== KPI =====
c1,c2,c3 = st.columns(3)
c1.metric(T[lang]["exams"], len(filtered_df))
c2.metric(T[lang]["classes"], filtered_df["Klasse"].nunique())
c3.metric(T[lang]["languages"], filtered_df["Langue"].nunique())

# ===== FOOTER PDF =====
def add_footer(c, width):
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    c.drawRightString(width-40, 20, f"Généré le {now}")

# ===== PDF FINAL =====
def generate_pdf(data):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp.name, pagesize=A4)

    width, height = A4

    data = data.sort_values(by=["Date_obj","Startzeit"])

    def draw_header():
