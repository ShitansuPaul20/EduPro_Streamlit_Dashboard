"""
EduPro — Instructor Performance and Course Quality Evaluation Dashboard
Run with: streamlit run app.py
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_style('whitegrid')
st.set_page_config(page_title="EduPro Instructor Performance Dashboard", layout="wide", page_icon="📊")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# -------------------------------------------------------------------
# DATA LOADING (bundled files, with manual-upload fallback)
# -------------------------------------------------------------------
def _read(name, uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


@st.cache_data
def build_dataset(teachers_raw, courses_raw, trans_raw):
    teachers = teachers_raw.copy()
    courses = courses_raw.copy()
    trans = trans_raw.copy()

    tmap = trans[['TeacherID', 'CourseID']].drop_duplicates().merge(
        courses[['CourseID', 'CourseRating', 'CourseCategory', 'CourseLevel']], on='CourseID'
    )

    avg_course_rating_taught = tmap.groupby('TeacherID')['CourseRating'].mean().rename('AvgCourseRatingTaught')
    course_rating_std = tmap.groupby('TeacherID')['CourseRating'].std().fillna(0).rename('CourseRatingStd')
    enrollments = trans.groupby('TeacherID').size().rename('Enrollments')

    teachers_full = teachers.merge(avg_course_rating_taught, on='TeacherID', how='left') \
                             .merge(course_rating_std, on='TeacherID', how='left') \
                             .merge(enrollments, on='TeacherID', how='left')
    teachers_full['Enrollments'] = teachers_full['Enrollments'].fillna(0)
    teachers_full['AvgCourseRatingTaught'] = teachers_full['AvgCourseRatingTaught'].fillna(0)

    max_std = courses['CourseRating'].std()
    teachers_full['ConsistencyScore'] = (1 - (teachers_full['CourseRatingStd'] / (2 * max_std)).clip(0, 1)) * 100

    course_enrollments = trans.groupby('CourseID').size().rename('Enrollments')
    courses_full = courses.merge(course_enrollments, on='CourseID', how='left')
    courses_full['Enrollments'] = courses_full['Enrollments'].fillna(0)

    return teachers_full, courses_full


st.sidebar.title("📁 Data")
use_own = st.sidebar.checkbox("Upload my own CSV files instead of bundled data", value=False)

teachers_up = courses_up = trans_up = None
if use_own:
    teachers_up = st.sidebar.file_uploader("Teachers.csv", type="csv")
    courses_up = st.sidebar.file_uploader("Courses.csv", type="csv")
    trans_up = st.sidebar.file_uploader("Transactions.csv", type="csv")

teachers_raw = _read("Teachers.csv", teachers_up)
courses_raw = _read("Courses.csv", courses_up)
trans_raw = _read("Transactions.csv", trans_up)

if teachers_raw is None or courses_raw is None or trans_raw is None:
    st.warning("⚠️ Data files not found. Please place Teachers.csv, Courses.csv and Transactions.csv "
               "inside a `data/` folder next to app.py, or upload them from the sidebar.")
    st.stop()

teachers_full, courses_full = build_dataset(teachers_raw, courses_raw, trans_raw)
trans = trans_raw

# -------------------------------------------------------------------
# SIDEBAR — FILTERS
# -------------------------------------------------------------------
st.sidebar.title("🔍 Filters")

expertise_options = sorted(teachers_full['Expertise'].unique())
selected_expertise = st.sidebar.multiselect("Instructor Expertise", expertise_options, default=expertise_options)

category_options = sorted(courses_full['CourseCategory'].unique())
selected_category = st.sidebar.multiselect("Course Category", category_options, default=category_options)

level_options = sorted(courses_full['CourseLevel'].unique())
selected_level = st.sidebar.multiselect("Course Level", level_options, default=level_options)

r_min = float(np.floor(teachers_full['TeacherRating'].min()))
r_max = float(np.ceil(teachers_full['TeacherRating'].max()))
rating_range = st.sidebar.slider("Teacher Rating Range", r_min, r_max, (r_min, r_max), step=0.1)

f_teachers = teachers_full[
    (teachers_full['Expertise'].isin(selected_expertise)) &
    (teachers_full['TeacherRating'] >= rating_range[0]) &
    (teachers_full['TeacherRating'] <= rating_range[1])
]
f_courses = courses_full[
    (courses_full['CourseCategory'].isin(selected_category)) &
    (courses_full['CourseLevel'].isin(selected_level))
]

if f_teachers.empty or f_courses.empty:
    st.error("No data matches the selected filters. Please widen your filter selection.")
    st.stop()

# -------------------------------------------------------------------
# HEADER + KPIs
# -------------------------------------------------------------------
st.title("📊 EduPro — Instructor Performance & Course Quality Dashboard")
st.caption("Data-driven evaluation of instructor effectiveness and course quality")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Avg Teacher Rating", f"{f_teachers['TeacherRating'].mean():.2f} / 5")
k2.metric("Avg Course Rating", f"{f_courses['CourseRating'].mean():.2f} / 5")
k3.metric("Rating Consistency Index", f"{f_teachers['ConsistencyScore'].mean():.1f} / 100")

exp_corr = f_teachers['YearsOfExperience'].corr(f_teachers['TeacherRating'])
k4.metric("Experience Impact Score", f"{exp_corr:.3f}" if pd.notna(exp_corr) else "N/A")

q1, q2 = teachers_full['TeacherRating'].quantile([0.33, 0.66])
def tier(r):
    return 'Low' if r <= q1 else ('Mid' if r <= q2 else 'High')
tf = f_teachers.copy()
tf['RatingTier'] = tf['TeacherRating'].apply(tier)
tier_enroll = tf.groupby('RatingTier')['Enrollments'].mean()
low_val = tier_enroll.get('Low', np.nan)
ratio = (tier_enroll.get('High', np.nan) / low_val) if low_val and not np.isnan(low_val) and low_val > 0 else np.nan
k5.metric("Enrollment Influence Ratio", f"{ratio:.2f}x" if pd.notna(ratio) else "N/A")

st.divider()

# -------------------------------------------------------------------
# TABS — CORE MODULES
# -------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 Instructor Leaderboard",
    "📈 Experience vs Rating",
    "🔥 Course Quality Heatmap",
    "🧩 Expertise Comparison",
    "🎯 Instructor Impact"
])

with tab1:
    st.subheader("Instructor Performance Leaderboard")
    max_n = max(5, min(30, len(f_teachers)))
    n = st.slider("Number of instructors to show", 5, max_n, min(10, max_n))
    sort_order = st.radio("Sort by", ["Top rated", "Bottom rated"], horizontal=True)
    lb = f_teachers.sort_values('TeacherRating', ascending=(sort_order == "Bottom rated")).head(n)

    fig, ax = plt.subplots(figsize=(9, max(3, n * 0.35)))
    color = '#55A868' if sort_order == "Top rated" else '#C44E52'
    ax.barh(lb['TeacherName'], lb['TeacherRating'], color=color)
    ax.set_xlim(0, 5)
    ax.set_xlabel("Teacher Rating")
    ax.invert_yaxis()
    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(
        lb[['TeacherName', 'Expertise', 'YearsOfExperience', 'TeacherRating',
            'AvgCourseRatingTaught', 'Enrollments', 'ConsistencyScore']]
        .round(2).reset_index(drop=True),
        use_container_width=True
    )

with tab2:
    st.subheader("Experience vs Rating Scatter Plots")
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.regplot(data=f_teachers, x='YearsOfExperience', y='TeacherRating',
                    scatter_kws={'alpha': 0.6, 'color': '#4C72B0'}, line_kws={'color': 'red'}, ax=ax)
        ax.set_title("Experience vs Teacher Rating")
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.regplot(data=f_teachers, x='YearsOfExperience', y='AvgCourseRatingTaught',
                    scatter_kws={'alpha': 0.6, 'color': '#55A868'}, line_kws={'color': 'red'}, ax=ax)
        ax.set_title("Experience vs Avg Course Rating Taught")
        st.pyplot(fig)
        plt.close(fig)

    c1 = f_teachers['YearsOfExperience'].corr(f_teachers['TeacherRating'])
    c2 = f_teachers['YearsOfExperience'].corr(f_teachers['AvgCourseRatingTaught'])
    st.info(f"Correlation (Experience, Teacher Rating): **{c1:.3f}**  |  "
            f"Correlation (Experience, Course Rating): **{c2:.3f}**")

with tab3:
    st.subheader("Course Quality Heatmap — Category vs Level")
    pivot = f_courses.pivot_table(index='CourseCategory', columns='CourseLevel',
                                   values='CourseRating', aggfunc='mean')
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt='.2f', cmap='YlGnBu', linewidths=0.5, ax=ax)
    st.pyplot(fig)
    plt.close(fig)

with tab4:
    st.subheader("Expertise-wise Performance Comparison")
    exp_summary = f_teachers.groupby('Expertise').agg(
        AvgTeacherRating=('TeacherRating', 'mean'),
        AvgCourseRating=('AvgCourseRatingTaught', 'mean'),
        NumTeachers=('TeacherID', 'count'),
        TotalEnrollments=('Enrollments', 'sum')
    ).round(2).sort_values('AvgTeacherRating', ascending=False)

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(exp_summary))
    w = 0.38
    ax.bar(x - w/2, exp_summary['AvgTeacherRating'], width=w, label='Avg Teacher Rating', color='#4C72B0')
    ax.bar(x + w/2, exp_summary['AvgCourseRating'], width=w, label='Avg Course Rating', color='#DD8452')
    ax.set_xticks(x)
    ax.set_xticklabels(exp_summary.index, rotation=45, ha='right')
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(exp_summary, use_container_width=True)

with tab5:
    st.subheader("Instructor Rating Tier vs Course Success")
    tier_summary = tf.groupby('RatingTier').agg(
        AvgCourseRating=('AvgCourseRatingTaught', 'mean'),
        TotalEnrollments=('Enrollments', 'sum'),
        AvgEnrollmentsPerTeacher=('Enrollments', 'mean'),
        NumTeachers=('TeacherID', 'count')
    ).round(2).reindex(['Low', 'Mid', 'High'])

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(5.5, 4.5))
        sns.barplot(x=tier_summary.index, y=tier_summary['AvgCourseRating'],
                    palette=['#C44E52', '#CCB974', '#55A868'], ax=ax)
        ax.set_title("Avg Course Rating by Tier")
        st.pyplot(fig)
        plt.close(fig)
    with col2:
        fig, ax = plt.subplots(figsize=(5.5, 4.5))
        sns.barplot(x=tier_summary.index, y=tier_summary['AvgEnrollmentsPerTeacher'],
                    palette=['#C44E52', '#CCB974', '#55A868'], ax=ax)
        ax.set_title("Avg Enrollments per Teacher by Tier")
        st.pyplot(fig)
        plt.close(fig)

    st.dataframe(tier_summary, use_container_width=True)

st.divider()
st.caption("EduPro Instructor Performance & Course Quality Evaluation | Built with Streamlit")
