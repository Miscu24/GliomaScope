import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


def plot_pca(expression_df, metadata_df=None, color_by=None, n_components=2):
    #Plots PCA from expression data. optionally uses colours by a metadata column 

    #Ensure expression data is numeric and indexed by sample ID
    expr = expression_df.copy()
    expr = expr.set_index(expr.columns[0]) #assumes first colums in sample ID
    expr_numeric = expr.select_dtypes(include='number')

    # debug line to check for missing values
    print(expr_numeric.isnull().sum().sum(), "missing values in expression data")

    pca = PCA(n_components=n_components)
    components = pca.fit_transform(expr_numeric)

    pca_df = pd.DataFrame(components, columns=[f'PC{i + 1}' for i in range(n_components)])
    pca_df['Sample'] = expr_numeric.index

    if metadata_df is not None and color_by in metadata_df.columns:
        merged = pd.merge(pca_df, metadata_df, on='Sample', how='left')
        colors = merged[color_by]
    else:
        merged = pca_df
        colors = None

        # Plot PCA
    plt.figure(figsize=(10, 8))
    
    print(f"[DEBUG] Colouring by: {color_by}")
    print(f"[DEBUG] Number of non-NaN color values: {pd.Series(colors).notna().sum()}")

    # Only use color mapping if valid
    if colors is not None and pd.Series(colors).notna().sum() > 0:
        encoded_colors = pd.factorize(colors)[0]
        scatter = plt.scatter(
            merged['PC1'], 
            merged['PC2'],
            c=encoded_colors, 
            cmap='viridis', 
            alpha=0.8
        )
        unique_labels = pd.unique(colors.dropna())
        plt.legend(
            handles=scatter.legend_elements()[0], 
            labels=unique_labels, 
            title=color_by, 
            loc='best'
        )
        plt.title(f"PCA of Expression Data (Colored by {color_by})")
    else:
        scatter = plt.scatter(
            merged['PC1'], 
            merged['PC2'], 
            color='blue', 
            alpha=0.8
        )
        plt.title("PCA of Expression Data")

    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.tight_layout()
    
    # Save plot to file instead of showing
    plot_filename = f"pca_visuals_{color_by if color_by else 'default'}.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"PCA plot saved to '{plot_filename}'")
    plt.close()  # Close the plot to free memory
