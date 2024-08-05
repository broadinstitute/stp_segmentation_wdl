import numpy as np

def tile_coords(image_height, image_width,
                tile_height, tile_width, 
                overlap):

    """This function returns a list of tile coordinates from a larger image.
    
    Parameters
    -----------
    image_height: Height of original large image
    image_width: Width of original large image
    tile_height: Height of tile
    tile_width: Width of tile
    
    Returns
    -----------
    tile_boundaries_list: list of list containing min/max coordinates of each tile
    """
    
    tile_boundaries_list = []

    y_min = 0
    while y_min < image_height:
        y_max = min(y_min + tile_height, image_height)  # Adjust y_max if it exceeds image height

        x_min = 0
        while x_min < image_width:
            x_max = min(x_min + tile_width, image_width)  # Adjust x_max if it exceeds image width

            #tile_boundaries_list.append(y_min, y_max, x_min, x_max)

            tile_boundaries_list.append([y_min, y_max, x_min, x_max])

            x_min += (tile_width - overlap)  # Move to the next tile with overlap

        y_min += (tile_height - overlap)  # Move to the next row of tiles with overlap
    
    return tile_boundaries_list