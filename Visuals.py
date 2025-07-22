import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


def plot_pca(expression_df, metadata_df=None, colour_by=None, n_components=2):
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
    pca_df['Sample_ID'] = expr_numeric.index

    if metadata_df is not None and colour_by in metadata_df.columns:
        merged = pd.merge(pca_df, metadata_df, on='Sample_ID', how='left')
        colours = merged[colour_by]
    else:
        merged = pca_df
        colours = None

    # Plot PCA
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(
        merged['PC1'], merged['PC2'], 
        c=pd.factorize(colours)[0] if colours is not None else 'blue', 
        cmap='viridis', alpha=0.8
        )

    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.title(f"PCA of Expression Data" + (f" (Coloured by {colour_by})" if colours is not None else ""))
    if colours is not None:
        unique_labels = pd.unique(colours) 
        plt.legend(handles=scatter.legend_elements()[0], labels=unique_labels, title=colour_by, loc='best')
    plt.tight_layout()
    plt.show()  