import cv2 as cv
import numpy as np
import tifffile as tf
import math
import os
import utils
import argparse
import csv
import pandas as pd

def main(tif_image, detected_transcripts, transform_mat,
             ntiles_width, ntiles_height, min_width, min_height, out_path):

    # read in tif file
    image = tf.imread(tif_image)
    # read in detected transcripts
    detected_transcripts_df = pd.read_csv(detected_transcripts)
    # micron to px transform
    transform = np.array(pd.read_csv(transform_mat, 
                        sep = " ", 
                        header = None))

    transformed_px = utils.convert_to_px(transform, 
                        detected_transcripts_df[["global_x", "global_y"]])

    detected_transcripts_df["x_px"]  = transformed_px[0]
    detected_transcripts_df["y_px"] = transformed_px[1]


    # get shape of original tif file
    image_width = image.shape[1]
    image_height = image.shape[0]

    # given the number of tiles, figure out size of tiles
    tile_width = int(np.ceil(image_width / ntiles_width))
    tile_height = int(np.ceil(image_height / ntiles_height))

    # given the tiles needed and tile size, figure out size of the remaining border
    border_width = tile_width - (ntiles_width * tile_width - image_width)
    border_height = tile_height - (ntiles_height * tile_height - image_height)
    
    if border_height == 0: border_height =  tile_height
    if border_width == 0: border_width =  tile_width

    if min_width >= image_width: min_width =  image_width
    if min_height >= image_height: min_height =  image_height

    # if the border is too small, change the tile size and number 
    while border_width < min_width:
        ntiles_width = ntiles_width - 1
        tile_width = int(np.ceil(image_width / ntiles_width))
        border_width = tile_width - (ntiles_width * tile_width - image_width)

    while border_height < min_height:
        ntiles_height = ntiles_height - 1
        tile_height = int(np.ceil(image_height / ntiles_height))
        border_height = tile_height - (ntiles_height * tile_height - image_height)

    # get the min/max boundaries of each tile
    tile_boundaries_list = utils.tile_coords(image_width = image_width, image_height = image_height,
                    tile_width = tile_width, tile_height = tile_height, 
                    rem_width = border_width, rem_height = border_height)


    with open(out_path + "/intervals.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(tile_boundaries_list)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tile merfish')
    parser.add_argument('--tif_image')
    parser.add_argument('--detected_transcripts')
    parser.add_argument('--transform_mat')
    parser.add_argument('--ntiles_width', type = int)
    parser.add_argument('--ntiles_height', type = int)
    parser.add_argument('--min_width', type = int)
    parser.add_argument('--min_height', type = int)   
    parser.add_argument('--out_path') 
    args = parser.parse_args()

    main(tif_image = args.tif_image,  
        detected_transcripts = args.detected_transcripts,
        transform_mat = args.transform_mat,
        ntiles_width = args.ntiles_width,
        ntiles_height = args.ntiles_height,
        min_width = args.min_width,
        min_height = args.min_height,
        out_path = args.out_path)