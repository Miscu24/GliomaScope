import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering

def plot_expression_heatmap(expression_df, metadata_df=None, genes=None, group_col=None):
    # Check for Sample
    if 'Sample' not in expression_df.columns:
        print("Error: 'Sample' column not found.")
        return

    if genes is None or not genes:
        print("Please provide a list of genes to include in the heatmap.")
        return

    # Import gene mapping functions
    from Utils import get_all_available_genes, map_probe_to_gene, load_gene_annotations
    
    # Load gene annotations and get all available genes
    annotations = load_gene_annotations()
    all_genes_mapping = get_all_available_genes(expression_df, annotations)
    
    # Convert gene names to probe IDs if needed (case-insensitive)
    converted_genes = []
    for gene in genes:
        gene_upper = gene.upper()  # Convert to uppercase for case-insensitive matching
        
        if gene in expression_df.columns:
            # Already a probe ID
            converted_genes.append(gene)
            print(f"SUCCESS: Using probe ID: '{gene}'")
        elif gene_upper in all_genes_mapping:
            # Found gene name in mapping
            probe_id = all_genes_mapping[gene_upper]
            converted_genes.append(probe_id)
            print(f"SUCCESS: Mapped '{gene}' to probe ID '{probe_id}'")
        else:
            print(f"ERROR: Could not find gene '{gene}' in available genes")
            print(f"   Try using one of the available genes from the list above")
    
    if not converted_genes:
        print("No valid genes found for heatmap.")
        return
    
    # Check for missing genes
    missing_genes = [gene for gene in converted_genes if gene not in expression_df.columns]
    if missing_genes:
        print(f"The following genes are missing in expression data: {', '.join(missing_genes)}")
        return

    # Subset data
    heatmap_data = expression_df[['Sample'] + converted_genes].copy()
    heatmap_data.set_index('Sample', inplace=True)
    
    # Create gene name mapping for display
    gene_display_names = {}
    for probe_id in converted_genes:
        gene_name = map_probe_to_gene(probe_id, annotations)
        gene_display_names[probe_id] = gene_name
    
    # Rename columns to show gene names
    heatmap_data.columns = [gene_display_names.get(col, col) for col in heatmap_data.columns]

    # Standardize across genes
    scaled_data = StandardScaler().fit_transform(heatmap_data)
    scaled_df = pd.DataFrame(scaled_data, index=heatmap_data.index, columns=heatmap_data.columns)

    # Optional grouping
    group_series = None
    if metadata_df is not None and group_col and group_col in metadata_df.columns:
        group_series = metadata_df.set_index('Sample')[group_col].reindex(scaled_df.index)

    # Create interactive heatmap with Plotly
    fig = go.Figure(data=go.Heatmap(
        z=scaled_df.values,
        x=scaled_df.columns,
        y=scaled_df.index,
        colorscale='RdBu_r',  # Red-Blue diverging colormap
        zmid=0,  # Centre the colormap at 0
        hoverongaps=False,
        hovertemplate='<b>Sample:</b> %{y}<br><b>Gene:</b> %{x}<br><b>Expression:</b> %{z:.2f}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title=f"Gene Expression Heatmap ({len(genes)} genes, {len(scaled_df)} samples)",
        xaxis_title="Genes",
        yaxis_title="Samples",
        width=1200,
        height=800,
        xaxis=dict(
            tickangle=45,
            tickmode='array',
            ticktext=scaled_df.columns,
            tickvals=list(range(len(scaled_df.columns)))
        )
    )

    # Save plot to HTML file
    plot_filename = f"heatmap_{'_'.join(genes[:3])}.html"
    fig.write_html(plot_filename)
    print(f"Heatmap saved to '{plot_filename}'")
    
    # Show plot in browser (non-blocking)
    try:
        import subprocess
        subprocess.Popen(['open', plot_filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Heatmap opened in your browser.")
    except Exception as e:
        print(f"Could not open heatmap automatically. Please open '{plot_filename}' manually in your browser.")
