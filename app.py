from flask import Flask, render_template, request, jsonify, send_file, session, send_from_directory
from werkzeug.utils import secure_filename
import os
import pandas as pd
import json
import tempfile
import base64
import io
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from functools import lru_cache
import time

# Import all the existing modules
from Data_loader import DataManager
from Utils import process_upload, list_available_genes, filter_metadata
from Explore_data import preview_dataframe, display_summary, warn_if_missing_columns
from Dimensionality_Reduction import plot_pca
from Patient_geomap import plot_patient_geomap, plot_study_summary
from Patient_metadata import display_patient_summary
from Dimensionality_Reduction import plot_umap
from Differential_expression import perform_differential_expression
from Gene_explorer import explore_gene_expression, map_gene_to_chromosome
from Heatmap_visualisation import plot_expression_heatmap

app = Flask(__name__)
app.secret_key = 'glioma_scope_secret_key_2024'

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Global data manager
data_manager = DataManager()

# Performance caching system
_data_cache = {
    'metadata_stats': None,
    'expression_stats': None,
    'metadata_preview': None,
    'expression_preview': None,
    'cache_time': 0,
    'cache_ttl': 300  # 5 minutes cache TTL
}

def reload_data_if_needed():
    """Reload data from saved files if data manager is empty (optimized)"""
    global _data_cache
    
    # Only reload if data is actually missing
    if data_manager.metadata is None and os.path.exists('cleaned_data/metadata_cleaned.csv'):
        print("Reloading metadata from saved file...")
        data_manager.metadata = pd.read_csv('cleaned_data/metadata_cleaned.csv')
        session['metadata_loaded'] = True
        # Clear cache when new data is loaded
        _data_cache['metadata_stats'] = None
        _data_cache['metadata_preview'] = None
        _data_cache['cache_time'] = 0
    
    if data_manager.expression is None and os.path.exists('cleaned_data/expression_cleaned.csv'):
        print("Reloading expression from saved file...")
        data_manager.expression = pd.read_csv('cleaned_data/expression_cleaned.csv')
        session['expression_loaded'] = True
        # Clear cache when new data is loaded
        _data_cache['expression_stats'] = None
        _data_cache['expression_preview'] = None
        _data_cache['cache_time'] = 0

def create_world_map(metadata_df=None, map_type='individual', zoom_enabled=False):
    """Create a world map with optional data points"""
    
    # Create base world map
    fig = go.Figure()
    
    # Add world map background
    fig.add_trace(go.Scattergeo(
        lon=[],
        lat=[],
        mode='markers',
        marker=dict(size=0),
        showlegend=False
    ))
    
    # Set up the layout for a full-screen world map
    fig.update_layout(
        title={
            'text': 'GliomaScope World Map',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2E8B57'}
        },
        geo=dict(
            scope='world',
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            showocean=True,
            oceancolor='rgb(204, 229, 255)',
            showcountries=True,
            countrycolor='rgb(128, 128, 128)',
            coastlinecolor='rgb(128, 128, 128)',
            coastlinewidth=1,
            showframe=False,
            framecolor='rgb(128, 128, 128)',
            framewidth=1,
            bgcolor='rgb(240, 248, 255)',
            center=dict(lon=0, lat=20),
            projection_scale=1.2
        ),
        height=800,  # Make it bigger
        width=None,  # Auto-width
        margin=dict(l=0, r=0, t=80, b=0),
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.2)',
            borderwidth=1
        )
    )
    
    # If we have metadata with geographic data, add points
    if metadata_df is not None and not metadata_df.empty:
        # Check for country column (case insensitive)
        country_col = None
        for col in metadata_df.columns:
            if col.lower() in ['country', 'nation', 'location']:
                country_col = col
                break
        
        if country_col:
            # Get unique countries and their counts
            country_counts = metadata_df[country_col].value_counts()
            
            # Sample coordinates for common countries
            country_coords = {
                'United States': (37.0902, -95.7129),
                'United Kingdom': (55.3781, -3.4360),
                'Germany': (51.1657, 10.4515),
                'France': (46.2276, 2.2137),
                'Canada': (56.1304, -106.3468),
                'Australia': (-25.2744, 133.7751),
                'China': (35.8617, 104.1954),
                'Japan': (36.2048, 138.2529),
                'India': (20.5937, 78.9629),
                'Brazil': (-14.2350, -51.9253),
                'Russia': (61.5240, 105.3188),
                'Italy': (41.8719, 12.5674),
                'Spain': (40.4637, -3.7492),
                'Netherlands': (52.1326, 5.2913),
                'Sweden': (60.1282, 18.6435),
                'Norway': (60.4720, 8.4689),
                'Denmark': (56.2639, 9.5018),
                'Finland': (61.9241, 25.7482),
                'Switzerland': (46.8182, 8.2275),
                'Austria': (47.5162, 14.5501),
                'Belgium': (50.8503, 4.3517),
                'Poland': (51.9194, 19.1451),
                'Czech Republic': (49.8175, 15.4730),
                'Hungary': (47.1625, 19.5033),
                'Romania': (45.9432, 24.9668),
                'Bulgaria': (42.7339, 25.4858),
                'Greece': (39.0742, 21.8243),
                'Portugal': (39.3999, -8.2245),
                'Ireland': (53.1424, -7.6921),
                'Iceland': (64.9631, -19.0208),
                'New Zealand': (-40.9006, 174.8860),
                'South Africa': (-30.5595, 22.9375),
                'Egypt': (26.8206, 30.8025),
                'Nigeria': (9.0820, 8.6753),
                'Kenya': (-0.0236, 37.9062),
                'Morocco': (31.7917, -7.0926),
                'Algeria': (28.0339, 1.6596),
                'Tunisia': (33.8869, 9.5375),
                'Libya': (26.3351, 17.2283),
                'Sudan': (12.8628, 30.2176),
                'Ethiopia': (9.1450, 40.4897),
                'Somalia': (5.1521, 46.1996),
                'Uganda': (1.3733, 32.2903),
                'Tanzania': (-6.3690, 34.8888),
                'Zimbabwe': (-19.0154, 29.1549),
                'Zambia': (-13.1339, 27.8493),
                'Botswana': (-22.3285, 24.6849),
                'Namibia': (-22.9576, 18.4904),
                'Angola': (-11.2027, 17.8739),
                'Mozambique': (-18.6657, 35.5296),
                'Madagascar': (-18.7669, 46.8691),
                'Mauritius': (-20.3484, 57.5522),
                'Seychelles': (-4.6796, 55.4920),
                'Comoros': (-11.6455, 43.3333),
                'Cape Verde': (16.5388, -23.0418),
                'São Tomé and Príncipe': (0.1864, 6.6131),
                'Equatorial Guinea': (1.6508, 10.2679),
                'Gabon': (-0.8037, 11.6094),
                'Congo': (-0.2280, 15.8277),
                'Central African Republic': (6.6111, 20.9394),
                'Chad': (15.4542, 18.7322),
                'Cameroon': (7.3697, 12.3547),
                'Niger': (17.6078, 8.0817),
                'Mali': (17.5707, -3.9962),
                'Burkina Faso': (12.2383, -1.5616),
                'Senegal': (14.4974, -14.4524),
                'Gambia': (13.4432, -15.3101),
                'Guinea-Bissau': (11.8037, -15.1804),
                'Guinea': (9.9456, -9.6966),
                'Sierra Leone': (8.4606, -11.7799),
                'Liberia': (6.4281, -9.4295),
                'Côte d\'Ivoire': (7.5400, -5.5471),
                'Ghana': (7.9465, -1.0232),
                'Togo': (8.6195, 0.8248),
                'Benin': (9.3077, 2.3158),
                'Congo, Democratic Republic of the': (-4.0383, 21.7587),
                'Rwanda': (-1.9403, 29.8739),
                'Burundi': (-3.3731, 29.9189),
                'Malawi': (-13.2543, 34.3015),
                'Lesotho': (-29.6099, 28.2336),
                'Eswatini': (-26.5225, 31.4659),
                'South Sudan': (6.8770, 31.3070),
                'Eritrea': (15.1794, 39.7823),
                'Djibouti': (11.8251, 42.5903),
                'Chile': (-35.6751, -71.5430),
                'Argentina': (-38.4161, -63.6167),
                'Uruguay': (-32.5228, -55.7658),
                'Paraguay': (-23.4425, -58.4438),
                'Bolivia': (-16.2902, -63.5887),
                'Peru': (-9.1900, -75.0152),
                'Ecuador': (-1.8312, -78.1834),
                'Colombia': (4.5709, -74.2973),
                'Venezuela': (6.4238, -66.5897),
                'Guyana': (4.8604, -58.9302),
                'Suriname': (3.9193, -56.0278),
                'French Guiana': (3.9339, -53.1258),
                'Mexico': (23.6345, -102.5528),
                'Guatemala': (15.7835, -90.2308),
                'Belize': (17.1899, -88.4976),
                'El Salvador': (13.7942, -88.8965),
                'Honduras': (15.1999, -86.2419),
                'Nicaragua': (12.8654, -85.2072),
                'Costa Rica': (9.9281, -84.0907),
                'Panama': (8.5380, -80.7821),
                'Cuba': (21.5218, -77.7812),
                'Jamaica': (18.1096, -77.2975),
                'Haiti': (18.9712, -72.2852),
                'Dominican Republic': (18.7357, -70.1627),
                'Puerto Rico': (18.2208, -66.5901),
                'Trinidad and Tobago': (10.6598, -61.5190),
                'Barbados': (13.1939, -59.5432),
                'Grenada': (12.1165, -61.6790),
                'Saint Vincent and the Grenadines': (12.9843, -61.2872),
                'Saint Lucia': (13.9094, -60.9789),
                'Dominica': (15.4150, -61.3710),
                'Antigua and Barbuda': (17.0608, -61.7964),
                'Saint Kitts and Nevis': (17.3578, -62.7830),
                'Bahamas': (25.0343, -77.3963),
                'Cayman Islands': (19.3133, -81.2546),
                'Turks and Caicos Islands': (21.6940, -71.7979),
                'British Virgin Islands': (18.4207, -64.6400),
                'U.S. Virgin Islands': (18.3358, -64.8963),
                'Aruba': (12.5211, -69.9683),
                'Curaçao': (12.1696, -68.9900),
                'Bonaire, Sint Eustatius and Saba': (12.1784, -68.2385),
                'Sint Maarten': (18.0425, -63.0548),
                'Saint Martin': (18.0708, -63.0501),
                'Saint Barthélemy': (17.9000, -62.8333),
                'Guadeloupe': (16.2650, -61.5510),
                'Martinique': (14.6415, -61.0242),
                'Saint Pierre and Miquelon': (46.8852, -56.3159),
                'Greenland': (71.7069, -42.6043),
                'Falkland Islands': (-51.7963, -59.5236),
                'South Georgia and the South Sandwich Islands': (-54.4296, -36.5879),
                'Bouvet Island': (-54.4208, 3.3464),
                'Heard Island and McDonald Islands': (-53.0818, 73.2207),
                'French Southern Territories': (-49.2804, 69.3486),
                'Norfolk Island': (-29.0408, 167.9547),
                'Christmas Island': (-10.4475, 105.6904),
                'Cocos (Keeling) Islands': (-12.1642, 96.8710),
                'Pitcairn': (-24.3768, -128.3242),
                'Tokelau': (-9.2002, -171.8484),
                'Niue': (-19.0544, -169.8672),
                'Cook Islands': (-21.2367, -159.7777),
                'American Samoa': (-14.2709, -170.1322),
                'Samoa': (-13.7590, -172.1046),
                'Tonga': (-21.1790, -175.1982),
                'Tuvalu': (-7.1095, 177.6493),
                'Kiribati': (-3.3704, -168.7340),
                'Marshall Islands': (7.1315, 171.1845),
                'Micronesia': (7.4256, 150.5508),
                'Palau': (7.5150, 134.5825),
                'Nauru': (-0.5228, 166.9315),
                'Vanuatu': (-15.3767, 166.9592),
                'New Caledonia': (-20.9043, 165.6180),
                'Fiji': (-17.7134, 178.0650),
                'Solomon Islands': (-9.6457, 160.1562),
                'Papua New Guinea': (-6.3150, 143.9555),
                'Timor-Leste': (-8.8742, 125.7275),
                'Indonesia': (-0.7893, 113.9213),
                'Malaysia': (4.2105, 108.9758),
                'Singapore': (1.3521, 103.8198),
                'Brunei': (4.5353, 114.7277),
                'Philippines': (12.8797, 121.7740),
                'Vietnam': (14.0583, 108.2772),
                'Laos': (19.8563, 102.4955),
                'Cambodia': (12.5657, 104.9910),
                'Thailand': (15.8700, 100.9925),
                'Myanmar': (21.9162, 95.9560),
                'Bangladesh': (23.6850, 90.3563),
                'Sri Lanka': (7.8731, 80.7718),
                'Maldives': (3.2028, 73.2207),
                'Nepal': (28.3949, 84.1240),
                'Bhutan': (27.5142, 90.4336),
                'Pakistan': (30.3753, 69.3451),
                'Afghanistan': (33.9391, 67.7100),
                'Iran': (32.4279, 53.6880),
                'Iraq': (33.2232, 43.6793),
                'Syria': (34.8021, 38.9968),
                'Lebanon': (33.8547, 35.8623),
                'Israel': (31.0461, 34.8516),
                'Palestine': (31.9522, 35.2332),
                'Jordan': (30.5852, 36.2384),
                'Saudi Arabia': (23.8859, 45.0792),
                'Yemen': (15.5527, 48.5164),
                'Oman': (21.4735, 55.9754),
                'United Arab Emirates': (23.4241, 53.8478),
                'Qatar': (25.3548, 51.1839),
                'Bahrain': (26.0667, 50.5577),
                'Kuwait': (29.3117, 47.4818),
                'Kazakhstan': (48.0196, 66.9237),
                'Uzbekistan': (41.3775, 64.5853),
                'Turkmenistan': (38.9697, 59.5563),
                'Tajikistan': (38.5358, 71.0965),
                'Kyrgyzstan': (41.2044, 74.7661),
                'Mongolia': (46.8625, 103.8467),
                'North Korea': (40.3399, 127.5101),
                'South Korea': (35.9078, 127.7669),
                'Taiwan': (23.6978, 121.1025),
                'Hong Kong': (22.3193, 114.1694),
                'Macau': (22.1987, 113.5439)
            }
            
            # Add data points for each country
            for country, count in country_counts.items():
                if country in country_coords:
                    lat, lon = country_coords[country]
                    
                    # Create hover text
                    hover_text = f"<b>{country}</b><br>"
                    hover_text += f"Samples: {count}<br>"
                    
                    # Add sample details if available
                    country_samples = metadata_df[metadata_df[country_col] == country]
                    if 'grade' in metadata_df.columns:
                        grades = country_samples['grade'].value_counts()
                        hover_text += f"Grades: {', '.join([f'{g}({c})' for g, c in grades.items()])}<br>"
                    
                    if 'idh' in metadata_df.columns:
                        idh_status = country_samples['idh'].value_counts()
                        hover_text += f"IDH: {', '.join([f'{i}({c})' for i, c in idh_status.items()])}<br>"
                    
                    # Determine marker color based on data
                    if 'grade' in metadata_df.columns:
                        # Color by most common grade
                        most_common_grade = country_samples['grade'].mode().iloc[0] if not country_samples['grade'].mode().empty else 'Unknown'
                        color_map = {'Grade 2': '#1f77b4', 'Grade 3': '#ff7f0e', 'Grade 4': '#d62728'}
                        marker_color = color_map.get(str(most_common_grade), '#7f7f7f')
                    else:
                        marker_color = '#1f77b4'
                    
                    # Add the trace for this country
                    fig.add_trace(go.Scattergeo(
                        lon=[lon],
                        lat=[lat],
                        mode='markers',
                        marker=dict(
                            size=min(count * 3 + 10, 50),  # Size based on count, max 50
                            color=marker_color,
                            line=dict(width=2, color='white'),
                            opacity=0.8
                        ),
                        text=hover_text,
                        hoverinfo='text',
                        name=f"{country} ({count})",
                        showlegend=True
                    ))
    
    return fig

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'tsv', 'txt'}

def create_plot_html(plot_func, *args, **kwargs):
    """Helper function to capture plotly plots and return HTML"""
    try:
        # Call the plot function first to get the result
        result = plot_func(*args, **kwargs)
        
        # For now, return a placeholder since the original functions use fig.show()
        # In a production environment, you'd want to modify the plotting functions
        # to return the figure object instead of showing it
        html_content = f"""
        <div class="alert alert-info">
            <h6>Plot Generated Successfully</h6>
            <p>The plot has been generated and should open in your browser.</p>
            <p>If the plot doesn't open automatically, check your browser's popup settings.</p>
        </div>
        """
        
        return html_content, result
    except Exception as e:
        return f"<p>Error generating plot: {str(e)}</p>", None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    file_type = request.form.get('file_type', 'auto')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            detected_type = None
            
            if file_type == 'metadata' or file_type == 'auto':
                data_manager.load_file_smart(filepath)
                session['metadata_loaded'] = True
                session['metadata_path'] = filepath
                detected_type = 'metadata'
                
                # Save metadata to cleaned_data folder for persistence
                if data_manager.metadata is not None:
                    data_manager.metadata.to_csv('cleaned_data/metadata_cleaned.csv', index=False)
            
            if file_type == 'expression' or file_type == 'auto':
                data_manager.load_file_smart(filepath)
                session['expression_loaded'] = True
                session['expression_path'] = filepath
                detected_type = 'expression'
                
                # Save expression to cleaned_data folder for persistence
                if data_manager.expression is not None:
                    data_manager.expression.to_csv('cleaned_data/expression_cleaned.csv', index=False)
            
            # Get data summary
            summary = {}
            if data_manager.metadata is not None:
                summary['metadata'] = {
                    'shape': [int(x) for x in data_manager.metadata.shape],
                    'columns': list(data_manager.metadata.columns),
                    'missing_values': int(data_manager.metadata.isnull().sum().sum()),
                    'preview': data_manager.metadata.head().to_html()
                }
            
            if data_manager.expression is not None:
                summary['expression'] = {
                    'shape': [int(x) for x in data_manager.expression.shape],
                    'columns': list(data_manager.expression.columns),
                    'missing_values': int(data_manager.expression.isnull().sum().sum()),
                    'preview': data_manager.expression.head().to_html()
                }
            
            return jsonify({
                'success': True,
                'message': f'File {filename} uploaded successfully',
                'file_type': detected_type,
                'summary': summary
            })
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/data_summary')
def data_summary():
    """Get summary of loaded data with enhanced preview (cached for performance)"""
    global _data_cache
    
    # Reload data if needed
    reload_data_if_needed()
    
    current_time = time.time()
    cache_valid = (current_time - _data_cache['cache_time']) < _data_cache['cache_ttl']
    
    summary = {}
    
    if data_manager.metadata is not None:
        # Use cached metadata stats if available and valid
        if cache_valid and _data_cache['metadata_stats']:
            summary['metadata'] = _data_cache['metadata_stats']
        else:
            print("Computing metadata stats...")
            # Show first 10 rows for faster preview (reduced from 20)
            preview_data = data_manager.metadata.head(10)
            metadata_stats = {
                'shape': [int(x) for x in data_manager.metadata.shape],
                'columns': list(data_manager.metadata.columns),
                'missing_values': int(data_manager.metadata.isnull().sum().sum()),
                'duplicates': int(data_manager.metadata.duplicated().sum()),
                'preview': preview_data.to_html(index=False, classes='table table-striped', table_id='metadata-preview')
            }
            _data_cache['metadata_stats'] = metadata_stats
            summary['metadata'] = metadata_stats
    else:
        summary['metadata'] = None
    
    if data_manager.expression is not None:
        # Use cached expression stats if available and valid
        if cache_valid and _data_cache['expression_stats']:
            summary['expression'] = _data_cache['expression_stats']
        else:
            print("Computing expression stats...")
            # Show first 10 samples, first 5 genes (reduced for speed)
            gene_cols = [col for col in data_manager.expression.columns if col != 'Sample'][:5]
            preview_cols = ['Sample'] + gene_cols
            preview_data = data_manager.expression[preview_cols].head(10)
            expression_stats = {
                'shape': [int(x) for x in data_manager.expression.shape],
                'columns': list(data_manager.expression.columns),
                'missing_values': int(data_manager.expression.isnull().sum().sum()),
                'duplicates': int(data_manager.expression.duplicated().sum()),
                'preview': preview_data.to_html(index=False, classes='table table-striped', table_id='expression-preview')
            }
            _data_cache['expression_stats'] = expression_stats
            summary['expression'] = expression_stats
    else:
        summary['expression'] = None
    
    # Update cache time if we computed new stats
    if not cache_valid:
        _data_cache['cache_time'] = current_time
    
    return jsonify(summary)

@app.route('/full_data_view')
def full_data_view():
    """Get full dataset view for metadata and expression data"""
    reload_data_if_needed()
    
    view_data = {}
    
    if data_manager.metadata is not None:
        # Return all metadata as HTML table
        metadata_html = data_manager.metadata.to_html(
            index=False, 
            classes='table table-striped table-hover', 
            table_id='full-metadata-table',
            escape=False
        )
        view_data['metadata'] = {
            'shape': [int(x) for x in data_manager.metadata.shape],
            'full_data': metadata_html,
            'total_rows': int(data_manager.metadata.shape[0]),
            'total_columns': int(data_manager.metadata.shape[1])
        }
    
    if data_manager.expression is not None:
        # Return all expression data as HTML table
        expression_html = data_manager.expression.to_html(
            index=False, 
            classes='table table-striped table-hover', 
            table_id='full-expression-table',
            escape=False
        )
        view_data['expression'] = {
            'shape': [int(x) for x in data_manager.expression.shape],
            'full_data': expression_html,
            'total_rows': int(data_manager.expression.shape[0]),
            'total_columns': int(data_manager.expression.shape[1])
        }
    
    if not view_data:
        return jsonify({'error': 'No data loaded. Please upload or download datasets first.'}), 400
    
    return jsonify(view_data)

@app.route('/view_metadata_data')
def view_metadata_data():
    """Get paginated metadata dataset for better performance"""
    reload_data_if_needed()
    
    view_data = {}
    
    if data_manager.metadata is not None:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)  # Show 50 rows per page
        
        total_rows = len(data_manager.metadata)
        total_pages = (total_rows + per_page - 1) // per_page
        
        # Calculate start and end indices
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_rows)
        
        # Get the current page of data
        current_page_data = data_manager.metadata.iloc[start_idx:end_idx]
        
        # Convert to HTML table
        metadata_html = current_page_data.to_html(
            index=False, 
            classes='table table-striped table-hover', 
            table_id='full-metadata-table',
            escape=False
        )
        
        view_data['metadata'] = {
            'shape': [int(x) for x in data_manager.metadata.shape],
            'current_data': metadata_html,
            'total_rows': total_rows,
            'total_columns': int(data_manager.metadata.shape[1]),
            'current_page': page,
            'total_pages': total_pages,
            'per_page': per_page,
            'start_row': start_idx + 1,
            'end_row': end_idx
        }
    else:
        view_data['error'] = 'No metadata loaded. Please upload or download data first.'
        view_data['metadata'] = None
    
    return jsonify(view_data)

@app.route('/view_expression_data')
def view_expression_data():
    """Get paginated expression dataset for better performance"""
    reload_data_if_needed()
    
    view_data = {}
    
    if data_manager.expression is not None:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)  # Show 50 rows per page
        
        total_rows = len(data_manager.expression)
        total_pages = (total_rows + per_page - 1) // per_page
        
        # Calculate start and end indices
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_rows)
        
        # Get the current page of data
        current_page_data = data_manager.expression.iloc[start_idx:end_idx]
        
        # Convert to HTML table
        expression_html = current_page_data.to_html(
            index=False, 
            classes='table table-striped table-hover', 
            table_id='full-expression-table',
            escape=False
        )
        
        view_data['expression'] = {
            'shape': [int(x) for x in data_manager.expression.shape],
            'current_data': expression_html,
            'total_rows': total_rows,
            'total_columns': int(data_manager.expression.shape[1]),
            'current_page': page,
            'total_pages': total_pages,
            'per_page': per_page,
            'start_row': start_idx + 1,
            'end_row': end_idx
        }
    else:
        view_data['error'] = 'No expression data loaded. Please upload or download data first.'
        view_data['expression'] = None
    
    return jsonify(view_data)

def dynamic_filter_metadata(df, filters):
    """Dynamic metadata filtering based on column availability"""
    filtered_df = df.copy()
    
    for filter_name, filter_data in filters.items():
        if not filter_data or not filter_data.get('value') or not filter_data.get('column'):
            continue
            
        column = filter_data['column']
        value = filter_data['value']
        
        if column not in df.columns:
            continue
            
        if filter_name == 'age_range':
            # Handle age range filtering
            try:
                age_min, age_max = map(int, value.split('-'))
                filtered_df = filtered_df[(filtered_df[column] >= age_min) & (filtered_df[column] <= age_max)]
            except (ValueError, AttributeError):
                continue
        else:
            # Handle categorical filtering (case insensitive partial match)
            filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(value, case=False, na=False)]
    
    return filtered_df

@app.route('/column_values', methods=['POST'])
def get_column_values():
    if data_manager.metadata is None:
        return jsonify({'error': 'No metadata loaded'}), 400
    
    data = request.get_json()
    column = data.get('column')
    
    if not column or column not in data_manager.metadata.columns:
        return jsonify({'error': f'Column {column} not found'}), 400
    
    try:
        # Get unique values and their counts
        value_counts = data_manager.metadata[column].value_counts().sort_index()
        values = value_counts.index.astype(str).tolist()
        counts = value_counts.values.tolist()
        
        return jsonify({
            'values': values,
            'counts': counts,
            'total_unique': len(values)
        })
        
    except Exception as e:
        print(f"Error getting column values: {str(e)}")
        return jsonify({'error': f'Error getting column values: {str(e)}'}), 500

@app.route('/filter_metadata', methods=['POST'])
def filter_metadata_route():
    if data_manager.metadata is None:
        return jsonify({'error': 'No metadata loaded'}), 400
    
    data = request.get_json()
    
    # Handle both old format (for compatibility) and new format
    if 'column' in data and 'values' in data:
        # New format - direct column filtering
        column = data.get('column')
        values = data.get('values')
        
        if column not in data_manager.metadata.columns:
            return jsonify({'error': f'Column {column} not found'}), 400
        
        try:
            # Apply filter
            filtered_df = data_manager.metadata[data_manager.metadata[column].astype(str).isin(values)]
            
            # Save filtered data
            filtered_path = os.path.join('cleaned_data', 'metadata_filtered.csv')
            os.makedirs('cleaned_data', exist_ok=True)
            filtered_df.to_csv(filtered_path, index=False)
            
            return jsonify({
                'success': True,
                'filtered_count': len(filtered_df),
                'original_count': len(data_manager.metadata),
                'preview': filtered_df.head().to_html(classes='table table-striped'),
                'download_path': filtered_path
            })
            
        except Exception as e:
            print(f"Error filtering data: {str(e)}")
            return jsonify({'error': f'Error filtering data: {str(e)}'}), 500
    
    else:
        # Old format - dynamic column support
        filters = {}
        
        if data.get('grade') and data.get('grade_column'):
            filters['grade'] = {
                'value': data.get('grade'),
                'column': data.get('grade_column')
            }
        
        if data.get('idh') and data.get('idh_column'):
            filters['idh'] = {
                'value': data.get('idh'),
                'column': data.get('idh_column')
            }
        
        if data.get('age_range') and data.get('age_column'):
            filters['age_range'] = {
                'value': data.get('age_range'),
                'column': data.get('age_column')
            }
        
        try:
            if filters:
                filtered_df = dynamic_filter_metadata(data_manager.metadata, filters)
            else:
                filtered_df = data_manager.metadata.copy()
            
            # Save filtered data
            filtered_path = os.path.join('cleaned_data', 'metadata_filtered.csv')
            os.makedirs('cleaned_data', exist_ok=True)
            filtered_df.to_csv(filtered_path, index=False)
            
            return jsonify({
                'success': True,
                'filtered_count': len(filtered_df),
                'original_count': len(data_manager.metadata),
                'preview': filtered_df.head().to_html(classes='table table-striped'),
                'download_path': filtered_path
            })
            
        except Exception as e:
            print(f"Error filtering data: {str(e)}")
            return jsonify({'error': f'Error filtering data: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download endpoint for filtered data files"""
    try:
        return send_from_directory('cleaned_data', filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'File not found: {str(e)}'}), 404

@app.route('/reset_data', methods=['POST'])
def reset_data():
    """Reset all data and cache for fresh analysis"""
    global data_manager, _data_cache
    
    try:
        # Clear data manager
        data_manager.metadata = None
        data_manager.expression = None
        
        # Clear cache
        _data_cache['metadata_stats'] = None
        _data_cache['expression_stats'] = None
        _data_cache['metadata_preview'] = None
        _data_cache['expression_preview'] = None
        _data_cache['cache_time'] = 0
        
        # Clear session
        session.clear()
        
        # Remove saved files to completely reset
        import glob
        import os
        
        # Remove all saved data files
        for file_path in glob.glob('cleaned_data/*.csv'):
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Removed file: {file_path}")
        
        return jsonify({
            'success': True,
            'message': 'All data has been completely reset. You can now start fresh with new datasets.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error resetting data: {str(e)}'
        }), 500

@app.route('/plot_pca', methods=['POST'])
def plot_pca_route():
    if data_manager.expression is None:
        return jsonify({'error': 'No expression data loaded'}), 400
    
    data = request.get_json()
    color_by = data.get('color_by')
    
    try:
        html_content, _ = create_plot_html(
            plot_pca,
            data_manager.expression,
            data_manager.metadata if data_manager.metadata is not None else None,
            color_by=color_by if color_by else None
        )
        
        return jsonify({
            'success': True,
            'plot_html': html_content
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating PCA plot: {str(e)}'}), 500

@app.route('/plot_umap', methods=['POST'])
def plot_umap_route():
    if data_manager.expression is None:
        return jsonify({'error': 'No expression data loaded'}), 400
    
    data = request.get_json()
    color_by = data.get('color_by')
    
    try:
        html_content, _ = create_plot_html(
            plot_umap,
            data_manager.expression,
            data_manager.metadata if data_manager.metadata is not None else None,
            color_by=color_by if color_by else None
        )
        
        return jsonify({
            'success': True,
            'plot_html': html_content
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating UMAP plot: {str(e)}'}), 500

@app.route('/differential_expression', methods=['POST'])
def differential_expression_route():
    if data_manager.expression is None or data_manager.metadata is None:
        return jsonify({'error': 'Both expression and metadata data must be loaded'}), 400
    
    data = request.get_json()
    group_col = data.get('group_col', 'grade')
    group_1 = data.get('group_1', 'Grade 2')
    group_2 = data.get('group_2', 'Grade 3')
    
    try:
        result_df = perform_differential_expression(
            data_manager.expression,
            data_manager.metadata,
            group_col=group_col,
            group_1=group_1,
            group_2=group_2
        )
        
        # Get significant results
        significant_results = result_df[result_df['adj_p_value'] < 0.05]
        
        return jsonify({
            'success': True,
            'total_genes': len(result_df),
            'significant_genes': len(significant_results),
            'top_results': result_df.head(20).to_dict('records'),
            'significant_results': significant_results.head(20).to_dict('records')
        })
        
    except Exception as e:
        return jsonify({'error': f'Error performing differential expression: {str(e)}'}), 500

@app.route('/gene_expression', methods=['POST'])
def gene_expression_route():
    if data_manager.expression is None or data_manager.metadata is None:
        return jsonify({'error': 'Both expression and metadata data must be loaded'}), 400
    
    data = request.get_json()
    gene_name = data.get('gene_name')
    group_col = data.get('group_col', 'grade')
    
    try:
        html_content, _ = create_plot_html(
            explore_gene_expression,
            data_manager.expression,
            data_manager.metadata,
            gene_name,
            group_col
        )
        
        return jsonify({
            'success': True,
            'plot_html': html_content
        })
        
    except Exception as e:
        return jsonify({'error': f'Error exploring gene expression: {str(e)}'}), 500

@app.route('/heatmap', methods=['POST'])
def heatmap_route():
    if data_manager.expression is None:
        return jsonify({'error': 'No expression data loaded'}), 400
    
    data = request.get_json()
    genes = data.get('genes', [])
    group_col = data.get('group_col')
    
    try:
        html_content, _ = create_plot_html(
            plot_expression_heatmap,
            data_manager.expression,
            data_manager.metadata if data_manager.metadata is not None else None,
            genes=genes,
            group_col=group_col if group_col else None
        )
        
        return jsonify({
            'success': True,
            'plot_html': html_content
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating heatmap: {str(e)}'}), 500

@app.route('/patient_geomap', methods=['POST'])
def patient_geomap_route():
    """Generate patient geographic map"""
    reload_data_if_needed()
    
    if data_manager.metadata is None:
        return jsonify({
            'success': False,
            'error': 'No metadata loaded. Please upload or download data first.'
        })
    
    try:
        # Get filter parameters if any
        data = request.get_json() or {}
        filter_applied = data.get('filter_applied')
        color_by = data.get('color_by', 'country')
        zoom_to_region = data.get('zoom_to_region', False)
        
        # Use the plot_patient_geomap function which saves to file and opens in browser
        from Patient_geomap import plot_patient_geomap
        
        plot_patient_geomap(
            data_manager.metadata, 
            filter_applied=filter_applied,
            color_by=color_by,
            zoom_to_region=zoom_to_region
        )
        
        return jsonify({
            'success': True,
            'message': 'Patient geographic map generated and opened in browser successfully'
        })
        
    except Exception as e:
        print(f"Error in patient_geomap_route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error generating map: {str(e)}'
        }), 500

@app.route('/world_map')
def get_world_map():
    """Get initial world map without data points"""
    try:
        import plotly.express as px
        
        # Create empty world map
        fig = px.scatter_geo(
            projection='natural earth',
            title='Glioma Patient Map - Upload Data to See Patient Locations'
        )
        
        # Add annotation
        fig.add_annotation(
            text="Upload metadata with country information to visualize patient locations on the map",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="blue"),
            xanchor='center',
            yanchor='middle'
        )
        
        # Update layout
        fig.update_layout(
            height=600,
            margin=dict(l=0, r=0, t=50, b=50),
            showlegend=False
        )
        
        # Save map to HTML file
        fig.write_html("world_map.html")
        print("World map saved to 'world_map.html'.")
        
        # Show map in browser (non-blocking)
        try:
            import subprocess
            subprocess.Popen(['open', 'world_map.html'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("World map opened in your browser.")
        except Exception as e:
            print(f"Could not open world map automatically. Please open 'world_map.html' manually in your browser.")
        
        return jsonify({
            'success': True,
            'message': 'World map generated and opened in browser successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error generating world map: {str(e)}'}), 500

@app.route('/geo_download', methods=['POST'])
def geo_download():
    data = request.get_json()
    geo_id = data.get('geo_id')
    
    if not geo_id:
        return jsonify({'error': 'GEO ID is required'}), 400
    
    try:
        from Utils import fetch_and_format_geo
        
        print(f"Downloading GEO dataset {geo_id}...")
        meta_df, expr_df = fetch_and_format_geo(geo_id)
        
        if meta_df is None or expr_df is None:
            return jsonify({'error': f'Failed to download GEO dataset {geo_id}'}), 500
        
        # Load into memory
        data_manager.load_metadata_df(meta_df)
        data_manager.load_expression_df(expr_df)
        
        # Save to CSVs
        meta_df.to_csv(f"cleaned_data/{geo_id}_metadata.csv", index=False)
        expr_df.to_csv(f"cleaned_data/{geo_id}_expression.csv", index=False)
        
        # Get summary
        summary = {}
        if data_manager.metadata is not None:
            summary['metadata'] = {
                'shape': [int(x) for x in data_manager.metadata.shape],
                'columns': list(data_manager.metadata.columns),
                'missing_values': int(data_manager.metadata.isnull().sum().sum()),
                'preview': data_manager.metadata.head().to_html()
            }
        
        if data_manager.expression is not None:
            summary['expression'] = {
                'shape': [int(x) for x in data_manager.expression.shape],
                'columns': list(data_manager.expression.columns),
                'missing_values': int(data_manager.expression.isnull().sum().sum()),
                'preview': data_manager.expression.head().to_html()
            }
        
        return jsonify({
            'success': True,
            'message': f'GEO dataset {geo_id} downloaded successfully',
            'samples': int(meta_df.shape[0]),
            'genes': int(expr_df.shape[1] - 1),  # Exclude Sample column
            'summary': summary
        })
        
    except Exception as e:
        print(f"Error downloading GEO dataset: {str(e)}")
        return jsonify({'error': f'Error downloading GEO dataset: {str(e)}'}), 500

@app.route('/format_dataset', methods=['POST'])
def format_dataset():
    try:
        # Get uploaded files
        expression_file = request.files.get('expressionFile')
        metadata_file = request.files.get('metadataFile')
        expr_sample_col = request.form.get('exprSampleCol', 'Sample')
        meta_sample_col = request.form.get('metaSampleCol', 'SampleID')
        
        if not expression_file or not metadata_file:
            return jsonify({'error': 'Both expression and metadata files are required'}), 400
        
        # Save uploaded files
        expr_filename = secure_filename(expression_file.filename)
        meta_filename = secure_filename(metadata_file.filename)
        expr_path = os.path.join(app.config['UPLOAD_FOLDER'], expr_filename)
        meta_path = os.path.join(app.config['UPLOAD_FOLDER'], meta_filename)
        
        expression_file.save(expr_path)
        metadata_file.save(meta_path)
        
        # Format the dataset
        from Format_data import format_for_gliomascope
        format_for_gliomascope(expr_path, meta_path, expr_sample_col, meta_sample_col)
        
        # Load formatted data
        cleaned_expr = "cleaned_data/expression_cleaned.csv"
        cleaned_meta = "cleaned_data/metadata_cleaned.csv"
        
        if os.path.exists(cleaned_expr):
            data_manager.load_expression(cleaned_expr)
        if os.path.exists(cleaned_meta):
            data_manager.load_file_smart(cleaned_meta)
        
        # Get summary
        summary = {}
        expression_samples = 0
        metadata_samples = 0
        matched_samples = 0
        
        if data_manager.metadata is not None:
            metadata_samples = int(data_manager.metadata.shape[0])
            summary['metadata'] = {
                'shape': [int(x) for x in data_manager.metadata.shape],
                'columns': list(data_manager.metadata.columns),
                'missing_values': int(data_manager.metadata.isnull().sum().sum()),
                'preview': data_manager.metadata.head().to_html()
            }
        
        if data_manager.expression is not None:
            expression_samples = int(data_manager.expression.shape[0])
            summary['expression'] = {
                'shape': [int(x) for x in data_manager.expression.shape],
                'columns': list(data_manager.expression.columns),
                'missing_values': int(data_manager.expression.isnull().sum().sum()),
                'preview': data_manager.expression.head().to_html()
            }
        
        if data_manager.merged is not None:
            matched_samples = int(data_manager.merged.shape[0])
        
        return jsonify({
            'success': True,
            'message': 'Dataset formatted and loaded successfully',
            'expression_samples': expression_samples,
            'metadata_samples': metadata_samples,
            'matched_samples': matched_samples,
            'summary': summary
        })
        
    except Exception as e:
        print(f"Error formatting dataset: {str(e)}")
        return jsonify({'error': f'Error formatting dataset: {str(e)}'}), 500

@app.route('/chromosome_mapping', methods=['POST'])
def chromosome_mapping():
    if data_manager.expression is None:
        return jsonify({'error': 'No expression data loaded'}), 400
    
    data = request.get_json()
    genes = data.get('genes', [])
    chromosome_filter = data.get('chromosome_filter')
    
    if not genes:
        return jsonify({'error': 'No genes provided'}), 400
    
    try:
        from Gene_explorer import map_gene_to_chromosome
        
        # For now, return a placeholder result
        # In a full implementation, you would call the actual chromosome mapping function
        html_content = f"""
        <div class="alert alert-info">
            <h6>Chromosome Mapping Results</h6>
            <p>Genes mapped: {', '.join(genes)}</p>
            <p>Chromosome filter: {chromosome_filter or 'All chromosomes'}</p>
            <p>The chromosome mapping visualization would appear here.</p>
            <p><em>Note: Full chromosome mapping implementation requires additional gene annotation data.</em></p>
        </div>
        """
        
        return jsonify({
            'success': True,
            'plot_html': html_content
        })
        
    except Exception as e:
        return jsonify({'error': f'Error performing chromosome mapping: {str(e)}'}), 500

@app.route('/available_genes')
def available_genes():
    if data_manager.expression is None:
        return jsonify({'error': 'No expression data loaded'}), 400
    
    try:
        genes = [col for col in data_manager.expression.columns if col.lower() != 'sample']
        return jsonify({
            'success': True,
            'genes': genes,
            'count': len(genes)
        })
    except Exception as e:
        return jsonify({'error': f'Error getting available genes: {str(e)}'}), 500

@app.route('/available_columns')
def available_columns():
    """Get available metadata columns for dropdown menus"""
    reload_data_if_needed()
    
    if data_manager.metadata is None:
        return jsonify({
            'success': False,
            'error': 'No metadata loaded. Please upload or download data first.',
            'columns': []
        })
    
    # Get all columns except 'Sample' (which is used for merging)
    available_cols = [col for col in data_manager.metadata.columns if col != 'Sample']
    
    return jsonify({
        'success': True,
        'columns': available_cols
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 