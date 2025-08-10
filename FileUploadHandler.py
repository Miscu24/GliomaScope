import os
from Utils import load_data, handle_missing_data, validate_file_type, summarise_dataframe, display_and_log_summary
from Data_loader import DataManager

def process_upload(file_path, data_manager, missing_method='fill_zero', save_cleaned=True):
    df = load_data(file_path)
    
    # Apply column name simplifications for metadata files
    if validate_file_type(df) == 'metadata':
        df = auto_rename_metadata_columns(df)
    
    df_cleaned = handle_missing_data(df, missing_method)
    
    file_type = validate_file_type(df_cleaned)

    if file_type == 'Metadata':
        if data_manager.metadata is not None:
            print("[!] Metadata already uploaded.")
            return
        data_manager.load_metadata_df(df_cleaned)
        display_and_log_summary(df_cleaned, name = 'Metadata')
    
    #summary 
        summary = summarise_dataframe(df_cleaned, name = 'Metadata')
        print("Metadata summary:")
        for key, value in summary.items():
            print(f" - {key}: {value}")

        if save_cleaned:
            os.makedirs('cleaned_data', exist_ok=True)
            df_cleaned.to_csv("cleaned_data/metadata_cleaned.csv", index=False)
            print("Saved cleaned metadata.")

    elif file_type == 'Expression':
        if data_manager.expression is not None:
            print("[!] Expression data already uploaded.")
            return
        data_manager.load_expression_df(df_cleaned)
        display_and_log_summary(df_cleaned, name = 'Expression')

    #summary
        summary = summarise_dataframe(df_cleaned, name = 'Expression')
        print("Expression summary:")
        for key, value in summary.items():
            print(f" - {key}: {value}")

        if save_cleaned:
            os.makedirs('cleaned_data', exist_ok=True)
            df_cleaned.to_csv("cleaned_data/expression_cleaned.csv", index=False)
            print("Saved cleaned expression data.")
    
    else:
        print(f"Unknown file type. Please upload metadata or expression data. {file_type}")