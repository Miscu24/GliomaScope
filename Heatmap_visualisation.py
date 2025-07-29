import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

def plot_expression_heatmap(expression_df, metadata_df=None, genes=None, group_col=None):
    # Check for Sample_ID
    if 'Sample_ID' not in expression_df.columns:
        print("Error: 'Sample_ID' column not found.")
        return

    if genes is None or not genes:
        print("Please provide a list of genes to include in the heatmap.")
        return

    missing_genes = [gene for gene in genes if gene not in expression_df.columns]
    if missing_genes:
        print(f"The following genes are missing in expression data: {', '.join(missing_genes)}")
        return

    # Subset data
    heatmap_data = expression_df[['Sample_ID'] + genes].copy()
    heatmap_data.set_index('Sample_ID', inplace=True)

    # Standardize across genes
    scaled_data = StandardScaler().fit_transform(heatmap_data)
    scaled_df = pd.DataFrame(scaled_data, index=heatmap_data.index, columns=heatmap_data.columns)

    # Optional grouping
    row_colors = None
    if metadata_df is not None and group_col and group_col in metadata_df.columns:
        group_series = metadata_df.set_index('Sample_ID')[group_col].reindex(scaled_df.index)
        lut = dict(zip(group_series.unique(), sns.color_palette("hsv", len(group_series.unique()))))
        row_colors = group_series.map(lut)

    # Plot heatmap
    sns.clustermap(
        scaled_df,
        row_colors=row_colors,
        cmap="vlag",
        xticklabels=True,
        yticklabels=True,
        figsize=(12, 10)
    )
    plt.title("Gene Expression Heatmap")
    plt.show()
