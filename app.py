# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="One-Screen Dashboard", layout="wide")
st.title("One-Screen Dashboard (Excel → interactive)")

MAX_UNIQUE = 100  # max unique values per dropdown

# --- Cached file reading ---
@st.cache_data
def read_file(file_path):
    if file_path.endswith(("xlsx", "xls")):
        return pd.read_excel(file_path, engine="openpyxl")
    else:
        return pd.read_csv(file_path)

# --- Fixed Excel file path ---
file_path = "ALL_DIVISION_DATA_1ST_SEP_24TH_SEP_25_CBO.xlsx"
df = read_file(file_path)

# Convert object columns to datetime if possible
for col in df.columns:
    if df[col].dtype == object:
        try:
            df[col] = pd.to_datetime(df[col])
        except Exception:
            pass

# --- Sidebar dropdown filters for all columns with 'ALL' option ---
st.sidebar.header("Filters (Dropdowns)")
filter_values = {}
for col in df.columns:
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        options = sorted(df[col].dt.strftime('%Y-%m-%d').unique())[:MAX_UNIQUE]
        options = ["ALL"] + options
        selected = st.sidebar.multiselect(f"{col}", options, default=["ALL"])
        if "ALL" not in selected:
            selected = pd.to_datetime(selected)
        else:
            selected = None  # No filtering if ALL
    else:
        options = sorted(df[col].dropna().unique())[:MAX_UNIQUE]
        options = ["ALL"] + options
        selected = st.sidebar.multiselect(f"{col}", options, default=["ALL"])
        if "ALL" not in selected:
            selected = selected
        else:
            selected = None  # No filtering if ALL
    filter_values[col] = selected

# Apply filters to get filtered dataframe
filtered_df = df.copy()
for col, selected in filter_values.items():
    if selected is not None:
        filtered_df = filtered_df[filtered_df[col].isin(selected)]

# --- KPIs ---
numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
value_col = st.sidebar.selectbox("Value (numeric)", numeric_cols) if numeric_cols else None
group_options = df.select_dtypes(include=["object", "category"]).columns.tolist()
group_col = st.sidebar.selectbox("Group by (categorical)", group_options) if group_options else None

k1, k2, k3 = st.columns(3)
k1.metric("Rows", len(filtered_df))
if value_col:
    k2.metric(f"Avg {value_col}", round(filtered_df[value_col].mean(), 2))
    k3.metric(f"Sum {value_col}", round(filtered_df[value_col].sum(), 2))

# --- Chart: top 10 by value ---
if group_col and value_col:
    agg = (
        filtered_df.groupby(group_col)[value_col]
        .sum()
        .reset_index()
        .sort_values(value_col, ascending=False)
        .head(10)
    )
    fig = px.bar(agg, x=group_col, y=value_col, title=f"Top 10 {group_col} by {value_col}")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Select a group and numeric value in the sidebar to see a chart.")

# --- Table and download (show all rows) ---
st.subheader("Data (filtered) - All rows from Excel")
st.dataframe(filtered_df, use_container_width=True)

csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered data as CSV", csv, "filtered.csv", "text/csv")
