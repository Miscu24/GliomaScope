#!/usr/bin/env python3
"""
GliomaScope Terminal Interface

A comprehensive command-line interface for glioma transcriptomics analysis.
Provides the same functionality as the web interface in a terminal format.
"""

import os

from src.data_handling.Data_loader import DataManager

# Global data manager instance
data_manager = DataManager()


def upload_and_format_dataset():
    """Upload and format custom dataset files."""
    print("\n=== Upload Custom Dataset ===")
    expr_path = input("Enter path to expression file (.csv/.tsv): ").strip()
    meta_path = input("Enter path to metadata file (.csv/.tsv): ").strip()
    expr_id = input("Column name for Sample ID in expression file "
                    "(default: Sample): ").strip() or "Sample"
    meta_id = input("Column name for Sample ID in metadata file "
                    "(default: SampleID): ").strip() or "SampleID"

    try:
        print("Formatting uploaded dataset...")
        from src.data_handling.Format_data import format_for_gliomascope
        format_for_gliomascope(expr_path, meta_path, expr_id, meta_id)
        print("Formatting complete. Loading cleaned data into GliomaScope...")

        cleaned_expr = "cleaned_data/expression.csv"
        cleaned_meta = "cleaned_data/metadata.csv"
        data_manager.load_expression(cleaned_expr)
        data_manager.load_file_smart(cleaned_meta)
        print("Data successfully loaded.")
    except Exception as e:
        print(f"Error processing dataset: {e}")


def print_banner():
    """Print the GliomaScope banner."""
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


def print_introduction():
    """Print the introduction text."""
    print("Are you looking for deeper insights into gliomas?")
    print("\nWell, here you can use your own metadata and gene expression data "
          "to explore the tumour landscape like never before.")
    print("GliomaScope lets you visualise PCA, UMAP, and gene expression "
          "patterns, perform differential analysis, map genes to their "
          "chromosomal locations, and generate publication-ready insights.")
    print("All right from your terminal.\n")

    input("   Press ENTER to dive in...")
    os.system('cls' if os.name == 'nt' else 'clear')


def print_menu():
    """Print the main menu options."""
        print("\n=== GliomaScope CLI ===")
        print("1. Download + load GEO dataset by ID")
        print("2. Format dataset (upload .csv/.tsv) and select to load")
        print("3. Upload metadata file")
        print("4. Upload expression file")
    print("5. Data Exploration & Filtering")
    print("6. Geographic Visualisation")
    print("7. Visualise PCA")
    print("8. Visualise UMAP")
    print("9. Differential expression analysis")
    print("10. Explore individual gene expression")
    print("11. Chromosomal gene mapping")
    print("12. Heatmap visualisation for gene sets")
    print("13. Exit")


def handle_geo_download():
    """Handle GEO dataset download."""
    from src.utils.Utils import fetch_and_format_geo, display_and_log_summary

            geo_id = input("Enter GEO Accession ID (e.g. GSE15824): ").strip()
    print("Loading dataset...")

            # Fetch DataFrames
            meta_df, expr_df = fetch_and_format_geo(geo_id)

            if meta_df is None or expr_df is None:
        print("Failed to load GEO dataset.")
                return

    # Load into data manager
    data_manager.metadata = meta_df
    data_manager.expression = expr_df

    # Display summary
    display_and_log_summary(meta_df, expr_df, geo_id)
    print("Dataset loaded successfully!")


def handle_data_upload():
    """Handle data file uploads."""
    from src.data_handling.FileUploadHandler import process_upload

    print("\n=== Data Upload ===")
    file_path = input("Enter path to file (.csv/.tsv): ").strip()

    if not os.path.exists(file_path):
        print("File not found!")
        return

    try:
        process_upload(file_path, data_manager)
        print("File uploaded and processed successfully!")
    except Exception as e:
        print(f"Error uploading file: {e}")


def handle_data_exploration():
    """Handle data exploration and filtering."""
    if data_manager.metadata is None and data_manager.expression is None:
        print("No data loaded. Please upload data first.")
        return

    from src.data_handling.Explore_data import preview_dataframe, display_summary

    print("\n=== Data Exploration ===")
    print("1. View metadata summary")
    print("2. View expression summary")
    print("3. Preview metadata")
    print("4. Preview expression")
    print("5. Back to main menu")

    choice = input("Enter choice (1-5): ").strip()

    if choice == '1' and data_manager.metadata is not None:
        display_summary(data_manager.metadata, "Metadata")
    elif choice == '2' and data_manager.expression is not None:
        display_summary(data_manager.expression, "Expression")
    elif choice == '3' and data_manager.metadata is not None:
        preview_dataframe(data_manager.metadata, "Metadata")
    elif choice == '4' and data_manager.expression is not None:
        preview_dataframe(data_manager.expression, "Expression")


def handle_geographic_visualization():
    """Handle geographic visualization."""
    if data_manager.metadata is None:
        print("No metadata loaded. Please upload metadata first.")
        return

    from src.visualization.Patient_geomap import plot_patient_geomap

    print("\n=== Geographic Visualization ===")
    print("Generating patient location map...")

    try:
        plot_patient_geomap(data_manager.metadata)
        print("Geographic map generated successfully!")
    except Exception as e:
        print(f"Error generating map: {e}")


def handle_pca_visualization():
    """Handle PCA visualization."""
            if data_manager.expression is None:
        print("No expression data loaded. Please upload expression data first.")
        return

    from src.visualization.Dimensionality_Reduction import plot_pca

    print("\n=== PCA Visualization ===")
    color_by = input("Enter column name to color by (or press Enter for default): ").strip()

    if not color_by:
        color_by = "default"

    try:
        plot_pca(data_manager.expression, data_manager.metadata, color_by)
        print("PCA plot generated successfully!")
    except Exception as e:
        print(f"Error generating PCA plot: {e}")


def handle_umap_visualization():
    """Handle UMAP visualization."""
    if data_manager.expression is None:
        print("No expression data loaded. Please upload expression data first.")
        return

    from src.visualization.Dimensionality_Reduction import plot_umap

    print("\n=== UMAP Visualization ===")
    color_by = input("Enter column name to color by (or press Enter for default): ").strip()

    if not color_by:
        color_by = "default"

    try:
        plot_umap(data_manager.expression, data_manager.metadata, color_by)
        print("UMAP plot generated successfully!")
                except Exception as e:
        print(f"Error generating UMAP plot: {e}")


def handle_differential_expression():
    """Handle differential expression analysis."""
    if data_manager.expression is None or data_manager.metadata is None:
        print("Both expression and metadata required. Please upload both first.")
        return

    from src.analysis.Differential_expression import perform_differential_expression

    print("\n=== Differential Expression Analysis ===")

    # Get available columns
                available_cols = [col for col in data_manager.metadata.columns if col != 'Sample']
    print(f"Available grouping columns: {', '.join(available_cols)}")

    group_col = input("Enter grouping column name: ").strip()

    if group_col not in available_cols:
        print(f"Column '{group_col}' not found in metadata.")
        return

    # Get unique values for the column
    unique_vals = data_manager.metadata[group_col].unique()
    print(f"Available groups: {', '.join(map(str, unique_vals))}")

    group1 = input("Enter first group name: ").strip()
    group2 = input("Enter second group name: ").strip()

    if group1 not in unique_vals or group2 not in unique_vals:
        print("Invalid group names.")
        return

    try:
        perform_differential_expression(
            data_manager.expression, data_manager.metadata,
            group_col, group1, group2
        )
        print("Differential expression analysis completed!")
                except Exception as e:
        print(f"Error in differential expression analysis: {e}")


def handle_gene_expression():
    """Handle individual gene expression analysis."""
    if data_manager.expression is None or data_manager.metadata is None:
        print("Both expression and metadata required. Please upload both first.")
        return

    from src.analysis.Gene_explorer import explore_gene_expression
    from src.utils.Utils import get_all_available_genes, load_gene_annotations

    print("\n=== Gene Expression Analysis ===")
    print("This tool lets you explore expression patterns of individual genes.")

    # Get available genes
    annotations = load_gene_annotations()
    all_genes_mapping = get_all_available_genes(data_manager.expression, annotations)

    # Create a unique list of GENE NAMES only (no probe IDs)
    unique_genes = {}  # gene_name -> probe_id
    display_names = []  # For numbered display (gene names only)
    probe_list = []     # Corresponding probe IDs

    # Collect only genes with known names
    for probe_id in data_manager.expression.columns:
        if probe_id != 'Sample':
            if annotations is not None:
                from src.utils.Utils import map_probe_to_gene
                mapped_name = map_probe_to_gene(probe_id, annotations)
                if mapped_name != probe_id:
                    if mapped_name not in unique_genes:
                        unique_genes[mapped_name] = probe_id
                        display_names.append(mapped_name)
                        probe_list.append(probe_id)

    # Sort gene names alphabetically
    sorted_genes = sorted(zip(display_names, probe_list))
    display_names = [gene for gene, probe in sorted_genes]
    probe_list = [probe for gene, probe in sorted_genes]

    if len(display_names) == 0:
        print("ERROR: No genes with known names found in this dataset.")
        print("This dataset may not have gene annotation information.")
        return

    print("\nAVAILABLE GENES FOR EXPRESSION ANALYSIS")
    print("=" * 60)
    print(f"Total genes with known names: {len(display_names):,}")
    print("(Sorted alphabetically for easy browsing)")

    # Show gene names with pagination
    for i, gene_name in enumerate(display_names, 1):
        print(f"   {i:4d}. {gene_name}")

        if i % 50 == 0 and i < len(display_names):
            continue_viewing = input(
                f"\nShowing {i}/{len(display_names)} genes. "
                "Press Enter to continue or 'q' to stop: "
            ).strip()
            if continue_viewing.lower() == 'q':
                print(f"... and {len(display_names) - i:,} more genes available")
                break

    print("=" * 60)
    print("TIP: Popular glioma genes include: TP53, EGFR, MGMT, IDH1, ATRX, PTEN")
    print("TIP: You can enter:")
    print(f"   • Number (1-{len(display_names)}) from the gene list above")
    print("   • Gene name directly (e.g., TP53, EGFR, MGMT)")
    print("   • Probe ID if you know it (e.g., 10000_at)")

    user_input = input(
        f"\nEnter gene number (1-{len(display_names)}), name, or probe ID: "
    ).strip()

    try:
        # Handle numbered input, gene names, or probe IDs
        probe_id = None
        gene_name = None

        if user_input.isdigit():
            # User entered a number
            gene_index = int(user_input) - 1
            if 0 <= gene_index < len(probe_list):
                probe_id = probe_list[gene_index]
                gene_name = display_names[gene_index]
                print(f"Selected: {gene_name}")
            else:
                print(f"Invalid number. Please enter 1-{len(probe_list)}.")
                return
            else:
            # User entered gene name or probe ID
            gene_name = user_input
            gene_upper = user_input.upper()

            if user_input in data_manager.expression.columns:
                        # Already a probe ID
                probe_id = user_input
                print(f"SUCCESS: Using probe ID: '{user_input}'")
                    elif gene_upper in all_genes_mapping:
                        # Found gene name in mapping
                        probe_id = all_genes_mapping[gene_upper]
                print(f"SUCCESS: Mapped '{user_input}' to probe ID '{probe_id}'")
                    else:
                print(f"ERROR: Gene '{user_input}' not found.")
                return

        # Get grouping column
                    available_cols = [col for col in data_manager.metadata.columns if col != 'Sample']
        print(f"\nAvailable grouping columns: {', '.join(available_cols)}")
        group_col = input("Enter grouping column name: ").strip()

        if group_col not in available_cols:
            print(f"Column '{group_col}' not found in metadata.")
            return

        # Generate the plot
        explore_gene_expression(
            data_manager.expression, data_manager.metadata,
            probe_id, group_col
        )
        print("Gene expression plot generated successfully!")
                    
                except Exception as e:
                    print(f"ERROR: Error occurred while exploring gene expression: {e}")
                    print("TIP: Make sure your data is properly loaded and formatted")


def handle_chromosome_mapping():
    """Handle chromosomal gene mapping."""
    if data_manager.expression is None or data_manager.metadata is None:
        print("Both expression and metadata required. Please upload both first.")
        return

    from src.analysis.Gene_explorer import map_gene_to_chromosome
    from src.utils.Utils import get_all_available_genes, load_gene_annotations

    print("\nCHROMOSOMAL GENE MAPPING")
    print("=" * 60)
    print("This tool maps genes to their chromosomal locations and displays")
    print("chromosome ideograms with gene positions.")

    # Get available genes
                    annotations = load_gene_annotations()
                    all_genes_mapping = get_all_available_genes(data_manager.expression, annotations)
                    
    # Create a unique list of GENE NAMES only
    unique_genes = {}  # gene_name -> probe_id
    display_names = []  # For numbered display (gene names only)
    probe_list = []     # Corresponding probe IDs

    # Collect only genes with known names
    for probe_id in data_manager.expression.columns:
        if probe_id != 'Sample':
            if annotations is not None:
                from src.utils.Utils import map_probe_to_gene
                mapped_name = map_probe_to_gene(probe_id, annotations)
                if mapped_name != probe_id:
                    if mapped_name not in unique_genes:
                        unique_genes[mapped_name] = probe_id
                        display_names.append(mapped_name)
                        probe_list.append(probe_id)

    # Sort gene names alphabetically
    sorted_genes = sorted(zip(display_names, probe_list))
    display_names = [gene for gene, probe in sorted_genes]
    probe_list = [probe for gene, probe in sorted_genes]

    if len(display_names) == 0:
        print("ERROR: No genes with known names found in this dataset.")
        print("This dataset may not have gene annotation information.")
        return

    print("\nAVAILABLE GENES FOR CHROMOSOME MAPPING")
    print("=" * 60)
    print(f"Total genes with known names: {len(display_names):,}")
    print("(Sorted alphabetically for easy browsing)")

    # Show gene names with pagination
    for i, gene_name in enumerate(display_names, 1):
        print(f"   {i:4d}. {gene_name}")

        if i % 20 == 0 and i < len(display_names):
            continue_viewing = input(
                f"\nShowing {i}/{len(display_names)} genes. "
                "Press Enter to continue or 'q' to stop: "
            ).strip()
            if continue_viewing.lower() == 'q':
                print(f"... and {len(display_names) - i:,} more genes available")
                break

    print("=" * 60)
    print("TIP: Popular glioma genes include: TP53, EGFR, MGMT, IDH1, ATRX, PTEN")
    print("TIP: You can enter:")
    print(f"   • Number (1-{len(display_names)}) from the gene list above")
    print("   • Gene name directly (e.g., TP53, EGFR, MGMT)")
    print("   • Probe ID if you know it (e.g., 10000_at)")

    user_input = input(
        f"\nEnter gene number (1-{len(display_names)}), name, or probe ID: "
    ).strip()

    try:
        # Handle numbered input, gene names, or probe IDs
        probe_id = None
        gene_name = None

        if user_input.isdigit():
            # User entered a number
            gene_index = int(user_input) - 1
            if 0 <= gene_index < len(probe_list):
                probe_id = probe_list[gene_index]
                gene_name = display_names[gene_index]
                print(f"Selected: {gene_name}")
            else:
                print(f"Invalid number. Please enter 1-{len(probe_list)}.")
                return
        else:
            # User entered gene name or probe ID
            gene_name = user_input
            gene_upper = user_input.upper()

            if user_input in data_manager.expression.columns:
                        # Already a probe ID
                probe_id = user_input
                print(f"SUCCESS: Using probe ID: '{user_input}'")
                    elif gene_upper in all_genes_mapping:
                        # Found gene name in mapping
                        probe_id = all_genes_mapping[gene_upper]
                print(f"SUCCESS: Mapped '{user_input}' to probe ID '{probe_id}'")
                    else:
                print(f"ERROR: Gene '{user_input}' not found.")
                return

        # Generate the chromosome map
        map_gene_to_chromosome(data_manager.expression, probe_id)
        print("Chromosome mapping completed successfully!")

    except Exception as e:
        print(f"ERROR: Error occurred while mapping gene to chromosome: {e}")
        print("TIP: Make sure your data is properly loaded and formatted")


def handle_heatmap_visualization():
    """Handle heatmap visualization."""
    if data_manager.expression is None or data_manager.metadata is None:
        print("Both expression and metadata required. Please upload both first.")
                        return
                    
    from src.visualization.Heatmap_visualisation import plot_expression_heatmap
    from src.utils.Utils import get_all_available_genes, load_gene_annotations

    print("\nHEATMAP VISUALIZATION")
    print("=" * 60)
    print("This tool creates expression heatmaps for multiple genes")
    print("with optional sample grouping.")

    # Get available genes
    annotations = load_gene_annotations()
    all_genes_mapping = get_all_available_genes(data_manager.expression, annotations)

    # Create a unique list of GENE NAMES only
    unique_genes = {}  # gene_name -> probe_id
    display_names = []  # For numbered display (gene names only)
    probe_list = []     # Corresponding probe IDs

    # Collect only genes with known names
    for probe_id in data_manager.expression.columns:
        if probe_id != 'Sample':
            if annotations is not None:
                from src.utils.Utils import map_probe_to_gene
                mapped_name = map_probe_to_gene(probe_id, annotations)
                if mapped_name != probe_id:
                    if mapped_name not in unique_genes:
                        unique_genes[mapped_name] = probe_id
                        display_names.append(mapped_name)
                        probe_list.append(probe_id)

    # Sort gene names alphabetically
    sorted_genes = sorted(zip(display_names, probe_list))
    display_names = [gene for gene, probe in sorted_genes]
    probe_list = [probe for gene, probe in sorted_genes]

    if len(display_names) == 0:
        print("ERROR: No genes with known names found in this dataset.")
        print("This dataset may not have gene annotation information.")
        return

    print("\nAVAILABLE GENES FOR HEATMAP VISUALIZATION")
    print("=" * 60)
    print(f"Total genes with known names: {len(display_names):,}")
    print("(Sorted alphabetically for easy browsing)")

    # Show gene names with pagination
    for i, gene_name in enumerate(display_names, 1):
        print(f"   {i:4d}. {gene_name}")

        if i % 20 == 0 and i < len(display_names):
            continue_viewing = input(
                f"\nShowing {i}/{len(display_names)} genes. "
                "Press Enter to continue or 'q' to stop: "
            ).strip()
            if continue_viewing.lower() == 'q':
                print(f"... and {len(display_names) - i:,} more genes available")
                break

    print("=" * 60)
    print("TIP: Popular glioma genes include: TP53, EGFR, MGMT, IDH1, ATRX, PTEN")
    print("TIP: You can enter:")
    print("   • Numbers (e.g., 1,3,5) from the gene list above")
    print("   • Gene names (e.g., TP53,EGFR,MGMT)")
    print("   • Mix of both (e.g., 1,EGFR,5)")

    gene_input = input("\nEnter genes for heatmap (comma-separated): ").strip()

    # Parse the input to handle numbers, gene names, and probe IDs
    gene_selections = [g.strip() for g in gene_input.split(',')]
    gene_list = []

    for selection in gene_selections:
        if selection.isdigit():
            # User entered a number
            gene_index = int(selection) - 1
            if 0 <= gene_index < len(probe_list):
                gene_list.append(display_names[gene_index])
                print(f"Selected #{selection}: {display_names[gene_index]}")
            else:
                print(f"Invalid number: {selection}. Please enter 1-{len(probe_list)}.")
        else:
            # User entered gene name or probe ID
            gene_upper = selection.upper()
            if gene_upper in all_genes_mapping:
                gene_list.append(selection)
                print(f"Selected gene: {selection}")
            elif selection in data_manager.expression.columns:
                gene_list.append(selection)
                print(f"Selected probe: {selection}")
            else:
                print(f"Gene '{selection}' not found. "
                      f"Available genes: {', '.join(display_names[:5])}...")

    if not gene_list:
        print("No valid genes selected. Please try again.")
        return

    # Get grouping column
    available_cols = [col for col in data_manager.metadata.columns if col != 'Sample']
    print(f"\nAvailable grouping columns: {', '.join(available_cols)}")
    group_col = input("Enter grouping column name (or press Enter for none): ").strip()

    if group_col and group_col not in available_cols:
        print(f"Column '{group_col}' not found in metadata.")
        return

    try:
        # Generate the heatmap
                    plot_expression_heatmap(
            data_manager.expression, data_manager.metadata,
            gene_list, group_col
        )
        print("Heatmap generated successfully!")

                except Exception as e:
        print(f"ERROR: Error occurred while generating heatmap: {e}")
        print("TIP: Make sure your data is properly loaded and formatted")


def main_menu():
    """Main menu loop."""
    os.system('clear')
    print_banner()
    print_introduction()

    while True:
        print_menu()
        choice = input("Enter your choice (1-13): ").strip()

        if choice == '1':
            handle_geo_download()
        elif choice == '2':
            upload_and_format_dataset()
        elif choice == '3':
            handle_data_upload()
        elif choice == '4':
            handle_data_upload()
        elif choice == '5':
            handle_data_exploration()
        elif choice == '6':
            handle_geographic_visualization()
        elif choice == '7':
            handle_pca_visualization()
        elif choice == '8':
            handle_umap_visualization()
        elif choice == '9':
            handle_differential_expression()
        elif choice == '10':
            handle_gene_expression()
        elif choice == '11':
            handle_chromosome_mapping()
        elif choice == '12':
            handle_heatmap_visualization()
        elif choice == '13':
            print("\nThank you for using GliomaScope!")
            print("Empowering you to explore and understand at the genomic level.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 13.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
        main_menu()
