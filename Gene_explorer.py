'''Gene-wise expression summaries (boxplots), chromosomal location logic'''

import pandas as pd
import plotly.express as px


def explore_gene_expression(expression_df, metadata_df, gene_name, group_col = 'grade'):
    #plots the expression of a specific gene grouped by a metadata column (e.g. grade)

    if gene_name not in expression_df.columns:
        print(f"Gene '{gene_name}' not found in expression data.")
        return
    
    #merge expression and metadata if provided
    df = expression_df[['Sample_ID', gene_name]].copy()
    merged = pd.merge(df, metadata_df[['Sample_ID', group_col]], on='Sample_ID', how='inner')

    #boxplot of expression based on the grade
    fig = px.box(
        merged,
        x=group_col,
        y=gene_name,
        points="all",
        title=f"{gene_name} Expression by {group_col.capitalize()}",
        labels={group_col: group_col.capitalize(), gene_name: "Expression Level"},
    )
    fig.update_traces(marker=dict(size=8, opacity=0.8))
    fig.show(renderer="browser")

def map_gene_to_chromosome(gene_name, gene_location_file="gene_location.csv"):
    try:
        df = pd.read_csv(gene_location_file)
        gene_info = df[df['Gene'].str.upper() == gene_name.upper()]

        if not gene_info.empty:
            chromosome = gene_info.iloc[0]['Chromosome']
            print(f"Gene '{gene_name}' is located on chromosome {chromosome}.")

            fig = px.bar(
                x=gene_info['Chromosome'],
                y=[1],
                labels={"x": "Chromosome", "y": ""},
                title = f"{gene_name} Location on Chromosome {chromosome}",
            )
            fig.update_yaxes(visible=False)
            fig.show(renderer="browser")
        else:
            print(f"Gene '{gene_name}' not found in gene location data.")
    except FileNotFoundError:
        print(f"Gene location file not found: {gene_location_file}")
    except Exception as e:
        print(f"Error occurred while processing gene location data: {e}")
        
 

#for debugging: list the available genes
def list_available_genes(expression_df):
    genes =[col for col in expression_df.columns if col.lower() != 'sample_id']
    print(f"Available genes: {', '.join(genes)}")


