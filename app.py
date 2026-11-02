import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page settings
st.set_page_config(
    page_title="Flood Risk Analysis",
    page_icon="🌊",
    layout="wide"
)

# Green dashboard styling
st.markdown("""
<style>
.stApp {
    background-color: #F4F8F6;
}
[data-testid="stSidebar"] {
    background-color: #E1EEE8;
}
h1 {
    color: #174D3A;
}
h2, h3 {
    color: #236B4D;
}
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #C8DED2;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# Load datasets
odisha = pd.read_csv("dataset/river_discharge_tele_hr_cwc_od_1970_2025.csv")
sikkim = pd.read_csv("dataset/river_discharge_tele_hr_cwc_sk_1970_2025.csv")
uttarakhand = pd.read_csv("dataset/river_discharge_tele_hr_cwc_uk_1970_2025.csv")
west_bengal = pd.read_csv("dataset/river_discharge_tele_hr_cwc_wb_1970_2025.csv")

# Combine datasets
df = pd.concat(
    [odisha, sikkim, uttarakhand, west_bengal],
    ignore_index=True
)

# Data cleaning
q_col = "Telemetry Hourly River Water Discharge (m3/sec)"

df["Data Acquisition Time"] = pd.to_datetime(
    df["Data Acquisition Time"],
    errors="coerce",
    dayfirst=True
)

df[q_col] = pd.to_numeric(df[q_col], errors="coerce")

df = df.dropna(
    subset=["Data Acquisition Time", "State", "Station", q_col]
)

df = df.drop_duplicates()
df = df[df[q_col] >= 0]

df["State_Station"] = (
    df["State"].astype(str) + "_" + df["Station"].astype(str)
)

df = df.sort_values(
    ["State_Station", "Data Acquisition Time"]
)

df = df.reset_index(drop=True)

# Sidebar
st.sidebar.title("Flood Monitoring")
st.sidebar.write("Select a state to analyse")

state_option = st.sidebar.selectbox(
    "Choose State",
    ["All States"] + sorted(df["State"].unique().tolist())
)

# Filter dataset
if state_option == "All States":
    df_view = df
else:
    df_view = df[df["State"] == state_option]

# Dashboard heading
st.title("Flood Risk Analysis Dashboard")
st.write("River Discharge Monitoring and Analysis")
st.write("Data Source: Central Water Commission (CWC), India")

# KPI cards
st.subheader("Dataset Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Records", df_view.shape[0])
col2.metric("Total Stations", df_view["Station"].nunique())
col3.metric("Average Discharge", round(df_view[q_col].mean(), 2))

# Dataset preview
st.subheader("Dataset Preview")
st.dataframe(df_view.head())

# State-wise record count
st.subheader("River Discharge Records by State")

state_count = df["State"].value_counts()

fig1, ax1 = plt.subplots(figsize=(9, 4))

sns.barplot(
    x=state_count.index,
    y=state_count.values,
    ax=ax1,
    color="#398765"
)

ax1.set_xlabel("State")
ax1.set_ylabel("Number of Records")
ax1.set_title("State-wise Record Count")

plt.xticks(rotation=30)
plt.tight_layout()

st.pyplot(fig1)
plt.close(fig1)

# Discharge distribution
st.subheader("Distribution of River Discharge")

fig2, ax2 = plt.subplots(figsize=(9, 4))

sns.histplot(
    data=df_view,
    x=q_col,
    bins=50,
    ax=ax2,
    color="#398765"
)

ax2.set_xlabel("River Discharge (m3/sec)")
ax2.set_ylabel("Frequency")
ax2.set_title("River Discharge Distribution")

plt.tight_layout()

st.pyplot(fig2)
plt.close(fig2)

# Discharge comparison
st.subheader("Discharge Comparison Across States")

fig3, ax3 = plt.subplots(figsize=(9, 4))

sns.boxplot(
    data=df_view,
    x="State",
    y=q_col,
    ax=ax3,
    color="#75B798",
    showfliers=False
)

ax3.set_xlabel("State")
ax3.set_ylabel("River Discharge (m3/sec)")
ax3.set_title("River Discharge Across States")

plt.xticks(rotation=30)
plt.tight_layout()

st.pyplot(fig3)
plt.close(fig3)

# Monthly average discharge
st.subheader("Monthly Average River Discharge")

df_view["Month"] = df_view["Data Acquisition Time"].dt.month

monthly = (
    df_view.groupby(["Month", "State"])[q_col]
    .mean()
    .reset_index()
)

fig4, ax4 = plt.subplots(figsize=(10, 4))

sns.lineplot(
    data=monthly,
    x="Month",
    y=q_col,
    hue="State",
    marker="o",
    ax=ax4
)

ax4.set_xlabel("Month")
ax4.set_ylabel("Average Discharge (m3/sec)")
ax4.set_title("Monthly Average River Discharge")

ax4.set_xticks(range(1, 13))
plt.tight_layout()

st.pyplot(fig4)
plt.close(fig4)

# Project note
st.subheader("Important Note")

st.info(
    "Low, Moderate and High risk categories in this project are "
    "discharge-based proxy categories. They are not official flood warnings."
)

st.caption(
    "Academic project | River Discharge Telemetry Data | CWC, India"
)
