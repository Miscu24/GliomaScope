'''	Differential gene expression (e.g. DESeq2-style or log2FC + p-values)'''

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import plotly.express as px

def perform_differential_expression(expression_df, metadata_df, group_col='grade', group_1='2', group_2='3'):

    #performs differential expression between two groups (grade 2 and grade 3)
    #return. dataframe with log2 fold change. p-values and volcano plot

    #step1. merge metadata and expression data
    expr = expression_df.copy()
    merged = pd.merge(expr, metadata_df[['Sample_ID', group_col]], on='Sample_ID', how='inner')

    #step2 filter for the two groups of intrest 
    filtered = merged[merged[group_col].isin([group_1, group_2])]
    filtered = filtered.set_index('Sample_ID')

    #step 3 to fit into groups
    group1_df = filtered[filtered[group_col] == group_1].drop(columns=[group_col])
    group2_df = filtered[filtered[group_col] == group_2].drop(columns=[group_col])

    #step 4 to calculate log2FC
    log2fc = np.log2((group2_df.mean() + 1e-6) / (group1_df.mean() + 1e-6))

    # step 5 calculate the p-values using t-test
    p_values = []
    for gene in group1_df.columns:
        stat, p = ttest_ind(group1_df[gene], group2_df[gene], equal_var=False)
        p_values.append(p)

    # step 6 prepare the result dataframe
    result_df = pd.DataFrame({
        'Gene': group1_df.columns,
        'log2FC': log2fc.values,
        'p_value': p_values
    })
    result_df['-log10(p_value)'] = -np.log10(result_df['p_value'])

    # step 7 volcano plot
    fig = px.scatter(
        result_df,
        x='log2FC',
        y='-log10(p_value)',
        text='Gene',
        title=f"Differential Expression: {group_1} vs {group_2}",
        color = result_df['p_value'] < 0.05,
        labels={'color': 'Significant (p-value < 0.05)'}
    )

    fig.update_traces(marker=dict(size=8, opacity=0.8), textposition='top center')
    fig.show(renderer="browser")

    return result_df.sort_values('p_value')