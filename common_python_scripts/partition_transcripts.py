import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import argparse

def main(transcript_file, cell_polygon_file, transcript_chunk_size):

    def find_containing_polygon(transcript):
        point = transcript.geometry
        possible_matches_index = list(cell_polygons_sindex.query(point, predicate='intersects'))
        
        if len(possible_matches_index) == 0:
            return None
        
        return possible_matches_index[0]

    def process_chunk(transcript_chunk, cell_polygons_gdf, cell_polygons_sindex):
        if not transcript_chunk.empty:
            transcript_chunk['cell_index'] = transcript_chunk.apply(find_containing_polygon, axis=1)
        else:
            transcript_chunk['cell_index'] = None
        
        return transcript_chunk

    transcript_df = pd.read_csv(transcript_file)
    transcript_df['geometry'] = transcript_df.apply(lambda row: Point(row['global_x'], row['global_y']), axis=1)
    transcripts_gdf = gpd.GeoDataFrame(transcript_df, geometry='geometry')

    cell_polygons_gdf = gpd.read_parquet(cell_polygon_file)

    cell_polygons_gdf.reset_index(inplace=True)
    cell_polygons_gdf.drop(['index', 'shard', 'job', '0'], axis=1, inplace=True)
    cell_polygons_gdf.rename(columns={'level_0': 'cell_ids'}, inplace=True)

    cell_polygons_sindex = cell_polygons_gdf.sindex

    transcript_chunks_indices = np.array_split(transcripts_gdf.index.to_list(), np.ceil(len(transcripts_gdf) / transcript_chunk_size))

    partitioned_transcripts = gpd.GeoDataFrame()

    for chunk_index in transcript_chunks_indices:
        chunk_result = process_chunk(transcript_chunk = transcripts_gdf.loc[chunk_index], 
                                    cell_polygons_gdf = cell_polygons_gdf, 
                                    cell_polygons_sindex = cell_polygons_sindex)
        
        partitioned_transcripts = pd.concat([partitioned_transcripts, chunk_result], ignore_index=True)

    partitioned_transcripts = gpd.GeoDataFrame(partitioned_transcripts, geometry='geometry')

    partitioned_transcripts['cell_index'].fillna(-1, inplace=True)
    partitioned_transcripts = partitioned_transcripts.rename(columns={'Unnamed: 0': 'transcript_id'})
    partitioned_transcripts_cleaned = partitioned_transcripts.groupby(['gene', 'cell_index']).size().reset_index(name='count')

    cell_by_gene_matrix = partitioned_transcripts_cleaned.pivot_table(index='cell_index', columns='gene', values='count', fill_value=0)

    cell_by_gene_matrix.to_csv('cell_by_gene_matrix.csv')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='partitioning')
    parser.add_argument('--transcript_file')
    parser.add_argument('--cell_polygon_file')
    parser.add_argument('--transcript_chunk_size', type = int)  
    args = parser.parse_args()

    main(transcript_file = args.transcript_file,  
        cell_polygon_file = args.cell_polygon_file,
        transcript_chunk_size = args.transcript_chunk_size)