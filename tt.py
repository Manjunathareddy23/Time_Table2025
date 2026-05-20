import streamlit as st
import pandas as pd
import random
from datetime import datetime
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Timetable Generator",
    page_icon="📚",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

[data-testid="stAppViewContainer"]{
    background: linear-gradient(to right,#dbeafe,#f0f9ff);
}

h1{
    text-align:center;
    color:#1e3a8a;
    font-weight:bold;
}

.stButton>button{
    background-color:#2563eb;
    color:white;
    border-radius:10px;
    height:50px;
    width:100%;
    font-size:18px;
    font-weight:bold;
}

.stButton>button:hover{
    background-color:#1d4ed8;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("📚 Advanced AI Timetable Generator")

# ---------------- COURSE TYPE ----------------
course_type = st.radio(
    "Select Institution Type",
    [
        "High School",
        "Intermediate",
        "B.Tech",
        "Degree",
        "Diploma",
        "ITI",
        "Others"
    ],
    horizontal=True
)

# ---------------- DEFAULT SUBJECTS ----------------
default_subjects = {
    "High School": {
        "Maths": "Ramesh",
        "Science": "Suresh",
        "English": "Kiran",
        "Social": "Mahesh",
        "Hindi": "Naresh",
        "Computer": "Anil"
    },

    "Intermediate": {
        "Maths": "Ramesh",
        "Physics": "Prasad",
        "Chemistry": "Suresh",
        "English": "Kiran"
    },

    "B.Tech": {
        "DBMS": "Ravi",
        "OS": "Suresh",
        "CN": "Naresh",
        "Python": "Kiran",
        "AI LAB": "Lab Faculty 1",
        "DBMS LAB": "Lab Faculty 2"
    },

    "Degree": {
        "Economics": "Ravi",
        "Statistics": "Anil",
        "Accounts": "Mahesh",
        "English": "Kiran"
    },

    "Diploma": {
        "C Programming": "Ramesh",
        "Java": "Naresh",
        "Networks": "Prasad",
        "C LAB": "Lab Faculty"
    },

    "ITI": {
        "Workshop": "Trainer 1",
        "Electrician": "Trainer 2",
        "Practical Lab": "Trainer 3"
    },

    "Others": {
        "Subject1": "Faculty1",
        "Subject2": "Faculty2"
    }
}

subject_teacher_map = default_subjects[course_type]

subjects = list(subject_teacher_map.keys())

# ---------------- SUBJECT WEEKLY LIMITS ----------------
subject_weekly_limits = {}

st.subheader("📘 Weekly Subject Period Limits")

cols = st.columns(3)

i = 0
for subject in subjects:

    with cols[i % 3]:
        subject_weekly_limits[subject] = st.number_input(
            f"{subject}",
            min_value=1,
            max_value=10,
            value=4,
            key=subject
        )

    i += 1

# ---------------- INPUTS ----------------
col1, col2, col3 = st.columns(3)

with col1:
    periods = st.number_input(
        "Periods Per Day",
        min_value=5,
        max_value=10,
        value=7
    )

with col2:
    num_sections = st.number_input(
        "Sections",
        min_value=1,
        max_value=10,
        value=2
    )

with col3:
    days_in_week = st.number_input(
        "Working Days",
        min_value=1,
        max_value=7,
        value=6
    )

# ---------------- DAYS ----------------
days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
][:days_in_week]

# ---------------- GLOBAL TRACKERS ----------------
faculty_schedule = {}
lab_schedule = {}
room_schedule = {}

# ---------------- SLOT CHECK ----------------
def is_slot_available(day, period, teacher, room, lab=None):

    if (day, period, teacher) in faculty_schedule:
        return False

    if (day, period, room) in room_schedule:
        return False

    if lab and (day, period, lab) in lab_schedule:
        return False

    return True

# ---------------- ASSIGN SLOT ----------------
def assign_slot(day, period, teacher, room, lab=None):

    faculty_schedule[(day, period, teacher)] = True

    room_schedule[(day, period, room)] = True

    if lab:
        lab_schedule[(day, period, lab)] = True

# ---------------- PDF EXPORT ----------------
def generate_pdf(section_name, df):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter
    )

    elements = []

    styles = getSampleStyleSheet()

    title = Paragraph(
        f"{section_name} Timetable",
        styles['Title']
    )

    elements.append(title)
    elements.append(Spacer(1, 20))

    data = [["Period"] + list(df.columns)]

    for idx, row in df.iterrows():
        data.append([idx] + list(row.values))

    table = Table(data)

    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
    ])

    table.setStyle(style)

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return buffer

# ---------------- TIMETABLE GENERATOR ----------------
def generate_timetable():

    for section in range(1, num_sections + 1):

        timetable = {}

        subject_counts = {
            sub: 0 for sub in subjects
        }

        for day in days:

            timetable[day] = []

            period = 0

            while period < periods:

                assigned = False

                shuffled_subjects = subjects.copy()
                random.shuffle(shuffled_subjects)

                for subject in shuffled_subjects:

                    limit = subject_weekly_limits[subject]

                    if subject_counts[subject] >= limit:
                        continue

                    teacher = subject_teacher_map[subject]

                    room = f"Room-{section}"

                    # ---------------- LAB LOGIC ----------------
                    if "LAB" in subject.upper():

                        if period + 2 >= periods:
                            continue

                        valid = True

                        for p in range(period, period + 3):

                            if not is_slot_available(
                                day,
                                p,
                                teacher,
                                room,
                                subject
                            ):
                                valid = False
                                break

                        if valid:

                            for p in range(period, period + 3):

                                timetable[day].append(subject)

                                assign_slot(
                                    day,
                                    p,
                                    teacher,
                                    room,
                                    subject
                                )

                            subject_counts[subject] += 3

                            period += 3

                            assigned = True
                            break

                    # ---------------- NORMAL SUBJECT ----------------
                    else:

                        if is_slot_available(
                            day,
                            period,
                            teacher,
                            room
                        ):

                            timetable[day].append(subject)

                            assign_slot(
                                day,
                                period,
                                teacher,
                                room
                            )

                            subject_counts[subject] += 1

                            period += 1

                            assigned = True
                            break

                # ---------------- AUTO RETRY ----------------
                if not assigned:

                    timetable[day].append("FREE")

                    period += 1

        # ---------------- DATAFRAME ----------------
        timetable_df = pd.DataFrame(timetable)

        timetable_df.index = [
            f"Period {i+1}"
            for i in range(periods)
        ]

        # ---------------- STYLE ----------------
        def highlight(val):

            if "LAB" in str(val).upper():
                return 'background-color:#fde68a;font-weight:bold'

            if val == "FREE":
                return 'background-color:#fecaca'

            return ''

        styled_df = timetable_df.style.map(highlight)

        st.subheader(f"📘 Section {section}")

        st.dataframe(
            styled_df,
            use_container_width=True
        )

        # ---------------- CSV DOWNLOAD ----------------
        csv = timetable_df.to_csv().encode('utf-8')

        st.download_button(
            f"⬇ Download CSV Section {section}",
            csv,
            file_name=f"Section_{section}.csv",
            mime="text/csv"
        )

        # ---------------- PDF DOWNLOAD ----------------
        pdf_buffer = generate_pdf(
            f"Section {section}",
            timetable_df
        )

        st.download_button(
            f"⬇ Download PDF Section {section}",
            pdf_buffer,
            file_name=f"Section_{section}.pdf",
            mime="application/pdf"
        )

# ---------------- GENERATE BUTTON ----------------
if st.button("🚀 Generate AI Timetable"):

    try:

        faculty_schedule.clear()
        lab_schedule.clear()
        room_schedule.clear()

        generate_timetable()

        st.success("✅ Collision-Free Timetable Generated Successfully!")

    except Exception as e:

        st.error(f"Error: {e}")

# ---------------- FOOTER ----------------
st.markdown("---")

st.success("Designed By Manjunatha Reddy 🚀")
