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

def main(input_image, tiles_dimension, overlap, amount_of_VMs):

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
    
    distribution = distribute_tasks(total_tasks=len(tile_boundaries_list), max_vms=amount_of_VMs)
    
    listed_intervals = {}
    listed_intervals['number_of_VMs'] = [[len(distribution.keys())]]

    jump = 0
    for vm_index, intervals_per_vm in distribution.items():
        listed_intervals[str(vm_index)] = tile_boundaries_list[jump:jump+intervals_per_vm]
        jump = jump + intervals_per_vm

    #listed_intervals = {}
    #j = 0

    #for i in range(0, len(tile_boundaries_list), intervals_per_VMs):
    #    listed_intervals[int(j)] = tile_boundaries_list[i:i+intervals_per_VMs]
    #    j=j+1

    with open("intervals.json", "w") as json_file:
        json.dump(listed_intervals, json_file)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tile merfish')
    parser.add_argument('--input_image')
    parser.add_argument('--tiles_dimension', type = int),
    parser.add_argument('--overlap', type = int),
    parser.add_argument('--amount_of_VMs', type = int)
    args = parser.parse_args()

    main(input_image = args.input_image,  
        tiles_dimension = args.tiles_dimension,
        overlap = args.overlap,
        amount_of_VMs = args.amount_of_VMs)
