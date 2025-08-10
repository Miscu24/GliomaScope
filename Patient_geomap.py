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

    # Check for country column with different possible names (including institute_country)
    country_col = None
    for col in ['institute_country', 'country', 'Country', 'COUNTRY']:
        if col in df.columns:
            country_col = col
            break
    
    if country_col is None:
        print("[!] No country column found. Available columns: " + ", ".join(df.columns))
        print("[!] Adding placeholder 'Unknown' country for all samples.")
        df['country'] = 'Unknown'
        country_col = 'country'
    else:
        # Rename the found country column to 'country' for consistency
        df['country'] = df[country_col]
        print(f"[✓] Using '{country_col}' column for country data")

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
        print("Geocoding countries to get Latitude and Longitude...")
        df[['Latitude', 'Longitude']] = df['country'].apply(lambda x: pd.Series(geocode_country(x)))
        print("Geocoded locations:")
        print(df[['Sample', 'country', 'Latitude', 'Longitude']])

        df.to_csv("output_with_coords.csv", index=False)
        print("Saved updated metadata with coordinates to 'output_with_coords.csv'.")

    df = df.dropna(subset=['Latitude', 'Longitude'])

    if df.empty:
        print("No valid geographic data to plot.")
        return
    
    #determine hover fields 
    hover_fields = []
    for col in ['age', 'sex', 'grade', 'idh', 'country', 'institute_country', 'institute_city']:
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
        hover_name='Sample',
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
    
    # Show map in browser (non-blocking)
    try:
        map_path = os.path.abspath("geomap_test.html")
        import subprocess
        subprocess.Popen(['open', map_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Map opened in your browser.")
    except Exception as e:
        print(f"Could not open map automatically. Please open 'geomap_test.html' manually in your browser.")

def create_patient_geomap_html(metadata_df, filter_applied=None, color_by='country', zoom_to_region=False):
    """Create a plotly figure for patient geomap and return as HTML string for web embedding"""
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

    # Check for country column with different possible names (including institute_country)
    country_col = None
    for col in ['institute_country', 'country', 'Country', 'COUNTRY']:
        if col in df.columns:
            country_col = col
            break
    
    if country_col is None:
        print("[!] No country column found. Available columns: " + ", ".join(df.columns))
        print("[!] Adding placeholder 'Unknown' country for all samples.")
        df['country'] = 'Unknown'
        country_col = 'country'
    else:
        # Rename the found country column to 'country' for consistency
        df['country'] = df[country_col]
        print(f"[✓] Using '{country_col}' column for country data")

    # Check if we already have coordinates
    has_geographic_data = 'Latitude' in df.columns and 'Longitude' in df.columns

    if not has_geographic_data:
        print("Geocoding countries to get Latitude and Longitude...")
        df[['Latitude', 'Longitude']] = df['country'].apply(lambda x: pd.Series(geocode_country(x)))
        print("Geocoded locations:")
        print(df[['Sample', 'country', 'Latitude', 'Longitude']])

    df = df.dropna(subset=['Latitude', 'Longitude'])

    if df.empty:
        # Create empty map with message
        fig = px.scatter_geo(
            projection='natural earth',
            title='Glioma Patient Map - No Geographic Data Available'
        )
        fig.add_annotation(
            text="No valid geographic data found. Please upload data with country information.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="red"),
            xanchor='center',
            yanchor='middle'
        )
    else:
        # Determine hover fields
        hover_fields = []
        for col in ['age', 'sex', 'grade', 'idh', 'country', 'institute_country', 'institute_city']:
            if col in df.columns:
                hover_fields.append(col)

        # Sample count and subtitle
        sample_count = len(df)
        subtitle_text = f"{sample_count} samples{filter_summary}"

        fig = px.scatter_geo(
            df,
            lat='Latitude',
            lon='Longitude',
            hover_name='Sample',
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

    # Update layout for better web display
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=50, b=50),
        showlegend=True
    )

    return fig

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
        'Sample': 'count',
        'age': 'mean' if 'age' in metadata_df.columns else 'first',
    }).reset_index()

    df_grouped.rename(columns={
        'Sample': 'Sample_Count',
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
    
    # Show map in browser (non-blocking)
    try:
        map_path = os.path.abspath(html_file)
        import subprocess
        subprocess.Popen(['open', map_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Map opened in your browser.")
    except Exception as e:
        print(f"Could not open map automatically. Please open '{html_file}' manually in your browser.")

def create_study_origin_map(metadata_df):
    """Create a map showing where studies originated based on institution information"""
    
    # Extract geographic information from institution fields
    geographic_data = []
    
    # Look for institution information columns
    institute_cols = [col for col in metadata_df.columns if 'institute' in col.lower()]
    
    if not institute_cols:
        print("ERROR: No institution information found in metadata.")
        print("Available columns:", ", ".join(metadata_df.columns))
        print("TIP: This visualization requires institution columns (institute, institute_city, institute_country)")
        return
    
    # Extract unique institutions and their locations
    institutions = {}
    for _, row in metadata_df.iterrows():
        # Try to get institution and location using available columns
        institute = row.get('institute', row.get('institute_name', 'Unknown Institute'))
        city = row.get('institute_city', row.get('city', 'Unknown City'))
        country = row.get('institute_country', row.get('country', 'Unknown Country'))
        
        key = f"{institute}_{city}_{country}"
        if key not in institutions:
            institutions[key] = {
                'institute': institute,
                'city': city,
                'country': country,
                'samples': 0,
                'studies': set()
            }
        
        institutions[key]['samples'] += 1
        study_id = row.get('study_id', row.get('series_id', row.get('geo_id', 'Unknown Study')))
        institutions[key]['studies'].add(study_id)
    
    # Convert to DataFrame
    if not institutions:
        print("ERROR: No geographic information could be extracted.")
        return
    
    # Geocode locations
    print("MAP: Geocoding institution locations...")
    for key, data in institutions.items():
        location_str = f"{data['city']}, {data['country']}"
        coords = geocode_country(location_str)
        data['latitude'] = coords[0]
        data['longitude'] = coords[1]
        data['study_count'] = len(data['studies'])
    
    # Create DataFrame
    df_map = pd.DataFrame([
        {
            'Institution': data['institute'],
            'City': data['city'],
            'Country': data['country'],
            'Latitude': data['latitude'],
            'Longitude': data['longitude'],
            'Sample_Count': data['samples'],
            'Study_Count': data['study_count']
        }
        for data in institutions.values()
    ])
    
    # Remove rows with invalid coordinates
    df_map = df_map.dropna(subset=['Latitude', 'Longitude'])
    
    if df_map.empty:
        print("ERROR: No valid geographic coordinates found.")
        return
    
    # Create the map
    fig = px.scatter_geo(
        df_map,
        lat='Latitude',
        lon='Longitude',
        size='Sample_Count',
        color='Study_Count',
        hover_name='Institution',
        hover_data=['City', 'Country', 'Sample_Count', 'Study_Count'],
        projection='natural earth',
        title='Glioma Research Institutions Worldwide',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        height=700,
        margin=dict(l=0, r=0, t=50, b=50),
        showlegend=True
    )
    
    # Save and display
    filename = "glioma_research_institutions_map.html"
    fig.write_html(filename)
    print(f"SUCCESS: Study origin map saved to '{filename}'")
    
    try:
        import subprocess
        subprocess.Popen(['open', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("MAP: Map opened in your browser.")
    except Exception as e:
        print(f"Could not automatically open browser: {e}")
        print(f"Please open '{filename}' manually in your browser.")


def create_institution_map(metadata_df):
    """Create a map showing sample distribution by institution"""
    
    # Look for institution information columns
    institute_cols = [col for col in metadata_df.columns if 'institute' in col.lower()]
    
    if not institute_cols:
        print("ERROR: No institution information found in metadata.")
        print("Available columns:", ", ".join(metadata_df.columns))
        return
    
    # Group by institution and count samples
    institution_counts = metadata_df.groupby('institute').size().reset_index(name='sample_count')
    
    # Get unique institutions with their locations
    institutions = {}
    for _, row in metadata_df.iterrows():
        institute = row.get('institute', 'Unknown Institute')
        city = row.get('institute_city', 'Unknown City')
        country = row.get('institute_country', 'Unknown Country')
        
        if institute not in institutions:
            institutions[institute] = {
                'city': city,
                'country': country,
                'samples': 0
            }
        institutions[institute]['samples'] += 1
    
    # Create DataFrame for mapping
    df_map = pd.DataFrame([
        {
            'Institution': institute,
            'City': data['city'],
            'Country': data['country'],
            'Sample_Count': data['samples']
        }
        for institute, data in institutions.items()
    ])
    
    # Geocode locations
    print("MAP: Geocoding institution locations...")
    df_map[['Latitude', 'Longitude']] = df_map.apply(
        lambda row: pd.Series(geocode_country(f"{row['City']}, {row['Country']}")), 
        axis=1
    )
    
    # Remove rows with invalid coordinates
    df_map = df_map.dropna(subset=['Latitude', 'Longitude'])
    
    if df_map.empty:
        print("ERROR: No valid geographic coordinates found.")
        return
    
    # Create the map
    fig = px.scatter_geo(
        df_map,
        lat='Latitude',
        lon='Longitude',
        size='Sample_Count',
        color='Sample_Count',
        hover_name='Institution',
        hover_data=['City', 'Country', 'Sample_Count'],
        projection='natural earth',
        title='Glioma Sample Distribution by Institution',
        color_continuous_scale='plasma'
    )
    
    fig.update_layout(
        height=700,
        margin=dict(l=0, r=0, t=50, b=50),
        showlegend=True
    )
    
    # Save and display
    filename = "institution_sample_distribution.html"
    fig.write_html(filename)
    print(f"SUCCESS: Institution map saved to '{filename}'")
    
    try:
        import subprocess
        subprocess.Popen(['open', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("MAP: Map opened in your browser.")
    except Exception as e:
        print(f"Could not automatically open browser: {e}")
        print(f"Please open '{filename}' manually in your browser.")


def create_timeline_map(metadata_df):
    """Create a timeline visualization of publications by location"""
    
    if 'submission_date' in metadata_df.columns:
        # Extract year from submission date
        metadata_df['year'] = pd.to_datetime(metadata_df['submission_date'], errors='coerce').dt.year
        
        # Group by year and institution
        timeline_data = metadata_df.groupby(['year', 'contact_institute']).size().reset_index(name='count')
        
        # Create timeline chart
        fig = px.scatter(
            timeline_data,
            x='year',
            y='count',
            color='contact_institute',
            size='count',
            hover_name='contact_institute',
            title="Glioma Research Timeline by Institution",
            labels={'year': 'Publication Year', 'count': 'Number of Samples'}
        )
        
        fig.update_layout(height=600)
        
        filename = "glioma_research_timeline.html"
        fig.write_html(filename)
        print(f"SUCCESS: Research timeline saved to '{filename}'")
        
        try:
            import subprocess
            subprocess.Popen(['open', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("TIMELINE: Timeline opened in your browser.")
        except Exception as e:
            print(f"Could not open timeline automatically. Please open '{filename}' manually in your browser.")
    else:
        print("ERROR: No submission date information found in metadata.")


def create_network_map(metadata_df):
    """Create a network visualization of research collaborations"""
    
    # This would be a more complex visualization showing research networks
    # For now, create a simple collaboration matrix
    
    if 'contact_institute' in metadata_df.columns and 'series_id' in metadata_df.columns:
        # Count studies per institution
        institution_studies = metadata_df.groupby('contact_institute')['series_id'].nunique()
        
        print("ANALYSIS: Research Network Summary:")
        print("=" * 50)
        print(f"   • Total institutions: {len(institution_studies)}")
        print(f"   • Total studies: {institution_studies.sum()}")
        print(f"   • Average studies per institution: {institution_studies.mean():.1f}")
        
        # Create a simple network visualization
        fig = px.scatter(
            x=institution_studies.values,
            y=range(len(institution_studies)),
            text=institution_studies.index,
            title="Research Activity by Institution",
            labels={'x': 'Number of Studies', 'y': 'Institution Rank'}
        )
        
        fig.update_traces(textposition='middle right')
        fig.update_layout(height=600)
        
        filename = "research_network_activity.html"
        fig.write_html(filename)
        print(f"SUCCESS: Research network visualization saved to '{filename}'")
        
        try:
            import subprocess
            subprocess.Popen(['open', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("NETWORK: Network visualization opened in your browser.")
        except Exception as e:
            print(f"Could not open visualization automatically. Please open '{filename}' manually in your browser.")
    else:
        print("ERROR: Insufficient data for network visualization.")


def create_geographic_summary(metadata_df):
    """Create a comprehensive geographic data summary"""
    
    print("LIST: GEOGRAPHIC DATA SUMMARY")
    print("=" * 60)
    
    # Check what geographic information is available
    contact_cols = [col for col in metadata_df.columns if 'contact' in col.lower()]
    
    if contact_cols:
        print("SUCCESS: Geographic information found:")
        for col in contact_cols:
            unique_vals = metadata_df[col].dropna().unique()
            print(f"   • {col}: {len(unique_vals)} unique values")
            if len(unique_vals) <= 5:
                print(f"     Values: {', '.join(map(str, unique_vals))}")
            else:
                print(f"     Values: {', '.join(map(str, unique_vals[:3]))}... (and {len(unique_vals)-3} more)")
    else:
        print("ERROR: No geographic information found in metadata.")
    
    # Show sample distribution
    print(f"\nINFO: Sample Distribution:")
    print(f"   • Total samples: {len(metadata_df)}")
    
    if 'contact_institute' in metadata_df.columns:
        institute_counts = metadata_df['contact_institute'].value_counts()
        print(f"   • Unique institutions: {len(institute_counts)}")
        print(f"   • Most active institution: {institute_counts.index[0]} ({institute_counts.iloc[0]} samples)")
    
    if 'series_id' in metadata_df.columns:
        study_counts = metadata_df['series_id'].value_counts()
        print(f"   • Unique studies: {len(study_counts)}")
        print(f"   • Largest study: {study_counts.index[0]} ({study_counts.iloc[0]} samples)")
    
    print("\nTIP: For better geographic visualizations, ensure your data includes:")
    print("   • contact_city, contact_country, contact_institute columns")
    print("   • submission_date for timeline analysis")
    print("   • series_id for study-level analysis")


def create_study_summary_html(metadata_df, group_by='country'):
    """Create a plotly figure for study summary map and return as HTML string for web embedding"""
    # Handle empty DataFrame
    if metadata_df.empty:
        fig = px.scatter_geo(
            projection='natural earth',
            title='Study Summary Map - Upload Geographic Data'
        )
        fig.add_annotation(
            text="Upload data with country information to see study summary on the map",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="blue"),
            xanchor='center',
            yanchor='middle'
        )
        fig.update_layout(
            height=600,
            margin=dict(l=0, r=0, t=50, b=50),
            showlegend=True
        )
        return fig
    
    # Check for group_by column with different possible names
    group_by_col = None
    for col in [group_by, group_by.capitalize(), group_by.upper()]:
        if col in metadata_df.columns:
            group_by_col = col
            break
    
    if group_by_col is None:
        # Create map with warning message
        fig = px.scatter_geo(
            projection='natural earth',
            title='Study Summary Map - Missing Geographic Data'
        )
        fig.add_annotation(
            text=f"Column '{group_by}' not found in metadata. Available columns: {', '.join(metadata_df.columns)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="red"),
            xanchor='center',
            yanchor='middle'
        )
        fig.update_layout(
            height=600,
            margin=dict(l=0, r=0, t=50, b=50),
            showlegend=True
        )
        return fig
    
    if 'Latitude' not in metadata_df.columns or 'Longitude' not in metadata_df.columns:
        print("Geocoding countries for study-level summary...")
        # Find the country column
        country_col = None
        for col in ['country', 'Country', 'COUNTRY']:
            if col in metadata_df.columns:
                country_col = col
                break
        
        if country_col is None:
            return f"<div class='alert alert-warning'>No country column found for geocoding. Available columns: {', '.join(metadata_df.columns)}</div>"
        
        metadata_df[['Latitude', 'Longitude']] = metadata_df[country_col].apply(lambda x: pd.Series(geocode_country(x)))

    df_grouped = metadata_df.groupby(group_by).agg({
        'Latitude': 'first',
        'Longitude': 'first',
        'Sample': 'count',
        'age': 'mean' if 'age' in metadata_df.columns else 'first',
    }).reset_index()

    df_grouped.rename(columns={
        'Sample': 'Sample_Count',
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

    # Update layout for better web display
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=50, b=50),
        showlegend=True
    )

    return fig