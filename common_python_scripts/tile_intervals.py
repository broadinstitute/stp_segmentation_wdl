import cv2 as cv
import tifffile as tf
import utils
import json
import geopandas as gpd

def distribute_tasks(total_tasks, max_vms):

        if max_vms >= 25:
            max_vms = 25
            
        tasks_per_vm = total_tasks // max_vms
        remainder_tasks = total_tasks % max_vms

        distribution = {}
        for vm in range(max_vms):
            if vm < remainder_tasks:
                distribution[vm] = tasks_per_vm + 1
            else:
                distribution[vm] = tasks_per_vm

        return distribution

def tile_intervals(subset_multi_channel_image, tiles_dimension, overlap, amount_of_VMs):

    if len(subset_multi_channel_image.shape) == 2:
        image_width = float(subset_multi_channel_image.shape[1])
        image_height = float(subset_multi_channel_image.shape[0])

    elif len(subset_multi_channel_image.shape) > 2:
        image_width = float(subset_multi_channel_image.shape[2])
        image_height = float(subset_multi_channel_image.shape[1])
    
    # given the number of tiles, figure out size of tiles
    tile_width = tiles_dimension
    tile_height = tiles_dimension
    
    tile_boundaries_list, tile_polygons = utils.tile_coords(image_width = image_width, image_height = image_height,
                    tile_width = tile_width, tile_height = tile_height, 
                    overlap = overlap)
    
    tile_gdf = gpd.GeoDataFrame(geometry=tile_polygons)
    tile_gdf.to_parquet('tile_polygons.parquet')

    distribution = distribute_tasks(total_tasks=len(tile_boundaries_list), max_vms=int(amount_of_VMs))
    
    listed_intervals = {}
    listed_intervals['number_of_VMs'] = [[len(distribution.keys())]]
    listed_intervals['number_of_tiles'] = [[len(tile_boundaries_list)]]

    jump = 0
    for vm_index, intervals_per_vm in distribution.items():
        listed_intervals[str(vm_index)] = tile_boundaries_list[jump:jump+intervals_per_vm]
        jump = jump + intervals_per_vm

    with open("intervals.json", "w") as json_file:
        json.dump(listed_intervals, json_file)

    return listed_intervals