
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    page_icon="🍬",
    layout="wide"
)

st.title("🍬 Nassau Candy Distributor")
st.subheader("Product Line Profitability & Margin Performance Dashboard")

st.markdown(
    "Interactive dashboard for analysing sales, cost, gross profit, "
    "profit margins, products, divisions and regions."
)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_csv("Nassau Candy Distributor.csv")

    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        errors="coerce"
    )

    df["Gross Profit"] = (
        df["Sales"] - df["Cost"]
    )

    df["Profit Margin %"] = np.where(
        df["Sales"] != 0,
        df["Gross Profit"] / df["Sales"] * 100,
        0
    )

    return df


df = load_data()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

# Date filter
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Division filter
divisions = sorted(df["Division"].dropna().unique())

selected_divisions = st.sidebar.multiselect(
    "Division",
    divisions,
    default=divisions
)

# Margin threshold
margin_threshold = st.sidebar.slider(
    "Minimum Profit Margin %",
    min_value=0,
    max_value=100,
    value=0,
    step=5
)

# Product search
product_search = st.sidebar.text_input(
    "Product Search"
)

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

if len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_df = filtered_df[
        (filtered_df["Order Date"] >= start_date)
        &
        (filtered_df["Order Date"] <= end_date)
    ]

if selected_divisions:

    filtered_df = filtered_df[
        filtered_df["Division"].isin(selected_divisions)
    ]

filtered_df = filtered_df[
    filtered_df["Profit Margin %"] >= margin_threshold
]

if product_search:

    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .str.contains(
            product_search,
            case=False,
            na=False
        )
    ]

# =========================================================
# KPI CALCULATIONS
# =========================================================

total_sales = filtered_df["Sales"].sum()
total_cost = filtered_df["Cost"].sum()
total_profit = filtered_df["Gross Profit"].sum()

if total_sales != 0:
    overall_margin = (
        total_profit / total_sales * 100
    )
else:
    overall_margin = 0

total_units = filtered_df["Units"].sum()

# =========================================================
# KPI CARDS
# =========================================================

st.markdown("## 📊 Executive KPIs")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Sales",
    f"${total_sales:,.2f}"
)

col2.metric(
    "Total Cost",
    f"${total_cost:,.2f}"
)

col3.metric(
    "Gross Profit",
    f"${total_profit:,.2f}"
)

col4.metric(
    "Profit Margin",
    f"{overall_margin:.2f}%"
)

col5.metric(
    "Total Units",
    f"{total_units:,.0f}"
)

st.divider()

# =========================================================
# PRODUCT PROFITABILITY
# =========================================================

st.header("1️⃣ Product Profitability Overview")

product_analysis = (
    filtered_df
    .groupby("Product Name")
    .agg(
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum")
    )
    .reset_index()
)

product_analysis["Gross Margin %"] = (
    product_analysis["Gross_Profit"]
    / product_analysis["Sales"] * 100
)

product_analysis["Profit per Unit"] = np.where(
    product_analysis["Units"] != 0,
    product_analysis["Gross_Profit"]
    / product_analysis["Units"],
    0
)

product_analysis = product_analysis.sort_values(
    "Gross_Profit",
    ascending=False
)

col1, col2 = st.columns(2)

with col1:

    fig_product_profit = px.bar(
        product_analysis,
        x="Product Name",
        y="Gross_Profit",
        title="Gross Profit by Product"
    )

    fig_product_profit.update_layout(
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig_product_profit,
        use_container_width=True
    )

with col2:

    margin_data = product_analysis.sort_values(
        "Gross Margin %",
        ascending=False
    )

    fig_margin = px.bar(
        margin_data,
        x="Product Name",
        y="Gross Margin %",
        title="Gross Margin % by Product"
    )

    fig_margin.update_layout(
        xaxis_tickangle=-45
    )

    st.plotly_chart(
        fig_margin,
        use_container_width=True
    )

st.subheader("Product Margin Leaderboard")

st.dataframe(
    product_analysis[
        [
            "Product Name",
            "Sales",
            "Cost",
            "Gross_Profit",
            "Units",
            "Gross Margin %",
            "Profit per Unit"
        ]
    ].round(2),
    use_container_width=True
)

# =========================================================
# DIVISION PERFORMANCE
# =========================================================

st.header("2️⃣ Division Performance")

division_analysis = (
    filtered_df
    .groupby("Division")
    .agg(
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum")
    )
    .reset_index()
)

division_analysis["Profit Margin %"] = (
    division_analysis["Gross_Profit"]
    / division_analysis["Sales"] * 100
)

col1, col2 = st.columns(2)

with col1:

    fig_division = px.bar(
        division_analysis,
        x="Division",
        y=["Sales", "Gross_Profit"],
        barmode="group",
        title="Revenue vs Gross Profit by Division"
    )

    st.plotly_chart(
        fig_division,
        use_container_width=True
    )

with col2:

    fig_division_margin = px.bar(
        division_analysis,
        x="Division",
        y="Profit Margin %",
        title="Profit Margin by Division"
    )

    st.plotly_chart(
        fig_division_margin,
        use_container_width=True
    )

st.dataframe(
    division_analysis.round(2),
    use_container_width=True
)

# =========================================================
# COST VS MARGIN DIAGNOSTICS
# =========================================================

st.header("3️⃣ Cost vs Margin Diagnostics")

cost_margin = (
    filtered_df
    .groupby("Product Name")
    .agg(
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

cost_margin["Profit Margin %"] = (
    cost_margin["Gross_Profit"]
    / cost_margin["Sales"] * 100
)

fig_scatter = px.scatter(
    cost_margin,
    x="Sales",
    y="Cost",
    size="Gross_Profit",
    hover_name="Product Name",
    color="Profit Margin %",
    title="Cost vs Sales by Product"
)

st.plotly_chart(
    fig_scatter,
    use_container_width=True
)

# Margin risk flags

risk_data = cost_margin.copy()

risk_data["Margin Risk"] = np.where(
    risk_data["Profit Margin %"] < 20,
    "High Risk",
    np.where(
        risk_data["Profit Margin %"] < 40,
        "Medium Risk",
        "Low Risk"
    )
)

st.subheader("⚠️ Margin Risk Flags")

st.dataframe(
    risk_data[
        [
            "Product Name",
            "Sales",
            "Cost",
            "Gross_Profit",
            "Profit Margin %",
            "Margin Risk"
        ]
    ].sort_values(
        "Profit Margin %"
    ).round(2),
    use_container_width=True
)

# =========================================================
# PROFIT CONCENTRATION / PARETO
# =========================================================

st.header("4️⃣ Profit Concentration Analysis")

pareto = product_analysis.sort_values(
    "Gross_Profit",
    ascending=False
).copy()

pareto["Cumulative Profit"] = (
    pareto["Gross_Profit"].cumsum()
)

pareto["Cumulative Profit %"] = (
    pareto["Cumulative Profit"]
    / pareto["Gross_Profit"].sum()
    * 100
)

fig_pareto = px.bar(
    pareto,
    x="Product Name",
    y="Gross_Profit",
    title="Product Profit Contribution"
)

fig_pareto.add_scatter(
    x=pareto["Product Name"],
    y=pareto["Cumulative Profit %"],
    mode="lines+markers",
    name="Cumulative Profit %",
    yaxis="y2"
)

fig_pareto.update_layout(
    yaxis2=dict(
        title="Cumulative Profit %",
        overlaying="y",
        side="right"
    ),
    xaxis_tickangle=-45
)

st.plotly_chart(
    fig_pareto,
    use_container_width=True
)

# =========================================================
# REGIONAL PERFORMANCE
# =========================================================

st.header("5️⃣ Regional Performance")

region_analysis = (
    filtered_df
    .groupby("Region")
    .agg(
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

region_analysis["Profit Margin %"] = (
    region_analysis["Gross_Profit"]
    / region_analysis["Sales"] * 100
)

fig_region = px.bar(
    region_analysis,
    x="Region",
    y="Gross_Profit",
    title="Gross Profit by Region"
)

st.plotly_chart(
    fig_region,
    use_container_width=True
)

# =========================================================
# MONTHLY TREND
# =========================================================

st.header("6️⃣ Monthly Sales & Profit Trend")

monthly = (
    filtered_df
    .set_index("Order Date")
    .resample("ME")
    .agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

fig_monthly = px.line(
    monthly,
    x="Order Date",
    y=["Sales", "Gross_Profit"],
    markers=True,
    title="Monthly Sales and Gross Profit"
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)

# =========================================================
# BUSINESS INSIGHTS
# =========================================================

st.header("💡 Key Business Insights")

if len(product_analysis) > 0:

    top_profit_product = product_analysis.iloc[0]

    top_margin_product = product_analysis.loc[
        product_analysis["Gross Margin %"].idxmax()
    ]

    top_region = region_analysis.loc[
        region_analysis["Gross_Profit"].idxmax()
    ]

    top_division = division_analysis.loc[
        division_analysis["Gross_Profit"].idxmax()
    ]

    st.success(
        f"""
        **Top Profit Product:** {top_profit_product['Product Name']}

        **Highest Margin Product:** {top_margin_product['Product Name']}

        **Best Region:** {top_region['Region']}

        **Best Division:** {top_division['Division']}
        """
    )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Nassau Candy Distributor | Product Line Profitability & "
    "Margin Performance Analysis"
)
