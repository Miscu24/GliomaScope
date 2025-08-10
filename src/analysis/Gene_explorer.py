'''Gene-wise expression summaries (boxplots), chromosomal location logic'''

import pandas as pd
import plotly.express as px
import webbrowser 


def explore_gene_expression(expression_df, metadata_df, gene_name, group_col=None):
    #plots the expression of a specific gene grouped by a metadata column (e.g. grade)

    if gene_name not in expression_df.columns:
        print(f"Gene '{gene_name}' not found in expression data.")
        return
    
    # If no group_col specified, try to find a suitable one
    if group_col is None or group_col == '':
        # Look for common grouping columns
        common_groups = ['grade', 'source_name_ch1', 'characteristics_ch1', 'type', 'organism_ch1']
        for col in common_groups:
            if col in metadata_df.columns:
                group_col = col
                print(f"INFO: Using '{group_col}' for grouping (auto-selected)")
                break
        
        # If still no group_col, use the first available column
        if group_col is None or group_col == '':
            available_cols = [col for col in metadata_df.columns if col != 'Sample']
            if available_cols:
                group_col = available_cols[0]
                print(f"INFO: Using '{group_col}' for grouping (first available column)")
            else:
                print("ERROR: No suitable grouping column found in metadata")
                return
    
    # Check if the group_col exists
    if group_col not in metadata_df.columns:
        print(f"ERROR: Error: Column '{group_col}' not found in metadata.")
        available_cols = [col for col in metadata_df.columns if col != 'Sample']
        print(f"Available columns: {', '.join(available_cols)}")
        return
    
    #merge expression and metadata if provided
    df = expression_df[['Sample', gene_name]].copy()
    merged = pd.merge(df, metadata_df[['Sample', group_col]], on='Sample', how='inner')

    # Get the gene symbol for the title
    from src.utils.Utils import map_probe_to_gene, load_gene_annotations
    annotations = load_gene_annotations()
    gene_symbol = map_probe_to_gene(gene_name, annotations)
    
    # Use gene symbol in title if available, otherwise use probe ID
    title_gene = gene_symbol if gene_symbol != gene_name else gene_name
    
    #boxplot of expression based on the grade
    fig = px.box(
        merged,
        x=group_col,
        y=gene_name,
        points="all",
        title=f"{title_gene} Expression by {group_col.capitalize()}",
        labels={group_col: group_col.capitalize(), gene_name: "Expression Level"},
    )
    fig.update_traces(marker=dict(size=8, opacity=0.8))
    
    # Save plot to HTML file
    plot_filename = f"gene_expression_{gene_name}_{group_col}.html"
    fig.write_html(plot_filename)
    print(f"Gene expression plot saved to '{plot_filename}'")
    
    # Show plot in browser (non-blocking)
    try:
        import subprocess
        subprocess.Popen(['open', plot_filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Plot opened in your browser.")
    except Exception as e:
        print(f"Could not open plot automatically. Please open '{plot_filename}' manually in your browser.")

def map_gene_to_chromosome(gene_name, gene_location_file="dummy_gene1.csv"):
    try:
        df = pd.read_csv(gene_location_file)
        gene_info = df[df['Gene'].str.upper() == gene_name.upper()]

        if not gene_info.empty:
            chromosome = gene_info.iloc[0]['Chromosome']
            print(f"Gene '{gene_name}' is located on chromosome {chromosome}.")

            #Ensemble & NCBI links
            ensembl_link = f"https://www.ensembl.org/Multi/Search/Results?q={gene_name}&site=ensembl"
            ncbi_link = f"https://www.ncbi.nlm.nih.gov/gene/?term={gene_name}"
            print(f" Ensembl: {ensembl_link}")
            print(f"NCBI: {ncbi_link}")

            # Automatically open database links in browser
            print("Opening database links in browser...")
            webbrowser.open(ensembl_link)
            webbrowser.open(ncbi_link)

            # Create a more informative chromosome visualization
            chromosome_num = gene_info.iloc[0]['Chromosome']
            start_pos = gene_info.iloc[0]['Start']
            end_pos = gene_info.iloc[0]['End']
            
            # Create chromosome ideogram with banding patterns
            import plotly.graph_objects as go
            
            # Define chromosome banding patterns (simplified)
            # These are approximate band positions for chromosome 17
            if chromosome_num == 17:
                bands = [
                    {'name': 'p13.3', 'start': 0, 'end': 2000000, 'color': 'white'},
                    {'name': 'p13.2', 'start': 2000000, 'end': 4000000, 'color': 'black'},
                    {'name': 'p13.1', 'start': 4000000, 'end': 6000000, 'color': 'white'},
                    {'name': 'p12', 'start': 6000000, 'end': 8000000, 'color': 'black'},
                    {'name': 'p11.2', 'start': 8000000, 'end': 12000000, 'color': 'gray'},
                    {'name': 'p11.1', 'start': 12000000, 'end': 16000000, 'color': 'white'},
                    {'name': 'q11.1', 'start': 16000000, 'end': 20000000, 'color': 'gray'},
                    {'name': 'q11.2', 'start': 20000000, 'end': 25000000, 'color': 'black'},
                    {'name': 'q12', 'start': 25000000, 'end': 30000000, 'color': 'white'},
                    {'name': 'q21.1', 'start': 30000000, 'end': 35000000, 'color': 'black'},
                    {'name': 'q21.2', 'start': 35000000, 'end': 40000000, 'color': 'white'},
                    {'name': 'q21.31', 'start': 40000000, 'end': 45000000, 'color': 'black'},
                    {'name': 'q21.32', 'start': 45000000, 'end': 50000000, 'color': 'white'},
                    {'name': 'q21.33', 'start': 50000000, 'end': 55000000, 'color': 'black'},
                    {'name': 'q22', 'start': 55000000, 'end': 60000000, 'color': 'white'},
                    {'name': 'q23.1', 'start': 60000000, 'end': 65000000, 'color': 'black'},
                    {'name': 'q23.2', 'start': 65000000, 'end': 70000000, 'color': 'white'},
                    {'name': 'q24.1', 'start': 70000000, 'end': 75000000, 'color': 'black'},
                    {'name': 'q24.2', 'start': 75000000, 'end': 80000000, 'color': 'white'},
                    {'name': 'q24.3', 'start': 80000000, 'end': 85000000, 'color': 'black'},
                    {'name': 'q25.1', 'start': 85000000, 'end': 90000000, 'color': 'white'},
                    {'name': 'q25.2', 'start': 90000000, 'end': 95000000, 'color': 'black'},
                    {'name': 'q25.3', 'start': 95000000, 'end': 100000000, 'color': 'white'}
                ]
            elif chromosome_num == 7:
                bands = [
                    {'name': 'p22.3', 'start': 0, 'end': 3000000, 'color': 'white'},
                    {'name': 'p22.2', 'start': 3000000, 'end': 6000000, 'color': 'black'},
                    {'name': 'p22.1', 'start': 6000000, 'end': 9000000, 'color': 'white'},
                    {'name': 'p21.3', 'start': 9000000, 'end': 12000000, 'color': 'black'},
                    {'name': 'p21.2', 'start': 12000000, 'end': 15000000, 'color': 'white'},
                    {'name': 'p21.1', 'start': 15000000, 'end': 18000000, 'color': 'black'},
                    {'name': 'p15.3', 'start': 18000000, 'end': 21000000, 'color': 'white'},
                    {'name': 'p15.2', 'start': 21000000, 'end': 24000000, 'color': 'black'},
                    {'name': 'p15.1', 'start': 24000000, 'end': 27000000, 'color': 'white'},
                    {'name': 'p14.3', 'start': 27000000, 'end': 30000000, 'color': 'black'},
                    {'name': 'p14.2', 'start': 30000000, 'end': 33000000, 'color': 'white'},
                    {'name': 'p14.1', 'start': 33000000, 'end': 36000000, 'color': 'black'},
                    {'name': 'p13', 'start': 36000000, 'end': 39000000, 'color': 'white'},
                    {'name': 'p12.3', 'start': 39000000, 'end': 42000000, 'color': 'black'},
                    {'name': 'p12.2', 'start': 42000000, 'end': 45000000, 'color': 'white'},
                    {'name': 'p12.1', 'start': 45000000, 'end': 48000000, 'color': 'black'},
                    {'name': 'p11.2', 'start': 48000000, 'end': 52000000, 'color': 'gray'},
                    {'name': 'p11.1', 'start': 52000000, 'end': 56000000, 'color': 'white'},
                    {'name': 'q11.1', 'start': 56000000, 'end': 60000000, 'color': 'gray'},
                    {'name': 'q11.21', 'start': 60000000, 'end': 65000000, 'color': 'black'},
                    {'name': 'q11.22', 'start': 65000000, 'end': 70000000, 'color': 'white'},
                    {'name': 'q11.23', 'start': 70000000, 'end': 75000000, 'color': 'black'},
                    {'name': 'q21.11', 'start': 75000000, 'end': 80000000, 'color': 'white'},
                    {'name': 'q21.12', 'start': 80000000, 'end': 85000000, 'color': 'black'},
                    {'name': 'q21.13', 'start': 85000000, 'end': 90000000, 'color': 'white'},
                    {'name': 'q21.2', 'start': 90000000, 'end': 95000000, 'color': 'black'},
                    {'name': 'q21.3', 'start': 95000000, 'end': 100000000, 'color': 'white'},
                    {'name': 'q22.1', 'start': 100000000, 'end': 105000000, 'color': 'black'},
                    {'name': 'q22.2', 'start': 105000000, 'end': 110000000, 'color': 'white'},
                    {'name': 'q22.3', 'start': 110000000, 'end': 115000000, 'color': 'black'},
                    {'name': 'q31.1', 'start': 115000000, 'end': 120000000, 'color': 'white'},
                    {'name': 'q31.2', 'start': 120000000, 'end': 125000000, 'color': 'black'},
                    {'name': 'q31.31', 'start': 125000000, 'end': 130000000, 'color': 'white'},
                    {'name': 'q31.32', 'start': 130000000, 'end': 135000000, 'color': 'black'},
                    {'name': 'q31.33', 'start': 135000000, 'end': 140000000, 'color': 'white'},
                    {'name': 'q32.1', 'start': 140000000, 'end': 145000000, 'color': 'black'},
                    {'name': 'q32.2', 'start': 145000000, 'end': 150000000, 'color': 'white'},
                    {'name': 'q32.3', 'start': 150000000, 'end': 155000000, 'color': 'black'},
                    {'name': 'q33', 'start': 155000000, 'end': 160000000, 'color': 'white'},
                    {'name': 'q34', 'start': 160000000, 'end': 165000000, 'color': 'black'},
                    {'name': 'q35', 'start': 165000000, 'end': 170000000, 'color': 'white'},
                    {'name': 'q36.1', 'start': 170000000, 'end': 175000000, 'color': 'black'},
                    {'name': 'q36.2', 'start': 175000000, 'end': 180000000, 'color': 'white'},
                    {'name': 'q36.3', 'start': 180000000, 'end': 185000000, 'color': 'black'}
                ]
            elif chromosome_num == 2:
                bands = [
                    {'name': 'p25.3', 'start': 0, 'end': 5000000, 'color': 'white'},
                    {'name': 'p25.2', 'start': 5000000, 'end': 10000000, 'color': 'black'},
                    {'name': 'p25.1', 'start': 10000000, 'end': 15000000, 'color': 'white'},
                    {'name': 'p24.3', 'start': 15000000, 'end': 20000000, 'color': 'black'},
                    {'name': 'p24.2', 'start': 20000000, 'end': 25000000, 'color': 'white'},
                    {'name': 'p24.1', 'start': 25000000, 'end': 30000000, 'color': 'black'},
                    {'name': 'p23.3', 'start': 30000000, 'end': 35000000, 'color': 'white'},
                    {'name': 'p23.2', 'start': 35000000, 'end': 40000000, 'color': 'black'},
                    {'name': 'p23.1', 'start': 40000000, 'end': 45000000, 'color': 'white'},
                    {'name': 'p22.3', 'start': 45000000, 'end': 50000000, 'color': 'black'},
                    {'name': 'p22.2', 'start': 50000000, 'end': 55000000, 'color': 'white'},
                    {'name': 'p22.1', 'start': 55000000, 'end': 60000000, 'color': 'black'},
                    {'name': 'p21', 'start': 60000000, 'end': 65000000, 'color': 'white'},
                    {'name': 'p16.3', 'start': 65000000, 'end': 70000000, 'color': 'black'},
                    {'name': 'p16.2', 'start': 70000000, 'end': 75000000, 'color': 'white'},
                    {'name': 'p16.1', 'start': 75000000, 'end': 80000000, 'color': 'black'},
                    {'name': 'p15', 'start': 80000000, 'end': 85000000, 'color': 'white'},
                    {'name': 'p14', 'start': 85000000, 'end': 90000000, 'color': 'black'},
                    {'name': 'p13.3', 'start': 90000000, 'end': 95000000, 'color': 'white'},
                    {'name': 'p13.2', 'start': 95000000, 'end': 100000000, 'color': 'black'},
                    {'name': 'p13.1', 'start': 100000000, 'end': 105000000, 'color': 'white'},
                    {'name': 'p12', 'start': 105000000, 'end': 110000000, 'color': 'black'},
                    {'name': 'p11.2', 'start': 110000000, 'end': 115000000, 'color': 'gray'},
                    {'name': 'p11.1', 'start': 115000000, 'end': 120000000, 'color': 'white'},
                    {'name': 'q11.1', 'start': 120000000, 'end': 125000000, 'color': 'gray'},
                    {'name': 'q11.2', 'start': 125000000, 'end': 130000000, 'color': 'black'},
                    {'name': 'q12.1', 'start': 130000000, 'end': 135000000, 'color': 'white'},
                    {'name': 'q12.2', 'start': 135000000, 'end': 140000000, 'color': 'black'},
                    {'name': 'q13', 'start': 140000000, 'end': 145000000, 'color': 'white'},
                    {'name': 'q14.1', 'start': 145000000, 'end': 150000000, 'color': 'black'},
                    {'name': 'q14.2', 'start': 150000000, 'end': 155000000, 'color': 'white'},
                    {'name': 'q14.3', 'start': 155000000, 'end': 160000000, 'color': 'black'},
                    {'name': 'q21.1', 'start': 160000000, 'end': 165000000, 'color': 'white'},
                    {'name': 'q21.2', 'start': 165000000, 'end': 170000000, 'color': 'black'},
                    {'name': 'q21.3', 'start': 170000000, 'end': 175000000, 'color': 'white'},
                    {'name': 'q22.1', 'start': 175000000, 'end': 180000000, 'color': 'black'},
                    {'name': 'q22.2', 'start': 180000000, 'end': 185000000, 'color': 'white'},
                    {'name': 'q22.3', 'start': 185000000, 'end': 190000000, 'color': 'black'},
                    {'name': 'q23.1', 'start': 190000000, 'end': 195000000, 'color': 'white'},
                    {'name': 'q23.2', 'start': 195000000, 'end': 200000000, 'color': 'black'},
                    {'name': 'q23.3', 'start': 200000000, 'end': 205000000, 'color': 'white'},
                    {'name': 'q24.1', 'start': 205000000, 'end': 210000000, 'color': 'black'},
                    {'name': 'q24.2', 'start': 210000000, 'end': 215000000, 'color': 'white'},
                    {'name': 'q24.3', 'start': 215000000, 'end': 220000000, 'color': 'black'},
                    {'name': 'q31.1', 'start': 220000000, 'end': 225000000, 'color': 'white'},
                    {'name': 'q31.2', 'start': 225000000, 'end': 230000000, 'color': 'black'},
                    {'name': 'q31.3', 'start': 230000000, 'end': 235000000, 'color': 'white'},
                    {'name': 'q32.1', 'start': 235000000, 'end': 240000000, 'color': 'black'},
                    {'name': 'q32.2', 'start': 240000000, 'end': 245000000, 'color': 'white'},
                    {'name': 'q32.3', 'start': 245000000, 'end': 250000000, 'color': 'black'},
                    {'name': 'q33.1', 'start': 250000000, 'end': 255000000, 'color': 'white'},
                    {'name': 'q33.2', 'start': 255000000, 'end': 260000000, 'color': 'black'},
                    {'name': 'q33.3', 'start': 260000000, 'end': 265000000, 'color': 'white'},
                    {'name': 'q34', 'start': 265000000, 'end': 270000000, 'color': 'black'},
                    {'name': 'q35', 'start': 270000000, 'end': 275000000, 'color': 'white'},
                    {'name': 'q36.1', 'start': 275000000, 'end': 280000000, 'color': 'black'},
                    {'name': 'q36.2', 'start': 280000000, 'end': 285000000, 'color': 'white'},
                    {'name': 'q36.3', 'start': 285000000, 'end': 290000000, 'color': 'black'},
                    {'name': 'q37.1', 'start': 290000000, 'end': 295000000, 'color': 'white'},
                    {'name': 'q37.2', 'start': 295000000, 'end': 300000000, 'color': 'black'},
                    {'name': 'q37.3', 'start': 300000000, 'end': 305000000, 'color': 'white'}
                ]
            elif chromosome_num == 8:
                bands = [
                    {'name': 'p23.3', 'start': 0, 'end': 5000000, 'color': 'white'},
                    {'name': 'p23.2', 'start': 5000000, 'end': 10000000, 'color': 'black'},
                    {'name': 'p23.1', 'start': 10000000, 'end': 15000000, 'color': 'white'},
                    {'name': 'p22', 'start': 15000000, 'end': 20000000, 'color': 'black'},
                    {'name': 'p21.3', 'start': 20000000, 'end': 25000000, 'color': 'white'},
                    {'name': 'p21.2', 'start': 25000000, 'end': 30000000, 'color': 'black'},
                    {'name': 'p21.1', 'start': 30000000, 'end': 35000000, 'color': 'white'},
                    {'name': 'p12', 'start': 35000000, 'end': 40000000, 'color': 'black'},
                    {'name': 'p11.23', 'start': 40000000, 'end': 45000000, 'color': 'white'},
                    {'name': 'p11.22', 'start': 45000000, 'end': 50000000, 'color': 'black'},
                    {'name': 'p11.21', 'start': 50000000, 'end': 55000000, 'color': 'white'},
                    {'name': 'p11.1', 'start': 55000000, 'end': 60000000, 'color': 'gray'},
                    {'name': 'q11.1', 'start': 60000000, 'end': 65000000, 'color': 'gray'},
                    {'name': 'q11.21', 'start': 65000000, 'end': 70000000, 'color': 'black'},
                    {'name': 'q11.22', 'start': 70000000, 'end': 75000000, 'color': 'white'},
                    {'name': 'q11.23', 'start': 75000000, 'end': 80000000, 'color': 'black'},
                    {'name': 'q12.1', 'start': 80000000, 'end': 85000000, 'color': 'white'},
                    {'name': 'q12.2', 'start': 85000000, 'end': 90000000, 'color': 'black'},
                    {'name': 'q12.3', 'start': 90000000, 'end': 95000000, 'color': 'white'},
                    {'name': 'q13.1', 'start': 95000000, 'end': 100000000, 'color': 'black'},
                    {'name': 'q13.2', 'start': 100000000, 'end': 105000000, 'color': 'white'},
                    {'name': 'q13.3', 'start': 105000000, 'end': 110000000, 'color': 'black'},
                    {'name': 'q21.1', 'start': 110000000, 'end': 115000000, 'color': 'white'},
                    {'name': 'q21.2', 'start': 115000000, 'end': 120000000, 'color': 'black'},
                    {'name': 'q21.3', 'start': 120000000, 'end': 125000000, 'color': 'white'},
                    {'name': 'q22.1', 'start': 125000000, 'end': 130000000, 'color': 'black'},
                    {'name': 'q22.2', 'start': 130000000, 'end': 135000000, 'color': 'white'},
                    {'name': 'q22.3', 'start': 135000000, 'end': 140000000, 'color': 'black'},
                    {'name': 'q23.1', 'start': 140000000, 'end': 145000000, 'color': 'white'},
                    {'name': 'q23.2', 'start': 145000000, 'end': 150000000, 'color': 'black'},
                    {'name': 'q23.3', 'start': 150000000, 'end': 155000000, 'color': 'white'},
                    {'name': 'q24.1', 'start': 155000000, 'end': 160000000, 'color': 'black'},
                    {'name': 'q24.2', 'start': 160000000, 'end': 165000000, 'color': 'white'},
                    {'name': 'q24.3', 'start': 165000000, 'end': 170000000, 'color': 'black'},
                    {'name': 'q24.21', 'start': 170000000, 'end': 175000000, 'color': 'white'},
                    {'name': 'q24.22', 'start': 175000000, 'end': 180000000, 'color': 'black'},
                    {'name': 'q24.23', 'start': 180000000, 'end': 185000000, 'color': 'white'},
                    {'name': 'q24.3', 'start': 185000000, 'end': 190000000, 'color': 'black'},
                    {'name': 'q25.1', 'start': 190000000, 'end': 195000000, 'color': 'white'},
                    {'name': 'q25.2', 'start': 195000000, 'end': 200000000, 'color': 'black'},
                    {'name': 'q25.3', 'start': 200000000, 'end': 205000000, 'color': 'white'}
                ]
            elif chromosome_num == 9:
                bands = [
                    {'name': 'p24.3', 'start': 0, 'end': 5000000, 'color': 'white'},
                    {'name': 'p24.2', 'start': 5000000, 'end': 10000000, 'color': 'black'},
                    {'name': 'p24.1', 'start': 10000000, 'end': 15000000, 'color': 'white'},
                    {'name': 'p23', 'start': 15000000, 'end': 20000000, 'color': 'black'},
                    {'name': 'p22.3', 'start': 20000000, 'end': 25000000, 'color': 'white'},
                    {'name': 'p22.2', 'start': 25000000, 'end': 30000000, 'color': 'black'},
                    {'name': 'p22.1', 'start': 30000000, 'end': 35000000, 'color': 'white'},
                    {'name': 'p21.3', 'start': 35000000, 'end': 40000000, 'color': 'black'},
                    {'name': 'p21.2', 'start': 40000000, 'end': 45000000, 'color': 'white'},
                    {'name': 'p21.1', 'start': 45000000, 'end': 50000000, 'color': 'black'},
                    {'name': 'p13.3', 'start': 50000000, 'end': 55000000, 'color': 'white'},
                    {'name': 'p13.2', 'start': 55000000, 'end': 60000000, 'color': 'black'},
                    {'name': 'p13.1', 'start': 60000000, 'end': 65000000, 'color': 'white'},
                    {'name': 'p12', 'start': 65000000, 'end': 70000000, 'color': 'black'},
                    {'name': 'p11.2', 'start': 70000000, 'end': 75000000, 'color': 'gray'},
                    {'name': 'p11.1', 'start': 75000000, 'end': 80000000, 'color': 'white'},
                    {'name': 'q11', 'start': 80000000, 'end': 85000000, 'color': 'gray'},
                    {'name': 'q12', 'start': 85000000, 'end': 90000000, 'color': 'black'},
                    {'name': 'q13', 'start': 90000000, 'end': 95000000, 'color': 'white'},
                    {'name': 'q21.11', 'start': 95000000, 'end': 100000000, 'color': 'black'},
                    {'name': 'q21.12', 'start': 100000000, 'end': 105000000, 'color': 'white'},
                    {'name': 'q21.13', 'start': 105000000, 'end': 110000000, 'color': 'black'},
                    {'name': 'q21.2', 'start': 110000000, 'end': 115000000, 'color': 'white'},
                    {'name': 'q21.31', 'start': 115000000, 'end': 120000000, 'color': 'black'},
                    {'name': 'q21.32', 'start': 120000000, 'end': 125000000, 'color': 'white'},
                    {'name': 'q21.33', 'start': 125000000, 'end': 130000000, 'color': 'black'},
                    {'name': 'q22.1', 'start': 130000000, 'end': 135000000, 'color': 'white'},
                    {'name': 'q22.2', 'start': 135000000, 'end': 140000000, 'color': 'black'},
                    {'name': 'q22.31', 'start': 140000000, 'end': 145000000, 'color': 'white'},
                    {'name': 'q22.32', 'start': 145000000, 'end': 150000000, 'color': 'black'},
                    {'name': 'q22.33', 'start': 150000000, 'end': 155000000, 'color': 'white'},
                    {'name': 'q31.1', 'start': 155000000, 'end': 160000000, 'color': 'black'},
                    {'name': 'q31.2', 'start': 160000000, 'end': 165000000, 'color': 'white'},
                    {'name': 'q31.3', 'start': 165000000, 'end': 170000000, 'color': 'black'},
                    {'name': 'q32', 'start': 170000000, 'end': 175000000, 'color': 'white'},
                    {'name': 'q33.1', 'start': 175000000, 'end': 180000000, 'color': 'black'},
                    {'name': 'q33.2', 'start': 180000000, 'end': 185000000, 'color': 'white'},
                    {'name': 'q33.3', 'start': 185000000, 'end': 190000000, 'color': 'black'},
                    {'name': 'q34.11', 'start': 190000000, 'end': 195000000, 'color': 'white'},
                    {'name': 'q34.12', 'start': 195000000, 'end': 200000000, 'color': 'black'},
                    {'name': 'q34.13', 'start': 200000000, 'end': 205000000, 'color': 'white'},
                    {'name': 'q34.2', 'start': 205000000, 'end': 210000000, 'color': 'black'},
                    {'name': 'q34.3', 'start': 210000000, 'end': 215000000, 'color': 'white'}
                ]
            elif chromosome_num == 10:
                bands = [
                    {'name': 'p15.3', 'start': 0, 'end': 5000000, 'color': 'white'},
                    {'name': 'p15.2', 'start': 5000000, 'end': 10000000, 'color': 'black'},
                    {'name': 'p15.1', 'start': 10000000, 'end': 15000000, 'color': 'white'},
                    {'name': 'p14', 'start': 15000000, 'end': 20000000, 'color': 'black'},
                    {'name': 'p13', 'start': 20000000, 'end': 25000000, 'color': 'white'},
                    {'name': 'p12.33', 'start': 25000000, 'end': 30000000, 'color': 'black'},
                    {'name': 'p12.32', 'start': 30000000, 'end': 35000000, 'color': 'white'},
                    {'name': 'p12.31', 'start': 35000000, 'end': 40000000, 'color': 'black'},
                    {'name': 'p12.2', 'start': 40000000, 'end': 45000000, 'color': 'white'},
                    {'name': 'p12.1', 'start': 45000000, 'end': 50000000, 'color': 'black'},
                    {'name': 'p11.23', 'start': 50000000, 'end': 55000000, 'color': 'white'},
                    {'name': 'p11.22', 'start': 55000000, 'end': 60000000, 'color': 'black'},
                    {'name': 'p11.21', 'start': 60000000, 'end': 65000000, 'color': 'white'},
                    {'name': 'p11.1', 'start': 65000000, 'end': 70000000, 'color': 'gray'},
                    {'name': 'q11.1', 'start': 70000000, 'end': 75000000, 'color': 'gray'},
                    {'name': 'q11.21', 'start': 75000000, 'end': 80000000, 'color': 'black'},
                    {'name': 'q11.22', 'start': 80000000, 'end': 85000000, 'color': 'white'},
                    {'name': 'q11.23', 'start': 85000000, 'end': 90000000, 'color': 'black'},
                    {'name': 'q21.1', 'start': 90000000, 'end': 95000000, 'color': 'white'},
                    {'name': 'q21.2', 'start': 95000000, 'end': 100000000, 'color': 'black'},
                    {'name': 'q21.3', 'start': 100000000, 'end': 105000000, 'color': 'white'},
                    {'name': 'q22.1', 'start': 105000000, 'end': 110000000, 'color': 'black'},
                    {'name': 'q22.2', 'start': 110000000, 'end': 115000000, 'color': 'white'},
                    {'name': 'q22.3', 'start': 115000000, 'end': 120000000, 'color': 'black'},
                    {'name': 'q23.1', 'start': 120000000, 'end': 125000000, 'color': 'white'},
                    {'name': 'q23.2', 'start': 125000000, 'end': 130000000, 'color': 'black'},
                    {'name': 'q23.31', 'start': 130000000, 'end': 135000000, 'color': 'white'},
                    {'name': 'q23.32', 'start': 135000000, 'end': 140000000, 'color': 'black'},
                    {'name': 'q23.33', 'start': 140000000, 'end': 145000000, 'color': 'white'},
                    {'name': 'q24.1', 'start': 145000000, 'end': 150000000, 'color': 'black'},
                    {'name': 'q24.2', 'start': 150000000, 'end': 155000000, 'color': 'white'},
                    {'name': 'q24.31', 'start': 155000000, 'end': 160000000, 'color': 'black'},
                    {'name': 'q24.32', 'start': 160000000, 'end': 165000000, 'color': 'white'},
                    {'name': 'q24.33', 'start': 165000000, 'end': 170000000, 'color': 'black'},
                    {'name': 'q25.1', 'start': 170000000, 'end': 175000000, 'color': 'white'},
                    {'name': 'q25.2', 'start': 175000000, 'end': 180000000, 'color': 'black'},
                    {'name': 'q25.3', 'start': 180000000, 'end': 185000000, 'color': 'white'},
                    {'name': 'q26.11', 'start': 185000000, 'end': 190000000, 'color': 'black'},
                    {'name': 'q26.12', 'start': 190000000, 'end': 195000000, 'color': 'white'},
                    {'name': 'q26.13', 'start': 195000000, 'end': 200000000, 'color': 'black'},
                    {'name': 'q26.2', 'start': 200000000, 'end': 205000000, 'color': 'white'},
                    {'name': 'q26.3', 'start': 205000000, 'end': 210000000, 'color': 'black'}
                ]
            else:
                # Generic banding for other chromosomes
                bands = [
                    {'name': 'p', 'start': 0, 'end': 50000000, 'color': 'lightgray'},
                    {'name': 'q', 'start': 50000000, 'end': 100000000, 'color': 'darkgray'}
                ]
            
            # Create chromosome ideogram with thin, realistic appearance
            fig = go.Figure()
            
            # Calculate chromosome dimensions for thin appearance
            chrom_width = 0.1  # Make chromosome very thin
            chrom_center = 0.5
            
            # Add chromosome bands with thin, realistic appearance
            for band in bands:
                # Create thin chromosome band
                fig.add_shape(
                    type="rect",
                    x0=chrom_center - chrom_width/2, 
                    x1=chrom_center + chrom_width/2,
                    y0=band['start'], 
                    y1=band['end'],
                    fillcolor=band['color'],
                    line=dict(color="black", width=0.5),
                    layer="below"
                )
                
                # Add band labels for major bands
                if band['end'] - band['start'] > 8000000:  # Only label major bands
                    fig.add_annotation(
                        x=chrom_center + chrom_width/2 + 0.05,
                        y=(band['start'] + band['end']) / 2,
                        text=band['name'],
                        showarrow=False,
                        font=dict(size=9),
                        xanchor='left'
                    )
            
            # Add centromere constriction effect
            # Find centromere region (usually gray bands)
            centromere_bands = [band for band in bands if band['color'] == 'gray']
            if centromere_bands:
                centromere_start = min([band['start'] for band in centromere_bands])
                centromere_end = max([band['end'] for band in centromere_bands])
                
                # Add constriction effect
                fig.add_shape(
                    type="rect",
                    x0=chrom_center - chrom_width/4, 
                    x1=chrom_center + chrom_width/4,
                    y0=centromere_start, 
                    y1=centromere_end,
                    fillcolor="gray",
                    line=dict(color="black", width=0.5),
                    layer="above"
                )
            
            # Add gene marker as a prominent red band
            fig.add_shape(
                type="rect",
                x0=chrom_center - chrom_width/2, 
                x1=chrom_center + chrom_width/2,
                y0=start_pos, 
                y1=end_pos,
                fillcolor="red",
                line=dict(color="darkred", width=2),
                layer="above"
            )
            
            # Add gene label positioned far to the side with clear arrow pointing to the gene
            fig.add_annotation(
                x=chrom_center + chrom_width/2 + 0.25,  # Move much further to the right
                y=(start_pos + end_pos) / 2,
                text=f"{gene_name}<br>{start_pos:,} - {end_pos:,}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="red",
                font=dict(size=10, color="black"),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="red",
                borderwidth=1,
                ax=-0.15,  # Arrow points back to the gene (longer arrow)
                ay=0       # No vertical offset
            )
            
            # Add chromosome arm labels
            # Find p and q arms
            p_bands = [band for band in bands if band['name'].startswith('p')]
            q_bands = [band for band in bands if band['name'].startswith('q')]
            
            if p_bands:
                p_center = (min([band['start'] for band in p_bands]) + max([band['end'] for band in p_bands])) / 2
                fig.add_annotation(
                    x=chrom_center - chrom_width/2 - 0.05,
                    y=p_center,
                    text="p",
                    showarrow=False,
                    font=dict(size=12, color="black"),
                    xanchor='right'
                )
            
            if q_bands:
                q_center = (min([band['start'] for band in q_bands]) + max([band['end'] for band in q_bands])) / 2
                fig.add_annotation(
                    x=chrom_center - chrom_width/2 - 0.05,
                    y=q_center,
                    text="q",
                    showarrow=False,
                    font=dict(size=12, color="black"),
                    xanchor='right'
                )
            
            # Update layout for thin chromosome appearance with space for label
            fig.update_layout(
                title=f"{gene_name} Location on Chromosome {chromosome_num}<br><sub>Chromosome Ideogram with Banding Pattern</sub>",
                xaxis=dict(
                    range=[chrom_center - 0.3, chrom_center + 0.5],  # Extended range for label
                    showticklabels=False,
                    showgrid=False
                ),
                yaxis=dict(
                    title="Position (bp)",
                    range=[0, max([band['end'] for band in bands])],
                    showgrid=True
                ),
                showlegend=False,
                height=700,
                width=500,  # Increased width for label space
                plot_bgcolor='white'
            )
            
            # Save plot to HTML file
            plot_filename = f"gene_chromosome_{gene_name}.html"
            fig.write_html(plot_filename)
            print(f"Gene chromosome plot saved to '{plot_filename}'")
            
            # Show plot in browser (non-blocking)
            try:
                import subprocess
                subprocess.Popen(['open', plot_filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("Plot opened in your browser.")
            except Exception as e:
                print(f"Could not open plot automatically. Please open '{plot_filename}' manually in your browser.")
        else:
            print(f"Gene '{gene_name}' not found in gene location data.")
    except FileNotFoundError:
        print(f"Gene location file not found: {gene_location_file}")
    except Exception as e:
        print(f"Error occurred while processing gene location data: {e}")
        
 

#for debugging: list the available genes
def list_available_genes(expression_df, limit=10):
    genes = [col for col in expression_df.columns if col.lower() != 'Sample']
    preview = ', '.join(genes[:limit])
    print(f"{preview}{'...' if len(genes) > limit else ''}")

