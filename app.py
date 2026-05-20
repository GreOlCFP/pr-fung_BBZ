import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
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
"teacher":"👨‍🏫 Enseignant",
"supervisor":"👀 Surveillance",
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
"time":"⏰ Zeit",
"teacher":"👨‍🏫 Lehrperson",
"supervisor":"👀 Aufsicht",
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
        "Prüfungszeit":"Heure",
        "Lehrperson der Klasse":"Enseignant",
        "Aufsichtsperson":"Surveillance",
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

# ✅ TRI GARANTI
filtered_df = filtered_df.sort_values(by=["Date_obj","Heure"])

# ===== KPI =====
c1,c2,c3 = st.columns(3)
c1.metric(T[lang]["exams"], len(filtered_df))
c2.metric(T[lang]["classes"], filtered_df["Klasse"].nunique())
c3.metric(T[lang]["languages"], filtered_df["Langue"].nunique())

# ===== PDF ULTRA DESIGN =====
def generate_pdf(data):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp.name, pagesize=A4)

    width, height = A4
    y = height - 60

    # TRI ABSOLU
    data = data.sort_values(by=["Date_obj", "Heure"])

    # LOGO
    try:
        c.drawImage(
            "logo.png",
            40, height - 85,
            width=70,
            height=40,
            preserveAspectRatio=True,
            mask='auto'
        )
    except:
        pass

    # TITRE
    c.setFont("Helvetica-Bold", 18)
    c.drawString(120, height - 55, "Planning des examens")

    c.setStrokeColor(colors.grey)
    c.line(40, height - 70, width - 40, height - 70)

    y -= 50

    # CONTENU PAR DATE
    for date_obj, group in data.groupby("Date_obj", sort=True):

        date_str = date_obj.strftime("%d.%m.%Y")

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.black)
        c.drawString(50, y, date_str)

        y -= 20

        for _, row in group.iterrows():

            # CARTE
            card_height = 75
            c.setFillColor(colors.whitesmoke)
            c.roundRect(45, y - card_height, width - 90, card_height, 10, fill=1)

            # TEXTE
            c.setFillColor(colors.black)

            c.setFont("Helvetica-Bold", 11)
            c.drawString(60, y - 20, row["Examen"])

            c.setFont("Helvetica", 9)
            c.setFillColor(colors.darkgray)
            c.drawString(60, y - 35, f"{row['Heure']}  |  {row['Klasse']}")
            c.drawString(60, y - 48, row["Enseignant"])
            c.drawString(60, y - 60, row["Surveillance"])

            # BADGE LANGUE CENTRÉ
            badge_w = 65
            badge_h = 20
            bx = width - 130
            by = y - 40

            color = colors.blue if "fr" in row["Langue"].lower() else colors.orange

            c.setFillColor(color)
            c.roundRect(bx, by, badge_w, badge_h, 6, fill=1)

            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 9)

            cx = bx + badge_w / 2
            cy = by + badge_h / 2 - 3

            c.drawCentredString(cx, cy, row["Langue"])

            y -= 90

            if y < 100:
                c.showPage()
                y = height - 60

    c.save()
    return tmp.name

# ===== EXPORT =====
if not filtered_df.empty:
    pdf = generate_pdf(filtered_df)
    with open(pdf, "rb") as f:
        st.download_button(T[lang]["export"], f, "planning_examens.pdf")

st.divider()

# ===== COULEURS UI =====
def get_color(langue):
    return "blue" if "fr" in langue.lower() else "orange"

# ===== AFFICHAGE =====
if filtered_df.empty:
    st.warning(T[lang]["no_results"])
else:
    for date_obj, group in filtered_df.groupby("Date_obj"):
        date_str = date_obj.strftime("%d.%m.%Y")

        st.header(f"{T[lang]['date']} : {date_str}")

        for _, row in group.iterrows():
            color = get_color(row["Langue"])

            with st.container(border=True):
                st.subheader(row["Examen"])
                st.write(f"{T[lang]['time']} : {row['Heure']}")
                st.write(f"{T[lang]['class']} : {row['Klasse']}")
                st.write(f"{T[lang]['teacher']} : {row['Enseignant']}")
                st.write(f"{T[lang]['supervisor']} : {row['Surveillance']}")

                st.markdown(
                    f"<span style='background-color:{color};color:white;padding:4px 8px;border-radius:6px'>{row['Langue']}</span>",
                    unsafe_allow_html=True
                )
