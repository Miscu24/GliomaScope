import pandas as pd
import os
from src.utils.Utils import load_data, handle_missing_data, validate_file_type, auto_rename_metadata_columns


class DataManager:
    def __init__(self):
        self.metadata = None
        self.expression = None
        self.merged = None
        self.metadata_path = None
        self.expression_path = None


    def load_file_smart(self, file_path, missing_method='fill_zero'):
        if not os.path.exists(file_path):
            print(f"[Error] File not found: {file_path}")
            return

        try:
            df = load_data(file_path)
        except Exception as e:
            print(f"[Error] Failed to load file: {e}")
            return

        df = auto_rename_metadata_columns(df)

        # Standardize Sample
        if 'Sample' not in df.columns:
            for col in df.columns:
                if 'sample' in col.lower() and 'id' in col.lower():
                    df.rename(columns={col: 'Sample'}, inplace=True)
                    break

        if 'Sample' not in df.columns:
            print("[Error] 'Sample' column missing.")
            return

        # Identify type
        file_type = validate_file_type(df).lower().capitalize()
        print(f"Detected file type: {file_type}")

        # Handle missing values
        df = handle_missing_data(df, method=missing_method)

        # Save to appropriate attribute
        if file_type == 'Metadata':
            self.metadata = df
            self.metadata_path = file_path
            print(f"[✓] Metadata loaded with shape {df.shape}")

        elif file_type == 'Expression':
            # Check and orient the expression matrix
            if df.columns.astype(str).str.startswith("Sample").any():  # samples in columns
                print("Detected: Genes as rows — transposing expression data")
                df = df.transpose()
                df.index.name = 'Sample'
                df.reset_index(inplace=True)
            elif df.index.astype(str).str.startswith("Sample").any():
                df.index.name = 'Sample'
                df.reset_index(inplace=True)
            else:
                print("Assuming samples are rows.")

            self.expression = df
            self.expression_path = file_path
            print(f"[✓] Expression loaded with shape {df.shape}")
        else:
            print("[!] Could not determine file type. Please check structure.")

        self._try_merge()

    def load_metadata(self, file_path, missing_method='fill_zero', save_cleaned=True):
        import os
        from src.utils.Utils import handle_missing_data, summarise_dataframe, log_summary, load_data, validate_file_type

        try:
            df = load_data(file_path)
        except Exception as e:
            print(f"[X] Failed to load file: {e}")
            return

        # 1. Apply column name simplifications first
        df = auto_rename_metadata_columns(df)
        
        # 2. Standardize remaining column names (for matching)
        df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]

        # 2. Validate file type
        file_type = validate_file_type(df).lower().capitalize()
        if file_type != "Metadata":
            print("[!] Warning: This file may not contain valid metadata.")

        # 3. Locate Sample column smartly
        sample_col = next((col for col in df.columns if 'sample' in col and 'id' in col), None)
        if not sample_col:
            print("[-] No column resembling 'Sample' found.")
            return
        df.rename(columns={sample_col: 'Sample'}, inplace=True)

        # 4. Handle missing data
        df = handle_missing_data(df, method=missing_method)

        # 5. Warn if expected columns are missing
        expected = ['sample_id', 'age', 'sex', 'grade', 'idh']
        found = [col for col in expected if col in df.columns]
        missing = set(expected) - set(found)
        if missing:
            print(f"[!] Warning: Missing expected metadata columns: {', '.join(missing)}")

        # 6. Save cleaned version
        if save_cleaned:
            os.makedirs("cleaned_data", exist_ok=True)
            df.to_csv("cleaned_data/metadata_cleaned.csv", index=False)
            print("[+] Cleaned metadata saved to cleaned_data/metadata_cleaned.csv")

        # 7. Store in DataManager
        self.metadata = df
        print("[+] Metadata loaded successfully.")

        # 8. Log summaray
        summary = summarise_dataframe(df, name='Metadata')
        log_summary(summary, filename="metadata_summary.json")


    
    def load_expression(self, file_path, missing_method='fill_zero', save_cleaned=True):
        from src.utils.Utils import load_data, handle_missing_data, summarise_dataframe, log_summary
        import os

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        # 1. Load and clean raw data
        try:
            df = load_data(file_path)
        except Exception as e:
            print(f"Failed to load file: {e}")
            return

        # 2. Standardize column names
        df.columns = [col.strip().replace(" ", "_") for col in df.columns]

        # 3. Identify Sample column (any variant)
        sample_col = next((col for col in df.columns if 'sample' in col.lower() and 'id' in col.lower()), None)
        if not sample_col:
            print("ERROR: No column resembling 'Sample' found in expression file.")
            return
        df.rename(columns={sample_col: 'Sample'}, inplace=True)

        # 4. Move Sample to front
        cols = ['Sample'] + [c for c in df.columns if c != 'Sample']
        df = df[cols]

        # 5. Handle missing data
        df = handle_missing_data(df, method=missing_method)

        # 6. Warn if not many numeric columns (sanity check)
        num_cols = df.select_dtypes(include='number')
        if num_cols.shape[1] < 10:
            print("WARNING: Warning: Expression file has very few numeric columns. Are you sure this is gene expression data?")

        # 7. Save cleaned file (optional)
        if save_cleaned:
            os.makedirs("cleaned_data", exist_ok=True)
            df.to_csv("cleaned_data/expression_cleaned.csv", index=False)
            print("SUCCESS: Cleaned expression data saved to cleaned_data/expression_cleaned.csv")

        # 8. Store in object
        self.expression = df

        # 9. Log summary
        summary = summarise_dataframe(df, name='Expression')
        log_summary(summary, filename="expression_summary.json")

        # 10. Try merge if metadata is already present
        self._try_merge()


    def load_metadata_df(self, df):
        # Apply column name simplifications
        df = auto_rename_metadata_columns(df)
        
        # Ensure Sample column exists
        if 'Sample' not in df.columns:
            # Try to find any column that looks like a sample ID
            for col in df.columns:
                if 'sample' in col.lower() and 'id' in col.lower():
                    df.rename(columns={col: 'Sample'}, inplace=True)
                    break
                elif col.startswith('GSM'):  # Handle GSM sample IDs
                    df.rename(columns={col: 'Sample'}, inplace=True)
                    break
        
        self.metadata = df
        self._try_merge()
        #load metadata directly from a pandas DataFrame

    def load_expression_df(self, df):
        # Ensure Sample column exists
        if 'Sample' not in df.columns:
            # Try to find any column that looks like a sample ID
            for col in df.columns:
                if 'sample' in col.lower() and 'id' in col.lower():
                    df.rename(columns={col: 'Sample'}, inplace=True)
                    break
                elif col.startswith('GSM'):  # Handle GSM sample IDs
                    df.rename(columns={col: 'Sample'}, inplace=True)
                    break
        
        self.expression = df
        self._try_merge()

        # load expression directly from a pandas DataFrame

    def _try_merge(self):
        if self.metadata is not None and self.expression is not None:
            # Check for Sample column in both dataframes
            meta_sample_col = None
            expr_sample_col = None
            
            # Look for Sample column in metadata
            if 'Sample' in self.metadata.columns:
                meta_sample_col = 'Sample'
            else:
                # Try to find any column that looks like a sample ID
                for col in self.metadata.columns:
                    if 'sample' in col.lower() and 'id' in col.lower():
                        meta_sample_col = col
                        self.metadata.rename(columns={col: 'Sample'}, inplace=True)
                        break
                    elif col.startswith('GSM'):  # Handle GSM sample IDs
                        meta_sample_col = col
                        self.metadata.rename(columns={col: 'Sample'}, inplace=True)
                        break
            
            # Look for Sample column in expression
            if 'Sample' in self.expression.columns:
                expr_sample_col = 'Sample'
            else:
                # Try to find any column that looks like a sample ID
                for col in self.expression.columns:
                    if 'sample' in col.lower() and 'id' in col.lower():
                        expr_sample_col = col
                        self.expression.rename(columns={col: 'Sample'}, inplace=True)
                        break
                    elif col.startswith('GSM'):  # Handle GSM sample IDs
                        expr_sample_col = col
                        self.expression.rename(columns={col: 'Sample'}, inplace=True)
                        break
            
            if not meta_sample_col or not expr_sample_col:
                print('ERROR: Warning: No Sample column found in metadata or expression data.')
                print(f'Metadata columns: {list(self.metadata.columns)}')
                print(f'Expression columns: {list(self.expression.columns)}')
                return
        
            # Standardize Sample format
            self.metadata['Sample'] = self.metadata['Sample'].astype(str).str.strip().str.upper()
            self.expression['Sample'] = self.expression['Sample'].astype(str).str.strip().str.upper()

            common_ids = set(self.metadata['Sample']).intersection(set(self.expression['Sample']))
            if len(common_ids) == 0:
                print('ERROR: No common samples found between metadata and expression data.')
                return
        
            self.merged = pd.merge(self.metadata, self.expression, on='Sample', how='inner')

    def preview_metadata(self, n=5):
        if self.metadata is not None:
            print(f"\n Preview of metadata loaded (first {n} rows).")
            print(self.metadata.head(n))
        else:
            print("No metadata loaded.")
    
    def preview_expression(self, n=5):
        if self.expression is not None:
            print(f"\n Preview of expression loaded (first {n} rows).")
            print(self.expression.head(n))
        else:
            print("No expression loaded.")


#dm = DataManager()
#dm.load_metadata("metadata.csv")
#dm.load_expression("expression.csv")

#dm.preview_metadata()
#dm.preview_expression()
