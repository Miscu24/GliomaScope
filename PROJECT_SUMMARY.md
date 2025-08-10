# GliomaScope Project Summary

## 🧬 Project Overview
GliomaScope is a comprehensive bioinformatics platform for glioma transcriptomics analysis, featuring both web and terminal interfaces. The project provides advanced data visualization, statistical analysis, and genomic exploration tools designed for researchers and clinicians.

## 🎯 Key Features

### **Dual Interface System**
- **🌐 Web Interface**: Modern Flask-based web application with DNA matrix theme
- **💻 Terminal Interface**: Command-line version with identical functionality
- **🔄 Shared Core**: Both interfaces use the same underlying analysis modules

### **Data Management**
- **📊 Smart File Upload**: Automatic detection of metadata vs expression data
- **🔍 Data Validation**: Comprehensive validation and cleaning pipelines
- **📈 Real-time Summary**: Live data overview and statistics
- **🔄 GEO Integration**: Direct download from NCBI GEO database

### **Advanced Analytics**
- **📊 PCA Analysis**: Principal Component Analysis with customizable coloring
- **🗺️ UMAP Visualization**: Non-linear dimensionality reduction
- **📈 Differential Expression**: Statistical analysis between groups
- **🧬 Gene Expression**: Individual gene analysis with interactive plots
- **🔥 Heatmap Visualization**: Multi-gene expression patterns
- **🌍 Geographic Mapping**: Patient location and study distribution maps
- **🧬 Chromosome Mapping**: Gene-to-chromosome location mapping

## 🏗️ Project Structure

```
GliomaScope/
├── src/                          # Core source code
│   ├── analysis/                 # Statistical analysis modules
│   │   ├── Differential_expression.py
│   │   └── Gene_explorer.py
│   ├── visualization/            # Plotting and visualization
│   │   ├── Dimensionality_Reduction.py
│   │   ├── Heatmap_visualisation.py
│   │   ├── Patient_geomap.py
│   │   └── Visuals.py
│   ├── data_handling/           # Data processing and management
│   │   ├── Data_loader.py
│   │   ├── Explore_data.py
│   │   ├── FileUploadHandler.py
│   │   ├── Format_data.py
│   │   └── Patient_metadata.py
│   └── utils/                   # Utility functions
│       └── Utils.py
├── static/                      # Web assets
│   ├── css/                     # Stylesheets
│   ├── js/                      # JavaScript files
│   └── images/                  # Images and icons
├── templates/                   # HTML templates
├── app.py                      # Main Flask application
├── Main.py                     # Terminal interface
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```

## 🚀 Quick Start

### **Web Interface**
```bash
python3 app.py
# Open http://localhost:5002
```

### **Terminal Interface**
```bash
python3 Main.py
```

### **Dependencies**
```bash
pip install -r requirements.txt
```

## 🛠️ Technical Stack

### **Backend**
- **Python 3.8+**: Core programming language
- **Flask**: Web framework for the web interface
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **SciPy**: Scientific computing
- **Scikit-learn**: Machine learning algorithms

### **Visualization**
- **Plotly**: Interactive plotting library
- **UMAP**: Dimensionality reduction
- **Matplotlib**: Static plotting (legacy)

### **Data Processing**
- **GEOparse**: NCBI GEO database integration
- **Geopy**: Geographic coordinate processing
- **Statsmodels**: Statistical analysis

### **Frontend**
- **HTML5/CSS3**: Modern web standards
- **JavaScript**: Interactive functionality
- **Bootstrap 5**: Responsive design framework
- **Font Awesome**: Icon library

## 📊 Supported Data Formats

### **Input Formats**
- **CSV/TSV**: Comma/tab-separated values
- **TXT**: Text files with delimiters
- **GEO Datasets**: Direct NCBI GEO integration

### **Data Types**
- **Metadata**: Patient information, clinical data
- **Expression Data**: Gene expression matrices
- **Annotation Files**: Gene mapping information

## 🔧 Configuration

### **Environment Variables**
- `FLASK_ENV`: Development/production mode
- `UPLOAD_FOLDER`: File upload directory
- `MAX_CONTENT_LENGTH`: Maximum file size (100MB)

### **File Structure**
- `uploads/`: Temporary file storage
- `cleaned_data/`: Processed data storage
- `logs/`: Application logs
- `static/images/`: Web assets

## 🧪 Testing

### **Import Tests**
```bash
# Test core modules
python3 -c "from src.data_handling.Data_loader import DataManager; print('✅ DataManager OK')"
python3 -c "from app import app; print('✅ Flask app OK')"
python3 -c "from Main import main_menu; print('✅ Terminal interface OK')"
```

### **Functionality Tests**
- Data upload and validation
- Visualization generation
- Statistical analysis
- Geographic mapping
- Gene exploration

## 📈 Performance Optimizations

### **Caching System**
- **Data Cache**: 5-minute TTL for metadata/expression stats
- **Plot Cache**: Generated plots cached for reuse
- **Session Management**: User session data persistence

### **Memory Management**
- **Lazy Loading**: Data loaded only when needed
- **Garbage Collection**: Automatic cleanup of temporary files
- **Streaming**: Large file processing in chunks

## 🔒 Security Features

### **File Upload Security**
- **File Type Validation**: Whitelist of allowed formats
- **Size Limits**: Maximum file size restrictions
- **Path Sanitization**: Secure file path handling

### **Data Privacy**
- **Local Processing**: All data processed locally
- **No External Storage**: No data sent to external servers
- **Session Isolation**: User data isolation

## 📚 Documentation

### **User Guides**
- `README.md`: Main project documentation
- `WEB_INTERFACE_README.md`: Web interface specific guide
- `PROJECT_SUMMARY.md`: This comprehensive overview

### **Code Documentation**
- **Docstrings**: Comprehensive function documentation
- **Type Hints**: Python type annotations
- **Comments**: Inline code explanations

## 🤝 Contributing

### **Development Setup**
1. Clone the repository
2. Create virtual environment
3. Install dependencies
4. Run tests
5. Submit pull request

### **Code Standards**
- **PEP 8**: Python style guide compliance
- **Type Hints**: Function parameter and return type annotations
- **Docstrings**: Comprehensive function documentation
- **Error Handling**: Robust exception management

## 📄 License

This project is designed for research and educational purposes. Please ensure compliance with data usage agreements and institutional policies.

## 🙏 Acknowledgments

- **Author**: Mishael Beppin (MSc Genomic Medicine)
- **Purpose**: Empowering genomic research through accessible bioinformatics tools
- **Inspiration**: Making complex transcriptomic analysis accessible to researchers without programming backgrounds

---

**GliomaScope**: Empowering you to explore and understand at the genomic level within Bioinformatics. 🧬✨ 