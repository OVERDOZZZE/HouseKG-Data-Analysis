import streamlit as st
import os
import sys
import pandas as pd
import re
import time
from pathlib import Path
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interface.dashboards import (
    price_distribution_dashboard,
    district_distribution_dashboard,
    region_avg_price_dashboard,
    plot_area_distribution_dashboard,
    communication_access_dashboard,
    bishkek_district_avg_price_dashboard,
    offer_type_distribution_dashboard
)
from parser_module.main import Builder

st.set_page_config(page_title='HouseKG Scraper', layout='wide')

def delete_file_after_delay(filepath, delay):
    time.sleep(delay)
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"Deleted {filepath}")

tab1, tab2, tab3 = st.tabs(["Main Page", "Dashboards Page", "Dynamic Parsing Page"])

with tab1:
    st.title("🏠 HouseKG Parser Interface")
    st.markdown("""
    ### Welcome to the HouseKG Parser UI
    This application allows you to:
    - 📊 Visualize dashboards of previously scraped real estate data
    - ⚙️ Dynamically scrape new data from [house.kg](https://house.kg) by selecting property type, page range, and number of threads

    **Technologies used:** `Streamlit`, `Pandas`, `Plotly`, `ThreadPoolExecutor`

    **Usage instructions:**
    1. Use **Dashboards Page** to explore data already scraped
    2. Use **Dynamic Parsing Page** to start live scraping of fresh data
    """)

with tab2:
    st.title("📊 Dashboards for Real Estate")
    property_type = st.selectbox("Select Property Type for Dashboard", ["sector", "private_house"], key="dashboard_property")
    file_path = f"data/sale_{property_type}.csv"

    if not os.path.exists(file_path):
        st.warning(f"No data found for {property_type}. Please scrape it first.")
    else:
        df = pd.read_csv(file_path)
        st.success(f"Loaded {len(df)} rows from {file_path}")

        if 'Цена' in df.columns:
            df['Цена (int)'] = (
                df['Цена']
                .astype(str)
                .str.replace('$', '', regex=False)
                .str.replace(' ', '', regex=False)
                .str.replace(',', '', regex=False)
                .str.extract(r'(\d+)')[0]
                .dropna()
                .astype(float)
            )
        if 'Площадь участка' in df.columns:
            df['Площадь (сотки)'] = df['Площадь участка'].str.extract(r'(\d+\.?\d*)').astype(float)

        view_type = st.selectbox("Select View Type", ["Visualizations", "Data Tables"], key="view_type")

        if view_type == "Visualizations":
            st.subheader("💰 Price Distribution")
            fig1 = price_distribution_dashboard(df)
            st.plotly_chart(fig1, use_container_width=True, key="price_dist")

            st.subheader("🗺️ Distribution of Listings by Districts of Bishkek")
            fig2 = district_distribution_dashboard(df)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True, key="district_dist")
            else:
                st.info("No district data available for Bishkek.")

            st.subheader("🌍 Average Price by Regions")
            fig3 = region_avg_price_dashboard(df)
            st.plotly_chart(fig3, use_container_width=True, key="region_avg_price")

            st.subheader("🏙️ Average Price by Districts in Bishkek")
            fig_top, fig_all = bishkek_district_avg_price_dashboard(df)
            if fig_top:
                st.plotly_chart(fig_top, use_container_width=True, key="bishkek_avg_price_top")
                with st.expander("Show all districts"):
                    st.plotly_chart(fig_all, use_container_width=True, key="bishkek_avg_price_all")
            else:
                st.info("No district data available for Bishkek.")

            st.subheader("📐 Plot Area Distribution")
            fig4 = plot_area_distribution_dashboard(df)
            if fig4:
                st.plotly_chart(fig4, use_container_width=True, key="plot_area_top")
                with st.expander("Show all plot areas"):
                    fig4_full = plot_area_distribution_dashboard(df, top_n=None)
                    st.plotly_chart(fig4_full, use_container_width=True, key="plot_area_full")

            st.subheader("🔌 Communication Access")
            fig5 = communication_access_dashboard(df)
            if fig5:
                st.plotly_chart(fig5, use_container_width=True, key="communication_access")

            st.subheader("📊 Distribution of Listings by Offer Type")
            fig_offer_type = offer_type_distribution_dashboard(df)
            st.plotly_chart(fig_offer_type, use_container_width=True, key="offer_type_dist")

        elif view_type == "Data Tables":
            st.subheader("📋 Data Tables")
            display_columns = ['Название', 'Область', 'Город/Село', 'Район', 'Цена', 'Площадь участка']

            st.write("### 10 Most Expensive Sectors")
            most_expensive = df.nlargest(10, 'Цена (int)')[display_columns]
            st.dataframe(most_expensive)

            st.write("### 10 Cheapest Sectors")
            cheapest = df.nsmallest(10, 'Цена (int)')[display_columns]
            st.dataframe(cheapest)

            if 'Площадь (сотки)' in df.columns:
                st.write("### 10 Largest Sectors")
                largest = df.nlargest(10, 'Площадь (сотки)')[display_columns]
                st.dataframe(largest)

                st.write("### 10 Smallest Sectors")
                smallest = df.nsmallest(10, 'Площадь (сотки)')[display_columns]
                st.dataframe(smallest)
            else:
                st.info("Area data not available for this property type.")

with tab3:
    st.title("⚙️ Dynamic Data Parsing")
    property_type = st.selectbox('Select property type:', ['sector', 'private_house'], key="parsing_property")
    deal = st.selectbox('Select deal type:', ['sale', 'rent'], key="deal_type")
    start_page = st.slider('Start page', min_value=1, max_value=1000, value=1, key="start_page")
    stop_page = st.slider('Stop page', min_value=start_page + 1, max_value=start_page + 20, value=start_page + 1, key="stop_page")
    threads = st.slider('Select number of threads', min_value=1, max_value=20, value=10, key="threads")

    if st.button('Start Live Scraping', key="scrape_button"):
        timestamp = int(time.time())
        unique_output_path = f"data/temp_{deal}_{property_type}_{timestamp}.csv"

        builder = Builder(property_type=property_type, start_page=start_page, stop_page=stop_page, deal=deal, output_path=unique_output_path)
        runner = builder.build()

        runner.parser.cache_lifetime = 0 

        st.info('⏳ Scraping started...')
        duration = runner.run()
        st.success(f'Scraping finished in {duration} seconds.')

        df = pd.read_csv(unique_output_path)
        if 'Цена' in df.columns:
            df['Цена (int)'] = (
                df['Цена']
                .astype(str)
                .str.replace('$', '', regex=False)
                .str.replace(' ', '', regex=False)
                .str.replace(',', '', regex=False)
                .str.extract(r'(\d+)')[0]
                .dropna()
                .astype(float)
            )
        if 'Площадь участка' in df.columns:
            df['Площадь (сотки)'] = df['Площадь участка'].str.extract(r'(\d+\.?\d*)').astype(float)

        st.subheader("💰 Price Distribution")
        fig1 = price_distribution_dashboard(df)
        st.plotly_chart(fig1, use_container_width=True, key="live_price_dist")

        st.subheader("🗺️ Distribution of Listings by Districts of Bishkek")
        fig2 = district_distribution_dashboard(df)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True, key="live_district_dist")
        else:
            st.info("No district data available for Bishkek.")

        st.subheader("🌍 Average Price by Regions")
        fig3 = region_avg_price_dashboard(df)
        st.plotly_chart(fig3, use_container_width=True, key="live_region_avg_price")

        st.subheader("🏙️ Average Price by Districts in Bishkek")
        fig_top, fig_all = bishkek_district_avg_price_dashboard(df)
        if fig_top:
            st.plotly_chart(fig_top, use_container_width=True, key="live_bishkek_avg_price_top")
            with st.expander("Show all districts"):
                st.plotly_chart(fig_all, use_container_width=True, key="live_bishkek_avg_price_all")
        else:
            st.info("No district data available for Bishkek.")

        st.subheader("📐 Plot Area Distribution")
        fig4 = plot_area_distribution_dashboard(df)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True, key="live_plot_area_top")
            with st.expander("Show all plot areas"):
                fig4_full = plot_area_distribution_dashboard(df, top_n=None)
                st.plotly_chart(fig4_full, use_container_width=True, key="live_plot_area_full")

        st.subheader("🔌 Communication Access")
        fig5 = communication_access_dashboard(df)
        if fig5:
            st.plotly_chart(fig5, use_container_width=True, key="live_communication_access")

        st.subheader("📊 Distribution of Listings by Offer Type")
        fig_offer_type = offer_type_distribution_dashboard(df)
        st.plotly_chart(fig_offer_type, use_container_width=True, key="live_offer_type_dist")

        st.subheader("📋 Data Tables")
        display_columns = ['Название', 'Область', 'Город/Село', 'Район', 'Цена', 'Площадь участка']

        st.write("### 10 Most Expensive Sectors")
        most_expensive = df.nlargest(10, 'Цена (int)')[display_columns]
        st.dataframe(most_expensive)

        st.write("### 10 Cheapest Sectors")
        cheapest = df.nsmallest(10, 'Цена (int)')[display_columns]
        st.dataframe(cheapest)

        if 'Площадь (сотки)' in df.columns:
            st.write("### 10 Largest Sectors")
            largest = df.nlargest(10, 'Площадь (сотки)')[display_columns]
            st.dataframe(largest)

            st.write("### 10 Smallest Sectors")
            smallest = df.nsmallest(10, 'Площадь (сотки)')[display_columns]
            st.dataframe(smallest)
        else:
            st.info("Area data not available for this property type.")

        threading.Thread(target=delete_file_after_delay, args=(unique_output_path, 60)).start()
