"""
Author: 
Anna Yeaton (ayeaton@broadinstitute.org)
OPP, Broad Institute of MIT and Harvard
Functions:
    change_origin()
    clean_polygons()
    convert_to_px_coords()
    molecules_to_px()
    plot_polygons_spots()
    tile_coords()
"""

import numpy as np


def convert_to_px_polygons(conversion_mat, mat):
    """This function transforms coordinates from um to px given a conversion matrix for the polygons
    plus 6??????
    
    Parameters
    -----------
    conversion: conversion matrix from vizgen the file is called micron_to_mosaic_pixel_transform
    mat: pandas df of x and y coordinates 
   
    
    Returns
    -----------
    xcoord_transformed: X coordinate with new origin and scaled
    ycoord_transformed: Y coordinate with new origin and scaled
    """
        
    mat = np.array(mat)
    new_col = np.ones((mat.shape[0], 1))
    all_data = np.concatenate((mat, new_col), 1)
    # affine transform
    transformed_mat = (conversion_mat @ np.array(all_data.T)).T
    
    conversion_mat2 = [[1, 0, -56], [0, 1, -56], [0,0,1]]
                    
    transformed_mat2 = (conversion_mat2 @ np.array(transformed_mat.T)).T

    
    return [pd.DataFrame(transformed_mat2)[[0]], pd.DataFrame(transformed_mat2)[[1]]]

def convert_to_px(conversion, mat):
    """This function transforms coordinates from um to px given a conversion matrix 
    
    Parameters
    -----------
    conversion: conversion matrix from vizgen the file is called micron_to_mosaic_pixel_transform
    mat: pandas df of x and y coordinates 
   
    
    Returns
    -----------
    xcoord_transformed: X coordinate with new origin and scaled
    ycoord_transformed: Y coordinate with new origin and scaled
    """
        
    mat = np.array(mat)
    new_col = np.ones((mat.shape[0], 1))
    all_data = np.concatenate((mat, new_col), 1)
    
    # affine transform
    transformed_mat = (conversion @ np.array(all_data.T)).T
    
    return [transformed_mat[:,0], transformed_mat[:,1]]

def change_origin(min_x_um,
                  min_y_um,
                  xcoord,
                  ycoord):
    """This function transforms coordinates to have a given origin # to do - 
    just make it matrix multiplica
    
    Parameters
    -----------
    min_x: X coordinate origin
    min_y: Y coordinate of origin
    xcoord: X coordinate 
    ycoord: Y coordinate 
    
    Returns
    -----------
    xcoord_rel_min: X coordinate with new origin
    ycoord_rel_min: Y coordinate with new origin
    """
    
    # convert to relative coords
    xcoord_rel = xcoord - min_x_um 
    ycoord_rel = ycoord - min_y_um 
    
    return [xcoord_rel, ycoord_rel]
    
def convert_to_px_coords(microns_per_pixel, 
                         xcoord_um, 
                         ycoord_um):
    
    """Molecule output from Vizgen is in um. This function converts um to px.
    
    Parameters
    -----------
    microns_per_pixel: Conversion microns to pixel space
    xcoord_um: X coordinate in um
    ycoord_um: Y coordinate in um
    
    Returns
    -----------
    xcoord_px: X coordinate in px
    ycoord_px: Y coordinate in px
    """
    
    # convert to px space from um
    xcoord_px = int(xcoord_um / microns_per_pixel)
    ycoord_px = int(ycoord_um / microns_per_pixel)
    
    return [xcoord_px, ycoord_px]

def molecules_to_px(microns_per_pixel, 
                    bbox_min_x_um,
                    bbox_min_y_um,
                    xcoord_um,
                    ycoord_um):
    
    """Vizgen outputs coordinates in um and the origin is not on the bounding box/area acquired. 
    This function transforms the origin to on the bounding box/area acquired and transforms
    the coordinates to pixel space. 
    
    Parameters
    -----------
    microns_per_pixel: Conversion microns to pixel space
    bbox_min_x_um: X coordinate of bounding box origin in um
    bbox_min_y_um: Y coordinate of bounding box origin in um
    xcoord_um: X coordinate in um
    ycoord_um: Y coordinate in um
    
    Returns
    -----------
    xcoord_rel_min_px: X coordinate in px with origin on bounding box
    ycoord_rel_min_px: Y coordinate in px with origin on bounding box
    """
    
    # convert to relative coords
    xcoord_rel_min, ycoord_rel_min =  change_origin(bbox_min_x_um, 
                         bbox_min_y_um,                          
                         xcoord_um,
                         ycoord_um)
    
    # convert um to px
    xcoord_rel_min_px, ycoord_rel_min_px = convert_to_px_coords(microns_per_pixel, 
                         xcoord_rel_min, 
                         ycoord_rel_min)
    
    return [xcoord_rel_min_px, ycoord_rel_min_px]

def clean_polygons(conversion,
                   polygon):
    """ Polygon output from Baysor is currently not clean. 
    This function cleans up the polygon output. 
    
    Parameters
    -----------
    polygon: DataFrame from polygon = pd.read_csv("polygons.csv",header=None)
    microns_per_pixel: Conversion microns to pixel space
    bbox_min_x_um: X coordinate of bounding box in um
    bbox_min_y_um: Y coordinate of bounding box in um
    
    Returns
    -----------
    polygon_list_px_int_array: array of list of polygon coordinates

    """
    
    # coords from julia syntax to python
    polygon[0] = polygon[0].str.replace('; ', '],[')
    polygon[0] = polygon[0].str.replace(' ', ',')
    
    # to list (from string)
    polygon_list = [list(eval(i)) for i in polygon[0]]
    
    polygon_list_px = [convert_to_px_polygons(conversion, 
                         np.asarray(y)) for y in polygon_list]
    
    # convert polygon um coords to px coords relative to bounding box
    #polygon_list_px = [[molecules_to_px(microns_per_pixel, 
    #                         bbox_min_x_um, 
    #                         bbox_min_y_um, 
    #                         x[0], 
    #                         x[1]) for x in y] for y in polygon_list]
    # conver to int and array 
    #polygon_list_px_int = [[[np.uint32(x) for x in lst] for lst in zz] for zz in polygon_list_px]
    #polygon_list_px_int_array = [[np.array(lst, np.int32) for lst in polygon_list_px_int]]
    
    polygon_list_px_int = [list(zip(np.int32(zz[0][0]), np.int32(zz[1][1]))) for zz in polygon_list_px]
    polygon_list_px_int_array = [[np.array(lst, np.int32) for lst in polygon_list_px_int]]

    
    return polygon_list_px_int_array

def plot_polygons_spots(tif_image,
                        tif_image_poly,
                        poly_image, 
                        spots,
                        title,
                        spot_size = 0.5,
                        spot_alpha = 0.3):
    """
    
    """
    
    plt.rcParams['figure.figsize'] = [10, 20]

    fig = plt.figure(constrained_layout=False)
    gs = fig.add_gridspec(3, 2)

    ax1 = fig.add_subplot(gs[0, 0])
    ax1.imshow(tif_image,
               origin='lower',
               cmap=plt.get_cmap("Blues"))
    ax1.set_ylabel("")
    ax1.set_xlabel("")
    ax1.set_title("tif image")

    ax2 = fig.add_subplot(gs[1, 0])
    ax2.imshow(tif_image_poly,
               origin='lower',
              cmap=plt.get_cmap("Blues"))
    ax2.set_ylabel("")
    ax2.set_xlabel("")
    ax2.set_title("polygons on tif image")

    ax3 = fig.add_subplot(gs[2, 0])
    ax3.imshow(tif_image, origin='lower',
              cmap=plt.get_cmap("Blues"))
    sns.scatterplot(data = spots, x = "x_px", y = "y_px",
                    s = spot_size, alpha = spot_alpha , color = "red")
    ax3.set_ylabel("")
    ax3.set_xlabel("")
    ax3.set_title("MERFISH spots on tif image " + title)

    ax4 = fig.add_subplot(gs[0, 1])
    ax4.imshow(poly_image,
               origin='lower',
              cmap=plt.get_cmap("Blues"))
    ax4.set_ylabel("")
    ax4.set_xlabel("")
    ax4.set_title("polygons")

    ax5 = fig.add_subplot(gs[1, 1])
    ax5.imshow(tif_image_poly, origin='lower',
              cmap=plt.get_cmap("Blues"))
    sns.scatterplot(data = spots, x = "x_px", y = "y_px",
                    s = spot_size, alpha = spot_alpha, color = "red")
    ax5.set_ylabel("")
    ax5.set_xlabel("")
    ax5.set_title("polygons and MERFISH spots " + title)
    
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.imshow(tif_image_poly, origin='lower',
              cmap=plt.get_cmap("Blues"))
    sns.scatterplot(data = spots, x = "x_px", y = "y_px",
                    s = spot_size, alpha = spot_alpha, color = "red")
    ax6.set_ylabel("")
    ax6.set_xlabel("")
    ax6.set_title("polygons and MERFISH spots on tif image " + title)



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

            tile_boundaries_list.append(f"{y_min}, {y_max}, {x_min}, {x_max}")

            x_min += (tile_width - overlap)  # Move to the next tile with overlap

        y_min += (tile_height - overlap)  # Move to the next row of tiles with overlap
    
    return tile_boundaries_list
