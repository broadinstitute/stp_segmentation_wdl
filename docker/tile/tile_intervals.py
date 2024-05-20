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

def main(input_image, detected_transcripts, transform_mat,
             tiles_dimension, overlap, out_path):

    # read in tif/jpeg file
    if input_image.lower().endswith(('.tif', '.tiff')):
        image = tf.imread(input_image)
    elif input_image.lower().endswith(('.jpg', '.jpeg')):
        image = cv.imread(input_image)
    else:
        print("Unsupported image format. Please provide a TIFF (.tif/.tiff) or JPEG (.jpg/.jpeg) image.")
    
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

    image_width = image.shape[1]
    image_height = image.shape[0]
    
    # given the number of tiles, figure out size of tiles
    tile_width = tiles_dimension
    tile_height = tiles_dimension
    
    tile_boundaries_list = utils.tile_coords(image_width = image_width, image_height = image_height,
                    tile_width = tile_width, tile_height = tile_height, 
                    overlap = overlap)
        
    #with open(out_path + "/intervals.csv", "w", newline="") as f:
    #    writer = csv.writer(f)
    #    header = ['y_min', 'y_max', 'x_min', 'x_max']  # Adjust column names as needed
    #   writer.writerow(header)
    #    writer.writerows(tile_boundaries_list)
    
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

    with open(out_path + "/data.json", "w") as json_file:
        json.dump(listed_intervals, json_file)
        
    #listed_intervals = []
    #for i in range(0, len(tile_boundaries_list), intervals_per_VMs):
    #    listed_intervals.append(tile_boundaries_list[i:i+intervals_per_VMs])

    #with open(out_path + "/intervals.txt", "w", newline="") as f:
    #    writer = csv.writer(f)
    #    writer.writerows(listed_intervals)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tile merfish')
    parser.add_argument('--input_image')
    parser.add_argument('--detected_transcripts')
    parser.add_argument('--transform')
    parser.add_argument('--tiles_dimension', type = int),
    parser.add_argument('--overlap', type = int)
    parser.add_argument('--out_path') 
    args = parser.parse_args()

    main(input_image = args.input_image,  
        detected_transcripts = args.detected_transcripts,
        transform_mat = args.transform,
        tiles_dimension = args.tiles_dimension,
        overlap = args.overlap,
        out_path = args.out_path)
