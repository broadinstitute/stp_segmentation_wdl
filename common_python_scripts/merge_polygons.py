import os
import argparse
import json
import pandas as pd
import geopandas as gpd
from google.cloud import storage
from shapely.geometry import Polygon, box
from shapely.validation import make_valid
from shapely.affinity import translate
import matplotlib.pyplot as plt
import warnings


def main(cell_outlines, intervals, original_tile_polygons, trimmed_tile_polygons, algorithm, merge_approach='larger'):

    tolerance = 0.001
    cell_outlines = cell_outlines.split(",")

    def list_blobs_paths(bucket, prefix):
        """Returns a list of blob paths in the bucket that begin with the prefix."""
        storage_client = storage.Client()
        blobs = storage_client.list_blobs(bucket, prefix=prefix)
        blob_paths = [blob.name for blob in blobs]
        return blob_paths

    def string_to_polygon(coord_string):
        coords = coord_string.split(',')
        it = iter(map(int, coords))
        return Polygon([(x, y) for x, y in zip(it, it)])

    with open(intervals, 'r') as file:
        data_json = json.load(file)

    number_of_tiles = data_json['number_of_tiles'][0][0]

    del data_json['number_of_VMs']
    del data_json['number_of_tiles']

    trimmed_tile_gdf = gpd.read_parquet(trimmed_tile_polygons)
    original_tile_gdf = gpd.read_parquet(original_tile_polygons)

    def update_data_json_with_trimmed_bounds(trimmed_gdf, data_json):
        # Flatten the list of bounds in trimmed_gdf to match the order in data_json
        trimmed_bounds = [row['rearranged_bounds'] for idx, row in trimmed_gdf.iterrows()]

        trimmed_data_json = {}

        # Counter to track the current position in trimmed_bounds list
        bound_counter = 0

        # Iterate through each key and the list of bounds in data_json
        for key, original_bounds_list in data_json.items():
            # Determine how many tiles are stored in this key (length of bounds list)

            num_tiles_in_key = len(original_bounds_list)

            # Extract the corresponding number of trimmed bounds from trimmed_gdf
            trimmed_bounds_subset = trimmed_bounds[bound_counter:bound_counter + num_tiles_in_key]

            trimmed_data_json[key] = []
            # Replace the bounds in data_json with the trimmed bounds
            for i in range(num_tiles_in_key):
                trimmed_data_json[key].append(trimmed_bounds_subset[i])

            # Move the counter forward by the number of tiles processed
            bound_counter += num_tiles_in_key

        return trimmed_data_json

    trimmed_data_json = update_data_json_with_trimmed_bounds(trimmed_gdf=trimmed_tile_gdf, data_json=data_json)

    color_list = ['red', 'blue', 'green', 'yellow', 'purple', 'black', 'orange', 'grey', 'pink', 'brown']

    gdf = None

    color_index = 0

    columns_to_check = ['0', 0, 'index', 'point_within_trimmed_tile']

    for inst_path in cell_outlines:

        if algorithm == "Watershed":

            inst_filename = os.path.basename(inst_path)
            inst_gdf = gpd.read_parquet(inst_path)
            parts = inst_filename.split('_')
            shard_index = parts[2]
            job_id = parts[3].split('.')[0]
    
            shard_name = f'shard-{shard_index}'
            job_name = f'{shard_name}_job-{job_id}'
            inst_gdf.index = [f'{job_name}_{i}' for i in range(len(inst_gdf))]
    
            inst_gdf['shard'] = shard_name
            inst_gdf['job'] = job_name
            
        else:
            
            inst_filename = inst_path.split('/')[-1]
            shard_index = inst_filename.split('_')[2].split('_')[0]
            job_id = inst_filename.split('_')[3].split('_')[0]
    
            shard_name = 'shard-' + str(shard_index)
            tmp_job_name = 'job-' + job_id
            job_name = shard_name + '_' + tmp_job_name
    
            inst_df = pd.read_csv(inst_path, delimiter='\t', header=None)
    
            inst_df.index = [job_name + '_' + str(x) for x in inst_df.index.tolist()]
    
            # Apply the conversion to each cell in the DataFrame
            inst_df['geometry'] = inst_df[0].apply(string_to_polygon)
    
            inst_df['shard'] = pd.Series(shard_name, index=inst_df.index)
            inst_df['job'] = pd.Series(job_name, index=inst_df.index)
    
            # Create a GeoDataFrame
            inst_gdf = gpd.GeoDataFrame(inst_df, geometry='geometry')

        trimmed_inst_coords = trimmed_data_json[str(shard_index)][int(job_id)]

        original_inst_coords = data_json[str(shard_index)][int(job_id)]

        y_min, y_max, x_min, x_max = [int(x) for x in trimmed_inst_coords]
        trimmed_geo_tile = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])

        y_min, y_max, x_min, x_max = [int(x) for x in original_inst_coords]
        original_geo_tile = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])

        inst_gdf['geometry'] = inst_gdf.geometry.apply(translate, xoff=x_min, yoff=y_min)

        point_within_trimmed_tile = inst_gdf['geometry'].apply(lambda point: point.intersects(trimmed_geo_tile))

        inst_gdf['point_within_trimmed_tile'] = point_within_trimmed_tile

        inst_gdf = inst_gdf[inst_gdf['point_within_trimmed_tile']==True]

        inst_color = color_list[color_index%len(color_list)]

        inst_gdf['color'] = pd.Series(inst_color, index=inst_gdf.index)

        color_index = color_index + 1

        if gdf is None:
            gdf = inst_gdf
        else:
            gdf = pd.concat([gdf, inst_gdf], axis=0)

    if number_of_tiles == 1:

        gdf.index = [str(x) for x in gdf.index.tolist()]

        gdf.columns = [str(col) for col in gdf.columns]
        
        # Intersect with actual columns present in the GeoDataFrame
        columns_to_drop = [col for col in columns_to_check if col in gdf.columns]
        
        # Drop them safely
        gdf.drop(columns=columns_to_drop, axis=1, inplace=True)

        gdf.to_parquet('pre_merged_cell_polygons.parquet')

        gdf.reset_index(inplace=True)
        gdf.drop(['index', 'shard', 'job', 'color'], axis=1, inplace=True)

        gdf.to_parquet('cell_polygons.parquet')

    else:
        gdf_copy = gdf.copy()
        gdf_copy.index = [str(x) for x in gdf_copy.index.tolist()]
        gdf_copy.columns = [str(col) for col in gdf_copy.columns]
        
        columns_to_drop = [col for col in columns_to_check if col in gdf_copy.columns]
        gdf_copy.drop(columns=columns_to_drop, axis=1, inplace=True)
        
        gdf_copy.to_parquet('pre_merged_cell_polygons.parquet')

        all_cells = gdf.index.tolist()

        # find cell polygons that intersect from aggregate cell segmentation
        intersecting_pairs = gdf.sindex.query(gdf.geometry, predicate='intersects')

        df_intersect = pd.DataFrame(intersecting_pairs).T

        df_intersect.columns = ['id_1', 'id_2']

        df_intersect = df_intersect[df_intersect['id_1'] != df_intersect['id_2']]

        # Add a new column that contains a sorted tuple of the id columns
        df_intersect['sorted_id_pair'] = df_intersect.apply(lambda row: tuple(sorted([row['id_1'], row['id_2']])), axis=1)

        # Drop duplicate rows based on the sorted_id_pair column
        df_intersect = df_intersect.drop_duplicates(subset='sorted_id_pair')

        # Optional: Drop the sorted_id_pair column if it is no longer needed
        df_intersect = df_intersect.drop(columns=['sorted_id_pair'])

        df_intersect.reset_index(inplace=True)
        df_intersect.drop(['index'], inplace=True, axis=1)

        list_conflict_ids = sorted(list(set(df_intersect['id_1'].unique().tolist() + df_intersect['id_2'].unique().tolist())))
        list_conflict_cells = [all_cells[x] for x in list_conflict_ids]

        list_no_conflict_cells = sorted(list(set(all_cells).difference(set(list_conflict_cells))))

        if len(list_conflict_ids) == 0:

            gdf.index = [x for x in range(len(gdf))]
            
            columns_to_drop = [col for col in columns_to_check if col in gdf.columns]
            columns_to_drop = list(set(columns_to_drop + ['shard', 'job', 'color']))
            
            gdf.drop(columns=columns_to_drop, axis=1, inplace=True)

            gdf.columns = [str(col) for col in gdf.columns]

            gdf.to_parquet('cell_polygons.parquet')

            return None

        # Calculating Overlap Area Parameters

        for inst_row in df_intersect.index.tolist():

            # look up pair of intersecting polygons
            id_1 = df_intersect.loc[inst_row, 'id_1']
            id_2 = df_intersect.loc[inst_row, 'id_2']

            cell_1 = all_cells[id_1]
            cell_2 = all_cells[id_2]

            poly_1 = gdf.loc[cell_1, 'geometry']

            poly_2 = gdf.loc[cell_2, 'geometry']

            if isinstance(poly_1, pd.Series):
                poly_1 = poly_1.values[0]
            if isinstance(poly_2, pd.Series):
                poly_2 = poly_2.values[0]

            poly_1 = make_valid(poly_1).buffer(0)
            poly_2 = make_valid(poly_2).buffer(0)

            poly_1 = poly_1.simplify(tolerance)
            poly_2 = poly_2.simplify(tolerance)

            area_1 = poly_1.area
            area_2 = poly_2.area

            area_intersection = poly_1.intersection(poly_2).area
            area_union = poly_1.union(poly_2).area

            if area_union <= 0:
                iou = 0
            else:
                iou = area_intersection/area_union

            df_intersect.loc[inst_row, 'iou'] = iou
            df_intersect.loc[inst_row, 'area_1'] = area_1
            df_intersect.loc[inst_row, 'area_2'] = area_2

            if area_1 > 0 and area_2 > 0:
                ioa_1 = area_intersection/area_1
                ioa_2 = area_intersection/area_2

                if area_1 <= area_2:
                    ioa_small = ioa_1
                else:
                    ioa_small = ioa_2

                df_intersect.loc[inst_row, 'ioa_1'] = ioa_1
                df_intersect.loc[inst_row, 'ioa_2'] = ioa_2
                df_intersect.loc[inst_row, 'ioa_small'] = ioa_small

            else:
                if area_1 <= 0:
                    ioa_1 = 0
                    df_intersect.loc[inst_row, 'ioa_1'] = 0

                else:
                    ioa_1 = area_intersection/area_1
                    df_intersect.loc[inst_row, 'ioa_1'] = ioa_1

                if area_2 <= 0:
                    ioa_2 = 0
                    df_intersect.loc[inst_row, 'ioa_2'] = 0

                else:
                    ioa_2 = area_intersection/area_2
                    df_intersect.loc[inst_row, 'ioa_2'] = ioa_2

                if area_1 <= area_2:
                    ioa_small = ioa_1
                    df_intersect.loc[inst_row, 'ioa_small'] = ioa_small

                else:
                    ioa_small = ioa_2
                    df_intersect.loc[inst_row, 'ioa_small'] = ioa_small

        # rank by easiest to resolve
        df_intersect.sort_values(by='ioa_small', ascending=False, inplace=True)

        # initialize gdf_nc
        gdf_nc = gdf.loc[list_no_conflict_cells]
        gdf_nc.reset_index(inplace=True)

        columns_to_drop = [col for col in columns_to_check if col in gdf_nc.columns]
        gdf_nc.drop(columns=columns_to_drop, axis=1, inplace=True)

        gdf_ = gdf.reset_index()
        ioa_small_thresh = 0.5

        # Suppress FutureWarning
        warnings.simplefilter(action='ignore', category=FutureWarning)

        def add_or_merge_into_gdf_nc(gdf_nc, poly, ioa_thresh):

            """
            This function allows us to add a new polygon to gdf_nc
            gdf_nc contains the no conflict polygons. We define conflict to mean
            a non-trivial intersection between polygons with a ioa_small above
            our threshold.

            This function will check for conflicts before adding poly and
            merge if necessary
            """

            # check if poly intersects with any polygons in gdf_nc
            possible_intersections = gdf_nc.sindex.query(poly, predicate='intersects')

            # if no intersection then add to gdf_nc
            if len(possible_intersections) == 0:

                new_data = {
                    'geometry': poly
                }

                # add poly to gdf_nc because there is no conflict
                new_row = gpd.GeoDataFrame([new_data])
                gdf_nc = gpd.GeoDataFrame(pd.concat([gdf_nc, new_row], ignore_index=True))

            # else poly intersects with one or more gdf_nc polygons

            else:

                # Assumption: the polygon we are adding to gdf_nc should only ever have to be
                # merged with one polygon from gdf_nc.

                max_ioa_merged = 0
                max_ioa_merged_index = 0

                if not poly.is_valid:
                    poly = make_valid(poly)

                for index in possible_intersections:

                    poly_intersect = gdf_nc.loc[index, 'geometry']

                    if not poly_intersect.is_valid:
                        poly_intersect = make_valid(poly_intersect).buffer(0)
                        poly_intersect = poly_intersect.simplify(tolerance)

                    if min(poly.area, poly_intersect.area) > 0:
                        ioa_merged = poly_intersect.intersection(poly).area / min(poly.area, poly_intersect.area)
                    else:
                        ioa_merged = 0

                    # find the polygon with the highest intersection and calculate ioa_merge

                    if ioa_merged >= max_ioa_merged:
                        max_ioa_merged = ioa_merged
                        max_ioa_merged_index = index

                if max_ioa_merged >= ioa_small_thresh:

                    # If ioa_merge >= threshold, then merged with gdf_nc polygon

                    poly_intersect = gdf_nc.loc[max_ioa_merged_index, 'geometry']

                    # poly_merged = ...

                    poly_intersect = make_valid(poly_intersect).buffer(0)
                    poly_intersect = poly_intersect.simplify(tolerance)

                    if merge_approach == 'union':
                        poly_merged = poly_intersect.union(poly)

                    elif merge_approach == 'larger':
                        poly_merged = poly if poly.area > poly_intersect.area else poly_intersect

                    elif merge_approach == 'smaller':
                        poly_merged = poly_intersect if poly.area > poly_intersect.area else poly

                    elif merge_approach == 'intersection':
                        poly_merged = poly_intersect.intersection(poly)

                    # delete intersecting polygon in gdf_nc

                    gdf_nc = gdf_nc.drop(max_ioa_merged_index)

                    # add polygon_merged to gdf_nc

                    new_data = {'geometry': poly_merged}

                    # add poly to gdf_nc because there is no conflict
                    new_row = gpd.GeoDataFrame([new_data])
                    gdf_nc = gpd.GeoDataFrame(pd.concat([gdf_nc, new_row], ignore_index=True))

                else:

                    # add poly to gdf_nc becuse there is a small conflict
                    new_data = {'geometry': poly}
                    new_row = gpd.GeoDataFrame([new_data])
                    gdf_nc = gpd.GeoDataFrame(pd.concat([gdf_nc, new_row], ignore_index=True))

            return gdf_nc

        # loop through df_intersect
        for inst_row in df_intersect.index.tolist():

            inst_ioa_small = df_intersect.loc[inst_row, 'ioa_small']

            id_1 = df_intersect.loc[inst_row, 'id_1']
            id_2 = df_intersect.loc[inst_row, 'id_2']

            poly_1 = gdf_.loc[id_1, 'geometry']
            poly_2 = gdf_.loc[id_2, 'geometry']

            poly_1 = make_valid(poly_1).buffer(0)
            poly_1 = poly_1.simplify(tolerance)

            poly_2 = make_valid(poly_2).buffer(0)
            poly_2 = poly_2.simplify(tolerance)

            if inst_ioa_small < ioa_small_thresh :

                gdf_nc = add_or_merge_into_gdf_nc(gdf_nc=gdf_nc, poly=poly_1, ioa_thresh=ioa_small_thresh)
                gdf_nc = add_or_merge_into_gdf_nc(gdf_nc=gdf_nc, poly=poly_2, ioa_thresh=ioa_small_thresh)

            else:

                if merge_approach == 'union':
                    poly_merged = poly_1.union(poly_2)

                elif merge_approach == 'larger':
                    poly_merged = poly_1 if poly_1.area > poly_2.area else poly_2

                elif merge_approach == 'smaller':
                    poly_merged = poly_2 if poly_1.area > poly_2.area else poly_1

                elif merge_approach == 'intersection':
                    poly_merged = poly_1.intersection(poly_2)

                gdf_nc = add_or_merge_into_gdf_nc(gdf_nc=gdf_nc, poly=poly_merged, ioa_thresh=ioa_small_thresh)

        def get_largest_polygon(geometry):
            if geometry.geom_type == 'MultiPolygon':
                largest_polygon = max(geometry.geoms, key=lambda p: p.area)
                return largest_polygon
            else:
                return geometry

        gdf_nc['geometry'] = gdf_nc['geometry'].apply(get_largest_polygon)

        gdf_nc.index = [str(x) for x in gdf_nc.index.tolist()]

        columns_to_drop = [col for col in columns_to_check if col in gdf_nc.columns]
        columns_to_drop = list(set(columns_to_drop + ['shard', 'job', 'color']))

        gdf_nc.drop(columns=columns_to_drop, axis=1, inplace=True)

        gdf_nc.columns = [str(col) for col in gdf_nc.columns]

        gdf_nc.to_parquet('cell_polygons.parquet')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='merging')
    parser.add_argument('--cell_outlines')
    parser.add_argument('--intervals')
    parser.add_argument('--original_tile_polygons')
    parser.add_argument('--trimmed_tile_polygons')
    parser.add_argument('--algorithm')
    parser.add_argument('--merge_approach')
    args = parser.parse_args()

    main(cell_outlines = args.cell_outlines,
        intervals = args.intervals,
        original_tile_polygons = args.original_tile_polygons,
        trimmed_tile_polygons = args.trimmed_tile_polygons,
        algorithm = args.algorithm,
        merge_approach = args.merge_approach)
