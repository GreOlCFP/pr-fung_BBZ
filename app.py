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

# ===== LOAD =====
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

    # ✅ TRI SOLIDE
    data = data.sort_values(by=["Date_obj","Startzeit"])

    def draw_header():
        logo_width = 70
        try:
            c.drawImage(
                "logo.png",
                40,
                height - 80,
                width=logo_width,
                preserveAspectRatio=True,
                mask='auto'
            )
        except:
            pass

        c.setFont("Helvetica-Bold", 18)
        c.drawString(120, height - 55, "Planning des examens")

        c.setStrokeColor(colors.grey)
        c.line(40, height - 90, width - 40, height - 90)

        return height - 120

    y = draw_header()

    # ✅ GROUPEMENT CORRECT
    for date_obj, group in data.groupby("Date_obj", sort=True):

        # Nouvelle page si manque de place
        if y < 150:
            add_footer(c, width)
            c.showPage()
            y = draw_header()

        date_str = date_obj.strftime("%d.%m.%Y")

        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.black)
        c.drawString(50, y, date_str)

        y -= 20

        for _, row in group.iterrows():

            card_h = 75

            c.setFillColor(colors.whitesmoke)
            c.roundRect(45, y - card_h, width - 90, card_h, 10, fill=1)

            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(60, y - 20, row["Examen"])

            c.setFont("Helvetica", 9)
            c.setFillColor(colors.darkgray)
            c.drawString(60, y - 35, f"{row['Startzeit']} | {row['Klasse']}")
            c.drawString(60, y - 50, row["Typ"])

            # ===== BADGE LANGUE CENTRÉ =====
            badge_w = 65
            badge_h = 20

            bx = width - 130
            by = y - 40

            color = colors.blue if "fr" in row["Langue"].lower() else colors.orange

            c.setFillColor(color)
            c.roundRect(bx, by, badge_w, badge_h, 8, fill=1)

            # ✅ centrage parfait
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 9)

            cx = bx + badge_w / 2
            cy = by + badge_h / 2 - 3

            c.drawCentredString(cx, cy, row["Langue"])

            y -= 90

    add_footer(c, width)
    c.save()
    return tmp.name

# ===== EXPORT =====
if not filtered_df.empty:
    pdf = generate_pdf(filtered_df)
    with open(pdf, "rb") as f:
        st.download_button(T[lang]["export"], f, "planning_examens.pdf")

st.divider()

# ===== UI =====
def get_color(langue):
    return "blue" if "fr" in langue.lower() else "orange"

if filtered_df.empty:
    st.warning(T[lang]["no_results"])
else:
    for date_obj, group in filtered_df.groupby("Date_obj"):
        st.header(f"{T[lang]['date']} : {date_obj.strftime('%d.%m.%Y')}")

        for _, row in group.iterrows():
            color = get_color(row["Langue"])

            with st.container(border=True):
                st.subheader(row["Examen"])
                st.write(f"{T[lang]['time']} : {row['Startzeit']}")
                st.write(f"{T[lang]['class']} : {row['Klasse']}")
                st.write(f"{T[lang]['type']} : {row['Typ']}")

                st.markdown(
                    f"<span style='background-color:{color};color:white;padding:4px 8px;border-radius:6px'>{row['Langue']}</span>",
                    unsafe_allow_html=True
                )
