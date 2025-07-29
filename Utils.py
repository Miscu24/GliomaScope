'''	Small reusable helpers (e.g. plotting wrappers, dict to JSON, label mapping)'''

'''Central loader for all datasets (CSV/TSV); handles missing/incomplete data'''

import pandas as pd
import os # For extracting file extensions
import numpy as np
import json
import umap
import plotly.express as px



def load_data(file_path):
 # Loads CSV or TSV file into a pandas DataFrame
    ext = os.path.splitext(file_path)[1]
    if ext == '.csv':
        return pd.read_csv(file_path)
    elif ext in ['.tsv', '.txt']:
        return pd.read_csv(file_path, sep='\t')
    else:
        raise ValueError("Unsupported file format. Use .csv or .tsv")
        
# Handles missing values: fill with zero, drop rows, or fill with column mean
def handle_missing_data(data, method='fill_zero'):

    if method == 'fill_zero':
        return data.fillna(0)
    elif method == 'drop':
        return data.dropna()
    elif method == 'fill_mean':
        return data.fillna(data.mean(numeric_only=True))
    else:
        raise ValueError("Invalid method. Choose from 'fill_zero', 'drop', 'fill_mean'")
 
 # Automatically detects if uploaded data is metadata or expression based on column names and content
def validate_file_type(df):
    cols = [col.lower() for col in df.columns]

    if 'sample_id' not in cols:
        raise ValueError("No 'Sample_ID' column found in the data")
    
    # If it contains typical metadata features
    metadata_keywords = ['age', 'sex', 'grade', 'idh', 'location']
    if any(key in col for col in cols for key in metadata_keywords):
        return 'Metadata'
    
    # If it contains many numeric gene expression values
    numeric_columns = df.drop(columns = [col for col in df.columns if 'sample_id' in col.lower()])
    if numeric_columns.shape[1] >= 30 and numeric_columns.dtypes.apply(lambda x: pd.api.types.is_numeric_dtype(x)).mean() > 0.8:
        return 'Expression'
    
    return 'Unknown'

def summarise_dataframe(df, name = 'DataFrame'):
    #returns a summary dictionary of uploaded dataset
    summary = {
        "name": name,
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "data_type": validate_file_type(df),
        "missing_values": df.isnull().sum().sum(),
        "duplicated_rows": df.duplicated().sum(),
        "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist()
    }
    return summary

def convert_np(obj):
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    else:
        return str(obj)
    
def log_summary(summary_dict, filename = "summary_log.json"):
   #save a summary dictionary to a JSON file in the logs folder
    os.makedirs("logs", exist_ok=True)
    filepath = os.path.join("logs", filename)

    with open(filepath, "w") as f:
        json.dump(summary_dict, f, indent=4, default=convert_np)

    print(f"Summary saved to {filepath}")

def display_and_log_summary(df, name = 'DataFrame', log=True):
    #prints and optinally logs a summary of the given DataFrame

    summary = summarise_dataframe(df, name)
    print(f"Summary for {name}:")
    print(json.dumps(summary, indent=4))

    if log:
        filename = f"{name.lower()}_summary.json"
        log_summary(summary, filename=filename)

def filter_metadata(metadata_df, grade=None, idh=None, age_range=None):
    # Filters metadata based on provided criteria
    filtered = metadata_df.copy()

    if grade:
        filtered = filtered[filtered['grade'].astype(str).str.lower() == grade.lower()]
    
    if idh:
        filtered = filtered[filtered['idh'].astype(str).str.upper() == idh.upper()]
    
    if age_range:
            try:
                min_age, max_age = age_range
                filtered = filtered[(filtered['age']>= min_age) & (filtered['age']<= max_age)]
            except ValueError:
                print("Invalid age range value. Skipping age filter.")

    print(f"\nFiltered dataset has {len(filtered)} samples.")
    return filtered.reset_index(drop=True)

def process_upload(file_path, data_manager, is_metadata=True, missing_method='fill_zero', save_cleaned=True):
    if not os.path.exists(file_path):
        print(f"File not found at {file_path}")
        return
    
    # Step 1: Try loading the file safely
    try:
        df = load_data(file_path)
    except Exception as e:
        print(f" Failed to load file: {e}")
        return
    
        # Step 2: Determine if it's metadata or expression (if not explicitly passed)
    if is_metadata is None:
        is_metadata = 'meta' in file_path.lower()

    # Step 3: Handle missing data
    df = handle_missing_data(df, method=missing_method)

    # Step 4: Save to data_manager
    if is_metadata:
        data_manager.metadata = df
    else:
        data_manager.expression = df

    #save cleaned file
    if save_cleaned and df is not None:
        filename = "metadata_cleaned.csv" if is_metadata else "expression_cleaned.csv"
        os.makedirs("cleaned_data", exist_ok=True)
        df.to_csv(f"cleaned_data/{filename}", index=False)
        print(f"Cleaned file saved to cleaned_data/{filename}.")

def smart_load_metadata(file_path, data_manager, missing_method='fill_zero', save_cleaned=True):
    #Check if the file actuazlly exists
    if not os.path.exists(file_path):
        print(f"File not found at {file_path}")
        return
    
    try:
        df = load_data(file_path)
    except Exception as e:
        print(f"Failed to load file: {e}")
        return
    
    #validate the file type that its metadata
    try:
        data_type = validate_file_type(df)
    except Exception as e:
        print(f"Failed to validate file type: {e}")
        return
    
    if data_type!= 'metadata':
        print("This file does not seem to be metadata.")
        return
    
    #handle missing values
    df = handle_missing_data(df, method=missing_method)
    #save to datamanager
    data_manager.metadata = df

    # save cleaned file
    if save_cleaned and df is not None:
        filename = "metadata_cleaned.csv"
        os.makedirs("cleaned_data", exist_ok=True)
        df.to_csv(f"cleaned_data/{filename}", index=False)
        print(f"Cleaned metadata saved to cleaned_data/{filename}.")

    # Filter metadata based on provided criteria
    grade = input("Enter grade (optional): ").strip().lower()
    idh = input("Enter IDH subtype (optional): ").strip().upper()

    #save cleaned version
    if save_cleaned and df is not None:
        os.makedirs("cleaned_data", exist_ok=True)
        df.to_csv("cleaned_data/metadata_cleaned.csv", index=False)
        print("Saved cleaned metadata to cleaned_data/metadata_cleaned.csv")

    # save to data_manager
    data_manager.metadata = df

    # save cleaned file
    if save_cleaned and df is not None:
        filename = "metadata_cleaned.csv"
        os.makedirs("cleaned_data", exist_ok=True)
        df.to_csv(f"cleaned_data/{filename}", index=False)
        print(f"Cleaned metadata saved to cleaned_data/{filename}.")

    # Filter metadata based on provided criteria
    grade = input("Enter grade (optional): ").strip().lower()
    idh = input("Enter IDH subtype (optional): ").strip().upper()

def list_available_genes(expression_df):
    genes = [col for col in expression_df.columns if col.lower() != 'sample_id']
    print(f"Available genes: {', '.join(genes)}")
    return genes
