'''	Loads metadata, filters by demographic (age, sex, grade, IDH1)'''
import os

def display_patient_summary(metadata_df):
    #displays patient metadata in a clear tabuar format

    if metadata_df.empty:
        print("No patient metadata available.")
        return
    
    #define columns to show
    columns_to_display = ['Sample_ID', 'age', 'sex', 'tumor_type', 'grade', 'idh', 'country']
    display_cols = [col for col in columns_to_display if col in metadata_df.columns]
    
    print("\n---- Patient Metadata Summary ----\n")
    print(metadata_df[display_cols].to_string(index=False))

    print("\n---- Summary Statistics ----")
    for col in ['tumor_type', 'grade', 'idh', 'country']:
        if col in metadata_df.columns:
            print(f"\n{col.title()} distribution:")
            print(metadata_df[col].value_counts(dropna=False))

    if 'age' in metadata_df.columns:
        print("\nAge statistics:")
        print(metadata_df['age'].describe())


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