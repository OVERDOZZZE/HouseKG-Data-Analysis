import pandas as pd
import plotly.express as px
import re

def price_distribution_dashboard(df):
    bins = [0, 10000, 25000, 50000, 75000, 100000, 150000, 200000, 300000, 500000, 1000000, float('inf')]
    labels = ['<10k', '10-25k', '25-50k', '50-75k', '75-100k', '100-150k', '150-200k', '200-300k', '300-500k', '500k-1M', '>1M']
    df['Price Range'] = pd.cut(df['Цена (int)'], bins=bins, labels=labels)
    price_bins = df['Price Range'].value_counts().sort_index().reset_index()
    price_bins.columns = ['Range', 'Count']
    fig = px.bar(
        price_bins,
        x='Range',
        y='Count',
        color='Count',
        color_continuous_scale='Blues',
        title='Price Distribution by Ranges'
    )
    fig.update_layout(coloraxis_showscale=False)
    return fig

def district_distribution_dashboard(df):
    bishkek_df = df[df['Город/Село'] == 'Бишкек']
    if not bishkek_df.empty and 'Район' in bishkek_df.columns:
        district_counts = bishkek_df['Район'].dropna().value_counts().reset_index()
        district_counts.columns = ['Район', 'count']
        fig = px.treemap(
            district_counts,
            path=['Район'],
            values='count',
            title="Treemap of Listings by Districts of Bishkek"
        )
        return fig
    return None

def region_avg_price_dashboard(df):
    true_regions = [
        'Чуйская область', 'Ошская область', 'Иссык-Кульская область',
        'Джалал-Абадская область', 'Баткенская область', 'Таласская область',
        'Нарынская область'
    ]
    region_avg_price = df[df['Область'].isin(true_regions)].groupby('Область').agg(avg_price=('Цена (int)', 'mean')).reset_index()
    region_avg_price = region_avg_price.sort_values('avg_price', ascending=False)
    region_avg_price['Rank'] = range(1, len(region_avg_price) + 1)
    fig = px.line(
        region_avg_price,
        x='Rank',
        y='avg_price',
        markers=True,
        hover_name='Область',
        hover_data={'avg_price': ':.0f'},
        title="Average Price per Region (Cleaned)"
    )
    fig.update_layout(
        xaxis=dict(title='', showticklabels=False),
        yaxis_title='Average Price ($)',
        showlegend=False
    )
    return fig

def plot_area_distribution_dashboard(df, top_n=30):
    if 'Площадь участка' in df.columns:
        area_counts = df['Площадь участка'].value_counts().reset_index()
        area_counts.columns = ['Площадь участка', 'count']
        if top_n:
            area_counts = area_counts.head(top_n)
        fig = px.bar(area_counts, x='Площадь участка', y='count', title="Plot Sizes Distribution")
        return fig
    return None

def communication_access_dashboard(df):
    if 'Коммуникации' in df.columns:
        comm_series = df['Коммуникации'].dropna()
        splitted = comm_series.str.split(',').explode().str.strip()
        comm_counts = splitted.value_counts().reset_index()
        comm_counts.columns = ['Коммуникация', 'count']
        top_comms = comm_counts.head(30)
        fig = px.pie(
            top_comms,
            names='Коммуникация',
            values='count',
            title="Top Communication Access (Separated - Pie Chart)",
            hole=0.4
        )
        return fig
    return None

def bishkek_district_avg_price_dashboard(df):
    bishkek_df = df[(df['Город/Село'] == 'Бишкек') & (df['Район'].notna())]
    if not bishkek_df.empty:
        district_avg = bishkek_df.groupby('Район')['Цена (int)'].mean().sort_values(ascending=False).reset_index()
        top_10 = district_avg.head(10)
        fig_top = px.bar(
            top_10,
            x='Район',
            y='Цена (int)',
            title='Top 10 Districts in Bishkek by Average Price',
            labels={'Цена (int)': 'Average Price ($)'}
        )
        fig_all = px.bar(
            district_avg,
            x='Район',
            y='Цена (int)',
            title='All Districts in Bishkek by Average Price',
            labels={'Цена (int)': 'Average Price ($)'}
        )
        return fig_top, fig_all
    return None, None

def bishkek_district_avg_price_private_house_dashboard(df):
    bishkek_df = df[(df['Город/Село'] == 'Бишкек') & (df['Район'].notna())]
    if not bishkek_df.empty:
        district_avg = bishkek_df.groupby('Район')['Цена (int)'].mean().sort_values(ascending=False).reset_index()
        top_10 = district_avg.head(20)
        fig_top = px.bar(
            top_10,
            x='Район',
            y='Цена (int)',
            title='Top 10 Districts in Bishkek by Average Price for Private Houses',
            labels={'Цена (int)': 'Average Price ($)'},
            color='Цена (int)',
            color_continuous_scale='Blues'
        )
        fig_all = px.bar(
            district_avg,
            x='Район',
            y='Цена (int)',
            title='All Districts in Bishkek by Average Price for Private Houses',
            labels={'Цена (int)': 'Average Price ($)'},
            color='Цена (int)',
            color_continuous_scale='Blues'
        )
        fig_top.update_layout(coloraxis_showscale=False)
        fig_all.update_layout(coloraxis_showscale=False)
        return fig_top, fig_all
    return None, None

def offer_type_distribution_dashboard(df):
    offer_type_counts = df['Тип предложения'].value_counts().reset_index()
    offer_type_counts.columns = ['Тип предложения', 'count']
    fig = px.bar(
        offer_type_counts,
        x='Тип предложения',
        y='count',
        color='Тип предложения',
        title="Distribution of Listings by Offer Type"
    )
    return fig

def rooms_distribution_dashboard(df):
    if 'Rooms' in df.columns:
        room_counts = df['Rooms'].value_counts().reset_index()
        room_counts.columns = ['Rooms', 'Count']
        room_counts['Rooms'] = pd.Categorical(room_counts['Rooms'], categories=['1', '2', '3', '4', '5', '6+'], ordered=True)
        room_counts = room_counts.sort_values('Rooms')
        fig = px.bar(
            room_counts,
            x='Rooms',
            y='Count',
            title='Distribution of Number of Rooms',
            labels={'Rooms': 'Number of Rooms', 'Count': 'Number of Houses'}
        )
        return fig
    return None

def house_area_distribution_dashboard(df):
    if 'House Area' in df.columns:
        bins = [0, 50, 100, 150, 200, 250, 300, 400, 500, float('inf')]
        labels = ['<50', '50-100', '100-150', '150-200', '200-250', '250-300', '300-400', '400-500', '>500']
        df['Area Range'] = pd.cut(df['House Area'], bins=bins, labels=labels)
        area_counts = df['Area Range'].value_counts().sort_index().reset_index()
        area_counts.columns = ['Area Range', 'Count']
        fig = px.bar(
            area_counts,
            x='Area Range',
            y='Count',
            title='House Area Distribution',
            labels={'Area Range': 'House Area (m²)', 'Count': 'Number of Houses'}
        )
        return fig
    return None

def heating_type_distribution_dashboard(df):
    if 'Отопление' in df.columns:
        heating_counts = df['Отопление'].value_counts().reset_index()
        heating_counts.columns = ['Heating Type', 'Count']
        fig = px.pie(
            heating_counts,
            names='Heating Type',
            values='Count',
            title='Heating Type Distribution',
            hole=0.4
        )
        return fig
    return None