'''PCA & UMAP dimensionality reduction logic, returns clustering data'''
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
import umap

def plot_pca(expression_df, metadata_df=None, color_by=None):
    
    #Plots PCA using top 2 components from expression data. 
    #Optionally merges metadata to colour by a label

    #drop down columns
    numeric_data = expression_df.select_dtypes(include='number')

    #ensure rows are patients columns are genes
    pca =PCA(n_components=2)
    pca_result = pca.fit_transform(numeric_data)

    # Build PCA result DataFrame
    pca_df = pd.DataFrame(pca_result, columns=['PC1', 'PC2'])
    
    # Attach Sample
    if 'Sample' in expression_df.columns:
        pca_df['Sample'] = expression_df['Sample'].values
    else:
        print("Error: 'Sample' column not found in expression_df.")
        return

    #merge with metadata if provided
    if metadata_df is not None:
        merged_df = pd.merge(pca_df, metadata_df, on='Sample', how='left')
    else:
        merged_df = pca_df

    # Create a more selective hover template with only relevant information
    hover_template = '<b>Sample:</b> %{customdata[0]}<br>'
    hover_template += '<b>PC1:</b> %{x:.3f}<br>'
    hover_template += '<b>PC2:</b> %{y:.3f}<br>'
    
    # Add colouring information if available
    if color_by and color_by in merged_df.columns:
        hover_template += f'<b>{color_by}:</b> %{{customdata[1]}}<br>'
    
    hover_template += '<extra></extra>'
    
    fig = px.scatter(
        merged_df,
        x='PC1',
        y='PC2',
        color=color_by if color_by in merged_df.columns else None,
        hover_name='Sample',
        hover_data=[color_by] if color_by and color_by in merged_df.columns else None,
        title=f"PCA Analysis: Colored by {color_by}" if color_by else "PCA Analysis of Gene Expression Data"
    )

    # Calculate explained variance for better axis labels
    explained_variance = pca.explained_variance_ratio_
    pc1_var = explained_variance[0] * 100
    pc2_var = explained_variance[1] * 100
    
    # Update layout with proper axis labels and styling
    fig.update_layout(
        xaxis_title=f"PC1 ({pc1_var:.1f}% variance explained)",
        yaxis_title=f"PC2 ({pc2_var:.1f}% variance explained)",
        title={
            'text': f"PCA Analysis: Colored by {color_by}" if color_by else "PCA Analysis of Gene Expression Data",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        plot_bgcolor='white',
        width=800,
        height=600,
        font=dict(family="Arial, sans-serif")
    )

    fig.update_traces(marker=dict(size=8, opacity=0.8, line=dict(width=0.5, color='DarkSlateGrey')))
    
    # Save plot to HTML file
    plot_filename = f"pca_plot_{color_by if color_by else 'default'}.html"
    fig.write_html(plot_filename)
    print(f"PCA plot saved to '{plot_filename}'")
    
    # Show plot in browser (non-blocking)
    try:
        import subprocess
        subprocess.Popen(['open', plot_filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Plot opened in your browser.")
    except Exception as e:
        print(f"Could not open plot automatically. Please open '{plot_filename}' manually in your browser.")


def plot_umap(expression_df, metadata_df=None, color_by=None):
    #Drop non-numeric columns
    numeric_data = expression_df.select_dtypes(include='number')

    #  Check if 'Sample' is present
    if 'Sample' not in expression_df.columns:
        print("Error: 'Sample' column not found in expression_df.")
        return

    #run umap
    reducer = umap.UMAP(n_components=2, random_state=42)
    umap_result = reducer.fit_transform(numeric_data)

    #build umap result dataframe
    umap_df = pd.DataFrame(umap_result, columns=['UMAP1', 'UMAP2'])
    umap_df['Sample'] = expression_df['Sample'].values

    #merge metadata if provided
    if metadata_df is not None:
        merged_df = pd.merge(umap_df, metadata_df, on='Sample', how='left')
    else:
        merged_df = umap_df

    # Note: Using simpler hover approach with hover_name and hover_data
    
    #create plot
    fig = px.scatter(
        merged_df,
        x='UMAP1',
        y='UMAP2',
        color=color_by if color_by in merged_df.columns else None,
        hover_name='Sample',
        hover_data=[color_by] if color_by and color_by in merged_df.columns else None,
        title=f"UMAP Analysis: Colored by {color_by}" if color_by else "UMAP Analysis of Gene Expression Data"
    )

    # Update layout with proper axis labels and styling
    fig.update_layout(
        xaxis_title="UMAP1 (Dimension 1)",
        yaxis_title="UMAP2 (Dimension 2)",
        title={
            'text': f"UMAP Analysis: Colored by {color_by}" if color_by else "UMAP Analysis of Gene Expression Data",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            title_font=dict(size=14),
            tickfont=dict(size=12)
        ),
        plot_bgcolor='white',
        width=800,
        height=600,
        font=dict(family="Arial, sans-serif")
    )

    fig.update_traces(marker=dict(size=8, opacity=0.8, line=dict(width=0.5, color='DarkSlateGrey')))
    
    # Save plot to HTML file
    plot_filename = f"umap_plot_{color_by if color_by else 'default'}.html"
    fig.write_html(plot_filename)
    print(f"UMAP plot saved to '{plot_filename}'")
    
    # Show plot in browser (non-blocking)
    try:
        import subprocess
        subprocess.Popen(['open', plot_filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Plot opened in your browser.")
    except Exception as e:
        print(f"Could not open plot automatically. Please open '{plot_filename}' manually in your browser.")
