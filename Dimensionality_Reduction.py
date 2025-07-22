'''PCA & UMAP dimensionality reduction logic, returns clustering data'''
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
import umap

def plot_pca(expression_df, metadata_df=None, colour_by=None):
    
    #Plots PCA using top 2 components from expression data. 
    #Optionally merges metadata to color to colour by a label

    #drop down columns
    numeric_data = expression_df.select_dtypes(include='number')

    #ensure rows are patients columns are genes
    pca =PCA(n_components=2)
    pca_result = pca.fit_transform(numeric_data)

    # Build PCA result DataFrame
    pca_df = pd.DataFrame(pca_result, columns=['PC1', 'PC2'])
    
    # Attach Sample_ID
    if 'Sample_ID' in expression_df.columns:
        pca_df['Sample_ID'] = expression_df['Sample_ID'].values
    else:
        print("Error: 'Sample_ID' column not found in expression_df.")
        return

    #merge with metadata if provided
    if metadata_df is not None:
        merged_df = pd.merge(pca_df, metadata_df, on='Sample_ID', how='left')
    else:
        merged_df = pca_df

    hover_data = {col: True for col in merged_df.columns if col not in ['PC1', 'PC2']}

    fig = px.scatter(
        merged_df,
        x='PC1',
        y='PC2',
        color = colour_by if colour_by in merged_df.columns else None,
        hover_name='Sample_ID',
        hover_data=hover_data,
        text='Sample_ID', 
        title=f"PCA Coloured by {colour_by}" if colour_by else "PCA of Expression Data"
)

    fig.update_traces(marker=dict(size=8, opacity=0.8), textposition='top center')
    fig.show(renderer="browser")


def plot_umap(expression_df, metadata_df=None, colour_by=None):
    #Drop non-numeric columns
    numeric_data = expression_df.select_dtypes(include='number')

    #run umap
    reducer = umap.UMAP(n_components=2, random_state=42)
    umap_result = reducer.fit_transform(numeric_data)

    #build umap result dataframe
    umap_df = pd.DataFrame(umap_result, columns=['UMAP1', 'UMAP2'])
    umap_df['Sample_ID'] = expression_df['Sample_ID'].values

    #merge metadata if provided
    if metadata_df is not None:
        merged_df = pd.merge(umap_df, metadata_df, on='Sample_ID', how='left')
    else:
        merged_df = umap_df

    #prepare hover data
    hover_data = {col: True for col in merged_df.columns if col not in ['UMAP1', 'UMAP2']}

    #create plot
    fig = px.scatter(
        merged_df,
        x='UMAP1',
        y='UMAP2',
        color=colour_by if colour_by in merged_df.columns else None,
        hover_name='Sample_ID',
        hover_data=hover_data,
        text='Sample_ID', 
        title=f"UMAP Coloured by {colour_by}" if colour_by else "UMAP of Expression Data"
    )

    fig.update_traces(marker=dict(size=8, opacity=0.8), textposition='top center')
    fig.show(renderer="browser")
    print("UMAP plot saved to your browser.")
