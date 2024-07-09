import cv2 as cv
import numpy as np
import tifffile as tf
import math
import matplotlib.pyplot as plt
import pandas as pd
import utils
import os
import seaborn as sns
import ast
import utils
import argparse
import json

def main(input_image, intervals, out_path, shard_index):

    # read in image file
    if input_image.lower().endswith(('.tif', '.tiff')):
        image = tf.imread(input_image)
    elif input_image.lower().endswith(('.jpg', '.jpeg')):
        image = cv.imread(input_image)
    else:
        print("Unsupported image format. Please provide a TIFF (.tif/.tiff) or JPEG (.jpg/.jpeg) image.") 
    
    #result = list(ast.literal_eval(intervals))
    with open(intervals, 'r') as file:
        data_json = json.load(file)
        
    #interval_range = 4
    #j=0
    # del data_json['number_of_VMs']

    for index, value in enumerate(data_json[shard_index]):
        #for i in range(0, len(result), interval_range):
    
        #range_ = result[i:i+interval_range]
        y_min, y_max, x_min, x_max = [int(z) for z in value]

        meta = pd.DataFrame({"y_min": [y_min], "y_max": [y_max],
                                "x_min": [x_min],
                                "x_max": [x_max]})

        meta.to_csv(out_path + f"/tile_metadata_{shard_index}_{index}.csv")

        if len(image.shape) == 2:
            print("in first if")
            current_tile = image[y_min:y_max, x_min:x_max]
            cv.imwrite(out_path + f"/tiled_image_{shard_index}_{index}.tiff", current_tile)   

        elif len(image.shape) == 3:
            print("in second if")
            current_tile = image[:, y_min:y_max, x_min:x_max]
            tf.imwrite(out_path + f"/tiled_image_{shard_index}_{index}.tiff", current_tile, photometric='minisblack')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tile merfish')
    parser.add_argument('--input_image')
    parser.add_argument('--intervals')
    parser.add_argument('--out_path')
    parser.add_argument('--shard_index')
    args = parser.parse_args()

    main(input_image = args.input_image,  
        intervals=args.intervals,
        out_path = args.out_path,
        shard_index = args.shard_index)
