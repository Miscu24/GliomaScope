import pandas as pd
import os

def format_for_gliomascope(expression_path, metadata_path,
                            expr_id_col='Sample_ID', meta_id_col='Sample_ID',
                            output_dir='cleaned_data'):
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load files
    expr = pd.read_csv(expression_path, sep=None, engine='python')
    meta = pd.read_csv(metadata_path, sep=None, engine='python')

    # === METADATA FIX ===
    if meta_id_col not in meta.columns:
        if meta.index.name:  # Index is named, likely contains GSM IDs
            print("[INFO] Promoting metadata index to Sample_ID")
            meta = meta.reset_index().rename(columns={meta.index.name: 'Sample_ID'})
        else:
            raise ValueError(f"[ERROR] Could not find '{meta_id_col}' in metadata columns or index.")

    # Rename ID columns to standard
    expr = expr.rename(columns={expr_id_col: 'Sample_ID'})
    meta = meta.rename(columns={meta_id_col: 'Sample_ID'})

    # Ensure Sample_ID is first column
    expr = expr[['Sample_ID'] + [col for col in expr.columns if col != 'Sample_ID']]
    meta = meta[['Sample_ID'] + [col for col in meta.columns if col != 'Sample_ID']]

    # Optional: rename key metadata fields if needed
    rename_map = {
        'Grade': 'grade',
        'Tumor_Grade': 'grade',
        'IDH': 'idh',
        'IDH_status': 'idh',
        'Age': 'age',
        'Location': 'location',
    }
    meta = meta.rename(columns={k: v for k, v in rename_map.items() if k in meta.columns})

    # Save to cleaned_data/
    expr_output = os.path.join(output_dir, 'expression.csv')
    meta_output = os.path.join(output_dir, 'metadata.csv')
    merged_output = os.path.join(output_dir, 'merged.csv')

    expr.to_csv(expr_output, index=False)
    meta.to_csv(meta_output, index=False)

    # Optionally merge and preview
    merged = pd.merge(expr, meta, on='Sample_ID', how='inner')
    merged.to_csv(merged_output, index=False)

    print(f"Expression saved to: {expr_output}")
    print(f"Metadata saved to: {meta_output}")
    print(f"Merged saved to: {merged_output}")
    print(f"Found {len(merged)} matched samples.")

    return expr_output, meta_output
