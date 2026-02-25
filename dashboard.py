import streamlit as st
import pandas as pd

st.set_page_config(page_title="Digital Marketing Decision Support System", layout="wide")
st.title("Digital Marketing DSS")

st.subheader("Step 1 – Load marketing dataset")

uploaded = st.file_uploader("Upload Marketing-Dataset.xlsx", type=["xlsx"])

if uploaded is not None:
    df = pd.read_excel(uploaded)
    st.write("Preview of data:")
    st.dataframe(df.head())

    # Make sure c_date is a proper date
    if "c_date" in df.columns:
        df["c_date"] = pd.to_datetime(df["c_date"])

    # 1) Compute ROAS and CPA (if columns exist)
    if "revenue" in df.columns and "mark_spent" in df.columns:
        df["ROAS"] = df["revenue"] / df["mark_spent"]

    if "mark_spent" in df.columns and "orders" in df.columns:
        df["CPA"] = df["mark_spent"] / df["orders"]

    # 2) Show ROAS alerts with colors
    st.subheader("ROAS alerts")

    if "ROAS" in df.columns:
        def roas_color(val):
            if val < 1:
                return "background-color: #ffcccc"   # red (bad)
            elif val < 2:
                return "background-color: #fff3cd"   # yellow (medium)
            else:
                return "background-color: #d4edda"   # green (good)

        alert_cols = ["campaign_name", "category", "mark_spent", "revenue", "ROAS"]
        existing_cols = [c for c in alert_cols if c in df.columns]

        styled = df[existing_cols].style.applymap(roas_color, subset=["ROAS"])
        st.dataframe(styled)
    else:
        st.info("ROAS could not be calculated. Check column names.")

    # 3) Campaign Drill-Down
    st.subheader("Campaign drill-down")

    if "campaign_name" in df.columns:
        selected_campaign = st.selectbox(
            "Choose a campaign to inspect:",
            sorted(df["campaign_name"].unique())
        )

        camp_df = df[df["campaign_name"] == selected_campaign]

        st.write("Details for:", selected_campaign)
        st.dataframe(
            camp_df[["c_date", "category", "mark_spent", "revenue", "ROAS"]]
        )

        # Summary metrics
        total_spend = camp_df["mark_spent"].sum()
        total_revenue = camp_df["revenue"].sum()
        avg_roas = camp_df["ROAS"].mean()

        st.metric("Total spend", f"{total_spend:,.0f}")
        st.metric("Total revenue", f"{total_revenue:,.0f}")
        st.metric("Average ROAS", f"{avg_roas:.2f}")

        # 4) ROAS trend over time (7‑day comparison idea)
        st.subheader("ROAS trend over time")

        if "c_date" in camp_df.columns and "ROAS" in camp_df.columns:
            trend = camp_df.sort_values("c_date").set_index("c_date")["ROAS"]
            st.line_chart(trend)
        else:
            st.info("Cannot plot trend – missing c_date or ROAS.")
    else:
        st.info("campaign_name column not found in dataset.")

else:
    st.info("Upload the approved marketing dataset to begin.")
