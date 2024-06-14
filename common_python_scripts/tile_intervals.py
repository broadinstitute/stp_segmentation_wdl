import cv2 as cv
import numpy as np
import tifffile as tf
import math
import os
import ast
import utils
import argparse
import csv
import json
import pandas as pd

def main(input_image, tiles_dimension, overlap):

    # read in tif/jpeg file
    if input_image.lower().endswith(('.tif', '.tiff')):
        image = tf.imread(input_image)
    elif input_image.lower().endswith(('.jpg', '.jpeg')):
        image = cv.imread(input_image)
    else:
        print("Unsupported image format. Please provide a TIFF (.tif/.tiff) or JPEG (.jpg/.jpeg) image.")
    
    image_width = image.shape[1]
    image_height = image.shape[0]
    
    # given the number of tiles, figure out size of tiles
    tile_width = tiles_dimension
    tile_height = tiles_dimension
    
    tile_boundaries_list = utils.tile_coords(image_width = image_width, image_height = image_height,
                    tile_width = tile_width, tile_height = tile_height, 
                    overlap = overlap)
    
    max_VMs = 25
    min_VM = 1
    intervals_per_VMs = 6

    num_VMs_in_use_unbounded = len(tile_boundaries_list) / intervals_per_VMs
    num_VMs_in_use = int(max_VMs if num_VMs_in_use_unbounded > max_VMs else (min_VM if num_VMs_in_use_unbounded < min_VM else num_VMs_in_use_unbounded))

    listed_intervals = {}

    j = 0
    for i in range(0, len(tile_boundaries_list), intervals_per_VMs):
        listed_intervals[int(j)] = tile_boundaries_list[i:i+intervals_per_VMs]
        j=j+1

    with open("data.json", "w") as json_file:
        json.dump(listed_intervals, json_file)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tile merfish')
    parser.add_argument('--input_image')
    parser.add_argument('--tiles_dimension', type = int),
    parser.add_argument('--overlap', type = int)
    args = parser.parse_args()

    main(input_image = args.input_image,  
        tiles_dimension = args.tiles_dimension,
        overlap = args.overlap)
