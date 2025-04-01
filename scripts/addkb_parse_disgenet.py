# This script parses DisGeNET gene-disease relationship data to extract relationships specific to HIV and substance use disorders.

import pandas as pd
from pathlib import Path

# read the files downloaded from the disgenet website - all files are stored in the OneDrive folder
disgenet_df = pd.read_csv("Path to file disease_mappings_to_attributes.tsv from disgenet", sep="\t", header=0)
disgenet_do_df = pd.read_csv("Path to file disease_mappings.tsv from disgenet", sep="\t", header=0)

# keywords used to filter the data - suggested by literature review and domain experts
keyword_list = pd.read_csv("/Users/ghosha/Documents/VSCode Projects/AddictionKB/scripts/All_Keywords.csv")

# Create an empty list to store DataFrames
dfs_to_concat = []

for keyword in keyword_list['Keywords']:
    print(keyword)
    # convert the keyword to a string
    keyword = str(keyword)
    df_keyword = disgenet_df.loc[disgenet_df["name"].str.contains(keyword, case=False), :].copy() # added the : afterwards
    df_keyword['keyword'] = keyword
    dfs_to_concat.append(df_keyword)

# Concatenate the DataFrames
disgenet_opioid_all_df = pd.concat(dfs_to_concat)
print("Size of disgenet_opioid_all_df: ", disgenet_opioid_all_df.shape)

# Get unique disease IDs
cuis = disgenet_opioid_all_df['diseaseId'].unique()

# Filter the disease ontology DataFrame
disgenet_opioid_all_do_df = disgenet_do_df.loc[disgenet_do_df.diseaseId.isin(cuis), :].copy()

# Group keywords by disease ID and join them
keyword_groups = disgenet_opioid_all_df.groupby('diseaseId')['keyword'].apply(lambda x: ', '.join(x)).reset_index()
disgenet_opioid_all_do_df = disgenet_opioid_all_do_df.merge(keyword_groups, on='diseaseId', how='left')

# print the shape of the final DataFrame
print("Size of disgenet_opioid_all_do_df: ", disgenet_opioid_all_do_df.shape)


# Convert the DataFrames to CSV files
disgenet_opioid_all_df.to_csv("/Path to store filtered data/disease_mappings_to_attributes_addkb_all.tsv", sep="\t", header=True, index=False)
disgenet_opioid_all_do_df.to_csv("Path to store filtered data/disease_mappings_addkb_all.tsv", sep="\t", header=True, index=False)