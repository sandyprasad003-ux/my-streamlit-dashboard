# entod_current_month_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import base64  # for embedding logo in HTML

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Entod Pharma Dashboard", layout="wide")

# -------------------------------
# Dashboard Title with Logo inside Red Box
# -------------------------------
try:
    with open("logo.png", "rb") as f:
        logo_bytes = f.read()
    logo_base64 = base64.b64encode(logo_bytes).decode()
    st.markdown(
        f"""
        <div style="background-color:#FF0D0D; padding:15px; border-radius:10px; display:flex; align-items:center; justify-content:center;">
            <img src="data:image/png;base64,{logo_base64}" 
                 alt="Company Logo" style="height:50px; margin-right:15px;">
            <h2 style="color:white; margin:0;">Entod Pharma - Current Month to Till Date Dashboard</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
except FileNotFoundError:
    st.markdown(
        """
        <div style="background-color:#FF0D0D; padding:15px; border-radius:10px; text-align:center;">
            <h2 style="color:white; margin:0;">Entod Pharma - Current Month to Till Date Dashboard</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------
# Info / Notification Bar (Moving)
# -------------------------------
st.markdown(
    """
    <marquee behavior="scroll" direction="left" scrollamount="6"
             style="background-color:#FFCCCB; color:black; padding:10px; border-radius:8px; font-size:16px;">
        ⚠️ This Dashboard Is Daily Refreshed at 10 AM and 5 PM. 
        You will be able to extract new updated data only after these times.
    </marquee>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data(file_path):
    if file_path.endswith(("xlsx", "xls")):
        return pd.read_excel(file_path, engine="openpyxl")
    else:
        return pd.read_csv(file_path)

file_path = "ALL_DIVISION_DATA_1ST_SEP_24TH_SEP_25_CBO.xlsx"
df = load_data(file_path)

# Strip spaces
for col in df.select_dtypes(include=["object"]):
    df[col] = df[col].astype(str).str.strip()

# -------------------------------
# Sidebar Metric Selector (Sales Qty or Sales Amt)
# -------------------------------
st.sidebar.header("Select Metric")
metric_options = [col for col in ["Sales Qty", "Sales Amt"] if col in df.columns]
selected_metric = st.sidebar.selectbox("Choose metric:", metric_options)

# -------------------------------
# Sidebar Filters for other columns
# -------------------------------
st.sidebar.header("Filters")
filter_values = {}
for col in df.columns:
    if col not in ["Sales Qty", "Sales Amt"]:
        options = sorted(df[col].dropna().unique())
        options = ["ALL"] + options
        selected = st.sidebar.multiselect(col, options, default=["ALL"])
        if "ALL" not in selected:
            filter_values[col] = selected

# Apply filters
filtered_df = df.copy()
for col, selected in filter_values.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected)]

# -------------------------------
# KPI Section (Selected Metric)
# -------------------------------
st.markdown("<br>", unsafe_allow_html=True)
if selected_metric in filtered_df.columns:
    total_value = round(filtered_df[selected_metric].sum(), 2)
    st.markdown(
        f"""
        <div style="background-color:#FF0D0D; padding:15px; border-radius:10px; text-align:center;">
            <h3 style="color:white; margin:0;">Total {selected_metric}</h3>
            <h2 style="color:white; margin:0;">{total_value}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.error(f"⚠️ '{selected_metric}' column not found in dataset.")

# -------------------------------
# Visualization 1: Top 10 States by Selected Metric
# -------------------------------
if "State Name" in filtered_df.columns and selected_metric in filtered_df.columns:
    st.markdown("<br>", unsafe_allow_html=True)
    state_agg = (
        filtered_df.groupby("State Name")[selected_metric]
        .sum()
        .reset_index()
        .sort_values(selected_metric, ascending=False)
        .head(10)
    )
    st.markdown(
        f"""
        <div style="background-color:#FF0D0D; padding:10px; border-radius:10px; text-align:center;">
            <h3 style="color:white; margin:0;">Top 10 States by {selected_metric}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    fig = px.bar(
        state_agg,
        x="State Name",
        y=selected_metric,
        title="",
        color_discrete_sequence=["#FF0D0D"],
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Visualization 2: Top 10 Divisions by Selected Metric
# -------------------------------
if "Division Name" in filtered_df.columns and selected_metric in filtered_df.columns:
    st.markdown("<br>", unsafe_allow_html=True)
    div_agg = (
        filtered_df.groupby("Division Name")[selected_metric]
        .sum()
        .reset_index()
        .sort_values(selected_metric, ascending=False)
        .head(10)
    )
    st.markdown(
        f"""
        <div style="background-color:#FF0D0D; padding:10px; border-radius:10px; text-align:center;">
            <h3 style="color:white; margin:0;">Top 10 Divisions by {selected_metric}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    fig2 = px.pie(div_agg, values=selected_metric, names="Division Name", hole=0.3)
    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# Filtered Data Table
# -------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="background-color:#FF0D0D; padding:10px; border-radius:10px; text-align:center;">
        <h3 style="color:white; margin:0;">Filtered Data - All Rows</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

# Format numeric columns to 2 decimals
filtered_display = filtered_df.copy()
for col in filtered_display.select_dtypes(include=["number"]).columns:
    filtered_display[col] = filtered_display[col].round(2)

st.dataframe(filtered_display, use_container_width=True, height=400)

csv = filtered_display.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered data as CSV", csv, "filtered.csv", "text/csv")
