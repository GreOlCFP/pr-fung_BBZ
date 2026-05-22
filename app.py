# (⚠️ IMPORTANT : mets ce code dans un fichier propre SANS aucune ligne ```)

import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
import tempfile

st.set_page_config(page_title="Examens", layout="wide")

col_logo, col_lang, _ = st.columns([1,2,5])

with col_logo:
    st.image("logo.png", width=100)

with col_lang:
    lang = st.selectbox("🌍", ["FR","DE"], label_visibility="collapsed")

T = {
"FR":{"title":"📊 Planification des examens","filters":"🔎 Filtres","language":"Langue","class":"Classe","search":"🔎 Recherche","reset":"🔄 Réinitialiser","export":"📄 Export PDF","date":"📅 Date","time":"⏰ Heure","type":"Type d’examen","no_results":"Aucun résultat","exams":"📋 Examens","classes":"🏫 Classes","languages":"🌍 Langues"},
"DE":{"title":"📊 Prüfungsplanung","filters":"🔎 Filter","language":"Sprache","class":"Klasse","search":"🔎 Suche","reset":"🔄 Zurücksetzen","export":"📄 PDF Export","date":"📅 Datum","time":"⏰ Beginn","type":"Prüfungsart","no_results":"Keine Ergebnisse","exams":"📋 Prüfungen","classes":"🏫 Klassen","languages":"🌍 Sprachen"}
}

st.title(T[lang]["title"])

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

st.sidebar.header(T[lang]["filters"])

if st.sidebar.button(T[lang]["reset"]):
    st.session_state.clear()
    st.rerun()

