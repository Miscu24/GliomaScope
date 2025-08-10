'''	Loads metadata, filters by demographic (age, sex, grade, IDH1)'''
import os

def display_patient_summary(metadata_df):
    #displays patient metadata in a clear tabular format

    if metadata_df.empty:
        print("No patient metadata available.")
        return
    
    print("\nLIST: PATIENT METADATA SUMMARY")
    print("=" * 60)
    
    # Show basic dataset info
    print(f"INFO: Dataset Overview:")
    print(f"   • Total samples: {len(metadata_df)}")
    print(f"   • Total columns: {len(metadata_df.columns)}")
    print(f"   • Sample ID format: {metadata_df['Sample'].iloc[0][:10]}... (GSM format)")
    
    # Show available columns
    print(f"\nLIST: Available Metadata Columns:")
    print("=" * 40)
    for i, col in enumerate(metadata_df.columns, 1):
        print(f"   {i:2d}. {col}")
    
    # Show patient-specific clinical information
    print(f"\nPATIENT CLINICAL INFORMATION:")
    print("=" * 40)
    
    # Look for patient-specific columns with various possible names
    patient_cols = {
        'age': ['age', 'Age', 'AGE', 'patient_age', 'age_at_diagnosis'],
        'sex': ['sex', 'Sex', 'SEX', 'gender', 'Gender', 'GENDER'],
        'grade': ['grade', 'Grade', 'GRADE', 'tumor_grade', 'who_grade'],
        'idh': ['idh', 'IDH', 'idh_status', 'idh1', 'IDH1', 'idh_mutation'],
        'tumor_type': ['tumor_type', 'Tumor_Type', 'tumor_type_ch1', 'diagnosis', 'tissue_type'],
        'survival': ['survival', 'Survival', 'overall_survival', 'os_time'],
        'status': ['status', 'Status', 'vital_status', 'outcome']
    }
    
    found_patient_cols = {}
    for category, possible_names in patient_cols.items():
        for name in possible_names:
            if name in metadata_df.columns:
                found_patient_cols[category] = name
                break
    
    # Display found patient information
    if found_patient_cols:
        for category, col_name in found_patient_cols.items():
            unique_vals = metadata_df[col_name].dropna().unique()
            print(f"\n{category.upper().replace('_', ' ')} ({col_name}):")
            if len(unique_vals) <= 10:
                for val in unique_vals:
                    count = len(metadata_df[metadata_df[col_name] == val])
                    print(f"   • {val} ({count} samples)")
            else:
                print(f"   • {len(unique_vals)} unique values")
                # Show most common values
                value_counts = metadata_df[col_name].value_counts()
                print(f"   • Most common: {value_counts.index[0]} ({value_counts.iloc[0]} samples)")
                if len(value_counts) > 1:
                    print(f"   • Second most common: {value_counts.index[1]} ({value_counts.iloc[1]} samples)")
    else:
        print("   • No standard patient clinical columns found")
    
    # Show GEO-specific columns if they exist
    print(f"\nGEO DATASET INFORMATION:")
    print("=" * 40)
    
    geo_cols = ['source_name_ch1', 'characteristics_ch1', 'type', 'organism_ch1', 'title', 'description', 
                'tissue_type', 'tissue_characteristics', 'sample_type', 'organism', 'sample_title', 'sample_description']
    found_geo_cols = [col for col in geo_cols if col in metadata_df.columns]
    
    if found_geo_cols:
        for col in found_geo_cols:
            unique_vals = metadata_df[col].dropna().unique()
            print(f"\n{col}:")
            if len(unique_vals) <= 5:
                for val in unique_vals:
                    count = len(metadata_df[metadata_df[col] == val])
                    print(f"   • {val} ({count} samples)")
            else:
                print(f"   • {len(unique_vals)} unique values")
                print(f"   • Most common: {metadata_df[col].mode().iloc[0] if not metadata_df[col].mode().empty else 'N/A'}")
    else:
        print("   • No standard GEO columns found")
    
    # Show sample preview with patient information
    print(f"\nPREVIEW: SAMPLE PREVIEW (first 5 samples):")
    print("=" * 40)
    
    # Prioritize patient columns for preview
    preview_cols = ['Sample']
    if found_patient_cols:
        preview_cols.extend([found_patient_cols[cat] for cat in ['age', 'sex', 'grade', 'idh'] if cat in found_patient_cols])
    if found_geo_cols:
        preview_cols.extend(found_geo_cols[:2])  # Add first 2 GEO columns
    
    # Ensure we don't have too many columns for preview
    preview_cols = preview_cols[:6]  # Limit to 6 columns for readability
    available_preview_cols = [col for col in preview_cols if col in metadata_df.columns]
    
    if available_preview_cols:
        print(metadata_df[available_preview_cols].head().to_string(index=False))
    else:
        print("No suitable columns found for preview")
    
    # Show summary statistics for numeric columns
    numeric_cols = metadata_df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        print(f"\nNUMERIC COLUMNS SUMMARY:")
        print("=" * 40)
        for col in numeric_cols:
            if col != 'Sample':  # Skip if Sample is numeric
                print(f"\n{col}:")
                print(f"   • Mean: {metadata_df[col].mean():.2f}")
                print(f"   • Min: {metadata_df[col].min():.2f}")
                print(f"   • Max: {metadata_df[col].max():.2f}")
                print(f"   • Missing: {metadata_df[col].isna().sum()}")
    
    # Show missing data summary
    print(f"\nMISSING DATA SUMMARY:")
    print("=" * 40)
    missing_data = metadata_df.isnull().sum()
    missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
    
    if len(missing_data) > 0:
        for col, missing_count in missing_data.items():
            missing_pct = (missing_count / len(metadata_df)) * 100
            print(f"   • {col}: {missing_count} missing ({missing_pct:.1f}%)")
    else:
        print("   • No missing data found")
    
    print(f"\nTIP: Use options 7, 8, or 9 to explore and filter this metadata further!")
    print("   • Option 7: Interactive filtering with simplified column names")
    print("   • Option 8: Geographic visualization")
    print("   • Option 9: Patient metadata summary & filtering")
    print("=" * 60)


def filter_metadata(metadata_df):
    print("\n --- Metadata Filter Options ---")
    filters = {}

    if 'grade' in metadata_df.columns:
        unique_grades = sorted(metadata_df['grade'].dropna().unique())
        print(f"Available grades: {', '.join(unique_grades)}")
        grade_input = input("Filter by grade (comma-separated list or leave blank to skip): ").strip()
        if grade_input:
            selected_grades = [g.strip() for g in grade_input.split(',')]
            filters['grade'] = selected_grades
            metadata_df = metadata_df[metadata_df['grade'].astype(str).isin(selected_grades)]

    if 'idh' in metadata_df.columns:
        unique_idhs = sorted(metadata_df['idh'].dropna().unique())
        print(f"Available IDH statuses: {', '.join(unique_idhs)}")
        idh_input = input("Filter by IDH status (comma-separated list or leave blank to skip): ").strip()
        if idh_input:
                selected_idhs = [i.strip() for i in idh_input.split(',')]
                filters['idh'] = selected_idhs
                metadata_df = metadata_df[metadata_df['idh'].astype(str).isin(selected_idhs)]

    return metadata_df, filters
    
def display_summary_statistics(metadata_df):
    print("\n---- Summary Statistics ----")

    if 'tumor_type' in metadata_df.columns:
        print("\nTumor Type Counts:")
        print(metadata_df['tumor_type'].value_counts().to_string())

    if 'grade' in metadata_df.columns:
        print("\nGrade Distribution:")
        print(metadata_df['grade'].value_counts().sort_index().to_string())

    if 'idh' in metadata_df.columns:
        print("\nIDH Status Counts:")
        print(metadata_df['idh'].value_counts().to_string())

def filter_and_export_metadata(metadata_df):
    print("\n--- Metadata Filter Options ---")

    #Grade
    if 'grade' in metadata_df.columns:
        grades = input("Enter grade(s) to filter by (comma-separated list): ").strip()
        if grades:
            grade_list = [g.strip() for g in grades.split(',')]
            metadata_df = metadata_df[metadata_df['grade'].astype(str).isin(grade_list)]
            
    #idh 
    if 'idh' in metadata_df.columns:
        idh_status = input ("Enter IDH statis to filter by (mutant or wildtype): ").strip()
        if idh_status:
            idh_list = [i.strip().lower() for i in idh_status.split(',')]
            metadata_df = metadata_df[metadata_df['idh'].astype(str).str.lower().isin(idh_list)]

    if 'age' in metadata_df.columns:
        age_range = input("Enter age range (min-max): ").strip()
        if '-' in age_range:
            try:
                min_age, max_age = map(int, age_range.split('-'))
                metadata_df = metadata_df[(metadata_df['age'] >= min_age) & (metadata_df['age'] <= max_age)]
            except:
                print("Invalid age range value. Skipping age filter.")
    
    print(f"\nFiltered dataset has {len(metadata_df)} samples.\n")
    print(metadata_df.head())

    #save
    save = input("Save filtered metadata to a file (y/n): ").strip().lower()
    if save == 'y':
        os.makedirs("cleaned_data", exist_ok=True)
        metadata_df.to_csv("cleaned_data/metadata_filtered.csv", index=False)
        print("Saved to cleaned_data/metadata_filtered.csv.")


    return metadata_df