from Data_loader import DataManager
from Utils import process_upload
from Explore_data import preview_dataframe, display_summary, warn_if_missing_columns, filter_metadata
from Visuals import plot_pca
from Patient_geomap import plot_patient_geomap
from Patient_metadata import display_patient_summary
from Dimensionality_Reduction import plot_pca as plot_pca
from Differential_exppression import perform_differential_expression
from Utils import list_available_genes
from Utils import filter_metadata
from Gene_explorer import explore_gene_expression, map_gene_to_chromosome
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time

data_manager = DataManager()

def main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    time
    while True:
        print("\n=== GliomaScope CLI ===")
        print("1. Upload metadata file")
        print("2. Upload expression file")
        print("3. Preview merged metadata + expression")
        print("4. Explore metadata summary")
        print("5. Explore expression summary")
        print("6. Filter metadata by grade/IDH/age")
        print("7. Plot PCA from expression data")
        print("8. Patient_Geomap from metadata")
        print("9. View patient metadata summary")
        print("10. Filter + export patient metadata")
        print("11. Visualise PCA")
        print("12. Visualise UMAP")
        print("13. Differential expression viewer")
        print("14. Run differential expression analysis")
        print("15. Chromosomal gene mapping")
        print("16. Exit")

        choice = input("Enter your choice from the options provided: ").strip()

        if choice == '1':
            file_path = input("Enter path to metadata file (or smart file): ")
            data_manager.load_file_smart(file_path)

        elif choice == '2':
            file_path = input("Enter path to expression file: ")
            data_manager.load_expression(file_path)

        elif choice == '3':
            if data_manager.merged is not None:
                print(data_manager.merged.head())
            else:
                print("No data loaded yet.")

        elif choice == '4':
            if data_manager.metadata is not None:
                preview_dataframe(data_manager.metadata, name='Metadata')
                display_summary(data_manager.metadata, name='Metadata')
                warn_if_missing_columns(data_manager.metadata, ['grade', 'idh', 'age'])
            else:
                print("No metadata loaded.")

        elif choice == '5':
            if data_manager.expression is not None:
                preview_dataframe(data_manager.expression, name='Expression')
                display_summary(data_manager.expression, name='Expression')
            else:
                print("No expression loaded.")

        elif choice == '6':
            if data_manager.metadata is None:
                print("No metadata loaded.")
                continue
            
            grade = input("Filter by grade (press enter to skip): ").strip()
            idh = input("Filter by IDH status (press enter to skip): ").strip()
            
            age_range = None
            age_input = input("Filter by age range (e.g. 40-50) or press enter to skip: ").strip()
            if age_input:
                try:
                    min_age, max_age = map(int, age_input.split('-'))
                    age_range = (min_age, max_age)
                except ValueError:
                    print("Invalid age range value. Skipping age filter.")

            filtered_metadata = filter_metadata(
                data_manager.metadata,
                grade or None,
                idh or None,
                age_range
            )

            print(f"\nFiltered metadata has {len(filtered_metadata)} rows:")
            print(filtered_metadata.head())

            save = input("Save filtered metadata to a file (y/n): ").lower()
            if save == 'y':
                filtered_metadata.to_csv("cleaned_data/metadata_filtered.csv", index=False)
                print("Filtered metadata saved to 'cleaned_data/metadata_filtered.csv'.")


        elif choice== '7':
            if data_manager.expression is None:
                print("Expression data is not loaded.")
                continue

            colour_by  = input("Colour PCA plot by metadata column (e.g. grade, idh) ? Leave blank for none:").strip()
            if colour_by and data_manager is not None:
                plot_pca(data_manager.expression, data_manager.metadata, colour_by=colour_by)
            else:
                plot_pca(data_manager.expression)
        
        elif choice == '8':
            if data_manager.metadata is not None:
                try:
                    plot_patient_geomap(data_manager.metadata)
                except Exception as e:
                    print(f"Error occurred while plotting patient geo map: {e}")
            else:
                print("No metadata loaded. Please upload metadata first.  ")

        
        elif choice == '9':
            if data_manager.metadata is not None:
                print(">>> Displaying patient summary...")
                display_patient_summary(data_manager.metadata)
            else:
                print("No metadata loaded.")

        elif choice == '10':
            if data_manager.expression is not None:
                colour_by = input("Enter metadata column to color by (or press Enter to skip): ").strip()
                plot_pca(data_manager.expression, data_manager.metadata, colour_by if colour_by else None)
            else:
                print("Please load expression data first.")

            
        elif choice == '11':
            if data_manager.expression is None:
                print("Expression data not loaded. Please upload expression data first (Option 2).")
            elif data_manager.metadata is None:
                print("Metadata is not loaded. Please upload metadata first (Option 1).")
            else:
                visible_columns = [col for col in data_manager.metadata.columns if col.lower() != "sample_id"]
                print("Available columns for PCA plot:", ", ".join(visible_columns))

                colour_by = input("Colour PCA plot by metadata column (e.g. grade, idh)? Leave blank for none: ").strip()
                matched_col = next((col for col in data_manager.metadata.columns if col.lower() == colour_by.lower()), None) if colour_by else None

                if colour_by and not matched_col:
                    print(f"Column '{colour_by}' not found in metadata. Skipping colour by column.")
                else:
                    try:
                        if matched_col:
                            plot_pca(data_manager.expression, data_manager.metadata, colour_by=matched_col)
                        else:
                            plot_pca(data_manager.expression)
                    except Exception as e:
                        print(f"Error occurred while plotting PCA: {e}")

        elif choice == '12':
            if data_manager.expression is None:
                print("Expression data not loaded. Please upload expression data first (Option 2).")
            elif data_manager.metadata is None:
                print("Metadata is not loaded. Please upload metadata first (Option 1).")
            else:
                from Dimensionality_Reduction import plot_umap
                
                visible_columns = [col for col in data_manager.expression.columns if col.lower()!= "sample_id"]
                print("Available columns for PCA plot:", ", ".join(visible_columns))

                colour_by = input("Colour PCA plot by metadata column (e.g. grade, idh)? Leave blank for none: ").strip()
                matched_col = next((col for col in data_manager.expression.columns if col.lower() == colour_by.lower()), None) if colour_by and data_manager.metadata is not None else None

                try:
                    plot_umap(
                        data_manager.expression,
                        data_manager.metadata,
                        colour_by = matched_col
                )
                except Exception as e:
                    print(f"Error occurred while plotting UMAP: {e}")

        elif choice == '13':
            if data_manager.expression is None:
                print("Expression data not loaded. Please upload expression data first (Option 2).")
            elif data_manager.metadata is None:
                print("Metadata is not loaded. Please upload metadata first (Option 1).")
            else:
                print("Running differential expression analysis. Grade 2 vs Grade 3...")
                try:
                    result_df = perform_differential_expression(
                        data_manager.expression,
                        data_manager.metadata,
                        group_col = 'grade',
                        group_1="Grade 2",
                        group_2="Grade 3"
                    )
                    print(result_df.head(10)[['Gene', 'log2FC', 'p_value']])
                except Exception as e:
                    print(f"Error occurred while performing differential expression: {e}")

        elif choice == '14':
            if data_manager.expression is None:
                print("Expression data not loaded. Please upload expression data first (Option 2).")
            elif data_manager.metadata is None:
                print("Metadata is not loaded. Please upload metadata first (Option 1).")
            else:
                genes = list_available_genes(data_manager.expression)
                print(f"Available Genes: {', '.join(genes[:10])}...") #showing top 10 genes
                gene_name = input("Enter a gene name to explore expression: ").strip()

                if gene_name not in genes:
                    print(f"Gene '{gene_name}' not found in expression data.")
                    continue 

                #show columns to group by 
                groupable_cols = [col for col in data_manager.metadata.columns if col.lower()!= "sample_id"]
                print(f"Available columns to group by: {', '.join(groupable_cols)}...")
                group_col = input("Enter metadata column to group by (or press Enter to skip): ").strip()

                if group_col not in groupable_cols:
                    print(f"Column '{group_col}' not found in metadata. Skipping grouping by column.")
                    continue

                try:
                    explore_gene_expression(data_manager.expression, data_manager.metadata, gene_name, group_col)
                except Exception as e:
                    print(f"Error occurred while exploring gene expression: {e}")

        elif choice == '15':
            gene_name = input("Enter the gene name to explore: ").strip()

            try:
                from Gene_explorer import explore_gene_expression, map_gene_to_chromosome
                explore_gene_expression(data_manager.expression, data_manager.metadata, gene_name)
                map_gene_to_chromosome(gene_name)
            except Exception as e:
                print(f"Error occurred while exploring gene expression or mapping gene to chromosome: {e}")

        elif choice == '16':
            print("Thank you for using our tool. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Please choose from 1-10. Try again.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()