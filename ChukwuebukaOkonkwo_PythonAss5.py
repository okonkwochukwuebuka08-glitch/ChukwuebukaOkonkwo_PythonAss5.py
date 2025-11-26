import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np  # included for requirements.txt consistency

st.set_page_config(page_title="Juice & Smoothie Sales Dashboard", layout="wide")

st.title("Juice & Smoothie Sales Analytics Dashboard")
st.write(
    """
    **BUIS 305 / INSS 405 – Module 5 (Streamlit & Python)**  
    Upload the provided juice sales dataset to explore category performance, sales over time,
    and customer service satisfaction.
    """
)

# ---- FILE UPLOADER ----
uploaded_file = st.file_uploader(
    "Upload the Juice Sales dataset (CSV or Excel file)",
    type=["csv", "xlsx"]
)

def detect_column(df, candidates):
    """
    Try to find a matching column name from a list of candidate names.
    Returns the first match or None if no match is found.
    """
    cols_lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None

if uploaded_file is not None:
    # Read the uploaded file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("File uploaded successfully!")

    st.subheader("Preview of the Dataset")
    st.write("First 5 rows:")
    st.dataframe(df.head())
    st.write("Last 5 rows:")
    st.dataframe(df.tail())

    # ---- DETECT IMPORTANT COLUMNS ----
    # Adjust these candidate names if your dataset uses slightly different labels
    category_col = detect_column(df, ["Category", "Product Category"])
    sales_col = detect_column(df, ["$ Sales", "Sales ($)", "Sales", "Total Sales"])
    date_col = detect_column(df, ["Date Ordered", "Order Date"])
    satisfaction_col = detect_column(df, ["Service Satisfaction Rating", "Satisfaction Rating"])

    if category_col is None:
        st.warning("⚠ Could not automatically detect the **Category** column. "
                   "Please rename it to 'Category' in the dataset if needed.")
    if sales_col is None:
        st.warning("⚠ Could not automatically detect the **Sales** column. "
                   "Please rename it to '$ Sales' or 'Sales' in the dataset if needed.")
    if date_col is None:
        st.warning("⚠ Could not automatically detect the **Date Ordered** column. "
                   "Please rename it to 'Date Ordered' in the dataset if needed.")
    if satisfaction_col is None:
        st.warning("⚠ Could not automatically detect the **Service Satisfaction Rating** column. "
                   "Please rename it to 'Service Satisfaction Rating' in the dataset if needed.")

    # ---- TABS FOR BONUS QUESTION ----
    tab1, tab2, tab3 = st.tabs(["Category Sales", "Sales Over Time", "Satisfaction Ratings"])

    # ============= TAB 1: CATEGORY SALES COMPARISON =============
    with tab1:
        st.subheader("Question 1: Compare Sales Performance – Juices vs Smoothies")

        if category_col is not None and sales_col is not None:
            # Group by category and sum sales
            category_sales = (
                df.groupby(category_col)[sales_col]
                .sum()
                .sort_values(ascending=False)
            )

            fig, ax = plt.subplots()
            ax.bar(category_sales.index, category_sales.values)
            ax.set_title("Total Sales by Category")
            ax.set_xlabel("Product Category")
            ax.set_ylabel("Total Sales ($)")
            plt.xticks(rotation=0)

            st.pyplot(fig)

            # Interpretation text
            if not category_sales.empty:
                top_category = category_sales.idxmax()
                top_value = category_sales.max()
                total_sales = category_sales.sum()
                if total_sales > 0:
                    top_pct = (top_value / total_sales) * 100
                else:
                    top_pct = 0

                st.markdown("**Brief Interpretation**")
                st.write(
                    f"- The category **{top_category}** generates the highest revenue, "
                    f"contributing approximately **{top_pct:.1f}%** of total sales.\n"
                    f"- This suggests that customers spend more money on **{top_category}** "
                    "compared to the other category.\n"
                    "- Management could prioritize promotions, inventory, and marketing around "
                    f"**{top_category}** while exploring why the other category is underperforming."
                )
            else:
                st.info("No sales data found after grouping by category.")
        else:
            st.error(
                "Unable to create the category comparison chart because the required columns "
                "were not found. Please check that your dataset has 'Category' and '$ Sales' "
                "or 'Sales' columns."
            )

    # ============= TAB 2: SALES OVER TIME (TIME SERIES) =============
    with tab2:
        st.subheader("Question 2: Sales Over Timeline (Daily Sales Trends)")

        if date_col is not None and sales_col is not None:
            df_time = df.copy()

            # Convert date column to datetime
            df_time[date_col] = pd.to_datetime(df_time[date_col], errors="coerce")

            # Drop rows where the date failed to convert
            df_time = df_time.dropna(subset=[date_col])

            # Group by date and sum sales
            daily_sales = (
                df_time.groupby(date_col)[sales_col]
                .sum()
                .sort_index()
            )

            if not daily_sales.empty:
                fig2, ax2 = plt.subplots()
                ax2.plot(daily_sales.index, daily_sales.values, marker="o")
                ax2.set_title("Daily Sales Over Time")
                ax2.set_xlabel("Date Ordered")
                ax2.set_ylabel("Total Sales ($)")
                plt.xticks(rotation=45)
                plt.tight_layout()

                st.pyplot(fig2)

                st.markdown("**Brief Interpretation**")

                # Basic interpretation: find peaks and overall trend
                max_date = daily_sales.idxmax()
                max_value = daily_sales.max()
                st.write(
                    f"- The highest daily sales occurred on **{max_date.date()}**, "
                    f"with total sales of approximately **${max_value:,.2f}**.\n"
                    "- The chart helps identify busy days, potential promotion effects, or "
                    "seasonal patterns.\n"
                    "- Management can use this to schedule staffing, plan inventory, and "
                    "target marketing campaigns around high-demand periods."
                )
            else:
                st.info("No valid daily sales data after processing the dates.")
        else:
            st.error(
                "Unable to create the time-series chart because the required columns "
                "('Date Ordered' and 'Sales') were not found."
            )

    # ============= TAB 3: SERVICE SATISFACTION DISTRIBUTION =============
    with tab3:
        st.subheader("Question 3: Service Satisfaction Rating Distribution")

        if satisfaction_col is not None:
            ratings = df[satisfaction_col].dropna()

            if not ratings.empty:
                # Count each rating (e.g., 1–5)
                rating_counts = ratings.value_counts().sort_index()

                fig3, ax3 = plt.subplots()
                ax3.bar(rating_counts.index.astype(str), rating_counts.values)
                ax3.set_title("Service Satisfaction Rating Distribution")
                ax3.set_xlabel("Rating Score")
                ax3.set_ylabel("Number of Customers")

                st.pyplot(fig3)

                most_common_rating = rating_counts.idxmax()
                st.markdown("**Brief Interpretation**")
                st.write(
                    f"- The most common service satisfaction score is **{most_common_rating}**.\n"
                    "- A higher concentration of ratings at the top end (e.g., 4–5) indicates "
                    "good customer experience and service quality.\n"
                    "- If there are many low ratings (1–2), management should investigate "
                    "pain points such as waiting times, staff behavior, or product quality.\n"
                    "- This chart supports decisions on staff training, process improvement, "
                    "and customer service policies."
                )
            else:
                st.info("No non-missing satisfaction ratings available in the dataset.")
        else:
            st.error(
                "Unable to plot satisfaction distribution because the column "
                "'Service Satisfaction Rating' (or similar) was not found."
            )

else:
    st.info("👆 Please upload the juice sales dataset to begin the analysis.")
