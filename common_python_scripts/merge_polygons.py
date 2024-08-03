import os
import argparse
import json
import pandas as pd
import geopandas as gpd
from google.cloud import storage
from shapely.geometry import Polygon, box
from shapely.affinity import translate
import matplotlib.pyplot as plt
import warnings

def main(cell_outlines, intervals):

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

    #del data_json['number_of_VMs']

    color_list = ['red', 'blue', 'green', 'yellow', 'purple', 'black', 'orange', 'grey', 'pink', 'brown']

    gdf = None

    gdf_tile = gpd.GeoDataFrame()

    color_index = 0

    print("intervals json")
    print(data_json)

    for inst_path in cell_outlines:
        
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

        # look up translation 
        #inst_coords = data_json[str(shard_index)][int(job_id)].split(', ')
        inst_coords = data_json[str(shard_index)][int(job_id)]
        
        y_min, y_max, x_min, x_max = [int(x) for x in inst_coords]
        
        geo_tile = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])
        
        tile_name = str(x_min) + '_' + str(x_max) + '_' + str(y_min) + '_' + str(y_max)
        
        gdf_tile.loc[tile_name, 'geometry'] = geo_tile

        # Translate all geometries at once
        inst_gdf['geometry'] = inst_gdf.geometry.apply(translate, xoff=x_min, yoff=y_min)
        
        inst_color = color_list[color_index%len(color_list)]
        
        inst_gdf['color'] = pd.Series(inst_color, index=inst_gdf.index)
        
        color_index = color_index + 1

        if gdf is None:
            gdf = inst_gdf
        else: 
            gdf = pd.concat([gdf, inst_gdf], axis=0)

    print("gdf", gdf)

    if data_json['number_of_tiles'][0][0] == 1:

        print("inside if statement, num of tiles check")

        #gdf.index = ['tmp'+ str(x) for x in gdf.index.tolist()]

        gdf.drop(['index', 'shard', 'job', 'color'], axis=1, inplace=True)

        gdf.index = [str(x) for x in gdf.index.tolist()]

        # confirm if the following is necessary
        gdf.columns = [str(col) for col in gdf.columns]

        print(gdf.columns)

        gdf.to_parquet('cell_polygons.parquet')
    # # trying to make unique indices
    # gdf.reset_index(inplace=True)

    else:

        print("inside else statement, num of tiles check")
        gdf_tile.reset_index(inplace=True)

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

        print("df_intersect before ioa calculation", df_intersect)
        # Calculating Overlap Area Parameters

        for inst_row in df_intersect.index.tolist():
            
            # look up pair of intersecting polygons
            id_1 = df_intersect.loc[inst_row, 'id_1']
            id_2 = df_intersect.loc[inst_row, 'id_2']

            cell_1 = all_cells[id_1]
            cell_2 = all_cells[id_2]

            poly_1 = gdf.loc[cell_1, 'geometry']

            area_1 = poly_1.area

            poly_2 = gdf.loc[cell_2, 'geometry']

            area_2 = poly_2.area
            
            area_intersection = poly_1.intersection(poly_2).area
            area_union = poly_1.union(poly_2).area
            
            if area_union <= 0:
                continue

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
                

        print("df_intersect after ioa calculation", df_intersect)
        # rank by easiest to resolve
        df_intersect.sort_values(by='ioa_small', ascending=False, inplace=True)    

        # initialize gdf_nc
        gdf_nc = gdf.loc[list_no_conflict_cells]
        gdf_nc.reset_index(inplace=True)
        gdf_nc.drop([0], axis=1, inplace=True)

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

            # elif poly intersects with one or more gdf_nc polygons
            
            elif len(possible_intersections) != 0:

                # Assumption: the polygon we are adding to gdf_nc should only ever have to be 
                # merged with one polygon from gdf_nc.
                
                max_ioa_merged = 0
                max_ioa_merged_index = 0
                
                for index in possible_intersections:

                    poly_intersect = gdf_nc.loc[index, 'geometry']

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
                    
                    poly_merged = poly_intersect.union(poly)
                    
                    # delete intersecting polygon in gdf_nc
                    
                    gdf_nc = gdf_nc.drop(max_ioa_merged_index)

                    # add polygon_merged to gdf_nc
                    
                    new_data = {'geometry': poly_merged}
                
                    # add poly to gdf_nc because there is no conflict  
                    new_row = gpd.GeoDataFrame([new_data])
                    gdf_nc = gpd.GeoDataFrame(pd.concat([gdf_nc, new_row], ignore_index=True))            
                # else 

                else:
            
                    # add poly to gdf_nc becuse there is a small conflict    
                    new_data = {'geometry': poly} 
                    new_row = gpd.GeoDataFrame([new_data])
                    gdf_nc = gpd.GeoDataFrame(pd.concat([gdf_nc, new_row], ignore_index=True))                      
        
            return gdf_nc


        def fix_invalid_geometries(gdf_nc):
            # Function to fix invalid geometries
            def fix_geometry(geom):
                if not geom.is_valid:
                    return geom.buffer(0)
                return geom
            
            gdf_nc['geometry'] = gdf_nc['geometry'].apply(fix_geometry)
            return gdf_nc

        gdf_nc = fix_invalid_geometries(gdf_nc)

        # loop through df_intersect
        for inst_row in df_intersect.index.tolist():
            
            inst_ioa_small = df_intersect.loc[inst_row, 'ioa_small']
            
            if inst_ioa_small < ioa_small_thresh :
                
                # do not merge conflicted cells and add both to gdf_nc
                
                gdf_nc = add_or_merge_into_gdf_nc(gdf_nc=gdf_nc, poly=poly_1, ioa_thresh=ioa_small_thresh)
                gdf_nc = add_or_merge_into_gdf_nc(gdf_nc=gdf_nc, poly=poly_2, ioa_thresh=ioa_small_thresh)
            
            elif inst_ioa_small >= ioa_small_thresh:
                
                # merge cells and add merged cell to gdf_nc
                
                id_1 = df_intersect.loc[inst_row, 'id_1']
                id_2 = df_intersect.loc[inst_row, 'id_2']
                
                poly_1 = gdf_.loc[id_1, 'geometry']
                poly_2 = gdf_.loc[id_2, 'geometry']

                poly_merged = poly_1.union(poly_2)
                
                gdf_nc = add_or_merge_into_gdf_nc(gdf_nc=gdf_nc, poly=poly_merged, ioa_thresh=ioa_small_thresh)
        
        #gdf_nc.index = ['tmp'+ str(x) for x in gdf_nc.index.tolist()]
        gdf_nc.index = [str(x) for x in gdf_nc.index.tolist()]

        gdf_nc.drop(['index', 'shard', 'job', 'color'], axis=1, inplace=True)
        # confirm if the following is necessary
        gdf_nc.columns = [str(col) for col in gdf_nc.columns]

        gdf_nc.to_parquet('cell_polygons.parquet')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='merging')
    parser.add_argument('--cell_outlines')
    parser.add_argument('--intervals')
    args = parser.parse_args()

    main(cell_outlines = args.cell_outlines,  
        intervals = args.intervals)
