from Data_loader import DataManager
from Utils import process_upload
from Explore_data import preview_dataframe, display_summary, warn_if_missing_columns, filter_metadata
from Visuals import plot_pca
from Patient_geomap import plot_patient_geomap
from Patient_metadata import display_patient_summary
from Dimensionality_Reduction import plot_pca as plot_dimred_pca
from Differential_expression import perform_differential_expression
from Utils import list_available_genes
from Utils import filter_metadata
from Gene_explorer import explore_gene_expression, map_gene_to_chromosome

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time

data_manager = DataManager()

def main_menu():
    os.system('clear')

    print(r"""
O       o O       o O       o O       o O       o         O
| O   o | | O   o | | O   o | | O   o | | O   o | | O   o |
| | O | | | | O | | | | O | | | | O | | | | O | | | | O | |
| o   O | | o   O | | o   O | | o   O | | o   O | | o   O |
o       O o       O o       O o       O o       O o       O
   ___ _ _                       __                      
  / _ \ (_) ___  _ __ ___   __ _/ _\ ___ ___  _ __   ___ 
 / /_\/ | |/ _ \| '_ ` _ \ / _` \ \ / __/ _ \| '_ \ / _ \
/ /_\\| | | (_) | | | | | | (_| |\ \ (_| (_) | |_) |  __/
\____/|_|_|\___/|_| |_| |_|\__,_\__/\___\___/| .__/ \___|
                                             |_|         
  
          Designed for all. Built for insight. 
        Dive deep into glioma transcriptomics.
             Fast. Intuitive. Insightful.
""")

    print("Are you looking for deeper insights into gliomas?")
    print("\nWell, here you can use your own metadata and gene expression data to explore the tumour landscape \nlike never before. \nGliomaScope lets you visualise PCA, UMAP, and gene expression patterns, perform differential analysis, \nmap genes to their chromosomal locations, and generate publication-ready insights. \nAll right from your terminal.\n")

    input("   Press ENTER to dive in...")

    os.system('cls' if os.name == 'nt' else 'clear')
    time
    while True:
        print("\n=== GliomaScope CLI ===")
        print("1. Upload metadata file")
        print("2. Upload expression file")
        print("3. Preview merged metadata + expression")
        print("4. Explore metadata summary")
        print("5. View patient metadata summary")
        print("6. Filter + export patient metadata")
        print("7. Filter metadata by grade/IDH/age")
        print("8. Explore expression summary")
        print("9. Patient_Geomap from metadata")
        print("10. Visualise PCA")
        print("11. Plot PCA from expression data")
        print("12. Visualise UMAP")
        print("13. Differential expression viewer (Grade 1 vs 2)")
        print("14. Custom differential expression analysis")
        print("15. Chromosomal gene mapping")
        print("16. Explore individual gene expression")
        print("17. Heatmap visualisation for gene sets")
        print("18. Exit")

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
            if data_manager.metadata is not None:
                print(">>> Displaying patient summary...")
                display_patient_summary(data_manager.metadata)
            else:
                print("No metadata loaded.")

        elif choice == '6':
            if data_manager.expression is not None:
                colour_by = input("Enter metadata column to color by (or press Enter to skip): ").strip()
                plot_pca(data_manager.expression, data_manager.metadata, colour_by if colour_by else None)
            else:
                print("Please load expression data first.")

        elif choice == '7':
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


        elif choice == '8':
            if data_manager.expression is not None:
                preview_dataframe(data_manager.expression, name='Expression')
                display_summary(data_manager.expression, name='Expression')
            else:
                print("No expression loaded.")

        elif choice == '9':
            if data_manager.metadata is not None:
                print("\n--- Geomap Options ---")
                print("1. Visualise individual patient location")
                print("2. Visualise study-level summary on a map")
                sub_choice = input("Enter your choice: 1 or 2: ").strip()

                try:
                    from Patient_geomap import plot_patient_geomap, plot_study_summary

                    if sub_choice == '1':
                        zoom_choice = input("Enable zoom to region? (y/n): ").strip().lower()
                        zoom_enabled = zoom_choice == 'y'
                        plot_patient_geomap(data_manager.metadata, zoom_to_region=zoom_enabled)

                    elif sub_choice == '2':
                        plot_study_summary(data_manager.metadata)
                        
                    else:
                        print("Invalid option. Please choose 1 or 2.")
                except Exception as e:
                    print(f"Error occurred while plotting patient geo map: {e}")
            else:
                print("No metadata loaded. Please upload metadata first.")

        elif choice == '10':
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

        elif choice== '11':
            if data_manager.expression is None:
                print("Expression data is not loaded.")
                continue

            colour_by  = input("Colour PCA plot by metadata column (e.g. grade, idh) ? Leave blank for none:").strip()
            if colour_by and data_manager is not None:
                plot_pca(data_manager.expression, data_manager.metadata, colour_by=colour_by)
            else:
                plot_pca(data_manager.expression)
        

        elif choice == '12':
            if data_manager.expression is None:
                print("Expression data not loaded. Please upload expression data first (Option 2).")
            elif data_manager.metadata is None:
                print("Metadata is not loaded. Please upload metadata first (Option 1).")
            else:
                from Dimensionality_Reduction import plot_umap
                
                visible_columns = [col for col in data_manager.metadata.columns if col.lower() != "sample_id"]
                print("Available columns for UMAP plot:", ", ".join(visible_columns))

                colour_by = input("Colour UMAP plot by metadata column (e.g. grade, idh)? Leave blank for none: ").strip()
                matched_col = next((col for col in data_manager.metadata.columns if col.lower() == colour_by.lower()), None) if colour_by and data_manager.metadata is not None else None

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
            if data_manager.expression is not None and data_manager.metadata is not None:
                from Differential_expression import perform_differential_expression

                print("\n--- Differential Expression ---")
                group_col = input("Enter metadata column to compare (e.g. grade): ").strip()
                group_1 = input("Enter first group label (e.g. 2): ").strip()
                group_2 = input("Enter second group label (e.g. 3): ").strip()

                try:
                    results = perform_differential_expression(
                        data_manager.expression,
                        data_manager.metadata,
                        group_col=group_col,
                        group_1=group_1,
                        group_2=group_2
                    )
                    # Filter for significant results (adjusted p < 0.05)
                    significant_results = results[results['adj_p_value'] < 0.05]

                    if not significant_results.empty:
                        print("\nTop 10 significant results by adjusted p-value (FDR < 0.05):")
                        print(significant_results.head(10).to_string(index=False))
                    else:
                        print("\nNo significant genes found (FDR < 0.05).")
                        
                except Exception as e:
                    print(f"Error during differential expression analysis: {e}")
            else:
                print("Expression or metadata file not loaded. Please upload both before using this option.")

        elif choice == '15':
            if data_manager.expression is not None and data_manager.metadata is not None:
                from Gene_explorer import explore_gene_expression, map_gene_to_chromosome, list_available_genes

                # Suggest a few available genes
                print("\nHere are some available genes you can explore:")
                list_available_genes(data_manager.expression)

                gene_name = input("Enter the gene name to explore: ").strip()

                try:
                    explore_gene_expression(data_manager.expression, data_manager.metadata, gene_name)
                    map_gene_to_chromosome(gene_name)
                except Exception as e:
                    print(f"Error occurred while exploring gene expression or mapping gene to chromosome: {e}")
            else:
                print("Expression or metadata file not loaded. Please upload both before using this option.")

        elif choice == '16':
            if data_manager.expression is None:
                print("Expression data not loaded. Please upload expression data first (Option 2).")
            elif data_manager.metadata is None:
                print("Metadata is not loaded. Please upload metadata first (Option 1).")
            else:
                genes = list_available_genes(data_manager.expression)
                if genes:
                    print(f"Available Genes: {', '.join(genes[:10])}...") #showing top 10 genes
                gene_name = input("Enter a gene name to explore expression: ").strip()

                if genes and gene_name not in genes:
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


        elif choice == '17':
            if data_manager.expression is not None and data_manager.metadata is not None:
                from Heatmap_visualisation import plot_expression_heatmap
                from Utils import list_available_genes

                all_genes = list_available_genes(data_manager.expression)
                print("Available genes (showing top 20):", ', '.join(all_genes[:20]))

                gene_input = input("Enter genes to visualise (comma-separated): ").strip()
                gene_list = [g.strip() for g in gene_input.split(',')]

                group_col = input("Optional: Enter metadata column to group by (e.g. grade): ").strip()

                try:
                    plot_expression_heatmap(
                        data_manager.expression,
                        data_manager.metadata,
                        genes=gene_list,
                        group_col=group_col if group_col else None
                    )
                except Exception as e:
                    print(f"Error generating heatmap: {e}")
            else:
                print("Please upload both expression and metadata files first.")

        elif choice == '18':
            print("Thank you for using our tool. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Please choose from 1-10. Try again.")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n[!] KeyboardInterrupt received. Exiting GliomaScope CLI gracefully.")
        sys.exit(0)
