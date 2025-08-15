# GliomaScope Web Interface

🧬 **Advanced Glioma Transcriptomics Analysis Platform - Web Edition**

## Overview

The GliomaScope Web Interface provides a modern, intuitive web-based GUI for all 13 functions available in the terminal version. Built with a DNA matrix biotech theme, it offers a professional and user-friendly experience for glioma research.

## Features

### 🔬 **Complete Function Coverage**
All 13 terminal functions are available with enhanced web interfaces:

1. **GEO Dataset Download** - Download datasets from NCBI GEO database
2. **Format Dataset** - Upload and format custom CSV/TSV files
3. **Upload Metadata** - Upload sample metadata files
4. **Upload Expression** - Upload gene expression data
5. **Data Exploration** - Explore, filter, and preview datasets
6. **Geographic Visualization** - Create interactive world maps
7. **PCA Analysis** - Principal Component Analysis with customization
8. **UMAP Analysis** - Non-linear dimensionality reduction
9. **Differential Expression** - Compare gene expression between groups
10. **Gene Exploration** - Individual gene expression analysis
11. **Chromosome Mapping** - Map genes to chromosomal locations
12. **Heatmap Visualization** - Generate expression heatmaps
13. **About & Help** - Documentation and system information

### 🎨 **DNA Matrix Biotech Theme**
- Animated DNA helix background
- Glass morphism design elements
- Professional biotech color scheme
- Responsive design for all devices
- Interactive UI elements with smooth animations

### 🚀 **Modern Web Technologies**
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript ES6+
- **Backend**: Flask (Python)
- **Visualization**: Plotly.js for interactive charts
- **Real-time**: AJAX for seamless data processing

## Quick Start

### 1. Start the Web Application
```bash
# Option 1: Using the startup script (recommended)
python3 run_app.py

# Option 2: Direct Flask app
python3 -c "from app import app; app.run(host='0.0.0.0', port=5002)"
```

### 2. Access the Interface
Open your web browser and navigate to:
```
http://localhost:5001
```

The browser should open automatically when using `run_app.py`.

### 3. Basic Workflow
1. **Upload Data**: Use functions 1-4 to load your data
2. **Explore**: Use function 5 to examine your dataset
3. **Visualize**: Use functions 6-8 for plots and maps
4. **Analyze**: Use functions 9-12 for gene expression analysis

## Function Details

### 🔄 **1. GEO Dataset Download**
- **Purpose**: Download pre-formatted datasets from NCBI GEO
- **Suggested Datasets**: GSE15824, GSE16011, GSE43378, GSE86574
- **Features**: Automatic metadata and expression extraction
- **Output**: Ready-to-analyze datasets

### 📂 **2. Format Dataset**
- **Purpose**: Upload and format your own CSV/TSV files
- **Requirements**: Expression file + Metadata file
- **Configuration**: Custom sample ID column mapping
- **Output**: Standardized, cleaned datasets

### 📊 **3-4. Upload Data**
- **Purpose**: Individual file uploads for metadata/expression
- **Supported Formats**: CSV, TSV, TXT
- **Auto-Detection**: Intelligent file type recognition
- **Validation**: Real-time data validation and preview

### 🔍 **5. Data Exploration**
- **Summary Statistics**: Sample counts, missing values, data types
- **Interactive Filtering**: Filter by grade, IDH status, age ranges
- **Data Preview**: Interactive table views
- **Export Options**: Download filtered datasets

### 🌍 **6. Geographic Visualization**
- **World Maps**: Interactive Plotly-based maps
- **Data Points**: Study locations, sample distributions
- **Customization**: Zoom controls, different map types
- **Real-time**: Automatic updates when data changes

### 📈 **7. PCA Analysis**
- **Dimensionality Reduction**: Principal Component Analysis
- **Color Coding**: Group samples by metadata columns
- **Component Selection**: PC1 vs PC2, PC1 vs PC3, PC2 vs PC3
- **Interactive**: Zoom, pan, hover information

### 🔀 **8. UMAP Analysis**
- **Non-linear Reduction**: UMAP algorithm implementation
- **Parameter Control**: Neighbors, minimum distance settings
- **Clustering**: Better separation than PCA for complex data
- **Visualization**: Interactive scatter plots

### 🧬 **9. Differential Expression**
- **Statistical Analysis**: Compare gene expression between groups
- **Customizable**: Choose comparison groups and p-value thresholds
- **Results**: Significant genes table with fold changes
- **Export**: Download results for further analysis

### 🔬 **10. Gene Exploration**
- **Individual Genes**: Detailed expression analysis for specific genes
- **Plot Types**: Violin, box, scatter, heatmap options
- **Gene Browser**: Search and select from available genes
- **Group Comparison**: Expression across different sample groups

### 📍 **11. Chromosome Mapping**
- **Gene Location**: Map genes to chromosomal positions
- **Multiple Genes**: Batch processing for gene sets
- **Chromosome Filter**: Focus on specific chromosomes
- **Ideogram**: Visual chromosome representation

### 🔥 **12. Heatmap Visualization**
- **Expression Patterns**: Multi-gene expression heatmaps
- **Clustering**: Sample and gene clustering options
- **Color Scales**: Multiple color scheme options
- **Customization**: Group samples, adjust clustering

## Technical Architecture

### Backend (Flask)
```
app.py                 # Main Flask application
├── Routes             # API endpoints for each function
├── Data Management    # Integration with existing modules
├── File Processing    # Upload and format handling
└── Visualization      # Plot generation and serving
```

### Frontend Structure
```
templates/
├── index.html         # Main SPA template
static/
├── css/
│   └── style.css      # DNA matrix theme styling
└── js/
    └── app.js         # Application logic and AJAX
```

### Integration with Terminal
- **Shared Modules**: Uses same Python modules as terminal version
- **Data Compatibility**: Same data formats and processing
- **No Conflicts**: Can run simultaneously with terminal version
- **Consistent Results**: Identical analysis outputs

## Compatibility

### Browser Support
- **Modern Browsers**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Features**: ES6+, CSS Grid, Flexbox, WebGL (for Plotly)
- **Responsive**: Mobile and tablet friendly

### System Requirements
- **Python**: 3.8+ (same as terminal version)
- **Memory**: 2GB+ RAM recommended for large datasets
- **Storage**: Same as terminal version
- **Network**: Local or network accessible

## Development Notes

### Adding New Functions
1. Add HTML section in `templates/index.html`
2. Add CSS styling in `static/css/style.css`
3. Add JavaScript handler in `static/js/app.js`
4. Add Flask route in `app.py`
5. Update sidebar navigation

### Customization
- **Theme Colors**: Modify CSS variables in `:root`
- **Icons**: FontAwesome classes can be changed
- **Layout**: Bootstrap grid system for responsiveness
- **Animations**: CSS animations and transitions

### Security Considerations
- **File Uploads**: Filename sanitization with `secure_filename()`
- **File Size**: 100MB limit configured
- **Input Validation**: Server-side validation for all inputs
- **Error Handling**: Graceful error handling with user feedback

## Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Kill existing processes on port 5001
lsof -ti:5001 | xargs kill -9
```

**2. Module Import Errors**
```bash
# Install missing dependencies
pip3 install -r requirements.txt
```

**3. File Upload Issues**
- Check file permissions in `uploads/` directory
- Verify file format (CSV, TSV, TXT only)
- Ensure file size is under 100MB

**4. Browser Compatibility**
- Clear browser cache
- Try a different browser
- Check JavaScript console for errors

### Debug Mode
The application runs in debug mode by default for development. For production:
```python
app.run(debug=False, host='0.0.0.0', port=5002)
```

## Future Enhancements

- **User Authentication**: Multi-user support with sessions
- **Project Management**: Save and load analysis projects
- **Advanced Visualizations**: Additional plot types and customization
- **API Documentation**: RESTful API documentation with Swagger
- **Performance Optimization**: Caching and background processing
- **Cloud Integration**: Support for cloud storage and computing

---

**Note**: This web interface complements the terminal version and can be used simultaneously. All analysis functions maintain the same scientific accuracy and output quality as the original command-line interface.