import cv2 as cv
import tifffile as tf
import utils
import json
import geopandas as gpd
from shapely.geometry import Polygon, box

def get_edges(polygon):
    """Extract the edges (sides) of a square polygon."""
    minx, miny, maxx, maxy = polygon.bounds
    return {
        'left': box(minx, miny, minx, maxy),
        'right': box(maxx, miny, maxx, maxy),
        'top': box(minx, maxy, maxx, maxy),
        'bottom': box(minx, miny, maxx, miny),
    }

def shrink_tile(tile, trim_amount, intersecting_sides, grid_bounds):
    """Shrink the tile by a certain number of pixels on intersecting sides, 
    but don't shrink sides that are along the boundary of the grid."""
    minx, miny, maxx, maxy = tile.bounds
    grid_minx, grid_miny, grid_maxx, grid_maxy = grid_bounds

    # Check if the tile is on the boundary of the grid
    if 'left' in intersecting_sides and minx != grid_minx:
        minx += trim_amount
    if 'right' in intersecting_sides and maxx != grid_maxx:
        maxx -= trim_amount
    if 'top' in intersecting_sides and maxy != grid_maxy:
        maxy -= trim_amount
    if 'bottom' in intersecting_sides and miny != grid_miny:
        miny += trim_amount

    return box(minx, miny, maxx, maxy)

def trim_intersecting_sides(gdf, trim_amount=50):
    """Reduce tile sizes where they intersect with adjacent tiles, but
    do not shrink the sides touching the grid boundary."""
    
    # Get the overall bounds of the entire grid
    grid_bounds = gdf.total_bounds
    
    trimmed_tiles = []

    for idx, tile in gdf.iterrows():
        intersecting_sides = []
        tile_edges = get_edges(tile.geometry)

        # Check for intersections with other tiles
        for other_idx, other_tile in gdf.iterrows():
            if idx != other_idx:  # Avoid checking the same tile
                other_tile_edges = get_edges(other_tile.geometry)
                
                # Check which sides are intersecting
                for side, edge in tile_edges.items():
                    if edge.intersects(other_tile.geometry):
                        intersecting_sides.append(side)

        # Shrink the tile based on intersecting sides, considering the grid bounds
        if intersecting_sides:
            trimmed_tile = shrink_tile(tile.geometry, trim_amount, intersecting_sides, grid_bounds)
            tile.geometry = trimmed_tile

        trimmed_tiles.append(tile)

    return gpd.GeoDataFrame(trimmed_tiles)


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

def tile_intervals(subset_multi_channel_image, tiles_dimension, overlap, amount_of_VMs, trim_amount):

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
    
    original_tiles_gdf = gpd.GeoDataFrame(geometry=tile_polygons)
    original_tiles_bounds = original_tiles_gdf['geometry'].bounds
    original_tiles_gdf['rearranged_bounds'] = original_tiles_bounds.apply(lambda row: [row.miny, row.maxy, row.minx, row.maxx], axis=1)

    trimmed_tiles_gdf = trim_intersecting_sides(gdf=original_tiles_gdf, trim_amount=trim_amount)
    trimmed_tiles_bounds = trimmed_tiles_gdf['geometry'].bounds
    trimmed_tiles_gdf['rearranged_bounds'] = trimmed_tiles_bounds.apply(lambda row: [row.miny, row.maxy, row.minx, row.maxx], axis=1)

    original_tiles_gdf.to_parquet('original_tile_polygons.parquet')
    trimmed_tiles_gdf.to_parquet('trimmed_tile_polygons.parquet')

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