import pandas as pd 
import argparse
import string

def main(segmentation_paths, segmentation_cell_stats_paths):
    
    segmentation_paths = segmentation_paths.split(",")
    segmentation_cell_stats_paths = segmentation_cell_stats_paths.split(",")

    st = string.ascii_lowercase
    ascii_string= [one+two for one in st for two in st] # 676


    segmentation_df_list = list()
    for idx, i in enumerate(segmentation_paths):
       segmentation_df = pd.read_csv(i)
       if segmentation_df.shape[1] > 4:
           segmentation_df["cell"] = ascii_string[idx] + segmentation_df['cell'].astype(str)
           segmentation_df["cluster"] = ascii_string[idx] + segmentation_df['cluster'].astype(str)
           segmentation_df_list.append(segmentation_df)

    segmentation_df_all = pd.concat(segmentation_df_list)

    segmentation_df_all_noise = segmentation_df_all[~segmentation_df_all["is_noise"]]
    segmentation_counts = pd.crosstab(segmentation_df_all_noise.cell, segmentation_df_all_noise.gene_reserved)

    segmentation_cell_stats_df_list = list()
    for idx, i in enumerate(segmentation_cell_stats_paths):
       segmentation_stats_df = pd.read_csv(i)
       if segmentation_stats_df.shape[1] > 4:
           segmentation_stats_df["cell"] = ascii_string[idx] + segmentation_stats_df['cell'].astype(str)
           segmentation_cell_stats_df_list.append(segmentation_stats_df)

    segmentation_cell_stats_df_all = pd.concat(segmentation_cell_stats_df_list)

    segmentation_counts.to_csv("merged_segmentation_counts.csv")
    segmentation_df_all.to_csv("merged_segmentation.csv")
    segmentation_cell_stats_df_all.to_csv("merged_segmentation_stats.csv")



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='merge segmentation_outs')
    parser.add_argument('--segmentation_paths')
    parser.add_argument('--segmentation_cell_stats_paths')
    args = parser.parse_args()

main(segmentation_paths = args.segmentation_paths,
    segmentation_cell_stats_paths = args.segmentation_cell_stats_paths)
