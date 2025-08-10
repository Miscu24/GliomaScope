# utils.py — Small reusable helpers (e.g. plotting wrappers, dict to JSON, label mapping)
# Central loader for all datasets (CSV/TSV); handles missing/incomplete data

import os
import json
import numpy as np
import pandas as pd
import plotly.express as px
import umap
import GEOparse  

# Add this function after the existing imports and before other functions

def get_column_name_mapping():
    """
    Returns a comprehensive mapping of GEO column names to user-friendly names.
    This makes the interface much more intuitive for users.
    """
    return {
        # Tissue and biological source
        'source_name_ch1': 'tissue_type',
        'source_name_ch2': 'tissue_type_2',
        'organism_ch1': 'organism',
        'organism_ch2': 'organism_2',
        
        # Sample characteristics
        'characteristics_ch1': 'tissue_characteristics',
        'characteristics_ch2': 'tissue_characteristics_2',
        'characteristics_ch3': 'tissue_characteristics_3',
        
        # Molecular information
        'molecule_ch1': 'molecule',
        'molecule_ch2': 'molecule_2',
        'extract_protocol_ch1': 'extraction_method',
        'extract_protocol_ch2': 'extraction_method_2',
        
        # Experimental protocols
        'label_protocol_ch1': 'labeling_method',
        'label_protocol_ch2': 'labeling_method_2',
        'hyb_protocol': 'hybridization_protocol',
        'scan_protocol': 'scanner_type',
        
        # Contact information
        'contact_name': 'submitter_name',
        'contact_email': 'submitter_email',
        'contact_phone': 'submitter_phone',
        'contact_laboratory': 'submitter_lab',
        'contact_department': 'submitter_dept',
        'contact_institute': 'institute',
        'contact_address': 'institute_address',
        'contact_city': 'institute_city',
        'contact_zip/postal_code': 'institute_zip',
        'contact_country': 'institute_country',
        
        # GEO identifiers
        'geo_accession': 'geo_id',
        'series_id': 'study_id',
        'data_row_count': 'gene_count',
        
        # Additional metadata
        'type': 'sample_type',
        'title': 'sample_title',
        'description': 'sample_description',
        'supplementary_file': 'supplementary_files',
        'relation': 'related_studies',
        
        # Common clinical fields (keep as is if already user-friendly)
        'age': 'age',
        'sex': 'sex',
        'gender': 'gender',
        'grade': 'tumor_grade',
        'idh': 'idh_status',
        'idh1': 'idh1_status',
        'idh2': 'idh2_status',
        'mgmt': 'mgmt_status',
        'survival': 'survival_time',
        'status': 'vital_status',
        'outcome': 'clinical_outcome',
        'diagnosis': 'diagnosis',
        'tumor_type': 'tumor_type',
        'location': 'tumor_location',
        'country': 'country',
        'institution': 'institution'
    }

# ----------------------------
# Basic Loaders and Cleaners
# ----------------------------

def load_data(file_path):
    ext = os.path.splitext(file_path)[1]
    if ext == '.csv':
        return pd.read_csv(file_path)
    elif ext in ['.tsv', '.txt']:
        return pd.read_csv(file_path, sep='\t')
    else:
        raise ValueError("Unsupported file format. Use .csv or .tsv")

def handle_missing_data(data, method='fill_zero'):
    if method == 'fill_zero':
        return data.fillna(0)
    elif method == 'drop':
        return data.dropna()
    elif method == 'fill_mean':
        return data.fillna(data.mean(numeric_only=True))
    else:
        raise ValueError("Invalid method. Choose 'fill_zero', 'drop', or 'fill_mean'")

import numpy as np  # Ensure this is imported at the top

def validate_file_type(df):
    import numpy as np

    # Standardise column names to lowercase for matching
    cols = [col.lower() for col in df.columns]

    # Check for metadata first (before looking for Sample column)
    metadata_keywords = ['age', 'sex', 'grade', 'idh', 'location']
    if any(key in col for col in cols for key in metadata_keywords):
        return 'metadata'

    # Check for expression: lots of numeric gene columns (before looking for Sample column)
    gene_cols = [col for col in df.columns if col.lower() not in ['Sample', 'gene_id']]
    numeric_cols = df[gene_cols].select_dtypes(include=[np.number])

    if len(gene_cols) >= 30 and len(numeric_cols.columns) / len(gene_cols) > 0.8:
        return 'expression'

    # Fallback: if 'Sample' column missing but index looks like sample IDs
    if not any(c == "Sample" for c in cols):
        if df.index.name and df.index.name.lower() == "sample":
            df.reset_index(inplace=True)
        elif df.index.dtype == 'object' and df.index.astype(str).str.startswith("GSM").all():  # GEO sample IDs
            df = df.copy()
            df.insert(0, "Sample", df.index)
            df.reset_index(drop=True, inplace=True)
        else:
            # Don't raise error, just return 'unknown' for now
            return 'unknown'

    return 'unknown'

# ----------------------------
# Summary + Logging
# ----------------------------

def summarise_dataframe(df, name='DataFrame'):
    return {
        "name": name,
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "data_type": validate_file_type(df),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicated_rows": int(df.duplicated().sum()),
        "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist()
    }

def convert_np(obj):
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    return str(obj)

def log_summary(summary_dict, filename="summary_log.json"):
    os.makedirs("logs", exist_ok=True)
    with open(os.path.join("logs", filename), "w") as f:
        json.dump(summary_dict, f, indent=4, default=convert_np)
    print(f"Summary saved to logs/{filename}")

def display_and_log_summary(df, name='DataFrame', log=True):
    summary = summarise_dataframe(df, name)
    
    # Show clean summary in terminal
    print(f"\n {name.upper()} SUMMARY:")
    print("=" * 50)
    print(f"Shape: {summary['shape']['rows']:,} rows × {summary['shape']['columns']:,} columns")
    print(f"Data type: {summary['data_type']}")
    print(f"Missing values: {summary['missing_values']:,}")
    print(f"Duplicated rows: {summary['duplicated_rows']:,}")
    print(f"Numeric columns: {len(summary['numeric_columns']):,}")
    
    if log:
        log_summary(summary, f"{name.lower()}_summary.json")
        print(f"Summary saved to logs/{name.lower()}_summary.json")

# ----------------------------
# Metadata Filtering
# ----------------------------

def filter_metadata(metadata_df, grade=None, idh=None, age_range=None):
    filtered = metadata_df.copy()
    
    # Check for grade column with various possible names
    grade_col = None
    for col in ['grade', 'Grade', 'GRADE', 'tumor_grade', 'who_grade']:
        if col in filtered.columns:
            grade_col = col
            break
    
    if grade and grade_col:
        filtered = filtered[filtered[grade_col].astype(str).str.lower() == grade.lower()]
        print(f"Filtered by {grade_col}: {grade}")
    elif grade:
        print(f"Warning: Grade column not found. Available columns: {list(filtered.columns)}")
    
    # Check for IDH column with various possible names
    idh_col = None
    for col in ['idh', 'IDH', 'idh_status', 'idh1', 'IDH1', 'idh_mutation']:
        if col in filtered.columns:
            idh_col = col
            break
    
    if idh and idh_col:
        filtered = filtered[filtered[idh_col].astype(str).upper() == idh.upper()]
        print(f"Filtered by {idh_col}: {idh}")
    elif idh:
        print(f"Warning: IDH column not found. Available columns: {list(filtered.columns)}")
    
    # Check for age column with various possible names
    age_col = None
    for col in ['age', 'Age', 'AGE', 'patient_age', 'age_at_diagnosis']:
        if col in filtered.columns:
            age_col = col
            break
    
    if age_range and age_col:
        try:
            min_age, max_age = age_range
            filtered = filtered[(filtered[age_col] >= min_age) & (filtered[age_col] <= max_age)]
            print(f"Filtered by {age_col}: {min_age}-{max_age}")
        except Exception as e:
            print(f"Invalid age range: {e}")
    elif age_range:
        print(f"Warning: Age column not found. Available columns: {list(filtered.columns)}")
    
    print(f"Filtered dataset has {len(filtered)} samples.")
    return filtered.reset_index(drop=True)

# ----------------------------
# Upload Handler
# ----------------------------

def process_upload(file_path, data_manager, is_metadata=True, missing_method='fill_zero', save_cleaned=True):
    if not os.path.exists(file_path):
        print("File not found.")
        return
    try:
        df = load_data(file_path)
    except Exception as e:
        print(f"Load error: {e}")
        return

    if is_metadata is None:
        is_metadata = 'meta' in file_path.lower()

    df = handle_missing_data(df, method=missing_method)

    if is_metadata:
        df = auto_rename_metadata_columns(df)
        data_manager.metadata = df
        fname = "metadata_cleaned.csv"
    else:
        data_manager.expression = df
        fname = "expression_cleaned.csv"

    if save_cleaned:
        os.makedirs("cleaned_data", exist_ok=True)
        df.to_csv(os.path.join("cleaned_data", fname), index=False)
        print(f"Saved cleaned file to cleaned_data/{fname}")


# ----------------------------
# Helper
# ----------------------------

def load_gene_annotations(annotation_file="gene_annotation.csv"):
    """Load gene annotations from CSV file"""
    try:
        annotations = pd.read_csv(annotation_file)
        return annotations
    except FileNotFoundError:
        print(f"Gene annotation file '{annotation_file}' not found. Using probe IDs only.")
        return None
    except Exception as e:
        print(f"Error loading gene annotation file '{annotation_file}': {e}")
        print("Using probe IDs only.")
        return None

def map_probe_to_gene(probe_id, annotations=None):
    """Map probe ID to gene symbol"""
    if annotations is None:
        annotations = load_gene_annotations()
    
    if annotations is None:
        return probe_id
    
    match = annotations[annotations['Probe_ID'] == probe_id]
    if not match.empty:
        return match.iloc[0]['Gene_Symbol']
    return probe_id

def map_gene_to_probe(gene_symbol, annotations=None):
    """Map gene symbol to probe ID (case-insensitive)"""
    if annotations is None:
        annotations = load_gene_annotations()
    
    if annotations is None:
        return gene_symbol
    
    # Case-insensitive matching
    match = annotations[annotations['Gene_Symbol'].str.upper() == gene_symbol.upper()]
    if not match.empty:
        return match.iloc[0]['Probe_ID']
    return gene_symbol

def get_all_available_genes(expression_df, annotations=None):
    """Get all available genes with their mappings"""
    if expression_df is None:
        return {}
    
    if annotations is None:
        annotations = load_gene_annotations()
    
    # Get all gene columns (exclude 'Sample')
    gene_cols = [col for col in expression_df.columns if col != 'Sample']
    
    # Create mapping dictionary
    gene_mapping = {}
    for probe_id in gene_cols:
        gene_name = map_probe_to_gene(probe_id, annotations)
        if gene_name != probe_id:
            gene_mapping[gene_name.upper()] = probe_id  # Store in uppercase for case-insensitive lookup
            gene_mapping[probe_id] = probe_id  # Also store probe ID as-is
    
    return gene_mapping

def list_all_available_genes(expression_df, show_gene_names=True, max_display=50):
    """List all available genes with their mappings"""
    if expression_df is None:
        print("No expression data loaded.")
        return {}
    
    # Get gene columns (exclude 'Sample' column)
    gene_cols = [col for col in expression_df.columns if col != 'Sample']
    total_genes = len(gene_cols)
    
    if show_gene_names:
        annotations = load_gene_annotations()
        if annotations is not None:
            print(f"\nLIST: GENE VISUALIZATION DATABASE")
            print("=" * 60)
            print(f"Total genes in dataset: {total_genes:,}")
            print(f"Genes with known names: {len(annotations)}")
            print(f"Showing first {max_display} genes with names:")
            print("=" * 60)
            
            # Create mapping for all genes
            available_genes = []
            gene_mapping = {}
            named_genes_count = 0
            
            for probe_id in gene_cols:
                gene_name = map_probe_to_gene(probe_id, annotations)
                if gene_name != probe_id:
                    available_genes.append(f"{gene_name} ({probe_id})")
                    gene_mapping[gene_name.upper()] = probe_id
                    gene_mapping[probe_id] = probe_id
                    named_genes_count += 1
                    
                    # Only display up to max_display named genes
                    if len(available_genes) <= max_display:
                        print(f"{len(available_genes):3d}. {gene_name} ({probe_id})")
                else:
                    gene_mapping[probe_id] = probe_id
            
            if named_genes_count > max_display:
                print(f"... and {named_genes_count - max_display} more genes with known names")
            
            print("=" * 60)
            print(f"TIP: You can enter:")
            print(f"   • Gene names: TP53, EGFR, MGMT, IDH1, ATRX, PTEN, PIK3CA, NF1")
            print(f"   • Probe IDs: 10000_at, 10001_at, 10002_at, etc.")
            print(f"   • Any case: tp53, Tp53, TP53 all work")
            print(f"TIP: Popular glioma genes: TP53, EGFR, MGMT, IDH1, ATRX, PTEN, PIK3CA, NF1, CDKN2A, CDKN2B")
            print(f"TIP: All {total_genes:,} genes can be visualised using their probe IDs")
            
            return gene_mapping
        else:
            print(f"Available genes: {', '.join(gene_cols[:20])}... (showing first 20 of {total_genes:,})")
            return {col: col for col in gene_cols}
    else:
        print(f"Available genes: {', '.join(gene_cols[:20])}... (showing first 20 of {total_genes:,})")
        return {col: col for col in gene_cols}

def list_available_genes(expression_df, show_gene_names=True):
    """List available genes in expression data with optional gene name mapping"""
    if expression_df is None:
        print("No expression data loaded.")
        return []
    
    # Get gene columns (exclude 'Sample' column)
    gene_cols = [col for col in expression_df.columns if col != 'Sample']
    
    if show_gene_names:
        annotations = load_gene_annotations()
        if annotations is not None:
            # Create mapping for available genes
            available_genes = []
            for probe_id in gene_cols[:5]:  # Show only top 5
                gene_name = map_probe_to_gene(probe_id, annotations)
                if gene_name != probe_id:
                    available_genes.append(f"{gene_name} ({probe_id})")
                else:
                    available_genes.append(probe_id)
            
            print(f"Available genes (showing top 5): {', '.join(available_genes)}")
            print("\nTIP: Tip: You can enter either probe IDs (e.g., '10000_at') or gene names (e.g., 'TP53')")
            print("TIP: Popular glioma genes: TP53, EGFR, MGMT, IDH1, ATRX, PTEN, PIK3CA, NF1")
        else:
            print(f"Available genes (showing top 5): {', '.join(gene_cols[:5])}")
    else:
        print(f"Available genes (showing top 5): {', '.join(gene_cols[:5])}")
    
    return gene_cols


def auto_rename_metadata_columns(df):
    """
    Automatically renames GEO column names to user-friendly names.
    This makes the interface much more intuitive for users.
    """
    mapping = get_column_name_mapping()
    
    # Create a copy to avoid modifying the original
    df_renamed = df.copy()
    
    # Track which columns were renamed for user feedback
    renamed_columns = {}
    
    for old_name in df.columns:
        if old_name in mapping:
            new_name = mapping[old_name]
            df_renamed.rename(columns={old_name: new_name}, inplace=True)
            renamed_columns[old_name] = new_name
    
    # Column names have been simplified silently for better user experience
    
    return df_renamed

def get_relevant_columns_for_analysis(metadata_df, min_values=2, max_values=50):
    """
    Returns only columns that are relevant for analysis by filtering out:
    - Columns with only 1 unique value (no variation)
    - Columns with too many unique values (like individual sample IDs)
    - Technical columns that aren't useful for grouping
    
    Args:
        metadata_df: pandas DataFrame
        min_values: minimum number of unique values (default: 2)
        max_values: maximum number of unique values (default: 50)
    
    Returns:
        list: filtered column names suitable for analysis
    """
    if metadata_df is None:
        return []
    
    relevant_cols = []
    exclude_patterns = ['sample', 'geo_id', 'submission_date', 'last_update_date', 
                       'supplementary_files', 'platform_id', 'gene_count']
    
    for col in metadata_df.columns:
        if col == 'Sample':  # Skip the main Sample column
            continue
            
        # Skip columns matching exclusion patterns
        if any(pattern in col.lower() for pattern in exclude_patterns):
            continue
            
        unique_vals = metadata_df[col].dropna().unique()
        num_unique = len(unique_vals)
        
        # Only include columns with reasonable number of unique values
        if min_values <= num_unique <= max_values:
            relevant_cols.append(col)
    
    return relevant_cols

def display_column_mapping_help():
    """
    Displays a helpful table showing the column name mappings.
    """
    mapping = get_column_name_mapping()
    
    print("\nCOLUMN NAME SIMPLIFICATIONS:")
    print("=" * 60)
    print("The following column names are automatically simplified for easier use:")
    print("=" * 60)
    
    for old_name, new_name in mapping.items():
        print(f"   '{old_name}' -> '{new_name}'")
    
    print(f"\nTotal: {len(mapping)} column name simplifications")
    print("These simplified names make filtering and analysis much easier!")

def fetch_and_format_geo(geo_id):
    print(f"Fetching {geo_id} from GEO...")

    # Set download location
    os.makedirs("uploads", exist_ok=True)

    try:
        gse = GEOparse.get_GEO(geo=geo_id, destdir="uploads", annotate_gpl=True)
    except Exception as e:
        print(f"[!] Failed to fetch GEO dataset: {e}")
        return None, None

    # Build metadata from GSM attributes
    metadata_rows = []
    for gsm_name, gsm in gse.gsms.items():
        row = {"Sample": gsm_name}
        # Flatten metadata: get first element if it's a list
        row.update({k: v[0] if isinstance(v, list) else v for k, v in gsm.metadata.items()})
        metadata_rows.append(row)
    metadata = pd.DataFrame(metadata_rows)
    
    # Apply column name simplifications to make it user-friendly
    metadata = auto_rename_metadata_columns(metadata)

    # Build expression matrix
    try:
        df_expr = gse.pivot_samples('VALUE')
        # The index contains gene IDs, columns contain sample IDs (GSM numbers)
        # We need to transpose so that samples are rows and genes are columns
        df_expr = df_expr.transpose()
        df_expr.reset_index(inplace=True)
        # Find the first column (should be the sample IDs) and rename it to 'Sample'
        first_col = df_expr.columns[0]
        df_expr.rename(columns={first_col: 'Sample'}, inplace=True)

    except Exception as e:
        print(f"[!] Could not extract expression matrix: {e}")
        return metadata, None

    # Save both
    os.makedirs("cleaned_data", exist_ok=True)
    metadata.to_csv(f"cleaned_data/{geo_id}_metadata.csv", index=False)
    df_expr.to_csv(f"cleaned_data/{geo_id}_expression.csv", index=False)

    print(f"[✓] Saved metadata and expression matrix to cleaned_data/")
    return metadata, df_expr
