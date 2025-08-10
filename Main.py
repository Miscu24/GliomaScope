import sys
import os
import time

from Data_loader import DataManager
from Utils import process_upload, fetch_and_format_geo, display_and_log_summary, list_available_genes, filter_metadata, get_relevant_columns_for_analysis
from Explore_data import preview_dataframe, display_summary, warn_if_missing_columns
from Visuals import plot_pca
from Patient_geomap import plot_patient_geomap
from Patient_metadata import display_patient_summary
from Dimensionality_Reduction import plot_pca as plot_dimred_pca
from Differential_expression import perform_differential_expression
from Gene_explorer import explore_gene_expression, map_gene_to_chromosome
from Format_data import format_for_gliomascope

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ==== GLOBALS ====
data_manager = DataManager()

def upload_and_format_dataset():
    print("\n=== Upload Custom Dataset ===")
    expr_path = input("Enter path to expression file (.csv/.tsv): ").strip()
    meta_path = input("Enter path to metadata file (.csv/.tsv): ").strip()
    expr_id = input("Column name for Sample ID in expression file (default: Sample): ").strip() or "Sample"
    meta_id = input("Column name for Sample ID in metadata file (default: SampleID): ").strip() or "SampleID"

    try:
        print("Formatting uploaded dataset...")
        from Format_data import format_for_gliomascope
        format_for_gliomascope(expr_path, meta_path, expr_id, meta_id)
        print("Formatting complete. Loading cleaned data into GliomaScope...")

        cleaned_expr = "cleaned_data/expression.csv"
        cleaned_meta = "cleaned_data/metadata.csv"
        data_manager.load_expression(cleaned_expr)
        data_manager.load_file_smart(cleaned_meta)
        print("Data successfully loaded.")
    except Exception as e:
        print(f"Error processing dataset: {e}")


def main_menu():
    os.system('clear')

    print(r"""
O       o O       o O       o O       o O       o         O
| O   o | | O   o | | O   o | | O   o | | O   o | | O   o |
| | O | | | | O | | | | O | | | | O | | | | O | | | | O | |
| o   O | | o   O | | o   O | | o   O | | o   O | | o   O |
o       O o       O o       O o       O o       O o       O
   ___ _ _                       __                      
  / _ \ (_) ___  _ __ ___   __ _/ _\ ___ ___  _ __   ___ 
 / /_\/ | |/ _ \| '_ ` _ \ / _` \ \ / __/ _ \| '_ \ / _ \
/ /_\\| | | (_) | | | | | | (_| |\ \ (_| (_) | |_) |  __/
\____/|_|_|\___/|_| |_| |_|\__,_\__/\___\___/| .__/ \___|
                                             |_|         
  
          Designed for all. Built for insight. 
        Dive deep into glioma transcriptomics.
             Fast. Intuitive. Insightful.
""")

    print("Are you looking for deeper insights into gliomas?")
    print("\nWell, here you can use your own metadata and gene expression data to explore the tumour landscape \nlike never before. \nGliomaScope lets you visualise PCA, UMAP, and gene expression patterns, perform differential analysis, \nmap genes to their chromosomal locations, and generate publication-ready insights. \nAll right from your terminal.\n")

    input("   Press ENTER to dive in...")

    os.system('cls' if os.name == 'nt' else 'clear')


    while True:
        print("\n=== GliomaScope CLI ===")
        print("1. Download + load GEO dataset by ID")
        print("2. Format dataset (upload .csv/.tsv) and select to load")
        print("3. Upload metadata file")
        print("4. Upload expression file")
        print("5. Data Exploration & Filtering")
        print("6. Geographic Visualization")
        print("7. Visualise PCA")
        print("8. Visualise UMAP")
        print("9. Differential expression analysis")
        print("10. Explore individual gene expression")
        print("11. Chromosomal gene mapping")
        print("12. Heatmap visualisation for gene sets")
        print("13. Exit")

        choice = input("Enter your choice (1-13): ").strip()

        if choice == '1':
            from Utils import fetch_and_format_geo, display_and_log_summary
            geo_id = input("Enter GEO Accession ID (e.g. GSE15824): ").strip()

            print("Loading dataset...")
            
            # Fetch DataFrames
            meta_df, expr_df = fetch_and_format_geo(geo_id)

            if meta_df is None or expr_df is None:
                print("Failed to load GEO dataset.")
                continue

            # Load into memory
            data_manager.load_metadata_df(meta_df)
            data_manager.load_expression_df(expr_df)

            # Optionally save to CSVs
            meta_df.to_csv(f"cleaned_data/{geo_id}_metadata.csv", index=False)
            expr_df.to_csv(f"cleaned_data/{geo_id}_expression.csv", index=False)

            # Display clean summary
            print(f"Successfully loaded GEO dataset {geo_id}")
            print(f"Metadata: {meta_df.shape[0]:,} samples × {meta_df.shape[1]:,} columns")
            print(f"Expression: {expr_df.shape[0]:,} samples × {expr_df.shape[1]:,} genes")
            if data_manager.merged is not None:
                print(f"Merged: {data_manager.merged.shape[0]:,} samples × {data_manager.merged.shape[1]:,} columns")
            print(f"Data ready for analysis!")

        elif choice == '2':
            upload_and_format_dataset()  # user uploads and formats their own dataset

        elif choice == '3':
            file_path = input("Enter path to metadata file (or smart file): ")
            data_manager.load_file_smart(file_path)

        elif choice == '4':
            file_path = input("Enter path to expression file: ")
            data_manager.load_expression(file_path)

        elif choice == '5':
            if data_manager.metadata is None and data_manager.expression is None:
                print("No data loaded. Please upload data first (Options 1-4).")
                continue
            
            print("\nDATA EXPLORATION & FILTERING")
            print("=" * 60)
            print("Explore and filter your data with a clean, unified interface.")
            print("=" * 60)
            
            while True:
                print("\nEXPLORATION OPTIONS:")
                print("1. View Data Summary")
                print("2. Preview Data")
                print("3. Filter Data")
                print("4. Back to Main Menu")
                
                sub_choice = input("\nSelect option (1-4): ").strip()
                
                if sub_choice == '1':
                    # Data Summary - Clean terminal output
                    print("\nDATA SUMMARY")
                    print("=" * 40)
                    
                    if data_manager.metadata is not None:
                        print(f"METADATA: {data_manager.metadata.shape[0]:,} samples × {data_manager.metadata.shape[1]:,} columns")
                        print(f"Missing values: {data_manager.metadata.isnull().sum().sum():,}")
                        print(f"Duplicate rows: {data_manager.metadata.duplicated().sum():,}")
                    
                    if data_manager.expression is not None:
                        print(f"EXPRESSION: {data_manager.expression.shape[0]:,} samples × {data_manager.expression.shape[1]:,} columns")
                        print(f"Missing values: {data_manager.expression.isnull().sum().sum():,}")
                        print(f"Duplicate rows: {data_manager.expression.duplicated().sum():,}")
                    
                    if data_manager.merged is not None:
                        print(f"MERGED: {data_manager.merged.shape[0]:,} samples × {data_manager.merged.shape[1]:,} columns")
                    
                    # Open detailed summary in browser
                    try:
                        import webbrowser
                        import tempfile
                        
                        if data_manager.metadata is not None:
                            # Create metadata summary
                            html_content = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <title>Data Summary</title>
                                <style>
                                    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                                    .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                                    h1, h2, h3 {{ color: #333; }}
                                    .summary-box {{ background-color: #e7f3ff; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #2196F3; }}
                                    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                                    .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
                                    .stat-number {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
                                    .stat-label {{ color: #666; margin-top: 5px; }}
                                    table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                    th {{ background-color: #f2f2f2; font-weight: bold; }}
                                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                                    .data-preview {{ max-height: 400px; overflow-y: auto; }}
                                </style>
                            </head>
                            <body>
                                <div class="container">
                                    <h1>Data Summary</h1>
                                    
                                    <div class="summary-box">
                                        <h3>Dataset Overview</h3>
                                        <div class="stats-grid">
                                            <div class="stat-card">
                                                <div class="stat-number">{data_manager.metadata.shape[0]:,}</div>
                                                <div class="stat-label">Samples</div>
                                            </div>
                                            <div class="stat-card">
                                                <div class="stat-number">{data_manager.metadata.shape[1]:,}</div>
                                                <div class="stat-label">Metadata Columns</div>
                                            </div>
                                            <div class="stat-card">
                                                <div class="stat-number">{data_manager.metadata.isnull().sum().sum():,}</div>
                                                <div class="stat-label">Missing Values</div>
                                            </div>
                                            <div class="stat-card">
                                                <div class="stat-number">{data_manager.metadata.duplicated().sum():,}</div>
                                                <div class="stat-label">Duplicate Rows</div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <h3>Column Information</h3>
                                    <table>
                                        <tr>
                                            <th>Column Name</th>
                                            <th>Data Type</th>
                                            <th>Non-Null Count</th>
                                            <th>Missing Values</th>
                                            <th>Unique Values</th>
                                        </tr>
                            """
                            
                            for col in data_manager.metadata.columns:
                                dtype = str(data_manager.metadata[col].dtype)
                                non_null = data_manager.metadata[col].count()
                                missing = data_manager.metadata[col].isnull().sum()
                                unique = data_manager.metadata[col].nunique()
                                
                                html_content += f"""
                                        <tr>
                                            <td>{col}</td>
                                            <td>{dtype}</td>
                                            <td>{non_null:,}</td>
                                            <td>{missing:,}</td>
                                            <td>{unique:,}</td>
                                        </tr>
                                """
                            
                            html_content += f"""
                                    </table>
                                    
                                    <h3>Data Preview</h3>
                                    <div class="data-preview">
                                        {data_manager.metadata.head(20).to_html(index=False)}
                                    </div>
                                </div>
                            </body>
                            </html>
                            """
                            
                            # Save to temporary file and open in browser
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                                f.write(html_content)
                                temp_file = f.name
                            
                            webbrowser.open(f'file://{temp_file}')
                            print("Opened detailed summary in browser")
                        
                    except Exception as e:
                        print(f"Could not open browser: {e}")
                
                elif sub_choice == '2':
                    # Data Preview - Clean terminal output
                    print("\nDATA PREVIEW")
                    print("=" * 40)
                    
                    if data_manager.metadata is not None:
                        print(f"METADATA: {data_manager.metadata.shape[0]:,} samples × {data_manager.metadata.shape[1]:,} columns")
                        print(f"Sample columns: {', '.join(data_manager.metadata.columns[:5])}{'...' if len(data_manager.metadata.columns) > 5 else ''}")
                    
                    if data_manager.expression is not None:
                        print(f"EXPRESSION: {data_manager.expression.shape[0]:,} samples × {data_manager.expression.shape[1]:,} columns")
                        gene_cols = [col for col in data_manager.expression.columns if col != 'Sample']
                        print(f"Genes: {len(gene_cols):,}")
                    
                    # Open preview in browser
                    try:
                        import webbrowser
                        import tempfile
                        
                        html_content = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Data Preview</title>
                            <style>
                                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                                h1, h2 {{ color: #333; }}
                                table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                th {{ background-color: #f2f2f2; font-weight: bold; }}
                                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                                .data-section {{ margin: 30px 0; }}
                            </style>
                        </head>
                        <body>
                            <div class="container">
                                <h1>Data Preview</h1>
                        """
                        
                        if data_manager.metadata is not None:
                            html_content += f"""
                                <div class="data-section">
                                    <h2>Metadata Preview (First 20 rows)</h2>
                                    {data_manager.metadata.head(20).to_html(index=False)}
                                </div>
                            """
                        
                        if data_manager.expression is not None:
                            # Show first 10 genes for preview
                            gene_cols = [col for col in data_manager.expression.columns if col != 'Sample'][:10]
                            preview_cols = ['Sample'] + gene_cols
                            html_content += f"""
                                <div class="data-section">
                                    <h2>Expression Preview (First 20 samples, First 10 genes)</h2>
                                    {data_manager.expression[preview_cols].head(20).to_html(index=False)}
                                </div>
                            """
                        
                        html_content += """
                            </div>
                        </body>
                        </html>
                        """
                        
                        # Save to temporary file and open in browser
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                            f.write(html_content)
                            temp_file = f.name
                        
                        webbrowser.open(f'file://{temp_file}')
                        print("Opened data preview in browser")
                        
                    except Exception as e:
                        print(f"Could not open browser: {e}")
                
                elif sub_choice == '3':
                    # Data Filtering - Clean and professional
                    if data_manager.metadata is None:
                        print("No metadata available for filtering.")
                        continue
                    
                    print("\nDATA FILTERING")
                    print("=" * 40)
                    print("Filter your data by selecting columns and values.")
                    print("Note: These datasets contain technical metadata (tissue type, extraction methods, etc.)")
                    print("Clinical metadata like age, grade, and IDH mutation status are not available.")
                    print("=" * 60)
                    
                    # Show available columns concisely
                    available_cols = list(data_manager.metadata.columns)
                    print(f"AVAILABLE COLUMNS ({len(available_cols)} total):")
                    for i, col in enumerate(available_cols, 1):
                        unique_count = data_manager.metadata[col].nunique()
                        print(f"   {i:2d}. {col}: {unique_count} values")
                    
                    filters = {}
                    
                    while True:
                        # Show current filter status
                        if filters:
                            filter_count = sum(len(vals) for vals in filters.values())
                            print(f"\nACTIVE FILTERS: {len(filters)} columns, {filter_count} total values applied")
                        else:
                            print(f"\nNO FILTERS APPLIED")
                        
                        col_choice = input(f"\nEnter column number to filter by (1-{len(available_cols)}) or 'done' to finish: ").strip()
                        
                        if col_choice.lower() == 'done':
                            break
                        
                        try:
                            col_index = int(col_choice) - 1
                            if 0 <= col_index < len(available_cols):
                                selected_col = available_cols[col_index]
                                
                                # Show available values concisely
                                unique_vals = data_manager.metadata[selected_col].dropna().unique()
                                print(f"\nVALUES IN '{selected_col}' ({len(unique_vals)} total):")
                                
                                # Show first 10 values with counts, then summarize
                                for i, val in enumerate(unique_vals[:10], 1):
                                    count = len(data_manager.metadata[data_manager.metadata[selected_col] == val])
                                    print(f"   {i:2d}. '{val}' ({count} samples)")
                                
                                if len(unique_vals) > 10:
                                    print(f"   ... and {len(unique_vals) - 10} more values")
                                
                                print(f"Tip: Type 'all' for all values, or numbers like '1,2,3'")
                                
                                # Get filter value
                                filter_input = input(f"Enter values to filter by for '{selected_col}' (comma-separated, numbers, or 'all'): ").strip()
                                
                                if filter_input.lower() == 'all':
                                    # Include all values for this column
                                    filters[selected_col] = list(unique_vals)
                                    print(f"Added: {selected_col} = all values")
                                else:
                                    selected_vals = [v.strip() for v in filter_input.split(',')]
                                    # Handle numeric indices
                                    try:
                                        numeric_vals = [int(v) - 1 for v in selected_vals]
                                        actual_vals = [unique_vals[i] for i in numeric_vals if 0 <= i < len(unique_vals)]
                                        if actual_vals:
                                            filters[selected_col] = actual_vals
                                            print(f"Added: {selected_col} = {actual_vals}")
                                        else:
                                            print("No valid values selected.")
                                    except ValueError:
                                        # Treat as actual values
                                        filters[selected_col] = selected_vals
                                        print(f"Added: {selected_col} = {selected_vals}")
                            else:
                                print(f"Please enter a number between 1 and {len(available_cols)}")
                        except ValueError:
                            print("Please enter a valid number or 'done'")
                    
                    # Apply filters
                    if filters:
                        filtered_metadata = data_manager.metadata.copy()
                        
                        for col, values in filters.items():
                            if col in filtered_metadata.columns:
                                filtered_metadata = filtered_metadata[filtered_metadata[col].astype(str).isin(values)]
                            else:
                                print(f"Warning: Column '{col}' not found in metadata")
                        
                        if len(filtered_metadata) > 0:
                            print(f"\nFiltered: {len(data_manager.metadata)} -> {len(filtered_metadata)} samples")
                            
                            # Automatically open in browser
                            try:
                                import webbrowser
                                import tempfile
                                
                                # Create HTML table
                                html_content = f"""
                                <!DOCTYPE html>
                                <html>
                                <head>
                                    <title>Filtered Data - {len(filtered_metadata)} samples</title>
                                    <style>
                                        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                                        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                                        h1, h2 {{ color: #333; }}
                                        .summary-box {{ background-color: #e7f3ff; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #2196F3; }}
                                        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                        th {{ background-color: #f2f2f2; font-weight: bold; }}
                                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                                    </style>
                                </head>
                                <body>
                                    <div class="container">
                                        <h1>Filtered Data Results</h1>
                                        <div class="summary-box">
                                            <h3>Filter Summary</h3>
                                            <p><strong>Original samples:</strong> {len(data_manager.metadata):,}</p>
                                            <p><strong>Filtered samples:</strong> {len(filtered_metadata):,}</p>
                                            <p><strong>Applied filters:</strong></p>
                                            <ul>
                            """
                                
                                for col, values in filters.items():
                                    html_content += f"<li><strong>{col}:</strong> {', '.join(str(v) for v in values)}</li>"
                                
                                html_content += f"""
                                            </ul>
                                        </div>
                                        <h2>Filtered Data</h2>
                                        {filtered_metadata.to_html(index=False)}
                                    </div>
                                </body>
                                </html>
                                """
                                
                                # Save to temporary file and open in browser
                                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                                    f.write(html_content)
                                    temp_file = f.name
                                
                                webbrowser.open(f'file://{temp_file}')
                                print(f"Opened {len(filtered_metadata)} samples in browser")
                                
                            except Exception as e:
                                print(f"Could not open in browser: {e}")
                                print("Showing data in terminal instead:")
                                print(filtered_metadata.head(10).to_string(index=False))
                        else:
                            print("No samples match the selected filters.")
                    else:
                        print("No filters selected.")
                
                elif sub_choice == '4':
                    break
                
                else:
                    print("Invalid option. Please select 1-4.")

        elif choice == '6':
            if data_manager.metadata is not None:
                print("\nGEOGRAPHIC VISUALIZATION")
                print("=" * 60)
                print("Choose how to visualise your data geographically:")
                print("=" * 60)
                print("1. Study Origin Map (where studies were conducted)")
                print("2. Sample Distribution by Institution")
                
                sub_choice = input("\nEnter your choice (1-2): ").strip()

                try:
                    from Patient_geomap import create_study_origin_map, create_institution_map

                    if sub_choice == '1':
                        print("\nCreating Study Origin Map...")
                        create_study_origin_map(data_manager.metadata)
                        
                    elif sub_choice == '2':
                        print("\nCreating Institution Distribution Map...")
                        create_institution_map(data_manager.metadata)
                        
                    else:
                        print("Invalid option. Please choose 1-2.")
                        
                except Exception as e:
                    print(f"Error occurred while creating geographic visualization: {e}")
                    print("This might be because the data doesn't contain geographic information")
            else:
                print("No metadata loaded. Please upload metadata first (Options 1-4).")

        elif choice == '7':
            if data_manager.expression is None:
                print("ERROR: Expression data not loaded. Please upload expression data first (Option 4).")
            elif data_manager.metadata is None:
                print("ERROR: Metadata is not loaded. Please upload metadata first (Option 3).")
            else:
                print("\nPCA VISUALIZATION")
                print("=" * 60)
                print("PCA (Principal Component Analysis) reduces high-dimensional")
                print("gene expression data to 2D for visualization.")
                print()
                print("WHAT YOU'RE LOOKING FOR:")
                print("   • Sample clustering patterns and group separation")
                print("   • Data variance structure (PC1 vs PC2 components)")
                print("   • Outlier samples that behave differently")
                print("   • How well different sample groups separate from each other")
                print("=" * 60)
                
                # Import required function
                from Dimensionality_Reduction import plot_pca
                
                # Get only relevant columns for PCA grouping
                relevant_cols = get_relevant_columns_for_analysis(data_manager.metadata, min_values=2, max_values=20)
                
                if len(relevant_cols) == 0:
                    print("INFO: No suitable grouping columns found. Using default coloring.")
                    color_by = None
                else:
                    print(f"AVAILABLE GROUPING OPTIONS:")
                    print("=" * 50)
                    for i, col in enumerate(relevant_cols, 1):
                        unique_vals = data_manager.metadata[col].dropna().unique()
                        print(f"   {i:2d}. '{col}' ({len(unique_vals)} different values)")
                
                    print("\nTIP: EXAMPLES:")
                    print("   • Enter 'tissue_type' to compare control vs glioma")
                    print("   • Press Enter for auto-selection (recommended)")
                    
                    user_input = input("\nEnter column number or name (or press Enter for auto-selection): ").strip()
                    
                    color_by = None
                    if user_input:
                        # Check if input is a number
                        if user_input.isdigit():
                            col_index = int(user_input) - 1
                            if 0 <= col_index < len(relevant_cols):
                                color_by = relevant_cols[col_index]
                                print(f"Selected: '{color_by}'")
                            else:
                                print(f"Invalid number. Please enter 1-{len(relevant_cols)}.")
                                print("Using auto-selection instead.")
                        else:
                            # Check if input is a valid and relevant column name
                            if user_input in relevant_cols:
                                color_by = user_input
                                print(f"Selected: '{color_by}'")
                            else:
                                print(f"Column '{user_input}' not found in relevant options.")
                                print("Using auto-selection instead.")
                    
                    # Auto-select first relevant column if none selected
                    if not color_by and relevant_cols:
                        color_by = relevant_cols[0]
                        print(f"Auto-selected: '{color_by}'")

                print(f"\nGenerating PCA plot...")
                if color_by:
                    print(f"   Colouring by: '{color_by}'")
                else:
                    print(f"   No colouring (all samples same colour)")

                try:
                    plot_pca(
                        data_manager.expression,
                        data_manager.metadata,
                        color_by=color_by
                    )
                except Exception as e:
                    print(f"Error occurred while plotting PCA: {e}")
                    print("Try a different grouping column or check your data")

        elif choice == '8':
            if data_manager.expression is None:
                print("ERROR: Expression data not loaded. Please upload expression data first (Option 4).")
            elif data_manager.metadata is None:
                print("ERROR: Metadata is not loaded. Please upload metadata first (Option 3).")
            else:
                print("\nUMAP VISUALIZATION")
                print("=" * 60)
                print("UMAP (Uniform Manifold Approximation and Projection) reduces")
                print("high-dimensional gene expression data to 2D for visualisation.")
                print()
                print("WHAT YOU'RE LOOKING FOR:")
                print("   • Local neighborhood structures and cell-type clustering")
                print("   • Non-linear relationships between samples")
                print("   • Tight clusters of similar samples (better than PCA)")
                print("   • Preserved local distances and manifold structure")
                print("=" * 60)
                
                # Import required function
                from Dimensionality_Reduction import plot_umap
                
                # Get only relevant columns for UMAP grouping
                relevant_cols = get_relevant_columns_for_analysis(data_manager.metadata, min_values=2, max_values=20)
                
                if len(relevant_cols) == 0:
                    print("INFO: No suitable grouping columns found. Using default coloring.")
                    color_by = None
                else:
                    print(f"AVAILABLE GROUPING OPTIONS:")
                    print("=" * 50)
                    for i, col in enumerate(relevant_cols, 1):
                        unique_vals = data_manager.metadata[col].dropna().unique()
                        print(f"   {i:2d}. '{col}' ({len(unique_vals)} different values)")
                
                    print("\nTIP: EXAMPLES:")
                    print("   • Enter 'tissue_type' to compare control vs glioma")
                    print("   • Press Enter for auto-selection (recommended)")
                    
                    user_input = input("\nEnter column number or name (or press Enter for auto-selection): ").strip()
                    
                    color_by = None
                    if user_input:
                        # Check if input is a number
                        if user_input.isdigit():
                            col_index = int(user_input) - 1
                            if 0 <= col_index < len(relevant_cols):
                                color_by = relevant_cols[col_index]
                                print(f"Selected: '{color_by}'")
                            else:
                                print(f"Invalid number. Please enter 1-{len(relevant_cols)}.")
                                print("Using auto-selection instead.")
                        else:
                            # Check if input is a valid and relevant column name
                            if user_input in relevant_cols:
                                color_by = user_input
                                print(f"Selected: '{color_by}'")
                            else:
                                print(f"Column '{user_input}' not found in relevant options.")
                                print("Using auto-selection instead.")
                    
                    # Auto-select first relevant column if none selected
                    if not color_by and relevant_cols:
                        color_by = relevant_cols[0]
                        print(f"Auto-selected: '{color_by}'")

                print(f"\nGenerating UMAP plot...")
                if color_by:
                    print(f"   Colouring by: '{color_by}'")
                else:
                    print(f"   No colouring (all samples same colour)")

                try:
                    plot_umap(
                        data_manager.expression,
                        data_manager.metadata,
                        color_by=color_by
                    )
                except Exception as e:
                    print(f"Error occurred while plotting UMAP: {e}")
                    print("Try a different grouping column or check your data")

        elif choice == '9':
            if data_manager.expression is not None and data_manager.metadata is not None:
                from Differential_expression import perform_differential_expression

                print("\nDIFFERENTIAL EXPRESSION ANALYSIS")
                print("=" * 60)
                print("This analysis compares gene expression between two groups of samples.")
                print("For example: control vs glioma, or different tissue types")
                print("=" * 60)
                
                # Get only relevant columns for analysis (filters out technical columns and single/too-many values)
                comparison_cols = get_relevant_columns_for_analysis(data_manager.metadata, min_values=2, max_values=50)
                
                if len(comparison_cols) == 0:
                    print("ERROR: No columns found with multiple values for comparison!")
                    print("All metadata columns contain only single values.")
                    print("Differential expression requires at least 2 different groups to compare.")
                    continue
                
                # Identify the most useful columns for differential expression
                useful_cols = ['tissue_type', 'sample_title', 'source_name_ch1', 'characteristics_ch1']
                
                print(f"RECOMMENDED COLUMNS FOR COMPARISON:")
                print("=" * 50)
                recommended_found = False
                for col in useful_cols:
                    if col in comparison_cols:
                        unique_vals = data_manager.metadata[col].dropna().unique()
                        if len(unique_vals) <= 5:
                            print(f"   • '{col}': {', '.join(map(str, unique_vals))}")
                        else:
                            print(f"   • '{col}': {', '.join(map(str, unique_vals[:3]))}... (and {len(unique_vals)-3} more)")
                        recommended_found = True
                
                if not recommended_found:
                    print("   No standard comparison columns found with multiple values.")
                    print("   See all available columns below.")
                
                print(f"\nALL AVAILABLE COLUMNS (with multiple values):")
                print("=" * 50)
                for i, col in enumerate(comparison_cols, 1):
                    unique_vals = data_manager.metadata[col].dropna().unique()
                    print(f"   {i:2d}. '{col}' ({len(unique_vals)} different values)")
                
                print("\nEXAMPLES:")
                print("   • Enter 'tissue_type' to compare control vs glioma brain tissue")
                print("   • Enter 'sample_title' to compare individual sample groups")
                print("   • Choose columns with 2+ different values for meaningful comparisons")
                
                print("\n" + "=" * 60)
                
                # Get user input with numbered selection
                user_input = input("Enter column number or name (or press Enter for auto-selection): ").strip()
                
                group_col = None
                if user_input:
                    # Check if input is a number
                    if user_input.isdigit():
                        col_index = int(user_input) - 1
                        if 0 <= col_index < len(comparison_cols):
                            group_col = comparison_cols[col_index]
                            print(f"Selected: '{group_col}'")
                        else:
                            print(f"Invalid number. Please enter 1-{len(comparison_cols)}.")
                            print("Using auto-selection instead.")
                    else:
                        # Check if input is a valid column name and has multiple values
                        if user_input in data_manager.metadata.columns:
                            if user_input in comparison_cols:
                                group_col = user_input
                                print(f"Selected: '{group_col}'")
                            else:
                                unique_vals = data_manager.metadata[user_input].dropna().unique()
                                print(f"ERROR: Column '{user_input}' has only {len(unique_vals)} unique value(s): {list(unique_vals)}")
                                print("Differential expression requires columns with at least 2 different values.")
                                print("Using auto-selection instead.")
                        else:
                            print(f"Column '{user_input}' not found in metadata.")
                            print("Using auto-selection instead.")
                
                # Auto-select if no valid input
                if not group_col:
                    for col in useful_cols:
                        if col in comparison_cols:
                            group_col = col
                            print(f"Auto-selected: '{group_col}'")
                            break
                    
                    # If no useful columns, pick the first available comparison column
                    if not group_col and comparison_cols:
                        group_col = comparison_cols[0]
                        print(f"Auto-selected: '{group_col}'")
                
                # Show available values for the selected column
                unique_vals = data_manager.metadata[group_col].dropna().unique()
                print(f"\nINFO: AVAILABLE VALUES IN '{group_col}':")
                print("=" * 50)
                for i, val in enumerate(unique_vals, 1):
                    count = len(data_manager.metadata[data_manager.metadata[group_col] == val])
                    print(f"   {i:2d}. '{val}' ({count:3d} samples)")
                
                print(f"\nTIP: Choose two different values to compare:")
                print("   You can enter either:")
                print("   • The number (1, 2, 3...) from the list above")
                print("   • The actual value name in quotes (e.g., 'RNA', 'Control')")
                group_1_input = input(f"Enter the first group value: ").strip()
                group_2_input = input(f"Enter the second group value: ").strip()
                
                # Convert index numbers to actual values
                def get_value_from_input(input_val, unique_vals):
                    # Try to convert to integer index
                    try:
                        index = int(input_val) - 1  # Convert to 0-based index
                        if 0 <= index < len(unique_vals):
                            return unique_vals[index]
                    except ValueError:
                        pass
                    
                    # If not an index, treat as actual value
                    return input_val
                
                group_1 = get_value_from_input(group_1_input, unique_vals)
                group_2 = get_value_from_input(group_2_input, unique_vals)
                
                # Check if same value selected
                if group_1 == group_2:
                    print(f"ERROR: You selected the same value '{group_1}' for both groups!")
                    print(f"TIP: Please choose two different values to compare.")
                    continue
                
                # Validate the values exist
                if group_1 not in unique_vals:
                    print(f"ERROR: Value '{group_1_input}' not found in column '{group_col}'")
                    print(f"\nINFO: Available values:")
                    for i, val in enumerate(unique_vals, 1):
                        count = len(data_manager.metadata[data_manager.metadata[group_col] == val])
                        print(f"   {i:2d}. '{val}' ({count:3d} samples)")
                    print(f"\nTIP: Please choose from the values listed above!")
                    print(f"   • Enter a number (1-{len(unique_vals)}) or the exact value name")
                    continue
                    
                if group_2 not in unique_vals:
                    print(f"ERROR: Value '{group_2_input}' not found in column '{group_col}'")
                    print(f"\nINFO: Available values:")
                    for i, val in enumerate(unique_vals, 1):
                        count = len(data_manager.metadata[data_manager.metadata[group_col] == val])
                        print(f"   {i:2d}. '{val}' ({count:3d} samples)")
                    print(f"\nTIP: Please choose from the values listed above!")
                    print(f"   • Enter a number (1-{len(unique_vals)}) or the exact value name")
                    continue

                print(f"\nANALYSIS: Running differential expression analysis...")
                print(f"   Comparing: {group_col} = '{group_1}' vs '{group_2}'")
                print(f"   Total samples: {len(data_manager.metadata)}")
                print(f"   Group 1 samples: {len(data_manager.metadata[data_manager.metadata[group_col] == group_1])}")
                print(f"   Group 2 samples: {len(data_manager.metadata[data_manager.metadata[group_col] == group_2])}")

                try:
                    results = perform_differential_expression(
                        data_manager.expression,
                        data_manager.metadata,
                        group_col=group_col,
                        group_1=group_1,
                        group_2=group_2
                    )
                    
                    # Filter for significant results (adjusted p < 0.05)
                    significant_results = results[results['adj_p_value'] < 0.05]

                    if not significant_results.empty:
                        print(f"\nSUCCESS: Analysis complete!")
                        print(f"INFO: Found {len(significant_results)} significant genes (FDR < 0.05)")
                        print(f"INFO: Total genes analysed: {len(results)}")
                        print("\nTOP: Top 10 most significant genes:")
                        print("=" * 80)
                        print(significant_results.head(10)[['Gene', 'log2FC', 'p_value', 'adj_p_value']].to_string(index=False))
                        print("=" * 80)
                        print("TIP: log2FC > 0: Higher in group 2 | log2FC < 0: Higher in group 1")
                    else:
                        print(f"\nINFO: Analysis complete!")
                        print(f"INFO: Total genes analysed: {len(results)}")
                        print("WARNING:  No significant genes found (FDR < 0.05)")
                        print("TIP: Try different groups or check your data quality")
                        
                except Exception as e:
                    print(f"ERROR: Error during differential expression analysis: {e}")
                    print("TIP: Make sure your groups have enough samples and the data is properly formatted")
            else:
                print("ERROR: Expression or metadata file not loaded. Please upload both before using this option.")

        elif choice == '10':
            if data_manager.expression is None:
                print("ERROR: Expression data not loaded. Please upload expression data first (Option 4).")
            elif data_manager.metadata is None:
                print("ERROR: Metadata is not loaded. Please upload metadata first (Option 3).")
            else:
                print("\nGENE: EXPLORE INDIVIDUAL GENE EXPRESSION")
                print("=" * 60)
                print("This tool lets you explore expression patterns of individual genes.")
                print("=" * 60)
                
                # Import required functions
                from Gene_explorer import explore_gene_expression
                from Utils import list_all_available_genes
                
                # Show available genes with their mappings in numbered format
                from Utils import get_all_available_genes, load_gene_annotations
                
                annotations = load_gene_annotations()
                all_genes_mapping = get_all_available_genes(data_manager.expression, annotations)
                
                # Create a unique list of GENE NAMES only (no probe IDs)
                unique_genes = {}  # gene_name -> probe_id
                display_names = []  # For numbered display (gene names only)
                probe_list = []     # Corresponding probe IDs
                
                # Collect only genes with known names - skip probe IDs without gene mappings
                for probe_id in data_manager.expression.columns:
                    if probe_id != 'Sample':
                        if annotations is not None:
                            from Utils import map_probe_to_gene
                            mapped_name = map_probe_to_gene(probe_id, annotations)
                            if mapped_name != probe_id:
                                # This probe has a known gene name - add it
                                if mapped_name not in unique_genes:
                                    unique_genes[mapped_name] = probe_id
                                    display_names.append(mapped_name)
                                    probe_list.append(probe_id)
                                # If gene already exists, skip duplicate (keep first mapping)
                        # Note: We skip probe IDs that don't have gene names
                
                # Sort gene names alphabetically for easier browsing
                sorted_genes = sorted(zip(display_names, probe_list))
                display_names = [gene for gene, probe in sorted_genes]
                probe_list = [probe for gene, probe in sorted_genes]
                
                if len(display_names) == 0:
                    print("ERROR: No genes with known names found in this dataset.")
                    print("This dataset may not have gene annotation information.")
                    print("You can still use probe IDs directly if you know them.")
                    continue
                
                print(f"\nAVAILABLE GENES FOR EXPRESSION ANALYSIS")
                print("=" * 60)
                print(f"Total genes with known names: {len(display_names):,}")
                print("(Sorted alphabetically for easy browsing)")
                print("=" * 60)
                
                # Show only gene names (no probe IDs)
                for i, gene_name in enumerate(display_names, 1):
                    print(f"   {i:4d}. {gene_name}")
                    
                    # Add pagination for better readability
                    if i % 50 == 0 and i < len(display_names):
                        continue_viewing = input(f"\nShowing {i}/{len(display_names)} genes. Press Enter to continue or 'q' to stop: ").strip()
                        if continue_viewing.lower() == 'q':
                            print(f"... and {len(display_names) - i:,} more genes available")
                            break
                
                print("=" * 60)
                print("TIP: Popular glioma genes include: TP53, EGFR, MGMT, IDH1, ATRX, PTEN")
                print("TIP: You can enter:")
                print(f"   • Number (1-{len(display_names)}) from the gene list above")
                print("   • Gene name directly (e.g., TP53, EGFR, MGMT)")
                print("   • Probe ID if you know it (e.g., 10000_at)")
                print("=" * 60)
                
                user_input = input(f"\nEnter gene number (1-{len(display_names)}), name, or probe ID: ").strip()

                try:
                    # Handle numbered input, gene names, or probe IDs
                    probe_id = None
                    gene_name = None
                    
                    if user_input.isdigit():
                        # User entered a number
                        gene_index = int(user_input) - 1
                        if 0 <= gene_index < len(probe_list):
                            probe_id = probe_list[gene_index]
                            gene_name = display_names[gene_index]
                            print(f"Selected: {gene_name}")
                        else:
                            print(f"Invalid number. Please enter 1-{len(probe_list)}.")
                            continue
                    else:
                        # User entered gene name or probe ID
                        gene_name = user_input
                        gene_upper = user_input.upper()
                        
                        if user_input in data_manager.expression.columns:
                            # Already a probe ID
                            probe_id = user_input
                            print(f"SUCCESS: Using probe ID: '{user_input}'")
                        elif gene_upper in all_genes_mapping:
                            # Found gene name in mapping
                            probe_id = all_genes_mapping[gene_upper]
                            print(f"SUCCESS: Mapped '{user_input}' to probe ID '{probe_id}'")
                        else:
                            print(f"ERROR: Could not find gene '{user_input}' in available genes")
                            print("TIP: Try using one of the numbered options (1-50) from the list above")
                            print("TIP: Popular glioma genes: TP53, EGFR, MGMT, IDH1, ATRX, PTEN")
                            
                            # Show some suggestions based on what the user typed
                            suggestions = []
                            for available_gene in all_genes_mapping.keys():
                                if gene_upper in available_gene.upper() or available_gene.upper() in gene_upper:
                                    suggestions.append(available_gene)
                            
                            if suggestions:
                                print(f"TIP: Did you mean one of these? {', '.join(suggestions[:5])}")
                            
                            continue

                    # Get only relevant columns for gene expression grouping
                    relevant_cols = get_relevant_columns_for_analysis(data_manager.metadata, min_values=2, max_values=20)
                    
                    print(f"\nINFO: GROUPING OPTIONS FOR GENE EXPRESSION PLOT:")
                    print("=" * 50)
                    print("Choose how to group your samples for comparison:")
                    
                    if len(relevant_cols) == 0:
                        print("INFO: No suitable grouping columns found. Will show overall expression.")
                        group_col = None
                    else:
                        for i, col in enumerate(relevant_cols, 1):
                            unique_vals = data_manager.metadata[col].dropna().unique()
                            print(f"   {i:2d}. '{col}' ({len(unique_vals)} different values)")
                    
                        print("\nTIP: EXAMPLES:")
                        print("   • Enter 'tissue_type' to compare control vs glioma")
                        print("   • Press Enter for auto-selection (recommended)")
                        
                        user_input = input("\nEnter column number or name (or press Enter for auto-selection): ").strip()
                        
                        group_col = None
                        if user_input:
                            # Check if input is a number
                            if user_input.isdigit():
                                col_index = int(user_input) - 1
                                if 0 <= col_index < len(relevant_cols):
                                    group_col = relevant_cols[col_index]
                                    print(f"Selected: '{group_col}'")
                                else:
                                    print(f"Invalid number. Please enter 1-{len(relevant_cols)}.")
                                    print("Using auto-selection instead.")
                            else:
                                # Check if input is a valid and relevant column name
                                if user_input in relevant_cols:
                                    group_col = user_input
                                    print(f"Selected: '{group_col}'")
                                else:
                                    print(f"Column '{user_input}' not found in relevant options.")
                                    print("Using auto-selection instead.")
                        
                        # Auto-select first relevant column if none selected
                        if not group_col and relevant_cols:
                            group_col = relevant_cols[0]
                            print(f"Auto-selected: '{group_col}'")

                    print(f"\nANALYSIS: Exploring gene expression for '{gene_name}'...")
                    explore_gene_expression(data_manager.expression, data_manager.metadata, probe_id, group_col)
                    
                except Exception as e:
                    print(f"ERROR: Error occurred while exploring gene expression: {e}")
                    print("TIP: Make sure your data is properly loaded and formatted")

        elif choice == '11':
            if data_manager.expression is not None and data_manager.metadata is not None:
                from Gene_explorer import explore_gene_expression, map_gene_to_chromosome
                from Utils import list_all_available_genes

                print("\nCHROMOSOMAL GENE MAPPING")
                print("=" * 60)
                print("This tool maps genes to their chromosomal locations and displays")
                print("chromosome ideograms with gene positions.")
                print("=" * 60)
                
                # Import required functions for gene mapping
                from Utils import get_all_available_genes, load_gene_annotations
                
                annotations = load_gene_annotations()
                all_genes_mapping = get_all_available_genes(data_manager.expression, annotations)
                
                # Create a unique list of GENE NAMES only (same logic as Option 10)
                unique_genes = {}  # gene_name -> probe_id
                display_names = []  # For numbered display (gene names only)
                probe_list = []     # Corresponding probe IDs
                
                # Collect only genes with known names - skip probe IDs without gene mappings
                for probe_id in data_manager.expression.columns:
                    if probe_id != 'Sample':
                        if annotations is not None:
                            from Utils import map_probe_to_gene
                            mapped_name = map_probe_to_gene(probe_id, annotations)
                            if mapped_name != probe_id:
                                # This probe has a known gene name - add it
                                if mapped_name not in unique_genes:
                                    unique_genes[mapped_name] = probe_id
                                    display_names.append(mapped_name)
                                    probe_list.append(probe_id)
                
                # Sort gene names alphabetically for easier browsing
                sorted_genes = sorted(zip(display_names, probe_list))
                display_names = [gene for gene, probe in sorted_genes]
                probe_list = [probe for gene, probe in sorted_genes]
                
                if len(display_names) == 0:
                    print("ERROR: No genes with known names found in this dataset.")
                    print("This dataset may not have gene annotation information.")
                    print("You can still use probe IDs directly if you know them.")
                    continue
                
                print(f"\nAVAILABLE GENES FOR CHROMOSOME MAPPING")
                print("=" * 60)
                print(f"Total genes with known names: {len(display_names):,}")
                print("(Sorted alphabetically for easy browsing)")
                print("=" * 60)
                
                # Show only gene names (no probe IDs)
                for i, gene_name in enumerate(display_names, 1):
                    print(f"   {i:4d}. {gene_name}")
                    
                    # Add pagination for better readability
                    if i % 20 == 0 and i < len(display_names):
                        continue_viewing = input(f"\nShowing {i}/{len(display_names)} genes. Press Enter to continue or 'q' to stop: ").strip()
                        if continue_viewing.lower() == 'q':
                            print(f"... and {len(display_names) - i:,} more genes available")
                            break
                
                print("=" * 60)
                print("TIP: Popular glioma genes include: TP53, EGFR, MGMT, IDH1, ATRX, PTEN")
                print("TIP: You can enter:")
                print(f"   • Number (1-{len(display_names)}) from the gene list above")
                print("   • Gene name directly (e.g., TP53, EGFR, MGMT)")
                print("   • Probe ID if you know it (e.g., 10000_at)")
                print("=" * 60)
                
                user_input = input(f"\nEnter gene number (1-{len(display_names)}), name, or probe ID: ").strip()

                try:
                    # Handle numbered input, gene names, or probe IDs
                    probe_id = None
                    gene_name = None
                    
                    if user_input.isdigit():
                        # User entered a number
                        gene_index = int(user_input) - 1
                        if 0 <= gene_index < len(probe_list):
                            probe_id = probe_list[gene_index]
                            gene_name = display_names[gene_index]
                            print(f"Selected: {gene_name}")
                        else:
                            print(f"Invalid number. Please enter 1-{len(probe_list)}.")
                            continue
                    else:
                        # User entered gene name or probe ID
                        gene_name = user_input

                        gene_upper = user_input.upper()
                        
                        if user_input in data_manager.expression.columns:
                            # Already a probe ID
                            probe_id = user_input
                            print(f"SUCCESS: Using probe ID: '{user_input}'")
                        elif gene_upper in all_genes_mapping:
                            # Found gene name in mapping
                            probe_id = all_genes_mapping[gene_upper]
                            print(f"SUCCESS: Mapped '{user_input}' to probe ID '{probe_id}'")
                            gene_name = user_input
                        else:
                            print(f"ERROR: Could not find gene '{user_input}' in available genes")
                            print("TIP: Try using one of the numbered options (1-10) from the list above")
                            print("TIP: Popular glioma genes: TP53, EGFR, MGMT, IDH1, ATRX, PTEN")
                            
                            # Show some suggestions based on what the user typed
                            suggestions = []
                            for available_gene in all_genes_mapping.keys():
                                if gene_upper in available_gene.upper() or available_gene.upper() in gene_upper:
                                    suggestions.append(available_gene)
                            
                            if suggestions:
                                print(f"TIP: Did you mean one of these? {', '.join(suggestions[:5])}")
                            
                            continue
                    
                    print(f"\nMAPPING: Mapping gene '{gene_name}' to chromosome...")
                    map_gene_to_chromosome(gene_name)
                    
                except Exception as e:
                    print(f"ERROR: Error occurred while mapping gene to chromosome: {e}")
                    print("TIP: Make sure your data is properly loaded and formatted")
            else:
                print("ERROR: Expression or metadata file not loaded. Please upload both before using this option.")

        elif choice == '12':
            if data_manager.expression is not None and data_manager.metadata is not None:
                from Heatmap_visualisation import plot_expression_heatmap
                from Utils import get_all_available_genes, load_gene_annotations
                
                print("\nHEATMAP VISUALIZATION")
                print("=" * 60)
                print("This tool creates expression heatmaps for multiple genes")
                print("with optional sample grouping.")
                print("=" * 60)
                
                # Import required functions for gene mapping
                annotations = load_gene_annotations()
                all_genes_mapping = get_all_available_genes(data_manager.expression, annotations)
                
                # Create a unique list of GENE NAMES only (same logic as Options 10 & 11)
                unique_genes = {}  # gene_name -> probe_id
                display_names = []  # For numbered display (gene names only)
                probe_list = []     # Corresponding probe IDs
                
                # Collect only genes with known names - skip probe IDs without gene mappings
                for probe_id in data_manager.expression.columns:
                    if probe_id != 'Sample':
                        if annotations is not None:
                            from Utils import map_probe_to_gene
                            mapped_name = map_probe_to_gene(probe_id, annotations)
                            if mapped_name != probe_id:
                                # This probe has a known gene name - add it
                                if mapped_name not in unique_genes:
                                    unique_genes[mapped_name] = probe_id
                                    display_names.append(mapped_name)
                                    probe_list.append(probe_id)
                
                # Sort gene names alphabetically for easier browsing
                sorted_genes = sorted(zip(display_names, probe_list))
                display_names = [gene for gene, probe in sorted_genes]
                probe_list = [probe for gene, probe in sorted_genes]
                
                if len(display_names) == 0:
                    print("ERROR: No genes with known names found in this dataset.")
                    print("This dataset may not have gene annotation information.")
                    print("You can still use probe IDs directly if you know them.")
                    continue
                
                print(f"\nAVAILABLE GENES FOR HEATMAP VISUALIZATION")
                print("=" * 60)
                print(f"Total genes with known names: {len(display_names):,}")
                print("(Sorted alphabetically for easy browsing)")
                print("=" * 60)
                
                # Show only gene names (no probe IDs)
                for i, gene_name in enumerate(display_names, 1):
                    print(f"   {i:4d}. {gene_name}")
                    
                    # Add pagination for better readability
                    if i % 20 == 0 and i < len(display_names):
                        continue_viewing = input(f"\nShowing {i}/{len(display_names)} genes. Press Enter to continue or 'q' to stop: ").strip()
                        if continue_viewing.lower() == 'q':
                            print(f"... and {len(display_names) - i:,} more genes available")
                            break
                
                print("=" * 60)
                print("TIP: Popular glioma genes include: TP53, EGFR, MGMT, IDH1, ATRX, PTEN")
                print("TIP: You can enter:")
                print(f"   • Numbers (e.g., 1,3,5) from the gene list above")
                print("   • Gene names (e.g., TP53,EGFR,MGMT)")
                print("   • Mix of both (e.g., 1,EGFR,5)")
                print("=" * 60)
                
                gene_input = input(f"\nEnter genes for heatmap (comma-separated): ").strip()
                
                # Parse the input to handle numbers, gene names, and probe IDs
                gene_selections = [g.strip() for g in gene_input.split(',')]
                gene_list = []
                
                for selection in gene_selections:
                    if selection.isdigit():
                        # User entered a number
                        gene_index = int(selection) - 1
                        if 0 <= gene_index < len(probe_list):
                            gene_list.append(display_names[gene_index])
                            print(f"Selected #{selection}: {display_names[gene_index]}")
                        else:
                            print(f"Invalid number: {selection}. Please enter 1-{len(probe_list)}.")
                    else:
                        # User entered gene name or probe ID
                        gene_upper = selection.upper()
                        if gene_upper in all_genes_mapping:
                            gene_list.append(selection)
                            print(f"Selected gene: {selection}")
                        elif selection in data_manager.expression.columns:
                            gene_list.append(selection)
                            print(f"Selected probe: {selection}")
                        else:
                            print(f"Gene '{selection}' not found. Available genes: {', '.join(display_names[:5])}...")
                
                if not gene_list:
                    print("No valid genes selected. Please try again.")
                    continue
                
                print(f"\nSelected genes for heatmap: {', '.join(gene_list)}")

                # Get only relevant columns for heatmap grouping
                relevant_cols = get_relevant_columns_for_analysis(data_manager.metadata, min_values=2, max_values=20)
                
                if len(relevant_cols) == 0:
                    print("INFO: No suitable grouping columns found. Creating ungrouped heatmap.")
                    group_col = None
                else:
                    print(f"\nOPTIONAL: GROUPING OPTIONS FOR HEATMAP:")
                    print("=" * 50)
                    for i, col in enumerate(relevant_cols, 1):
                        unique_vals = data_manager.metadata[col].dropna().unique()
                        print(f"   {i:2d}. '{col}' ({len(unique_vals)} different values)")
                    
                    # Create example text from first 2 relevant columns
                    if len(relevant_cols) >= 2:
                        example_text = f"e.g. {relevant_cols[0]}, {relevant_cols[1]}"
                    elif len(relevant_cols) == 1:
                        example_text = f"e.g. {relevant_cols[0]}"
                    else:
                        example_text = ""
                    
                    group_col = input(f"Optional: Enter metadata column to group by ({example_text}) or press Enter to skip: ").strip()

                try:
                    plot_expression_heatmap(
                        data_manager.expression,
                        data_manager.metadata,
                        genes=gene_list,
                        group_col=group_col if group_col else None
                    )
                except Exception as e:
                    print(f"Error generating heatmap: {e}")
            else:
                print("Please upload both expression and metadata files first.")

        elif choice == '13':
            print("\n" + "=" * 60)
            print("Thank you for using GliomaScope!")
            print("=" * 60)
            print(r"""
O       o O       o O       o O       o O       o         O
| O   o | | O   o | | O   o | | O   o | | O   o | | O   o |
| | O | | | | O | | | | O | | | | O | | | | O | | | | O | |
| o   O | | o   O | | o   O | | o   O | | o   O | | o   O |
o       O o       O o       O o       O o       O o       O
   ___ _ _                       __                      
  / _ \ (_) ___  _ __ ___   __ _/ _\ ___ ___  _ __   ___ 
 / /_\/ | |/ _ \| '_ ` _ \ / _` \ \ / __/ _ \| '_ \ / _ \
/ /_\\| | | (_) | | | | | | (_| |\ \ (_| (_) | |_) |  __/
\____/|_|_|\___/|_| |_| |_|\__,_\__/\___\___/| .__/ \___|
                                             |_|         
  
          Thank you for exploring glioma transcriptomics!
        Your insights contribute to advancing brain cancer research.
             Until next time, keep discovering!
""")
            sys.exit()
        else:
            print("Invalid choice. Please choose from 1-13. Try again.")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("Thank you for using GliomaScope!")
        print("=" * 60)
        print(r"""
O       o O       o O       o O       o O       o         O
| O   o | | O   o | | O   o | | O   o | | O   o | | O   o |
| | O | | | | O | | | | O | | | | O | | | | O | | | | O | |
| o   O | | o   O | | o   O | | o   O | | o   O | | o   O |
o       O o       O o       O o       O o       O o       O
   ___ _ _                       __                      
  / _ \ (_) ___  _ __ ___   __ _/ _\ ___ ___  _ __   ___ 
 / /_\/ | |/ _ \| '_ ` _ \ / _` \ \ / __/ _ \| '_ \ / _ \
/ /_\\| | | (_) | | | | | | (_| |\ \ (_| (_) | |_) |  __/
\____/|_|_|\___/|_| |_| |_|\__,_\__/\___\___/| .__/ \___|
                                             |_|         
  
          Thank you for exploring glioma transcriptomics!
        Your insights contribute to advancing brain cancer research.
             Until next time, keep discovering!
""")
        sys.exit(0)
