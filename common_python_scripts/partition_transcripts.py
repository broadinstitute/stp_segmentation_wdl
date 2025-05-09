import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
import numpy as np
import argparse
import json
from shapely.affinity import affine_transform

def main(transcript_file, cell_polygon_file, transcript_chunk_size, technology, transform_file, algorithm, dataset_name, pre_merged_cell_polygons=None):

    def find_containing_polygon(transcript):
        point = transcript.geometry
        possible_matches_index = list(cell_polygons_sindex.query(point, predicate='intersects'))

        if len(possible_matches_index) == 0:
            return None

        return cell_polygons_gdf.iloc[possible_matches_index[0]].name

    def process_chunk(transcript_chunk, cell_polygons_gdf, cell_polygons_sindex):
        if not transcript_chunk.empty:
            transcript_chunk['cell_index'] = transcript_chunk.apply(find_containing_polygon, axis=1)
        else:
            transcript_chunk['cell_index'] = 'UNASSIGNED'

        return transcript_chunk

    def apply_affine_transform(x, y, transformation_matrix_inverse):
        coords = np.array([x, y, 1])

        transformed_coords = np.dot(transformation_matrix_inverse, coords)

        return transformed_coords[0], transformed_coords[1]

    if technology == 'MERSCOPE':
        x_col = 'global_x'
        y_col = 'global_y'
        gene = 'gene'
        transcript_id = 'Unnamed: 0'

    elif technology == 'Xenium':
        x_col = 'x_location'
        y_col = 'y_location'
        gene = 'feature_name'
        transcript_id = 'transcript_id'

    cell_polygons_gdf = gpd.read_parquet(cell_polygon_file)

    cell_polygons_gdf.reset_index(inplace=True)

    cell_polygons_gdf.rename(columns={'index': 'cell_index'}, inplace=True)
    cell_polygons_gdf.rename(columns={'geometry': 'geometry_image_space'}, inplace=True)
    cell_polygons_gdf.set_geometry("geometry_image_space", inplace=True)

    cell_polygons_gdf['cell_index'] = cell_polygons_gdf['cell_index'].astype(str).apply(lambda x: 'c-' + x)

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

    partitioned_transcripts['cell_index'].fillna("UNASSIGNED", inplace=True)
    partitioned_transcripts = partitioned_transcripts.rename(columns={transcript_id: 'transcript_index', gene: 'gene'})

    partitioned_transcripts_cleaned = partitioned_transcripts.groupby(['gene', 'cell_index']).size().reset_index(name='count')
    cell_by_gene_matrix = partitioned_transcripts_cleaned.pivot_table(index='cell_index', columns='gene', values='count', fill_value=0)

    cell_by_gene_matrix = cell_by_gene_matrix.drop(index="UNASSIGNED", errors='ignore')

    cell_by_gene_matrix.to_csv('cell_by_gene_matrix.csv', index=True)
    cell_by_gene_matrix.to_parquet('cell_by_gene_matrix.parquet')

    partitioned_transcripts.drop(['cell_id'], axis=1, inplace=True)

    partitioned_transcripts.rename(columns={x_col: 'x_image_coords', y_col: 'y_image_coords'}, inplace=True)

    transformation_matrix = pd.read_csv(transform_file, sep=' ', header=None).values[:3,:3]

    transformation_matrix_inverse = np.linalg.inv(transformation_matrix)

    partitioned_transcripts['x'], partitioned_transcripts['y'] = zip(*partitioned_transcripts.apply(lambda row: apply_affine_transform(row['x_image_coords'],
                                                                                                    row['y_image_coords'],
                                                                                                    transformation_matrix_inverse), axis=1))

    partitioned_transcripts.rename(columns={'geometry': 'geometry_image_space'}, inplace=True)
    partitioned_transcripts['geometry'] = partitioned_transcripts.apply(lambda row: Point(row['x'], row['y']), axis=1)

    partitioned_transcripts.to_parquet("transcripts.parquet")

    cell_polygons_gdf['geometry'] = cell_polygons_gdf['geometry_image_space'].apply(lambda geom: affine_transform(geom, [transformation_matrix_inverse[0, 0],
                                                                                           transformation_matrix_inverse[0, 1],
                                                                                           transformation_matrix_inverse[1, 0],
                                                                                           transformation_matrix_inverse[1, 1],
                                                                                           transformation_matrix_inverse[0, 2],
                                                                                           transformation_matrix_inverse[1, 2]]))

    cell_polygons_gdf['area'] = cell_polygons_gdf['geometry'].area
    cell_polygons_gdf = cell_polygons_gdf[cell_polygons_gdf['area'] > 0]

    cell_polygons_gdf['centroid'] = cell_polygons_gdf['geometry'].centroid
    cell_polygons_gdf['technology'] = technology

    cell_polygons_gdf[['area', 'centroid']].to_parquet("cell_metadata_micron_space.parquet")
    cell_polygons_gdf.set_geometry("geometry", inplace=True)
    cell_polygons_gdf.drop(['area', 'centroid'], axis=1, inplace=True)

    cell_polygons_gdf.to_parquet('cell_polygons.parquet')

    pre_merged_cell_polygons_gdf = gpd.read_parquet(pre_merged_cell_polygons)
    pre_merged_cell_polygons_gdf.rename(columns={'geometry': 'geometry_image_space'}, inplace=True)
    pre_merged_cell_polygons_gdf.set_geometry("geometry_image_space", inplace=True)

    pre_merged_cell_polygons_gdf['geometry'] = pre_merged_cell_polygons_gdf['geometry_image_space'].apply(lambda geom: affine_transform(geom, [transformation_matrix_inverse[0, 0],
                                                                                           transformation_matrix_inverse[0, 1],
                                                                                           transformation_matrix_inverse[1, 0],
                                                                                           transformation_matrix_inverse[1, 1],
                                                                                           transformation_matrix_inverse[0, 2],
                                                                                           transformation_matrix_inverse[1, 2]]))

    pre_merged_cell_polygons_gdf['area'] = pre_merged_cell_polygons_gdf['geometry'].area
    pre_merged_cell_polygons_gdf['centroid'] = pre_merged_cell_polygons_gdf['geometry'].centroid

    pre_merged_cell_polygons_gdf.drop(['shard', "job", "color"], axis=1, inplace=True)

    pre_merged_cell_polygons_gdf.to_parquet('pre_merged_cell_polygons.parquet')

    segmentation_parameters = {}
    segmentation_parameters['technology'] = 'custom'
    segmentation_parameters['segmentation_approach'] = algorithm
    segmentation_parameters['dataset_name'] = dataset_name

    with open("segmentation_parameters.json", "w") as json_file:
        json.dump(segmentation_parameters, json_file, indent=4)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='partitioning')
    parser.add_argument('--transcript_file')
    parser.add_argument('--cell_polygon_file')
    parser.add_argument('--transcript_chunk_size', type = int)
    parser.add_argument('--technology')
    parser.add_argument('--transform_file')
    parser.add_argument('--pre_merged_cell_polygons')
    parser.add_argument('--algorithm')
    parser.add_argument('--dataset_name')
    args = parser.parse_args()

    main(transcript_file = args.transcript_file,
        cell_polygon_file = args.cell_polygon_file,
        transcript_chunk_size = args.transcript_chunk_size,
        technology = args.technology,
        transform_file = args.transform_file,
        pre_merged_cell_polygons=args.pre_merged_cell_polygons,
        algorithm=args.algorithm,
        dataset_name=args.dataset_name)