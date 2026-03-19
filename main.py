import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Store Sales Dashboard")

# Upload
file = st.file_uploader("Upload your dataset (.csv)", type=["csv"])

if file:
    # Auto-detect delimiter
    df = pd.read_csv(file, sep=None, engine="python")

    st.subheader("📄 Raw Data Preview")
    st.dataframe(df.head())

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w_]", "", regex=True)
    )

    st.write("Detected columns:", list(df.columns))

    required_columns = {
        "store", "date", "weekly_sales",
        "holiday_flag", "temperature",
        "fuel_price", "cpi", "unemployment"
    }

    if not required_columns.issubset(df.columns):
        st.error(f"Dataset must contain: {required_columns}")
        st.stop()

    # Convert types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["weekly_sales"] = pd.to_numeric(df["weekly_sales"], errors="coerce")
    df["holiday_flag"] = pd.to_numeric(df["holiday_flag"], errors="coerce")
    df["unemployment"] = pd.to_numeric(df["unemployment"], errors="coerce")

    df = df.dropna()

    # KPIs
    total_sales = df["weekly_sales"].sum()
    avg_sales = df["weekly_sales"].mean()
    total_stores = df["store"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${total_sales:,.2f}")
    col2.metric("Average Weekly Sales", f"${avg_sales:,.2f}")
    col3.metric("Total Stores", total_stores)

    # Top 3 stores
    top3 = (
        df.groupby("store")["weekly_sales"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
        .reset_index()
    )

    st.subheader("🏆 Top 3 Stores by Sales")
    st.dataframe(top3)

    # 🎯 STRATEGIC ANALYSIS (FOCUS ON PROFIT IMPROVEMENT)

    st.subheader("💡 Profit Optimization Insights")

    median_sales = df["weekly_sales"].median()

    def strategy(row):
        if row["weekly_sales"] > median_sales and row["holiday_flag"] == 1:
            return "🔥 Invest More (High Sales + Holiday)"
        elif row["weekly_sales"] > median_sales:
            return "⚖️ Maintain (Consistent Sales)"
        else:
            return "❌ Improve (Low Performance)"

    df["strategy"] = df.apply(strategy, axis=1)

    strategy_counts = df["strategy"].value_counts().reset_index()
    strategy_counts.columns = ["strategy", "count"]

    # Pie chart
    fig_pie = px.pie(
        strategy_counts,
        names="strategy",
        values="count",
        title="Sales Strategy Distribution"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

    # Optional: show filtered actionable data
    st.subheader("📌 Actionable Data")
    st.dataframe(
        df[["store", "date", "weekly_sales", "holiday_flag", "strategy"]])
