# entod_current_month_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Entod Current-Month Dashboard", layout="wide")

# -------------------------------
# Red Box Function for Sections
# -------------------------------
def red_section_box(title):
    st.markdown(
        f"""
        <div style="
            padding: 15px;
            border-radius: 15px;
            background-color: #FF0D0D;
            color: #FFFFFF;
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
            margin-bottom: 10px;
        ">
            {title}
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# Dashboard Title in Red Box
# -------------------------------
st.markdown(
    f"""
    <div style="
        padding: 20px;
        border-radius: 15px;
        background-color: #FF0D0D;
        color: #FFFFFF;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    ">
        📊 Entod Pharma - Current Month Dashboard
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Moving Colored Notification Banner (Marquee)
# -------------------------------
st.markdown(
    """
    <marquee behavior="scroll" direction="left" scrollamount="6">
        <div style="
            padding: 15px;
            border-radius: 10px;
            background-color: #FFCC00;
            color: #000000;
            font-weight: bold;
            font-size: 16px;
            text-align: center;
            width: 100%;
        ">
            ⚠️ This Dashboard is refreshed daily at <b>10 AM</b> and <b>5 PM</b>. 
            You will only see updated data after these times.
        </div>
    </marquee>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Dark/Light Mode Toggle (entire screen)
# -------------------------------
theme_choice = st.sidebar.radio("Choose Theme", ["Light Mode", "Dark Mode"])

if theme_choice == "Dark Mode":
    st.markdown(
        """
        <style>
        .css-1l02zno {background-color: #1E1E1E;}  
        .css-18ni7ap, .css-10trblm, .stButton button {color: #FFFFFF;} 
        .css-1d391kg {background-color: #2E2E2E;}  
        .stDataFrame {background-color: #2E2E2E; color: #FFFFFF;}
        .css-1w3fvcr {background-color: #2E2E2E; color: #FFFFFF;}  
        </style>
        """,
        unsafe_allow_html=True
    )
    bg_color = "#1E1E1E"
    fg_color = "#FFFFFF"
else:
    st.markdown(
        """
        <style>
        .css-1l02zno {background-color: #f0f2f6;}  
        .css-18ni7ap, .css-10trblm, .stButton button {color: #000000;} 
        .css-1d391kg {background-color: #FFFFFF;}  
        .stDataFrame {background-color: #FFFFFF; color: #000000;}
        .css-1w3fvcr {background-color: #FFFFFF; color: #000000;}  
        </style>
        """,
        unsafe_allow_html=True
    )
    bg_color = "#f0f2f6"
    fg_color = "#000000"

# -------------------------------
# Cached file reading
# -------------------------------
@st.cache_data
def read_file(file_path):
    if file_path.endswith(("xlsx", "xls")):
        return pd.read_excel(file_path, engine="openpyxl")
    else:
        return pd.read_csv(file_path)

# -------------------------------
# Load Excel file
# -------------------------------
file_path = "ALL_DIVISION_DATA_1ST_SEP_24TH_SEP_25_CBO.xlsx"
df = read_file(file_path)

# Strip spaces from string columns
for col in df.select_dtypes(include=["object"]):
    df[col] = df[col].astype(str).str.strip()

# Convert object columns to datetime if possible
for col in df.columns:
    if df[col].dtype == object:
        try:
            df[col] = pd.to_datetime(df[col])
        except Exception:
            pass

# -------------------------------
# Sidebar dropdown filters
# -------------------------------
st.sidebar.header("Filters")
filter_values = {}
for col in df.columns:
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        options = sorted(df[col].dt.strftime('%Y-%m-%d').unique())
        options = ["ALL"] + options
        selected = st.sidebar.multiselect(f"{col}", options, default=["ALL"])
        if "ALL" not in selected:
            selected = pd.to_datetime(selected)
        else:
            selected = None
    else:
        options = sorted(df[col].dropna().unique())
        options = ["ALL"] + options
        selected = st.sidebar.multiselect(f"{col}", options, default=["ALL"])
        if "ALL" not in selected:
            selected = selected
        else:
            selected = None
    filter_values[col] = selected

# Apply filters
filtered_df = df.copy()
for col, selected in filter_values.items():
    if selected is not None:
        filtered_df = filtered_df[filtered_df[col].isin(selected)]

# -------------------------------
# KPI Cards (Box Style - Red for all)
# -------------------------------
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
value_col = st.sidebar.selectbox("Value (numeric)", numeric_cols) if numeric_cols else None
group_options = df.select_dtypes(include=["object", "category"]).columns.tolist()
group_col = st.sidebar.selectbox("Group by (categorical)", group_options) if group_options else None

kpi_style = """
<div style="
    padding: 20px;
    margin: 10px;
    border-radius: 15px;
    background-color: {bg};
    color: #FFFFFF;
    text-align: center;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.2);
">
    <h4>{label}</h4>
    <h2>{value}</h2>
</div>
"""

kpi_bg_color = "#FF0D0D"  # Red color for all KPIs

k1, k2, k3 = st.columns(3)
k1.markdown(kpi_style.format(bg=kpi_bg_color, label="Rows", value=len(filtered_df)), unsafe_allow_html=True)
if value_col:
    k2.markdown(kpi_style.format(bg=kpi_bg_color, label=f"Avg {value_col}", value=round(filtered_df[value_col].mean(),2)), unsafe_allow_html=True)
    k3.markdown(kpi_style.format(bg=kpi_bg_color, label=f"Sum {value_col}", value=round(filtered_df[value_col].sum(),2)), unsafe_allow_html=True)

# -------------------------------
# Bar Chart (Top 10 by value)
# -------------------------------
if group_col and value_col:
    red_section_box(f"Top 10 {group_col} by {value_col}")  # Section header
    agg = (
        filtered_df.groupby(group_col)[value_col]
        .sum()
        .reset_index()
        .sort_values(value_col, ascending=False)
        .head(10)
    )
    fig_bar = px.bar(
        agg,
        x=group_col,
        y=value_col,
        text=value_col,
        color_discrete_sequence=["#FF0D0D"]  # Red bars
    )
    fig_bar.update_layout(plot_bgcolor=bg_color, paper_bgcolor=bg_color, font_color=fg_color)
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Select a group and numeric value in the sidebar to see a chart.")

# -------------------------------
# Line Chart (trend over datetime)
# -------------------------------
date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
if date_cols and value_col:
    date_col = st.sidebar.selectbox("Date for trend", date_cols)
    trend_df = filtered_df.groupby(date_col)[value_col].sum().reset_index()
    fig_line = px.line(trend_df, x=date_col, y=value_col, title=f"{value_col} Trend over Time")
    fig_line.update_layout(plot_bgcolor=bg_color, paper_bgcolor=bg_color, font_color=fg_color)
    st.plotly_chart(fig_line, use_container_width=True)

# -------------------------------
# Pie Chart (Top 10 Division Proportion) with Red Box
# -------------------------------
if group_col and value_col:
    red_section_box(f"Top 10 {group_col} Proportion")  # Red box header
    pie_df = filtered_df.groupby(group_col)[value_col].sum().reset_index()
    pie_df = pie_df.sort_values(value_col, ascending=False).head(10)
    fig_pie = px.pie(pie_df, names=group_col, values=value_col, title=f"Top 10 {group_col} Proportion")
    fig_pie.update_traces(textinfo='percent+label')
    fig_pie.update_layout(plot_bgcolor=bg_color, paper_bgcolor=bg_color, font_color=fg_color)
    st.plotly_chart(fig_pie, use_container_width=True)

# -------------------------------
# Filtered Data Table with Red Header & 2 Decimal Places
# -------------------------------
red_section_box("Filtered Data - All Rows")  # Section header

# Format numeric columns to 2 decimals
formatted_df = filtered_df.copy()
for col in formatted_df.select_dtypes(include=["number"]):
    formatted_df[col] = formatted_df[col].map(lambda x: f"{x:.2f}")

# Style header only for performance
styled_df = formatted_df.style.set_table_styles([
    {'selector': 'thead', 'props': [('background-color', '#FF0D0D'), ('color', 'white')]}
])

st.dataframe(styled_df, use_container_width=True, height=500)
st.download_button("Download filtered data as CSV", formatted_df.to_csv(index=False).encode("utf-8"), "filtered.csv", "text/csv")
