// GliomaScope Web Application JavaScript

class GliomaScopeApp {
    constructor() {
        console.log('Initializing GliomaScopeApp...');
        try {
            this.initializeEventListeners();
            this.loadDataSummary();
            console.log('GliomaScopeApp initialized successfully');
        } catch (error) {
            console.error('Error initializing GliomaScopeApp:', error);
        }
    }

    initializeEventListeners() {
        // GEO Dataset Download
        const geoDownloadForm = document.getElementById('geoDownloadForm');
        if (geoDownloadForm) {
            geoDownloadForm.addEventListener('submit', (e) => this.handleGeoDownload(e));
        }
        
        // Format Dataset
        const formatDatasetForm = document.getElementById('formatDatasetForm');
        if (formatDatasetForm) {
            formatDatasetForm.addEventListener('submit', (e) => this.handleFormatDataset(e));
        }
        
        // Upload Metadata
        const uploadMetadataForm = document.getElementById('uploadMetadataForm');
        if (uploadMetadataForm) {
            uploadMetadataForm.addEventListener('submit', (e) => this.handleFileUpload(e, 'metadataUploadResults'));
        }
        
        // Upload Expression
        const uploadExpressionForm = document.getElementById('uploadExpressionForm');
        if (uploadExpressionForm) {
            uploadExpressionForm.addEventListener('submit', (e) => this.handleFileUpload(e, 'expressionUploadResults'));
        }
        
        // Data Exploration Filter
        const explorationFilterForm = document.getElementById('explorationFilterForm');
        if (explorationFilterForm) {
            explorationFilterForm.addEventListener('submit', (e) => this.handleDataFiltering(e, 'explorationFilterResults'));
        }
        
        // Geographic Visualization
        const geoVizForm = document.getElementById('geoVizForm');
        if (geoVizForm) {
            geoVizForm.addEventListener('submit', (e) => this.handleGeomap(e));
        }
        
        // PCA Analysis
        const pcaAnalysisForm = document.getElementById('pcaAnalysisForm');
        if (pcaAnalysisForm) {
            pcaAnalysisForm.addEventListener('submit', (e) => this.handlePCA(e));
        }
        
        // UMAP Analysis
        const umapAnalysisForm = document.getElementById('umapAnalysisForm');
        if (umapAnalysisForm) {
            umapAnalysisForm.addEventListener('submit', (e) => this.handleUMAP(e));
        }
        
        // Differential Expression Analysis
        const diffExpAnalysisForm = document.getElementById('diffExpAnalysisForm');
        if (diffExpAnalysisForm) {
            diffExpAnalysisForm.addEventListener('submit', (e) => this.handleDifferentialExpression(e));
        }
        
        // Gene Exploration
        const geneExplorationForm = document.getElementById('geneExplorationForm');
        if (geneExplorationForm) {
            geneExplorationForm.addEventListener('submit', (e) => this.handleGeneExpression(e));
        }
        
        // Chromosome Mapping
        const chromosomeMappingForm = document.getElementById('chromosomeMappingForm');
        if (chromosomeMappingForm) {
            chromosomeMappingForm.addEventListener('submit', (e) => this.handleChromosomeMapping(e));
        }
        
        // Heatmap Visualization
        const heatmapVizForm = document.getElementById('heatmapVizForm');
        if (heatmapVizForm) {
            heatmapVizForm.addEventListener('submit', (e) => this.handleHeatmap(e));
        }
        
        // Sidebar navigation
        this.initializeSidebarNavigation();
    }

    initializeSidebarNavigation() {
        console.log('Initializing sidebar navigation...');
        // Handle sidebar link clicks
        const sidebarLinks = document.querySelectorAll('.sidebar-link');
        console.log('Found sidebar links:', sidebarLinks.length);
        
        sidebarLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                console.log('Sidebar link clicked:', page);
                this.navigateToPage(page);
            });
        });

        // Handle URL hash changes
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.slice(1);
            if (hash) {
                this.navigateToPage(hash);
            }
        });

        // Initialize page based on URL hash
        const hash = window.location.hash.slice(1);
        if (hash) {
            this.navigateToPage(hash);
        }
    }

    navigateToPage(pageName) {
        console.log('Navigating to page:', pageName);
        
        // Hide all pages
        const pages = document.querySelectorAll('.page');
        console.log('Found pages:', pages.length);
        pages.forEach(page => {
            page.classList.remove('active');
        });

        // Remove active class from all sidebar links
        const sidebarLinks = document.querySelectorAll('.sidebar-link');
        sidebarLinks.forEach(link => {
            link.classList.remove('active');
        });

        // Show selected page
        const targetPage = document.getElementById(`${pageName}-page`);
        console.log('Target page element:', targetPage);
        if (targetPage) {
            targetPage.classList.add('active');
            console.log('Page activated:', pageName);
        } else {
            console.error('Target page not found:', `${pageName}-page`);
        }

        // Update active sidebar link
        const activeLink = document.querySelector(`[data-page="${pageName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
            console.log('Sidebar link activated:', pageName);
        } else {
            console.error('Sidebar link not found:', pageName);
        }

        // Update URL hash
        window.location.hash = pageName;

        // Scroll to top
        window.scrollTo(0, 0);

        // No auto-generation for geographic visualization - user must click generate button
        
        // Auto-load data summary on data exploration page
        if (pageName === 'data-exploration') {
            setTimeout(() => this.loadDataSummary(), 500);
        }
        
        // Populate PCA columns when PCA analysis page is loaded
        if (pageName === 'pca-analysis') {
            setTimeout(() => this.populatePCAColumns(), 500);
        }
        
        // Populate UMAP columns when UMAP analysis page is loaded
        if (pageName === 'umap-analysis') {
            setTimeout(() => this.populateUMAPColumns(), 500);
        }
    }

    async loadInitialWorldMap() {
        try {
            console.log('Loading initial world map...');
            const response = await fetch('/world_map', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            console.log('Initial map result:', result);
            
            if (result.success) {
                console.log('Initial world map generated and opened in browser');
                
                // Clear the results area completely - no info box
                const geomapResults = document.getElementById('geomapResults');
                if (geomapResults) {
                    geomapResults.innerHTML = '';
                }
            } else {
                console.error('Initial map generation failed:', result.error);
            }
        } catch (error) {
            console.error('Error loading initial world map:', error);
        }
    }

    async autoGenerateMap() {
        try {
            console.log('Auto-generating map with data...');
            const response = await fetch('/patient_geomap', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    map_type: 'individual',
                    zoom_enabled: false
                })
            });
            
            const result = await response.json();
            console.log('Map generation result:', result);
            
            if (result.success) {
                console.log('Patient geographic map generated and opened in browser');
                
                // Clear the results area completely - no info box
                const geomapResults = document.getElementById('geomapResults');
                if (geomapResults) {
                    geomapResults.innerHTML = '';
                }
            } else {
                console.error('Map generation failed:', result.error);
            }
        } catch (error) {
            console.error('Error auto-generating map:', error);
        }
    }

    showLoading() {
        try {
            const modalElement = document.getElementById('loadingModal');
            if (modalElement) {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
                
                // Auto-hide after 30 seconds to prevent getting stuck
                setTimeout(() => {
                    this.hideLoading();
                }, 30000);
            }
        } catch (error) {
            console.error('Error showing loading modal:', error);
        }
    }

    hideLoading() {
        try {
            const modalElement = document.getElementById('loadingModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                } else {
                    // Fallback: manually hide the modal
                    modalElement.classList.remove('show');
                    modalElement.style.display = 'none';
                    document.body.classList.remove('modal-open');
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                }
            }
        } catch (error) {
            console.error('Error hiding loading modal:', error);
        }
    }

    showAlert(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the body
        document.body.insertBefore(alertDiv, document.body.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    async handleGeoDownload(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const geoId = formData.get('geoId') || document.getElementById('geoId').value;
        
        if (!geoId) {
            this.showAlert('Please enter a GEO Accession ID.', 'danger');
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/geo_download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ geo_id: geoId })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(`GEO dataset ${geoId} downloaded successfully!`, 'success');
                document.getElementById('geoDownloadResults').innerHTML = `
                    <div class="alert alert-success">
                        <h6>Download Complete</h6>
                        <p>Dataset: ${geoId}</p>
                        <p>Samples: ${result.samples}</p>
                        <p>Genes: ${result.genes}</p>
                    </div>
                `;
                this.updateDataSummary(result.summary);
            } else {
                this.showAlert(result.error || 'Download failed', 'danger');
            }
        } catch (error) {
            console.error('GEO download error:', error);
            this.showAlert('Error downloading GEO dataset: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    async handleFormatDataset(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        
        if (!formData.get('expressionFile') || !formData.get('metadataFile')) {
            this.showAlert('Please select both expression and metadata files.', 'danger');
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/format_dataset', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('Dataset formatted and loaded successfully!', 'success');
                document.getElementById('formatResults').innerHTML = `
                    <div class="alert alert-success">
                        <h6>Format Complete</h6>
                        <p>Expression samples: ${result.expression_samples}</p>
                        <p>Metadata samples: ${result.metadata_samples}</p>
                        <p>Matched samples: ${result.matched_samples}</p>
                    </div>
                `;
                this.updateDataSummary(result.summary);
            } else {
                this.showAlert(result.error || 'Format failed', 'danger');
            }
        } catch (error) {
            console.error('Format error:', error);
            this.showAlert('Error formatting dataset: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    async handleChromosomeMapping(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const genes = formData.get('chromosomeGenes').split(/[,\n]/).map(g => g.trim()).filter(g => g);
        const chromosomeFilter = formData.get('chromosomeFilter');
        
        if (genes.length === 0) {
            this.showAlert('Please enter at least one gene name.', 'warning');
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/chromosome_mapping', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    genes: genes,
                    chromosome_filter: chromosomeFilter
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(`Chromosome mapping for ${genes.length} genes generated successfully`, 'success');
                document.getElementById('chromosomeMappingResults').innerHTML = `
                    <div class="plotly-container">
                        ${result.plot_html}
                    </div>
                `;
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error generating chromosome mapping: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    async handleFileUpload(event, resultElementId = 'uploadResults') {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const file = formData.get('file');
        const fileType = formData.get('file_type');
        
        if (!file) {
            this.showAlert('Please select a file to upload.', 'danger');
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                // Show success message with filename and detected type
                const detectedType = result.file_type || fileType || 'data';
                const message = `File "${file.name}" uploaded successfully as ${detectedType}!`;
                this.showAlert(message, 'success');
                
                // Update specific result area
                const resultElement = document.getElementById(resultElementId);
                if (resultElement) {
                    resultElement.innerHTML = `
                        <div class="alert alert-success">
                            <h6>Upload Complete</h6>
                            <p>File: ${file.name}</p>
                            <p>Type: ${detectedType}</p>
                            <p>Status: Successfully loaded</p>
                        </div>
                    `;
                }
                
                this.updateDataSummary(result.summary);
                
                // Reset the form
                event.target.reset();
                
                // Enable analysis sections
                this.enableAnalysisSections();
                
                // Update upload status display
                this.updateUploadStatus(file.name, detectedType);
                
                // Auto-refresh map if we're on the world map page and uploaded metadata
                if (detectedType === 'metadata' && window.location.hash === '#geographic-viz') {
                    setTimeout(() => this.autoGenerateMap(), 1000);
                }
            } else {
                this.showAlert(result.error || 'Upload failed', 'danger');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showAlert('Error uploading file: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    updateUploadStatus(filename, fileType) {
        const dataSummary = document.getElementById('dataSummary');
        if (dataSummary) {
            // Create upload status element
            const statusDiv = document.createElement('div');
            statusDiv.className = 'alert alert-success alert-sm mb-3';
            statusDiv.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>
                <strong>${fileType}</strong>: ${filename}
                <small class="text-muted ms-2">✓ Uploaded successfully</small>
            `;
            
            // Remove any existing upload status messages
            const existingStatus = dataSummary.querySelector('.alert-success');
            if (existingStatus) {
                existingStatus.remove();
            }
            
            // Add new status at the top
            dataSummary.insertBefore(statusDiv, dataSummary.firstChild);
        }

        // Update upload status indicators
        this.updateUploadStatusIndicators(fileType, filename);
    }

    updateUploadStatusIndicators(fileType, filename) {
        const uploadStatus = document.getElementById('uploadStatus');
        if (!uploadStatus) return;

        if (fileType === 'metadata') {
            const metadataItem = uploadStatus.querySelector('.upload-status-item:first-child');
            if (metadataItem) {
                metadataItem.innerHTML = `
                    <i class="fas fa-file-alt text-success me-2"></i>
                    <span class="text-success">✓ ${filename}</span>
                `;
            }
        } else if (fileType === 'expression') {
            const expressionItem = uploadStatus.querySelector('.upload-status-item:last-child');
            if (expressionItem) {
                expressionItem.innerHTML = `
                    <i class="fas fa-chart-line text-success me-2"></i>
                    <span class="text-success">✓ ${filename}</span>
                `;
            }
        }
    }

    async loadDataSummary() {
        try {
            const response = await fetch('/data_summary');
            const summary = await response.json();
            this.updateDataSummary(summary);
        } catch (error) {
            console.error('Error loading data summary:', error);
        }
    }

    updateDataSummary(summary) {
        const summaryContainer = document.getElementById('dataSummary');
        
        // Check if any data is available
        if (!summary || (!summary.metadata && !summary.expression)) {
            summaryContainer.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    <strong>No Data Available</strong><br>
                    Please upload or download datasets to see data summary.
                </div>
            `;
            return;
        }

        let html = '';
        
        if (summary.metadata) {
            html += `
                <div class="data-summary-card">
                    <h6><i class="fas fa-table me-2"></i>Metadata</h6>
                    <p><strong>Shape:</strong> ${summary.metadata.shape[0]} rows × ${summary.metadata.shape[1]} columns</p>
                    <p><strong>Missing Values:</strong> ${summary.metadata.missing_values}</p>
                    <p><strong>Columns:</strong> ${summary.metadata.columns.slice(0, 5).join(', ')}${summary.metadata.columns.length > 5 ? '...' : ''}</p>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="window.gliomaScopeApp.showDataPreview('metadata')">
                            <i class="fas fa-eye me-1"></i>Preview Data
                        </button>
                    </div>
                </div>
            `;
        }
        
        if (summary.expression) {
            html += `
                <div class="data-summary-card">
                    <h6><i class="fas fa-chart-line me-2"></i>Expression Data</h6>
                    <p><strong>Shape:</strong> ${summary.expression.shape[0]} rows × ${summary.expression.shape[1]} columns</p>
                    <p><strong>Missing Values:</strong> ${summary.expression.missing_values}</p>
                    <p><strong>Genes:</strong> ${summary.expression.columns.slice(0, 5).join(', ')}${summary.expression.columns.length > 5 ? '...' : ''}</p>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="window.gliomaScopeApp.showDataPreview('expression')">
                            <i class="fas fa-eye me-1"></i>Preview Data
                        </button>
                    </div>
                </div>
            `;
        }
        
        summaryContainer.innerHTML = html;
        
        // Show success message only if data is actually loaded
        if (summary.metadata || summary.expression) {
            this.showAlert('Data loaded successfully! You can now proceed with analysis.', 'success');
        }
        
        // Update filter options based on available columns
        if (summary.metadata && summary.metadata.columns) {
            this.updateFilterOptions(summary.metadata.columns);
        }
    }
    
    updateFilterOptions(columns) {
        // Update filter inputs based on available columns
        const gradeFilter = document.getElementById('gradeFilter');
        const idhFilter = document.getElementById('idhFilter');
        const ageFilter = document.getElementById('ageFilter');
        
        // Check for common column variations
        const gradeColumns = columns.filter(col => 
            col.toLowerCase().includes('grade') || 
            col.toLowerCase().includes('tumor') ||
            col.toLowerCase().includes('tissue_type') ||
            col.toLowerCase().includes('sample_type')
        );
        
        const idhColumns = columns.filter(col => 
            col.toLowerCase().includes('idh') || 
            col.toLowerCase().includes('mutation')
        );
        
        const ageColumns = columns.filter(col => 
            col.toLowerCase().includes('age')
        );
        
        // Update grade filter
        if (gradeFilter) {
            if (gradeColumns.length > 0) {
                gradeFilter.placeholder = `Filter by ${gradeColumns[0]}`;
                gradeFilter.disabled = false;
                gradeFilter.setAttribute('data-column', gradeColumns[0]);
                gradeFilter.title = `Available column: ${gradeColumns[0]}`;
            } else {
                gradeFilter.placeholder = 'No grade/tissue column found';
                gradeFilter.disabled = true;
            }
        }
        
        // Update IDH filter
        if (idhFilter) {
            if (idhColumns.length > 0) {
                idhFilter.placeholder = `Filter by ${idhColumns[0]}`;
                idhFilter.disabled = false;
                idhFilter.setAttribute('data-column', idhColumns[0]);
                idhFilter.title = `Available column: ${idhColumns[0]}`;
            } else {
                idhFilter.placeholder = 'No IDH column found';
                idhFilter.disabled = true;
            }
        }
        
        // Update age filter
        if (ageFilter) {
            if (ageColumns.length > 0) {
                ageFilter.placeholder = `Filter by ${ageColumns[0]} (e.g., 40-60)`;
                ageFilter.disabled = false;
                ageFilter.setAttribute('data-column', ageColumns[0]);
                ageFilter.title = `Available column: ${ageColumns[0]}`;
            } else {
                ageFilter.placeholder = 'No age column found';
                ageFilter.disabled = true;
            }
        }
    }
    
    async showDataPreview(dataType) {
        try {
            const response = await fetch('/data_summary');
            const summary = await response.json();
            
            let previewData = null;
            let title = '';
            
            if (dataType === 'metadata' && summary.metadata) {
                previewData = summary.metadata.preview;
                title = 'Metadata Preview';
            } else if (dataType === 'expression' && summary.expression) {
                previewData = summary.expression.preview;
                title = 'Expression Data Preview';
            }
            
            if (previewData) {
                const previewDiv = document.getElementById('dataPreview');
                if (previewDiv) {
                    previewDiv.innerHTML = `
                        <h5><i class="fas fa-eye me-2"></i>${title}</h5>
                        <div class="table-responsive mt-3" style="max-height: 400px; overflow-y: auto;">
                            ${previewData}
                        </div>
                    `;
                    previewDiv.style.display = 'block';
                    
                    // Scroll to preview
                    previewDiv.scrollIntoView({ behavior: 'smooth' });
                }
            }
        } catch (error) {
            console.error('Error showing data preview:', error);
            this.showAlert('Error loading data preview', 'danger');
        }
    }

    // New functions matching terminal functionality
    async showDataSummary() {
        // Hide other sections
        document.getElementById('previewSection').style.display = 'none';
        document.getElementById('filterSection').style.display = 'none';
        
        // Show summary section
        document.getElementById('summarySection').style.display = 'block';
        
        // Load summary data
        try {
            const response = await fetch('/data_summary');
            const summary = await response.json();
            
            const summaryDiv = document.getElementById('dataSummary');
            
            if (Object.keys(summary).length === 0) {
                summaryDiv.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        No data loaded. Please upload or download data first (Options 1-4).
                    </div>
                `;
                return;
            }
            
            let html = '<div class="row g-3">';
            
            if (summary.metadata) {
                html += `
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header bg-primary text-white">
                                <h6 class="mb-0"><i class="fas fa-table me-2"></i>METADATA</h6>
                            </div>
                            <div class="card-body">
                                <p><strong>Samples:</strong> ${(summary.metadata.shape[0] || 0).toLocaleString()}</p>
                                <p><strong>Columns:</strong> ${(summary.metadata.shape[1] || 0).toLocaleString()}</p>
                                <p><strong>Missing values:</strong> ${(summary.metadata.missing_values || 0).toLocaleString()}</p>
                                <p><strong>Duplicate rows:</strong> ${(summary.metadata.duplicates || 0).toLocaleString()}</p>
                                <button class="btn btn-sm btn-outline-primary" onclick="window.gliomaScopeApp.showDataPreview('metadata')">
                                    <i class="fas fa-eye me-1"></i>Preview
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            if (summary.expression) {
                html += `
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header bg-success text-white">
                                <h6 class="mb-0"><i class="fas fa-chart-line me-2"></i>EXPRESSION</h6>
                            </div>
                            <div class="card-body">
                                <p><strong>Samples:</strong> ${(summary.expression.shape[0] || 0).toLocaleString()}</p>
                                <p><strong>Genes:</strong> ${(summary.expression.shape[1] || 0).toLocaleString()}</p>
                                <p><strong>Missing values:</strong> ${(summary.expression.missing_values || 0).toLocaleString()}</p>
                                <p><strong>Duplicate rows:</strong> ${(summary.expression.duplicates || 0).toLocaleString()}</p>
                                <button class="btn btn-sm btn-outline-success" onclick="window.gliomaScopeApp.showDataPreview('expression')">
                                    <i class="fas fa-eye me-1"></i>Preview
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
            summaryDiv.innerHTML = html;
            
        } catch (error) {
            console.error('Error loading data summary:', error);
            document.getElementById('dataSummary').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error loading data summary: ${error.message}
                </div>
            `;
        }
    }

    async showDataPreview() {
        // Hide other sections
        document.getElementById('summarySection').style.display = 'none';
        document.getElementById('filterSection').style.display = 'none';
        
        // Show preview section
        document.getElementById('previewSection').style.display = 'block';
        
        // Load preview data
        try {
            const response = await fetch('/data_summary');
            const summary = await response.json();
            
            const previewDiv = document.getElementById('dataPreview');
            
            if (Object.keys(summary).length === 0) {
                previewDiv.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        No data loaded. Please upload or download data first (Options 1-4).
                    </div>
                `;
                return;
            }
            
            let html = '';
            
            if (summary.metadata) {
                html += `
                    <div class="mb-4">
                        <h5><i class="fas fa-table me-2"></i>Metadata Preview</h5>
                        <p class="text-muted small mb-2">
                            <i class="fas fa-info-circle me-1"></i>
                            Showing first 20 rows of ${(summary.metadata.shape[0] || 0).toLocaleString()} samples with ${(summary.metadata.shape[1] || 0).toLocaleString()} columns
                        </p>
                        <div class="table-responsive">
                            ${summary.metadata.preview}
                        </div>
                    </div>
                `;
            }
            
            if (summary.expression) {
                html += `
                    <div class="mb-4">
                        <h5><i class="fas fa-chart-line me-2"></i>Expression Data Preview</h5>
                        <p class="text-muted small mb-2">
                            <i class="fas fa-info-circle me-1"></i>
                            Showing first 20 samples with first 10 genes out of ${(summary.expression.shape[1] - 1 || 0).toLocaleString()} total genes
                        </p>
                        <div class="table-responsive">
                            ${summary.expression.preview}
                        </div>
                    </div>
                `;
            }
            
            previewDiv.innerHTML = html;
            
        } catch (error) {
            console.error('Error loading data preview:', error);
            document.getElementById('dataPreview').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error loading data preview: ${error.message}
                </div>
            `;
        }
    }

    async showFullDataView() {
        // Show choice dialog for which data to view
        const choice = await this.showDataViewChoice();
        if (!choice) return; // User cancelled
        
        // Hide other sections
        document.getElementById('summarySection').style.display = 'none';
        document.getElementById('filterSection').style.display = 'none';
        
        // Show preview section (reusing the same section)
        document.getElementById('previewSection').style.display = 'block';
        
        // Ensure any modal overlays are removed
        this.removeModalOverlays();
        
        // Load first page of data
        await this.loadDataPage(choice, 1);
    }

    removeModalOverlays() {
        // Remove any modal backdrops that might be causing the dimming
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        
        // Remove modal-open class from body
        document.body.classList.remove('modal-open');
        
        // Remove any inline styles that might be causing issues
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }

    async loadDataPage(dataType, page = 1) {
        const previewDiv = document.getElementById('dataPreview');
        
        // Show loading message with better styling
        previewDiv.innerHTML = `
            <div class="text-center p-5">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h5 class="text-light">Loading ${dataType} data...</h5>
                <p class="text-muted">Page ${page} • Please wait while we prepare your data</p>
            </div>
        `;
        
        try {
            const perPage = window.currentPerPage || 50;
            const response = await fetch(`/view_${dataType}_data?page=${page}&per_page=${perPage}`);
            const viewData = await response.json();
            
            if (viewData.error) {
                previewDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        ${viewData.error}
                    </div>
                `;
                return;
            }
            
            let html = '';
            
            if (dataType === 'metadata' && viewData.metadata) {
                html += this.createDataTableHTML('metadata', viewData.metadata);
            } else if (dataType === 'expression' && viewData.expression) {
                html += this.createDataTableHTML('expression', viewData.expression);
            }
            
            // Clear loading state and set content
            previewDiv.innerHTML = html;
            
            // Ensure proper scrolling after content is loaded
            this.initializeTableScrolling();
            
        } catch (error) {
            console.error('Error loading data page:', error);
            previewDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error loading ${dataType} dataset. Please try again.
                </div>
            `;
        }
    }

    initializeTableScrolling() {
        // Ensure the table container is properly scrollable
        const tableContainers = document.querySelectorAll('.table-responsive');
        tableContainers.forEach(container => {
            container.style.maxHeight = '70vh';
            container.style.overflowY = 'auto';
            container.style.overflowX = 'auto';
            
            // Add smooth scrolling
            container.style.scrollBehavior = 'smooth';
            
            // Ensure the container is visible and not blocked
            container.style.position = 'relative';
            container.style.zIndex = '1';
        });
        
        // Remove any potential blocking overlays
        this.removeModalOverlays();
    }

    createDataTableHTML(dataType, data) {
        const icon = dataType === 'metadata' ? 'fas fa-table' : 'fas fa-chart-line';
        const title = dataType === 'metadata' ? 'Metadata Dataset' : 'Expression Dataset';
        const description = dataType === 'metadata' ? 'samples with columns' : 'samples with columns (genes)';
        
        return `
            <div class="mb-4 data-view-container">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <h5><i class="${icon} me-2"></i>${title}</h5>
                        <p class="text-muted small mb-0">
                            <i class="fas fa-database me-1"></i>
                            Total: ${data.total_rows.toLocaleString()} ${description}
                        </p>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                        <label class="form-label mb-0 me-2">Rows per page:</label>
                        <select class="form-select form-select-sm" style="width: auto;" onchange="window.gliomaScopeApp.changePerPage('${dataType}', this.value)">
                            <option value="25" ${data.per_page === 25 ? 'selected' : ''}>25</option>
                            <option value="50" ${data.per_page === 50 ? 'selected' : ''}>50</option>
                            <option value="100" ${data.per_page === 100 ? 'selected' : ''}>100</option>
                        </select>
                    </div>
                </div>
                
                <div class="table-responsive data-table-container" style="max-height: 70vh; overflow-y: auto; overflow-x: auto; border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 8px;">
                    ${data.current_data}
                </div>
                
                <div class="d-flex justify-content-between align-items-center mt-3">
                    <div class="text-muted small">
                        Showing rows ${data.start_row} to ${data.end_row} of ${data.total_rows.toLocaleString()}
                    </div>
                    <div class="pagination-container">
                        ${this.createPaginationHTML(dataType, data)}
                    </div>
                </div>
            </div>
        `;
    }

    createPaginationHTML(dataType, data) {
        const currentPage = data.current_page;
        const totalPages = data.total_pages;
        
        let paginationHTML = '<nav><ul class="pagination pagination-sm mb-0">';
        
        // Previous button
        paginationHTML += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="window.gliomaScopeApp.loadDataPage('${dataType}', ${currentPage - 1})" ${currentPage === 1 ? 'tabindex="-1"' : ''}>
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
        
        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        if (startPage > 1) {
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="window.gliomaScopeApp.loadDataPage('${dataType}', 1)">1</a>
                </li>
            `;
            if (startPage > 2) {
                paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            paginationHTML += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="window.gliomaScopeApp.loadDataPage('${dataType}', ${i})">${i}</a>
                </li>
            `;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
            paginationHTML += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="window.gliomaScopeApp.loadDataPage('${dataType}', ${totalPages})">${totalPages}</a>
                </li>
            `;
        }
        
        // Next button
        paginationHTML += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="window.gliomaScopeApp.loadDataPage('${dataType}', ${currentPage + 1})" ${currentPage === totalPages ? 'tabindex="-1"' : ''}>
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
        
        paginationHTML += '</ul></nav>';
        return paginationHTML;
    }

    async changePerPage(dataType, perPage) {
        // Store the current data type and per page value globally
        window.currentDataType = dataType;
        window.currentPerPage = parseInt(perPage);
        await this.loadDataPage(dataType, 1); // Reset to first page when changing per page
    }

    async showDataViewChoice() {
        return new Promise((resolve) => {
            // Create modal dialog
            const modalHtml = `
                <div class="modal fade" id="dataViewChoiceModal" tabindex="-1" aria-hidden="true" data-bs-backdrop="static">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content" style="background: linear-gradient(135deg, rgba(0, 123, 255, 0.1), rgba(0, 212, 255, 0.1)); border: 1px solid rgba(0, 212, 255, 0.3); backdrop-filter: blur(10px);">
                            <div class="modal-header" style="border-bottom: 1px solid rgba(0, 212, 255, 0.3);">
                                <h5 class="modal-title text-light">
                                    <i class="fas fa-eye me-2"></i>Choose Data to View
                                </h5>
                            </div>
                            <div class="modal-body text-center">
                                <p class="text-light mb-4">Which dataset would you like to view?</p>
                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <button class="btn btn-primary btn-lg w-100" onclick="window.selectDataChoice('metadata')">
                                            <i class="fas fa-table me-2"></i>
                                            Metadata
                                            <small class="d-block mt-1">Sample information & annotations</small>
                                        </button>
                                    </div>
                                    <div class="col-md-6">
                                        <button class="btn btn-success btn-lg w-100" onclick="window.selectDataChoice('expression')">
                                            <i class="fas fa-chart-line me-2"></i>
                                            Expression Data
                                            <small class="d-block mt-1">Gene expression values</small>
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer" style="border-top: 1px solid rgba(0, 212, 255, 0.3);">
                                <button type="button" class="btn btn-outline-secondary" onclick="window.selectDataChoice(null)">Cancel</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Add modal to page
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            
            // Set up global choice handler
            window.selectDataChoice = (choice) => {
                // Properly hide and remove modal
                const modalElement = document.getElementById('dataViewChoiceModal');
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) {
                        modal.hide();
                    }
                    
                    // Remove modal after it's hidden
                    modalElement.addEventListener('hidden.bs.modal', () => {
                        modalElement.remove();
                        // Clean up any remaining backdrop
                        const backdrops = document.querySelectorAll('.modal-backdrop');
                        backdrops.forEach(backdrop => backdrop.remove());
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                    }, { once: true });
                }
                
                delete window.selectDataChoice;
                resolve(choice);
            };
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('dataViewChoiceModal'));
            modal.show();
        });
    }

    async showDataFilter() {
        // Hide other sections
        document.getElementById('summarySection').style.display = 'none';
        document.getElementById('previewSection').style.display = 'none';
        
        // Show filter section
        document.getElementById('filterSection').style.display = 'block';
        
        // Load available columns
        try {
            const response = await fetch('/data_summary');
            const summary = await response.json();
            
            const columnsDiv = document.getElementById('availableColumns');
            
            if (!summary.metadata) {
                columnsDiv.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        No metadata available for filtering.
                    </div>
                `;
                return;
            }
            
            const columns = summary.metadata.columns;
            
            let html = `
                <div class="row">
                    <div class="col-md-8">
                        <h6><i class="fas fa-columns me-2"></i>Select Column to Filter:</h6>
                        <div class="input-group mb-3">
                            <span class="input-group-text">
                                <i class="fas fa-filter"></i>
                            </span>
                            <select class="form-select" id="columnSelect" onchange="window.gliomaScopeApp.onColumnSelectChange()">
                                <option value="">🔍 Choose a column to filter by...</option>
            `;
            
            // Add columns to dropdown with helpful icons
            for (let i = 0; i < columns.length; i++) {
                const col = columns[i];
                let icon = '📊'; // default icon
                
                // Add contextual icons based on column name
                if (col.toLowerCase().includes('tissue') || col.toLowerCase().includes('sample')) {
                    icon = '🧬';
                } else if (col.toLowerCase().includes('date') || col.toLowerCase().includes('time')) {
                    icon = '📅';
                } else if (col.toLowerCase().includes('geo') || col.toLowerCase().includes('id')) {
                    icon = '🆔';
                } else if (col.toLowerCase().includes('status') || col.toLowerCase().includes('type')) {
                    icon = '🏷️';
                } else if (col.toLowerCase().includes('count') || col.toLowerCase().includes('channel')) {
                    icon = '🔢';
                } else if (col.toLowerCase().includes('institute') || col.toLowerCase().includes('submitter')) {
                    icon = '🏥';
                }
                
                html += `<option value="${col}">${icon} ${col}</option>`;
            }
            
            html += `
                            </select>
                            <button class="btn btn-primary" onclick="window.gliomaScopeApp.loadColumnValues()" id="loadValuesBtn" disabled>
                                <i class="fas fa-search me-1"></i>Load Values
                            </button>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <h6><i class="fas fa-info-circle me-2"></i>Filter Info:</h6>
                        <div class="card card-body p-2">
                            <small class="text-muted">
                                <strong>Total Columns:</strong> ${columns.length}<br>
                                <strong>Available for filtering:</strong> All metadata columns
                            </small>
                        </div>
                    </div>
                </div>
                <div class="alert alert-info">
                    <i class="fas fa-lightbulb me-2"></i>
                    <strong>How to filter:</strong> Select a column from the dropdown above, then click "Load Values" to see available filter options.
                </div>
            `;
            
            columnsDiv.innerHTML = html;
            
        } catch (error) {
            console.error('Error loading columns:', error);
            document.getElementById('availableColumns').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error loading columns: ${error.message}
                </div>
            `;
        }
    }

    // New dropdown helper functions
    onColumnSelectChange() {
        const selectElement = document.getElementById('columnSelect');
        const loadBtn = document.getElementById('loadValuesBtn');
        
        if (selectElement.value) {
            loadBtn.disabled = false;
            loadBtn.innerHTML = '<i class="fas fa-search me-1"></i>Load Values';
        } else {
            loadBtn.disabled = true;
            loadBtn.innerHTML = '<i class="fas fa-search me-1"></i>Load Values';
            // Clear any existing filter results
            document.getElementById('filterBuilder').innerHTML = '';
            document.getElementById('explorationFilterResults').innerHTML = '';
        }
    }

    async loadColumnValues() {
        const selectElement = document.getElementById('columnSelect');
        const columnName = selectElement.value;
        
        if (!columnName) {
            this.showAlert('Please select a column first', 'warning');
            return;
        }
        
        const loadBtn = document.getElementById('loadValuesBtn');
        loadBtn.disabled = true;
        loadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
        
        try {
            await this.selectColumnForFilter(columnName, 0);
        } finally {
            loadBtn.disabled = false;
            loadBtn.innerHTML = '<i class="fas fa-search me-1"></i>Load Values';
        }
    }

    async selectColumnForFilter(columnName, columnIndex) {
        try {
            // Get unique values for the selected column
            const response = await fetch('/column_values', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ column: columnName })
            });
            
            const data = await response.json();
            
            if (data.error) {
                this.showAlert(data.error, 'danger');
                return;
            }
            
            const filterBuilderDiv = document.getElementById('filterBuilder');
            const values = data.values;
            const counts = data.counts;
            
            let html = `
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="fas fa-filter me-2"></i>Filter by: ${columnName}</h6>
                    </div>
                    <div class="card-body">
                        <p><strong>Values in '${columnName}' (${values.length} total):</strong></p>
                        <div class="row g-2 mb-3" style="max-height: 300px; overflow-y: auto;">
            `;
            
            // Show first 10 values with counts
            const displayValues = values.slice(0, 10);
            for (let i = 0; i < displayValues.length; i++) {
                const value = displayValues[i];
                const count = counts[i];
                html += `
                    <div class="col-md-6">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" value="${value}" id="filter_${i}">
                            <label class="form-check-label" for="filter_${i}">
                                <small><strong>${i + 1}.</strong> '${value}' (${count} samples)</small>
                            </label>
                        </div>
                    </div>
                `;
            }
            
            if (values.length > 10) {
                html += `
                    <div class="col-12">
                        <small class="text-muted">... and ${values.length - 10} more values</small>
                    </div>
                `;
            }
            
            html += `
                        </div>
                        <div class="mb-3">
                            <button class="btn btn-outline-secondary btn-sm me-2" onclick="window.gliomaScopeApp.selectAllFilterValues()">
                                <i class="fas fa-check-square me-1"></i>Select All
                            </button>
                            <button class="btn btn-outline-secondary btn-sm" onclick="window.gliomaScopeApp.clearAllFilterValues()">
                                <i class="fas fa-square me-1"></i>Clear All
                            </button>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-success" onclick="window.gliomaScopeApp.applyColumnFilter('${columnName}')">
                                <i class="fas fa-filter me-1"></i>Apply Filter
                            </button>
                            <button class="btn btn-secondary" onclick="window.gliomaScopeApp.cancelFilter()">
                                <i class="fas fa-times me-1"></i>Cancel
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            filterBuilderDiv.innerHTML = html;
            
        } catch (error) {
            console.error('Error loading column values:', error);
            this.showAlert('Error loading column values', 'danger');
        }
    }

    selectAllFilterValues() {
        const checkboxes = document.querySelectorAll('#filterBuilder input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = true);
    }

    clearAllFilterValues() {
        const checkboxes = document.querySelectorAll('#filterBuilder input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = false);
    }

    cancelFilter() {
        document.getElementById('filterBuilder').innerHTML = '';
    }

    async applyColumnFilter(columnName) {
        const checkboxes = document.querySelectorAll('#filterBuilder input[type="checkbox"]:checked');
        const selectedValues = Array.from(checkboxes).map(cb => cb.value);
        
        if (selectedValues.length === 0) {
            this.showAlert('Please select at least one value to filter by', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/filter_metadata', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    column: columnName,
                    values: selectedValues
                })
            });
            
            const result = await response.json();
            
            if (result.error) {
                this.showAlert(result.error, 'danger');
                return;
            }
            
            const resultsDiv = document.getElementById('explorationFilterResults');
            
            if (result.success) {
                resultsDiv.innerHTML = `
                    <div class="alert alert-success">
                        <h6><i class="fas fa-check-circle me-2"></i>Filter Applied Successfully</h6>
                        <p><strong>Original samples:</strong> ${(result.original_count || 0).toLocaleString()}</p>
                        <p><strong>Filtered samples:</strong> ${(result.filtered_count || 0).toLocaleString()}</p>
                        <p><strong>Applied filter:</strong> ${columnName} = ${selectedValues.join(', ')}</p>
                        
                        <div class="mt-3">
                            <h6>Filtered Data Preview:</h6>
                            <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
                                ${result.preview}
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <button class="btn btn-primary btn-sm" onclick="window.gliomaScopeApp.downloadFilteredData()">
                                <i class="fas fa-download me-1"></i>Download Filtered Data
                            </button>
                        </div>
                    </div>
                `;
                
                // Clear filter builder
                document.getElementById('filterBuilder').innerHTML = '';
                
                this.showAlert(`Filtered data: ${result.filtered_count} samples`, 'success');
            }
            
        } catch (error) {
            console.error('Error applying filter:', error);
            this.showAlert('Error applying filter', 'danger');
        }
    }

    downloadFilteredData() {
        window.open('/download/metadata_filtered.csv', '_blank');
    }

    // Reset data functionality
    async resetAllData() {
        // Show confirmation dialog
        const confirmed = confirm(
            '🔄 Reset All Data?\n\n' +
            'This will completely clear:\n' +
            '• All loaded datasets\n' +
            '• All cached results\n' +
            '• All saved files\n' +
            '• All session data\n\n' +
            'You will need to upload/download datasets again.\n\n' +
            'Are you sure you want to continue?'
        );
        
        if (!confirmed) return;
        
        try {
            // Show loading state
            this.showAlert('🔄 Resetting all data...', 'info');
            
            const response = await fetch('/reset_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Clear all UI elements and show "no data" messages
                document.getElementById('dataSummary').innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>No Data Available</strong><br>
                        Please upload or download datasets to see data summary.
                    </div>
                `;
                
                document.getElementById('dataPreview').innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>No Data Available</strong><br>
                        Please upload or download datasets to view data.
                    </div>
                `;
                
                document.getElementById('availableColumns').innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>No Data Available</strong><br>
                        Please upload or download datasets to filter data.
                    </div>
                `;
                
                document.getElementById('filterBuilder').innerHTML = '';
                document.getElementById('explorationFilterResults').innerHTML = '';
                
                // Clear upload results
                document.getElementById('geoDownloadResults').innerHTML = '';
                document.getElementById('formatResults').innerHTML = '';
                document.getElementById('metadataUploadResults').innerHTML = '';
                document.getElementById('expressionUploadResults').innerHTML = '';
                
                // Clear summaries
                document.getElementById('metadataSummary').innerHTML = `
                    <p class="text-muted">Upload metadata to see summary</p>
                `;
                document.getElementById('expressionSummary').innerHTML = `
                    <p class="text-muted">Upload expression data to see summary</p>
                `;
                
                // Reset status indicators
                this.updateDataStatus();
                
                // Show success message
                this.showAlert('✅ ' + result.message, 'success');
                
                // Navigate back to homepage
                this.navigateToPage('home');
                
            } else {
                this.showAlert('❌ Error: ' + result.error, 'danger');
            }
            
        } catch (error) {
            console.error('Error resetting data:', error);
            this.showAlert('❌ Error resetting data: ' + error.message, 'danger');
        }
    }

    async handleDataFiltering(event, resultElementId = 'filterResults') {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        
        // Get dynamic column names from the form elements
        const gradeFilter = document.getElementById('gradeFilter');
        const idhFilter = document.getElementById('idhFilter');
        const ageFilter = document.getElementById('ageFilter');
        
        const data = {
            grade: formData.get('gradeFilter') || formData.get('exploreGradeFilter') || null,
            idh: formData.get('idhFilter') || formData.get('exploreIdhFilter') || null,
            age_range: formData.get('ageFilter') || formData.get('exploreAgeFilter') || null,
            // Include the actual column names for dynamic filtering
            grade_column: gradeFilter ? gradeFilter.getAttribute('data-column') : null,
            idh_column: idhFilter ? idhFilter.getAttribute('data-column') : null,
            age_column: ageFilter ? ageFilter.getAttribute('data-column') : null
        };

        this.showLoading();
        
        try {
            const response = await fetch('/filter_metadata', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(`Filtered data: ${result.filtered_count} samples`, 'success');
                const resultElement = document.getElementById(resultElementId);
                if (resultElement) {
                    resultElement.innerHTML = `
                        <div class="alert alert-success">
                            <h6>Filter Results</h6>
                            <p>Filtered ${result.filtered_count} samples</p>
                            <a href="/download/metadata_filtered.csv" class="btn btn-sm btn-outline-primary">
                                <i class="fas fa-download me-2"></i>Download Filtered Data
                            </a>
                        </div>
                        <div class="plotly-container">
                            ${result.preview}
                        </div>
                    `;
                }
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error filtering data: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    async handleDifferentialExpression(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const data = {
            group_col: formData.get('groupCol'),
            group_1: formData.get('group1'),
            group_2: formData.get('group2')
        };

        this.showLoading();
        
        try {
            const response = await fetch('/differential_expression', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(`Analysis complete: ${result.significant_genes} significant genes found`, 'success');
                
                let html = `
                    <div class="alert alert-success">
                        <h6>Differential Expression Results</h6>
                        <p>Total genes: ${result.total_genes}</p>
                        <p>Significant genes (FDR < 0.05): ${result.significant_genes}</p>
                    </div>
                `;
                
                if (result.significant_results.length > 0) {
                    html += `
                        <div class="plotly-container">
                            <h6>Top Significant Genes</h6>
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Gene</th>
                                            <th>Log2FC</th>
                                            <th>P-value</th>
                                            <th>Adj P-value</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${result.significant_results.map(gene => `
                                            <tr>
                                                <td>${gene.Gene}</td>
                                                <td>${gene.log2FC.toFixed(3)}</td>
                                                <td>${gene.p_value.toExponential(3)}</td>
                                                <td>${gene.adj_p_value.toExponential(3)}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;
                }
                
                document.getElementById('diffExpResults').innerHTML = html;
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error performing differential expression: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    async populatePCAColumns() {
        try {
            const response = await fetch('/available_columns');
            const result = await response.json();
            
            const colorBySelect = document.getElementById('pcaColorBy');
            if (!colorBySelect) return;
            
            // Clear existing options except the first one
            colorBySelect.innerHTML = '<option value="">Select a column to color by...</option>';
            
            if (result.success && result.columns.length > 0) {
                result.columns.forEach(column => {
                    const option = document.createElement('option');
                    option.value = column;
                    option.textContent = column;
                    colorBySelect.appendChild(option);
                });
            } else {
                // Add a disabled option if no columns available
                const option = document.createElement('option');
                option.value = "";
                option.textContent = "No metadata columns available";
                option.disabled = true;
                colorBySelect.appendChild(option);
            }
        } catch (error) {
            console.error('Error populating PCA columns:', error);
        }
    }

    async populateUMAPColumns() {
        try {
            const response = await fetch('/available_columns');
            const result = await response.json();
            
            const colorBySelect = document.getElementById('umapColorBy');
            if (!colorBySelect) return;
            
            // Clear existing options except the first one
            colorBySelect.innerHTML = '<option value="">Select a column to color by...</option>';
            
            if (result.success && result.columns.length > 0) {
                result.columns.forEach(column => {
                    const option = document.createElement('option');
                    option.value = column;
                    option.textContent = column;
                    colorBySelect.appendChild(option);
                });
            } else {
                // Add a disabled option if no columns available
                const option = document.createElement('option');
                option.value = "";
                option.textContent = "No metadata columns available";
                option.disabled = true;
                colorBySelect.appendChild(option);
            }
        } catch (error) {
            console.error('Error populating UMAP columns:', error);
        }
    }

    async handlePCA(event) {
        event.preventDefault();
        
        const colorBy = document.getElementById('pcaColorBy').value;
        const data = {
            color_by: colorBy || null
        };

        this.showLoading();
        
        try {
            const response = await fetch('/plot_pca', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('PCA plot generated successfully', 'success');
                document.getElementById('pcaResults').innerHTML = `
                    <div class="plotly-container">
                        ${result.plot_html}
                    </div>
                `;
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error generating PCA plot: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    async handleUMAP(event) {
        event.preventDefault();
        
        const colorBy = document.getElementById('umapColorBy').value;
        const data = {
            color_by: colorBy || null
        };

        this.showLoading();
        
        try {
            const response = await fetch('/plot_umap', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert('UMAP plot generated successfully', 'success');
                document.getElementById('umapResults').innerHTML = `
                    <div class="plotly-container">
                        ${result.plot_html}
                    </div>
                `;
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error generating UMAP plot: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    async handleGeneExpression(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const data = {
            gene_name: formData.get('geneName') || formData.get('geneNameExplore'),
            group_col: formData.get('geneGroupBy')
        };

        if (!data.gene_name) {
            this.showAlert('Please enter a gene name', 'warning');
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/gene_expression', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(`Gene expression plot for ${data.gene_name} generated successfully`, 'success');
                document.getElementById('geneExpResults').innerHTML = `
                    <div class="plotly-container">
                        ${result.plot_html}
                    </div>
                `;
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error exploring gene expression: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    async showAvailableGenes() {
        try {
            const genes = await this.getAvailableGenes();
            if (genes.length > 0) {
                const geneList = genes.slice(0, 50).join(', ');
                const totalGenes = genes.length;
                
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.innerHTML = `
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content glass-card">
                            <div class="modal-header">
                                <h5 class="modal-title">Available Genes (${totalGenes} total)</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="mb-3">
                                    <input type="text" class="form-control" id="geneSearchInput" placeholder="Search genes...">
                                </div>
                                <div class="gene-list" style="max-height: 400px; overflow-y: auto;">
                                    ${genes.map(gene => `
                                        <div class="gene-item" onclick="this.selectGene('${gene}')">
                                            ${gene}
                                        </div>
                                    `).join('')}
                                </div>
                                <div class="mt-3">
                                    <small class="text-muted">
                                        Showing first 50 genes. Use search to find specific genes.
                                        Total available: ${totalGenes}
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
                const bootstrapModal = new bootstrap.Modal(modal);
                bootstrapModal.show();
                
                // Add search functionality
                const searchInput = modal.querySelector('#geneSearchInput');
                searchInput.addEventListener('input', (e) => {
                    const searchTerm = e.target.value.toLowerCase();
                    const geneItems = modal.querySelectorAll('.gene-item');
                    geneItems.forEach(item => {
                        const geneName = item.textContent.toLowerCase();
                        item.style.display = geneName.includes(searchTerm) ? 'block' : 'none';
                    });
                });
                
                // Clean up when modal is hidden
                modal.addEventListener('hidden.bs.modal', () => {
                    document.body.removeChild(modal);
                });
            } else {
                this.showAlert('No genes available. Please load expression data first.', 'warning');
            }
        } catch (error) {
            this.showAlert('Error loading available genes: ' + error.message, 'danger');
        }
    }

    selectGene(geneName) {
        // Fill in the gene name in the current form
        const geneInputs = document.querySelectorAll('#geneName, #geneNameExplore, #heatmapGenes, #heatmapGenesViz, #chromosomeGenes');
        geneInputs.forEach(input => {
            if (input && input.offsetParent !== null) { // Check if input is visible
                input.value = geneName;
            }
        });
        
        // Close the modal
        const modal = document.querySelector('.modal.show');
        if (modal) {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
            }
        }
        
        this.showAlert(`Gene "${geneName}" selected`, 'info');
    }

    async handleHeatmap(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const genesInput = formData.get('heatmapGenes') || formData.get('heatmapGenesViz');
        const genes = genesInput.split(/[,\n]/).map(g => g.trim()).filter(g => g);
        
        if (genes.length === 0) {
            this.showAlert('Please enter at least one gene name', 'warning');
            return;
        }

        const data = {
            genes: genes,
            group_col: formData.get('heatmapGroupBy') || formData.get('heatmapGroupByViz') || null
        };

        this.showLoading();
        
        try {
            const response = await fetch('/heatmap', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(`Heatmap for ${genes.length} genes generated successfully`, 'success');
                document.getElementById('heatmapResults').innerHTML = `
                    <div class="plotly-container">
                        ${result.plot_html}
                    </div>
                `;
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error generating heatmap: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    async handleGeomap(event) {
        event.preventDefault();
        
        const mapType = document.getElementById('mapType').value || 'individual';
        const zoomEnabled = document.getElementById('zoomEnabled').checked;
        
        const data = {
            map_type: mapType,
            zoom_enabled: zoomEnabled
        };

        this.showLoading();
        
        try {
            const response = await fetch('/patient_geomap', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showAlert(result.message || 'Geographic map generated and opened in browser successfully', 'success');
                
                // Clear the results area completely - no info box
                const geomapResults = document.getElementById('geomapResults');
                if (geomapResults) {
                    geomapResults.innerHTML = '';
                }
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error generating geomap: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    // Utility function to get available genes
    async getAvailableGenes() {
        try {
            const response = await fetch('/available_genes');
            const result = await response.json();
            
            if (result.success) {
                return result.genes;
            } else {
                console.error('Error getting available genes:', result.error);
                return [];
            }
        } catch (error) {
            console.error('Error getting available genes:', error);
            return [];
        }
    }

    // Auto-complete for gene names
    async setupGeneAutocomplete() {
        const geneInputs = document.querySelectorAll('#geneName, #heatmapGenes');
        
        geneInputs.forEach(input => {
            input.addEventListener('focus', async () => {
                const genes = await this.getAvailableGenes();
                if (genes.length > 0) {
                    const datalist = document.createElement('datalist');
                    datalist.id = `genes-${input.id}`;
                    
                    genes.forEach(gene => {
                        const option = document.createElement('option');
                        option.value = gene;
                        datalist.appendChild(option);
                    });
                    
                    document.body.appendChild(datalist);
                    input.setAttribute('list', datalist.id);
                }
            });
        });
    }

    // Enable analysis sections after data upload
    enableAnalysisSections() {
        const analysisSections = document.querySelectorAll('#analysis-section, #visualization-section');
        analysisSections.forEach(section => {
            section.classList.add('enabled');
        });
        
        // Add visual feedback
        this.showAlert('Analysis sections are now available!', 'info');
    }

    // Show data preview
    showDataPreview(dataType) {
        const summaryContainer = document.getElementById('dataSummary');
        const currentContent = summaryContainer.innerHTML;
        
        // Create a modal to show the data preview
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'dataPreviewModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content glass-card">
                    <div class="modal-header">
                        <h5 class="modal-title">${dataType.charAt(0).toUpperCase() + dataType.slice(1)} Data Preview</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div id="dataPreviewContent">
                            Loading preview...
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show the modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Load the preview content
        this.loadDataPreview(dataType);
        
        // Clean up when modal is hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }

    // Load data preview content
    async loadDataPreview(dataType) {
        try {
            const response = await fetch('/data_summary');
            const summary = await response.json();
            
            const contentDiv = document.getElementById('dataPreviewContent');
            if (summary[dataType] && summary[dataType].preview) {
                contentDiv.innerHTML = `
                    <div class="table-responsive">
                        ${summary[dataType].preview}
                    </div>
                `;
            } else {
                contentDiv.innerHTML = '<p class="text-muted">No preview available</p>';
            }
        } catch (error) {
            console.error('Error loading data preview:', error);
            document.getElementById('dataPreviewContent').innerHTML = 
                '<p class="text-danger">Error loading preview</p>';
        }
    }
}

// Global navigation function
window.navigateToPage = function(pageName) {
    if (window.gliomaScopeApp) {
        window.gliomaScopeApp.navigateToPage(pageName);
    }
};

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing app...');
    try {
        window.gliomaScopeApp = new GliomaScopeApp();
        console.log('App initialized successfully');
        
        // Setup gene autocomplete
        setTimeout(() => {
            if (window.gliomaScopeApp) {
                window.gliomaScopeApp.setupGeneAutocomplete();
            }
        }, 1000);
    } catch (error) {
        console.error('Error during app initialization:', error);
    }
    
    // Add some interactive effects
    document.querySelectorAll('.glass-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Add parallax effect to DNA background
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('.dna-background');
        if (parallax) {
            const speed = scrolled * 0.5;
            parallax.style.transform = `translateY(${speed}px)`;
        }
    });
});

// Add some additional utility functions
window.GliomaScopeUtils = {
    // Format numbers for display
    formatNumber: (num) => {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    },
    
    // Format p-values
    formatPValue: (pValue) => {
        if (pValue < 0.001) {
            return pValue.toExponential(3);
        } else if (pValue < 0.01) {
            return pValue.toFixed(4);
        } else {
            return pValue.toFixed(3);
        }
    },
    
    // Download data as CSV
    downloadCSV: (data, filename) => {
        const csvContent = "data:text/csv;charset=utf-8," + data;
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}; 