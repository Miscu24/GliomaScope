import pandas as pd

def preview_dataframe(df, name='Data', n=5):
    print(f"\nPreview of {name} loaded (first {n} rows).")
    print(df.head(n))

def display_summary(df, name='Data'):
    print(f"\nSummary for {name}:")
    print(f"Shape: {df.shape}")
    print(f"Missing columns: {df.isnull().sum().sum()}")
    print(f"Duplicated rows: {df.duplicated().sum()}")
    print(f"Column types:\n{df.dtypes}")
    print(f"Numeric columns: {df.select_dtypes(include='number').columns.tolist()}")

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