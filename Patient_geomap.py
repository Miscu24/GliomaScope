'''Handles patient location mapping logic (e.g. by country, IDH1 prevalence)'''
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
import time
import webbrowser
import os
import ssl
import certifi

# Explicitly create SSL context using certifi bundle
ctx = ssl.create_default_context(cafile=certifi.where())

# Pass SSL context to geolocator
geolocator = Nominatim(user_agent="GliomaScope_mapper", ssl_context=ctx)
geo_cache = {}


def geocode_country(country):
    if country in geo_cache:
        return geo_cache[country]
    try:
        print(f"Geocoding: {country}")
        location = geolocator.geocode(country, timeout=10)
        time.sleep(1)  # avoid rate limit
        if location:
            coords = (location.latitude, location.longitude)
            geo_cache[country] = coords
            return coords
    except Exception as e:
        print(f"Failed to geocode {country}: {e}")
    return (None, None)

def plot_patient_geomap(metadata_df, filter_applied=None, color_by='country', zoom_to_region=False):
    df = metadata_df.copy()

    filter_summary = ""
    if filter_applied:
        summary_parts = []
        for key, value in filter_applied.items():
            if isinstance(value, (list, tuple, set)):
                summary_parts.append(f"{key} = [{', '.join(map(str, value))}]")
            else:
                summary_parts.append(f"{key} = {value}")
        filter_summary = " | Filters: " + "; ".join(summary_parts)

    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        if 'country' not in df.columns:
            raise ValueError("Missing 'country' column to perform geocoding.")
        
        print("Geocoding countries to get Latitude and Longitude...")
        df[['Latitude', 'Longitude']] = df['country'].apply(lambda x: pd.Series(geocode_country(x)))
        print("Geocoded locations:")
        print(df[['Sample_ID', 'country', 'Latitude', 'Longitude']])

    
        df.to_csv("output_with_coords.csv", index=False)
        print("Saved updated metadata with coordinates to 'output_with_coords.csv'.")

    df = df.dropna(subset=['Latitude', 'Longitude'])

    if df.empty:
        print("No valid geographic data to plot.")
        return
    
    #determine hover feilds 
    hover_fields = []
    for col in ['age', 'sex', 'grade', 'idh', 'country']:
        if col in df.columns:
            hover_fields.append(col)

    # Sample count and subtitle
    num_samples = len(df)
    subtitle = f"Glioma Patient Map ({num_samples} samples shown){filter_summary}"
    main_title = f"Glioma Patient Map {subtitle}"
# Main title and subtitle
    sample_count = len(df)
    title_text = "Glioma Patient Map"
    subtitle_text = f"{sample_count} samples{filter_summary}"

    fig = px.scatter_geo(
        df,
        lat='Latitude',
        lon='Longitude',
        hover_name='Sample_ID',
        text='Sample_ID',
        color='country',
        hover_data=hover_fields,
        projection='natural earth',
        title='Glioma Patient Map'
    )
    if zoom_to_region:
        fig.update_geos(fitbounds="locations", visible=True)
        # Add bottom subtitle annotation
    fig.add_annotation(
        text=subtitle_text,
        xref="paper", yref="paper",
        x=0.5, y=-0.1,  # below the plot
        showarrow=False,
        font=dict(size=12),
        xanchor='center'
    )

    print("Saving map...")
    fig.write_html("geomap_test.html")
    print("Map saved to 'geomap_test.html'.")

    # Try to open map in browser
    map_path = os.path.abspath("geomap_test.html")
    os.system(f"open '{map_path}'")  # Mac-specific fallback

def plot_study_summary(metadata_df, group_by='country'):
    if group_by not in metadata_df.columns:
        print(f"Column '{group_by}' not found in metadata.")
        return
    
    if 'Latitude' not in metadata_df.columns or 'Longitude' not in metadata_df.columns:
        print("Geocoding countries for study-level summary...")
        metadata_df[['Latitude', 'Longitude']] = metadata_df['country'].apply(lambda x: pd.Series(geocode_country(x)))

    df_grouped = metadata_df.groupby(group_by).agg({
        'Latitude': 'first',
        'Longitude': 'first',
        'Sample_ID': 'count',
        'age': 'mean' if 'age' in metadata_df.columns else 'first',
    }).reset_index()

    df_grouped.rename(columns={
        'Sample_ID': 'Sample_Count',
        'age': 'Mean_Age'
    }, inplace=True)

    def summarize_column(col_data):
        return ', '.join([f"{k}: {v}" for k, v in col_data.value_counts().to_dict().items()])
    
    sex_summary = metadata_df.groupby(group_by)['sex'].apply(lambda x: summarize_column(x) if x.notna().any() else 'N/A')
    idh_summary = metadata_df.groupby(group_by)['idh'].apply(lambda x: summarize_column(x) if x.notna().any() else 'N/A')

    df_grouped['Sex_Summary'] = df_grouped[group_by].map(sex_summary)
    df_grouped['IDH_Summary'] = df_grouped[group_by].map(idh_summary)

    hover_data = {
        'Sample_Count': True,
        'Mean_Age': ':.1f',
        'Sex_Summary': True,
        'IDH_Summary': True
    }

    fig = px.scatter_geo(
        df_grouped,
        lat='Latitude',
        lon='Longitude',
        size='Sample_Count',
        color='Sample_Count',
        text=group_by,
        hover_data=hover_data,
        projection='natural earth',
        title=f"Study-Level Summary Map by {group_by.capitalize()}"
    )
    fig.update_geos(fitbounds="locations", visible=True)

    fig.update_traces(
        marker=dict(
            sizemode='area',
            sizeref=2.* max(df_grouped['Sample_Count']) / (100.**2),
            sizemin=4
        )
    )
    html_file = f"study_summary_{group_by}.html"
    fig.write_html(html_file)
    print(f"Study summary map saved to '{html_file}'.")
    
    map_path = os.path.abspath(html_file)
    os.system(f"open '{map_path}'")