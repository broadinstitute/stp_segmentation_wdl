import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
import numpy as np
import argparse
from shapely.affinity import affine_transform

def main(transcript_file, original_transcript_file, cell_polygon_file, transcript_chunk_size, technology, transform_file):

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

    if technology == 'MERSCOPE':
        x_col = 'global_x'
        y_col = 'global_y'    
        gene = 'gene'   
        transcript_id = 'Unnamed: 0'

    elif technology == 'XENIUM':
        x_col = 'x_location'
        y_col = 'y_location'  
        gene = 'feature_name'
        transcript_id = 'transcript_id'

    cell_polygons_gdf = gpd.read_parquet(cell_polygon_file)

    cell_polygons_gdf.reset_index(inplace=True)

    cell_polygons_gdf.rename(columns={'index': 'cell_index'}, inplace=True)
    cell_polygons_gdf.rename(columns={'geometry': 'geometry_image_space'}, inplace=True)

    cell_polygons_gdf['cell_index'] = cell_polygons_gdf['cell_index'].astype(str)

    cell_polygons_gdf.set_index('cell_index', inplace=True)

    cell_polygons_sindex = cell_polygons_gdf.sindex

    partitioned_transcripts = gpd.GeoDataFrame()

    for chunk in pd.read_csv(transcript_file, chunksize=transcript_chunk_size):

        chunk['geometry'] = chunk.apply(lambda row: Point(row[x_col], row[y_col]), axis=1)
        chunked_transcripts_gdf = gpd.GeoDataFrame(chunk, geometry='geometry')

        chunk_result = process_chunk(transcript_chunk = chunked_transcripts_gdf, 
                                    cell_polygons_gdf = cell_polygons_gdf, 
                                    cell_polygons_sindex = cell_polygons_sindex)

        partitioned_transcripts = pd.concat([partitioned_transcripts, chunk_result], ignore_index=True)

    partitioned_transcripts = gpd.GeoDataFrame(partitioned_transcripts, geometry='geometry')

    partitioned_transcripts['cell_index'].fillna(-1, inplace=True)
    partitioned_transcripts = partitioned_transcripts[partitioned_transcripts['cell_index'] != -1]
    partitioned_transcripts = partitioned_transcripts.rename(columns={transcript_id: 'transcript_index', gene: 'gene'})

    partitioned_transcripts['cell_index'] = partitioned_transcripts['cell_index'].astype(int)
    cell_polygons_gdf.index = cell_polygons_gdf.index.astype(int)
    cell_polygons_gdf = cell_polygons_gdf[cell_polygons_gdf.index.isin(partitioned_transcripts['cell_index'])]

    partitioned_transcripts_cleaned = partitioned_transcripts.groupby(['gene', 'cell_index']).size().reset_index(name='count')
    cell_by_gene_matrix = partitioned_transcripts_cleaned.pivot_table(index='cell_index', columns='gene', values='count', fill_value=0)
    
    cell_by_gene_matrix.to_csv('cell_by_gene_matrix.csv', index=True)
    cell_by_gene_matrix.to_parquet('cell_by_gene_matrix.parquet')

    partitioned_transcripts.drop(['cell_id'], axis=1, inplace=True)

    partitioned_transcripts.rename(columns={x_col: 'x_image_coords', y_col: 'y_image_coords'}, inplace=True)

    if original_transcript_file.endswith(".parquet"):
        original_transcripts = pd.read_parquet(original_transcript_file)
    else:
        original_transcripts = pd.read_csv(original_transcript_file)

    partitioned_transcripts[x_col] = original_transcripts[x_col]
    partitioned_transcripts[y_col] = original_transcripts[y_col]

    partitioned_transcripts.rename(columns={x_col: 'x', y_col: 'y'}, inplace=True)

    partitioned_transcripts.to_parquet("transcripts.parquet")

    transformation_matrix = pd.read_csv(transform_file).values[:3,:3]

    transformation_matrix_inverse = np.linalg.inv(transformation_matrix)

    cell_polygons_gdf['geometry'] = cell_polygons_gdf['geometry_image_space'].apply(lambda geom: affine_transform(geom, [transformation_matrix_inverse[0, 0], 
                                                                                           transformation_matrix_inverse[0, 1], 
                                                                                           transformation_matrix_inverse[1, 0], 
                                                                                           transformation_matrix_inverse[1, 1], 
                                                                                           transformation_matrix_inverse[0, 2], 
                                                                                           transformation_matrix_inverse[1, 2]]))

    cell_polygons_gdf['area'] = cell_polygons_gdf['geometry'].area
    cell_polygons_gdf['centroid'] = cell_polygons_gdf['geometry'].centroid
    cell_polygons_gdf[['area', 'centroid']].to_parquet("cell_metadata_micron_space.parquet")
    cell_polygons_gdf.to_parquet('cell_polygons.parquet')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='partitioning')
    parser.add_argument('--transcript_file')
    parser.add_argument('--original_transcript_file')
    parser.add_argument('--cell_polygon_file')
    parser.add_argument('--transcript_chunk_size', type = int)  
    parser.add_argument('--technology')  
    parser.add_argument('--transform_file')
    args = parser.parse_args()

    main(transcript_file = args.transcript_file, 
        original_transcript_file = args.original_transcript_file, 
        cell_polygon_file = args.cell_polygon_file,
        transcript_chunk_size = args.transcript_chunk_size,
        technology = args.technology,
        transform_file = args.transform_file)