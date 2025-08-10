# GliomaScope Web Application

A modern, interactive web application for advanced glioma transcriptomics analysis with a beautiful biotech/DNA matrix theme.

## Features

### **Data Management**
- **Smart File Upload**: Intelligent detection of metadata vs expression data
- **Data Validation**: Automatic validation and cleaning of uploaded files
- **Data Summary**: Real-time data overview and statistics

### **Advanced Analytics**
- **PCA Analysis**: Principal Component Analysis with customizable coloring
- **UMAP Visualization**: Uniform Manifold Approximation and Projection
- **Differential Expression**: Statistical analysis between groups
- **Gene Expression Exploration**: Individual gene analysis with boxplots

### 🗺️ **Geographic Mapping**
- **Patient Location Mapping**: Visualize patient geographic distribution
- **Study Summary Maps**: Aggregate study-level geographic analysis
- **Interactive Maps**: Zoom and pan functionality

### 🔥 **Heatmap Visualization**
- **Gene Expression Heatmaps**: Multi-gene expression patterns
- **Customizable Grouping**: Group by metadata columns
- **Standardized Scaling**: Z-score normalization for better visualization

### 📈 **Data Filtering & Export**
- **Metadata Filtering**: Filter by grade, IDH status, age range
- **Export Functionality**: Download filtered and processed data
- **Results Download**: Export analysis results as CSV files

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd GliomaScope
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the web application**
   Open your browser and navigate to: `http://localhost:5000`

## Usage Guide

### 1. Data Upload
- **Supported Formats**: CSV, TSV, TXT files
- **File Types**: 
  - **Metadata**: Patient information (age, sex, grade, IDH status, etc.)
  - **Expression Data**: Gene expression matrix
- **Auto-detection**: The system automatically detects file type based on content

### 2. Data Analysis Workflow

#### Step 1: Upload Your Data
1. Navigate to the "Data Upload" section
2. Select your file (metadata or expression data)
3. Choose file type or let the system auto-detect
4. Click "Upload File"

#### Step 2: Explore Your Data
1. View data summary in the right panel
2. Check data quality and missing values
3. Review column names and data types

#### Step 3: Filter Data (Optional)
1. Go to "Data Analysis" section
2. Apply filters by grade, IDH status, or age range
3. Download filtered data if needed

#### Step 4: Run Visualizations
1. **PCA Analysis**: Reduce dimensionality and visualize sample clustering
2. **UMAP Analysis**: Non-linear dimensionality reduction
3. **Gene Expression**: Explore individual gene patterns
4. **Heatmaps**: Visualize multiple gene expression patterns

#### Step 5: Differential Expression Analysis
1. Specify groups to compare (e.g., Grade 2 vs Grade 3)
2. Run analysis to identify differentially expressed genes
3. Review results table with statistics

#### Step 6: Geographic Mapping
1. Generate patient location maps
2. Choose between individual patient or study summary views
3. Enable zoom functionality for detailed exploration

### 3. Download Results
- All processed data and results can be downloaded as CSV files
- Use the "Results & Downloads" section to access files

## File Format Requirements

### Metadata File
Should contain a `Sample_ID` column and patient information:
```csv
Sample_ID,age,sex,grade,idh,country
Sample_001,45,M,Grade 2,WT,USA
Sample_002,52,F,Grade 3,MUT,Canada
...
```

### Expression Data File
Should contain a `Sample_ID` column and gene expression values:
```csv
Sample_ID,Gene1,Gene2,Gene3,...
Sample_001,10.5,8.2,12.1,...
Sample_002,9.8,11.3,7.9,...
...
```

## Technical Details

### Architecture
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Visualization**: Plotly.js
- **Styling**: Bootstrap 5 with custom biotech theme

### Key Components
- `app.py`: Main Flask application
- `templates/index.html`: Main web interface
- `static/css/style.css`: Custom styling with DNA matrix theme
- `static/js/app.js`: Interactive functionality
- `Data_loader.py`: Data management and validation
- `Dimensionality_Reduction.py`: PCA and UMAP analysis
- `Differential_expression.py`: Statistical analysis
- `Patient_geomap.py`: Geographic mapping
- `Gene_explorer.py`: Gene-specific analysis
- `Heatmap_visualisation.py`: Heatmap generation

### Dependencies
- **Core**: Flask, pandas, numpy
- **Machine Learning**: scikit-learn, umap-learn
- **Statistics**: scipy, statsmodels
- **Visualization**: plotly, seaborn, matplotlib
- **Geographic**: geopy

## Customization

### Theme Customization
The application uses CSS custom properties for easy theming:
```css
:root {
    --primary-color: #00d4ff;
    --secondary-color: #0099cc;
    --accent-color: #ff6b35;
    /* ... more variables */
}
```

### Adding New Features
1. Create new Python modules in the root directory
2. Add routes to `app.py`
3. Create corresponding frontend components
4. Update the navigation and UI as needed

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in app.py
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

2. **Missing dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **File upload errors**
   - Check file format (CSV, TSV, TXT)
   - Ensure Sample_ID column is present
   - Verify file size (max 100MB)

4. **Memory issues with large datasets**
   - Consider sampling data for initial exploration
   - Use data filtering to reduce dataset size
   - Close other applications to free memory

### Performance Tips
- Use smaller datasets for initial testing
- Enable data filtering to reduce processing time
- Close browser tabs to free memory
- Use SSD storage for faster file I/O

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

## Acknowledgments

- Built with Flask and modern web technologies
- Inspired by the need for accessible bioinformatics tools
- Designed for researchers and clinicians working with glioma data

---

**GliomaScope** - Designed for all. Built for insight. 