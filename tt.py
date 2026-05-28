import streamlit as st
import pandas as pd
import random
from datetime import datetime

# Apply CSS styling
st.markdown("""
<style>
    body {
        background-color: #f0f2f6;
    }

    .stTextArea, .stNumberInput, .stTimeInput, .stButton {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        cursor: pointer;
    }

    .stButton > button:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)


# Function to generate timetable
def generate_timetable(subjects, periods, num_sections,
                        lab_subjects, start_time,
                        days_in_week, period_duration):

    days = ['Monday', 'Tuesday', 'Wednesday',
            'Thursday', 'Friday', 'Saturday',
            'Sunday'][:days_in_week]

    lab_colors = {
        "ML LAB": "#000080",
        "NSC LAB": "#FFC0CB",
        "WT LAB": "#FFFF00"
    }

    for section in range(1, num_sections + 1):

        available_subjects = [
            subject for subject in subjects
            if subject not in lab_subjects
        ]

        section_subjects = available_subjects.copy()

        # Create empty timetable
        timetable_dict = {
            day: [""] * (periods + 1)
            for day in days
        }

        # Assign labs
        random_days = random.sample(
            days,
            min(len(lab_subjects), len(days))
        )

        for lab, day in zip(lab_subjects, random_days):

            possible_slots = [0, 1]

            if periods >= 7:
                possible_slots.append(5)

            lab_start_period = random.choice(possible_slots)

            timetable_dict[day][
                lab_start_period:lab_start_period + 3
            ] = [lab] * 3

        # Fill timetable
        for day in days:

            day_schedule = timetable_dict[day]
            i = 0

            while i < len(day_schedule):

                # Lunch break
                if i == 4:
                    day_schedule[i] = "Lunch Break"
                    i += 1
                    continue

                # Skip filled slots
                if day_schedule[i] != "":
                    i += 1
                    continue

                # Reload subjects if empty
                if not section_subjects:
                    section_subjects = available_subjects.copy()

                subject = random.choice(section_subjects)
                section_subjects.remove(subject)

                day_schedule[i] = subject
                i += 1

        # Convert to DataFrame
        timetable_df = pd.DataFrame(timetable_dict)

        timetable_df.index = [
            f'Period {i + 1}' if i != 4 else 'Lunch Break'
            for i in range(periods + 1)
        ]

        # Highlight labs
        def highlight_labs(val):

            if val == "Lunch Break":
                return 'background-color: #D3D3D3; font-weight: bold;'

            color = lab_colors.get(val, "")

            return f'background-color: {color}' if color else ""

        styled_df = timetable_df.style.applymap(highlight_labs)

        st.subheader(f"Generated Timetable for Section {section}")

        st.write(styled_df)

        # Download CSV
        csv = timetable_df.to_csv(index=False)

        st.download_button(
            label=f"Download Section {section} Timetable as CSV",
            data=csv,
            file_name=f"timetable_section_{section}.csv",
            mime="text/csv"
        )


# Streamlit Interface
st.title("College Timetable Generator")

subjects_input = st.text_area(
    "Enter Subject Names (comma separated)",
    "ML, BDA, WT, NSC, SS, CBE, LIB, ML LAB, NSC LAB, WT LAB"
)

subjects = [
    subject.strip()
    for subject in subjects_input.split(',')
]

lab_subjects_input = st.text_area(
    "Enter Lab Subjects (comma separated)",
    "ML LAB, NSC LAB, WT LAB"
)

lab_subjects = [
    subject.strip()
    for subject in lab_subjects_input.split(',')
]

periods = st.number_input(
    "Enter Number of Periods",
    min_value=5,
    max_value=10,
    value=7
)

period_duration = st.number_input(
    "Enter Duration of Each Period (minutes)",
    min_value=30,
    max_value=120,
    value=50
)

num_sections = st.number_input(
    "Enter Number of Sections",
    min_value=1,
    max_value=10,
    value=1
)

days_in_week = st.number_input(
    "Enter Number of Working Days",
    min_value=1,
    max_value=7,
    value=6
)

start_time = st.time_input(
    "Enter Start Time",
    datetime(2023, 1, 1, 9, 30).time()
)

st.success("Designed by Manjunatha Reddy")

# Generate button
if st.button("Generate Timetable"):

    generate_timetable(
        subjects,
        periods,
        num_sections,
        lab_subjects,
        start_time,
        days_in_week,
        period_duration
    )

st.success("Designed by Manjunatha Reddy")
