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
col_logo, col_lang, _ = st.columns([1, 2, 5])

with col_logo:
    st.image("logo.png", width=100)

with col_lang:
    lang = st.selectbox("🌍", ["FR", "DE"], label_visibility="collapsed")

# ===== TRAD =====
T = {
    "FR": {
        "title": "📊 Planification des examens",
        "filters": "🔎 Filtres",
        "language": "Langue",
        "class": "Classe",
        "search": "🔎 Recherche",
        "reset": "🔄 Réinitialiser",
        "export": "📄 Export PDF",
        "date": "📅 Date",
        "time": "⏰ Heure",
        "type": "Type d’examen",
        "no_results": "Aucun résultat",
    },
    "DE": {
        "title": "📊 Prüfungsplanung",
        "filters": "🔎 Filter",
        "language": "Sprache",
        "class": "Klasse",
        "search": "🔎 Suche",
        "reset": "🔄 Zurücksetzen",
        "export": "📄 PDF Export",
        "date": "📅 Datum",
        "time": "⏰ Beginn",
        "type": "Prüfungsart",
        "no_results": "Keine Ergebnisse",
    },
}

st.title(T[lang]["title"])

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    df = pd.read_excel("examens.xlsx")
    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "Prüfung": "Examen",
        "Prüfungsdatum": "Date",
        "Prüfungszeit": "Startzeit",
        "Art der Prüfung": "Typ",
        "Sprache": "Langue",
    })

    df["Date_obj"] = pd.to_datetime(df["Date"], errors="coerce")

    # ✅ CORRECTION MAJEURE (évite dates dupliquées)
    df["Date_only"] = df["Date_obj"].dt.date

    return df

df = load_data()

# ===== SIDEBAR =====
st.sidebar.header(T[lang]["filters"])

if st.sidebar.button(T[lang]["reset"]):
    st.session_state.clear()
    st.rerun()

selected_langue = st.sidebar.multiselect(
    T[lang]["language"], sorted(df["Langue"].dropna().unique())
)

selected_classe = st.sidebar.multiselect(
    T[lang]["class"], sorted(df["Klasse"].dropna().unique())
)

search = st.sidebar.text_input(T[lang]["search"])

# ===== FILTRAGE =====
filtered_df = df.copy()

if selected_langue:
    filtered_df = filtered_df[filtered_df["Langue"].astype(str).isin(selected_langue)]

if selected_classe:
    filtered_df = filtered_df[filtered_df["Klasse"].astype(str).isin(selected_classe)]

if search:
    filtered_df = filtered_df[
        filtered_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
    ]

filtered_df = filtered_df.sort_values(by=["Date_obj", "Startzeit"])

# ===== PDF =====
def generate_pdf(data):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(tmp.name, pagesize=A4)

    width, height = A4

    # ✅ CONSTANTES DESIGN
    TOP = height - 110
    BOTTOM = 80
    BLOCK = 100
    DATE_SPACE = 30

    data = data.sort_values(by=["Date_obj", "Startzeit"])

    def draw_header():
        try:
            c.drawImage("logo.png", 40, height - 70, width=70, preserveAspectRatio=True)
        except:
            pass

        c.setFont("Helvetica-Bold", 18)
        c.drawString(120, height - 55, "Planning des examens")
        c.line(40, height - 85, width - 40, height - 85)

        return TOP

    def footer():
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        now = datetime.now().strftime("%d.%m.%Y %H:%M")
        c.drawRightString(width - 40, 20, f"Généré le {now}")

    # ✅ ICÔNE CALENDRIER PROPRE
    def draw_calendar_icon(x, y):
        c.setFillColor(colors.darkblue)
        c.roundRect(x, y - 6, 12, 10, 2, fill=1)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(x + 6, y - 2, "D")

    y = draw_header()

    # ✅ GROUPBY CORRECT
    for date_obj, group in data.groupby("Date_only", sort=True):

        date_str = pd.to_datetime(date_obj).strftime("%d.%m.%Y")

        if y < BOTTOM + DATE_SPACE:
            footer()
            c.showPage()
            y = draw_header()

        # ✅ DESSIN DATE
        draw_calendar_icon(50, y)

        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(70, y, date_str)

        y -= DATE_SPACE

        for _, row in group.iterrows():

            if y - BLOCK < BOTTOM:
                footer()
                c.showPage()
                y = draw_header()

                draw_calendar_icon(50, y)
                c.setFont("Helvetica-Bold", 13)
                c.drawString(70, y, date_str)
                y -= DATE_SPACE

            # CARTE
            c.setFillColor(colors.whitesmoke)
            c.roundRect(45, y - 75, width - 90, 75, 10, fill=1)

            # TEXTE
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(60, y - 20, row["Examen"])

            c.setFont("Helvetica", 9)
            c.setFillColor(colors.darkgray)
            c.drawString(60, y - 35, f"{row['Startzeit']} | {row['Klasse']}")
            c.drawString(60, y - 50, row["Typ"])

            # BADGE LANGUE
            bx, by = width - 130, y - 40
            color = colors.blue if "fr" in str(row["Langue"]).lower() else colors.orange

            c.setFillColor(color)
            c.roundRect(bx, by, 65, 20, 8, fill=1)

            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 9)
            c.drawCentredString(bx + 32.5, by + 7, row["Langue"])

            y -= BLOCK

    footer()
    c.save()
    return tmp.name


# ===== EXPORT =====
if not filtered_df.empty:
    pdf = generate_pdf(filtered_df)
    with open(pdf, "rb") as f:
        st.download_button(T[lang]["export"], f, "planning_examens.pdf")

st.divider()

# ===== AFFICHAGE =====
if filtered_df.empty:
    st.warning(T[lang]["no_results"])
else:
    for date_obj, group in filtered_df.groupby("Date_only", sort=True):

        st.header(f"{T[lang]['date']} : {pd.to_datetime(date_obj).strftime('%d.%m.%Y')}")

        for _, row in group.iterrows():

            color = "blue" if "fr" in str(row["Langue"]).lower() else "orange"

            with st.container(border=True):
                st.subheader(row["Examen"])
                st.write(f"{T[lang]['time']} : {row['Startzeit']}")
                st.write(f"{T[lang]['class']} : {row['Klasse']}")
                st.write(f"{T[lang]['type']} : {row['Typ']}")

                st.markdown(
                    f"<span style='background-color:{color};color:white;padding:4px 8px;border-radius:6px'>{row['Langue']}</span>",
                    unsafe_allow_html=True
                )
