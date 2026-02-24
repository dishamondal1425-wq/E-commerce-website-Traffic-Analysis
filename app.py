import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================================================
# PAGE SETTINGS
# =========================================================
st.set_page_config(layout="wide")

st.markdown("""
<style>

/* ===== App Background ===== */
.stApp {
    background: linear-gradient(135deg, #eef2f7, #dfe6f1);
    color: #000000 !important;   /* TEXT COLOR CHANGED TO BLACK */
}

/* ===== Container Spacing (FULL WIDTH ENABLED) ===== */
.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100% !important;   /* FULL SCREEN WIDTH */
}

/* ===== Main Title ===== */
.main-title {
    text-align: center;
    font-size: 46px;
    font-weight: 900;
    margin-bottom: 15px;
    color: #000000;   /* BLACK FONT */
}

/* ===== Subtitle ===== */
.subtitle {
    text-align: center;
    font-size: 20px;
    color: #000000;   /* BLACK FONT */
    margin-bottom: 50px;
}

/* ===== Section Headers ===== */
h2 {
    font-size: 32px !important;
    font-weight: 800 !important;
    margin-top: 30px !important;
    color: #000000 !important;
}

/* ===== Sub Headers ===== */
h3 {
    font-size: 24px !important;
    font-weight: 700 !important;
    color: #000000 !important;
}

/* ===== KPI Cards ===== */
div[data-testid="metric-container"] {
    padding: 35px;
    border-radius: 16px;
    background-color: white;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.06);
    transition: 0.3s ease;
    color: #000000 !important;   /* BLACK TEXT */
}

div[data-testid="metric-container"] > div {
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #000000 !important;
}

div[data-testid="metric-container"] label {
    font-size: 18px !important;
    font-weight: 600 !important;
    color: #000000 !important;
}

div[data-testid="metric-container"]:hover {
    transform: translateY(-8px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
    color: #000000 !important;
}

/* ===== General Text ===== */
p, span, label, div {
    color: #000000 !important;
}

</style>
""", unsafe_allow_html=True)



# =========================================================
# TITLE
# =========================================================
st.markdown('<div class="main-title">📊 E-commerce Website Traffic Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analyze website traffic, user behavior and revenue performance</div>', unsafe_allow_html=True)

# ================= LOAD DATA =================

@st.cache_data
def load_data():
    oct_data = pd.read_csv("2019-Oct.csv").sample(200000)
    nov_data = pd.read_csv("2019-Nov.csv").sample(200000)

    df = pd.concat([oct_data, nov_data], ignore_index=True)

    df['event_time'] = pd.to_datetime(df['event_time'])
    df['hour'] = df['event_time'].dt.hour
    df['day'] = df['event_time'].dt.day_name()

    return df

df = load_data()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Advanced Filter Options")

event_filter = st.sidebar.multiselect(
    "Select Event Type",
    options=df['event_type'].unique(),
    default=df['event_type'].unique()
)

filtered_df = df[df['event_type'].isin(event_filter)]

min_date = df["event_time"].min().date()
max_date = df["event_time"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df["event_time"].dt.date >= start_date) &
        (filtered_df["event_time"].dt.date <= end_date)
    ]

selected_hours = st.sidebar.slider("Select Hour Range", 0, 23, (0, 23))
filtered_df = filtered_df[
    (filtered_df["hour"] >= selected_hours[0]) &
    (filtered_df["hour"] <= selected_hours[1])
]

category_filter = st.sidebar.multiselect(
    "Select Product Category",
    options=df["category_code"].dropna().unique(),
    default=df["category_code"].dropna().unique()
)

filtered_df = filtered_df[
    filtered_df["category_code"].isin(category_filter)
]

min_price = float(df["price"].min())
max_price = float(df["price"].max())

price_range = st.sidebar.slider(
    "Select Price Range",
    min_price,
    max_price,
    (min_price, max_price)
)

filtered_df = filtered_df[
    (filtered_df["price"] >= price_range[0]) &
    (filtered_df["price"] <= price_range[1])
]

top_n = st.sidebar.slider("Show Top N Categories", 5, 20, 10)

# =========================================================
# KPIs
# =========================================================

st.markdown("## 📊 Key Performance Indicators")

total_events = len(filtered_df)
total_users = filtered_df["user_id"].nunique()
purchase_df = filtered_df[filtered_df["event_type"] == "purchase"]
total_revenue = purchase_df["price"].sum()

views = len(filtered_df[filtered_df["event_type"] == "view"])
purchases = len(filtered_df[filtered_df["event_type"] == "purchase"])
conversion_rate = (purchases / views * 100) if views > 0 else 0

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Events", f"{total_events:,}")
col2.metric("Unique Users", f"{total_users:,}")
col3.metric("Conversion Rate", f"{conversion_rate:.2f}%")
col4.metric("Revenue", f"${total_revenue:,.2f}")

st.markdown("<hr>", unsafe_allow_html=True)

# =========================================================
# TRAFFIC ANALYSIS
# =========================================================

st.markdown("## 📈 Website Traffic Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Visits by Hour")
    hourly = filtered_df.groupby("hour").size()
    fig, ax = plt.subplots()
    hourly.plot(kind="bar", ax=ax)
    st.pyplot(fig)

with col2:
    st.subheader("Visits by Day")
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    daily = filtered_df.groupby("day").size().reindex(day_order)
    fig, ax = plt.subplots()
    daily.plot(kind="bar", ax=ax)
    st.pyplot(fig)

# ===== Dynamic Traffic Insight =====
if not filtered_df.empty and not hourly.empty and not daily.empty:
    peak_hour = hourly.idxmax()
    low_hour = hourly.idxmin()
    peak_day = daily.idxmax()
    low_day = daily.idxmin()

    st.info(f"""
 **Traffic Performance Summary**

• Highest Traffic Hour: **{peak_hour}:00**  
• Lowest Traffic Hour: **{low_hour}:00**  
• Highest Traffic Day: **{peak_day}**  
• Lowest Traffic Day: **{low_day}**

📊 Recommendation: Allocate advertising budget and promotional campaigns 
during peak hours and high-performing days to maximize engagement.
""")

st.markdown("<hr>", unsafe_allow_html=True)

# =========================================================
# USER BEHAVIOR
# =========================================================

st.markdown("## 🧍 User Behavior Analysis")

behavior = filtered_df['event_type'].value_counts()
fig, ax = plt.subplots()
sns.barplot(x=behavior.index, y=behavior.values, ax=ax)
st.pyplot(fig)

# ===== Dynamic Behavior Insight =====
if not behavior.empty:
    most_action = behavior.idxmax()
    least_action = behavior.idxmin()

    st.info(f"""
 **User Behavior Summary**

• Most Common Action: **{most_action}**  
• Least Common Action: **{least_action}**

📊 Recommendation: Improve the journey from {most_action} 
to purchase through better UI, offers, and call-to-action optimization.
""")

st.markdown("<hr>", unsafe_allow_html=True)

# =========================================================
# CONVERSION FUNNEL
# =========================================================

st.markdown("## 💰 Conversion Funnel")

cart = len(filtered_df[filtered_df['event_type']=="cart"])
purchase = len(filtered_df[filtered_df['event_type']=="purchase"])

conversion_data = pd.DataFrame({
    "Stage":["View","Cart","Purchase"],
    "Users":[views,cart,purchase]
})

fig, ax = plt.subplots(figsize=(10,7))

sns.barplot(data=conversion_data, x="Stage", y="Users", ax=ax)
st.pyplot(fig)

# ===== Dynamic Funnel Insight =====
if views > 0:
    cart_rate = (cart/views)*100
    purchase_rate = (purchase/views)*100
else:
    cart_rate = purchase_rate = 0

st.info(f"""
 **Conversion Performance Summary**

• View → Cart Rate: **{cart_rate:.2f}%**  
• View → Purchase Rate: **{purchase_rate:.2f}%**

📊 Recommendation: Optimize checkout experience and reduce friction 
to improve final purchase conversions.
""")

st.markdown("<hr>", unsafe_allow_html=True)

# =========================================================
# TOP CATEGORIES
# =========================================================

st.markdown("## 🛍️ Top Product Categories")

top_categories = filtered_df['category_code'].value_counts().head(top_n)

fig, ax = plt.subplots(figsize=(8,5))
top_categories.plot(kind="barh", ax=ax)
st.pyplot(fig)

# ===== Dynamic Category Insight =====
if not top_categories.empty:
    best_cat = top_categories.idxmax()
    worst_cat = top_categories.idxmin()

    st.info(f"""
📌 **Category Performance Summary**

• Top Performing Category: **{best_cat}**  
• Lowest Performing (within top {top_n}): **{worst_cat}**

📊 Recommendation: Scale promotions for high-performing categories 
and reevaluate pricing or marketing for lower-performing ones.
""")

st.markdown("<hr>", unsafe_allow_html=True)