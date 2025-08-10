import pandas as pd

def preview_dataframe(df, name='Data', n=5):
    print(f"\n{name.upper()} PREVIEW (first {n} rows):")
    print("=" * 50)
    print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]:,} columns")
    print(f"Columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
    print("=" * 50)
    
    # Show first few rows
    if len(df.columns) <= 10:
        print(df.head(n).to_string(index=False))
    else:
        print("Dataset has many columns. Showing first 5 columns:")
        print(df.iloc[:n, :5].to_string(index=False))
    
    print(f"\nUse Option 6 to explore full data in browser")


def display_summary(df, name='Data'):
    print(f"\n{name.upper()} SUMMARY:")
    print("=" * 50)
    print(f"Shape: {df.shape[0]:,} rows × {df.shape[1]:,} columns")
    print(f"Missing values: {df.isnull().sum().sum():,}")
    print(f"Duplicated rows: {df.duplicated().sum():,}")
    
    # Column types summary
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    print(f"Column types:")
    print(f"  - Numeric columns: {len(numeric_cols):,} columns")
    print(f"  - Categorical columns: {len(categorical_cols):,} columns")
    
    # Show sample of numeric columns
    if len(numeric_cols) > 0:
        print(f"Numeric columns: {len(numeric_cols):,} columns")
        if len(numeric_cols) <= 10:
            print(f"  {', '.join(numeric_cols)}")
        else:
            print(f"  {', '.join(numeric_cols[:5])}... and {len(numeric_cols)-5} more")
    
    # Create detailed HTML summary
    try:
        import webbrowser
        import tempfile
        
        # Generate comprehensive HTML summary
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{name} Summary</title>
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
                <h1>{name} Dataset Summary</h1>
                
                <div class="summary-box">
                    <h3>Dataset Summary</h3>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{df.shape[0]:,}</div>
                            <div class="stat-label">Rows</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{df.shape[1]:,}</div>
                            <div class="stat-label">Columns</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{df.isnull().sum().sum():,}</div>
                            <div class="stat-label">Missing Values</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{df.duplicated().sum():,}</div>
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
        
        for col in df.columns:
            dtype = str(df[col].dtype)
            non_null = df[col].count()
            missing = df[col].isnull().sum()
            unique = df[col].nunique()
            
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
                    {df.head(20).to_html(index=False)}
                </div>
                
                <h3>Numeric Columns Summary</h3>
                {df.describe().to_html() if len(numeric_cols) > 0 else '<p>No numeric columns found.</p>'}
            </div>
        </body>
        </html>
        """
        
        # Save to temporary file and open in browser
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_file = f.name
        
        webbrowser.open(f'file://{temp_file}')
        print(f"Opened detailed {name} data in browser")
        
    except Exception as e:
        print(f"Could not open browser: {e}")
        print("Showing summary in terminal:")
        print(df.describe())

def warn_if_missing_columns(df, required_columns):
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print(f"\nWarning: The following columns are missing from the dataset: {', '.join(missing)}")
    else:
        print("\nNo missing columns found.")

def filter_metadata(df):
    print("\n---- Filter metadata ----")
    if 'grade' not in df.columns or 'idh' not in df.colums or 'age' not in df.columns:
        print("Missing one or more required metadata columns: 'grade', 'idh', 'age'")
        return df
    
    grade = input("Filter by Grade (e.h. II, III, IV) or press enter to skip: ").strip()
    idh = input("Filter by IDH status (e.g. Mutant, Wildtype) or press enter to skip: ").strip()
    age = input("Filter by minimum age (e.g. 50) or press enter to skip: ").strip()

    filtered = df.copy()

    if grade:
        filtered = filtered[filtered['grade'].astype(str).str.upper() == grade.upper()]
    if idh:
        filtered = filtered[filtered['idh'].astype(str).str.upper() == idh.upper()]
        if age:
            try:
                age_val = float(age)
                filtered = filtered[filtered['age']>= age_val]
            except ValueError:
                print("Invalid age value. Skipping age filter.")
        
        print(f"\nFiltered dataset has {len(filtered)} samples.")
        return filtered