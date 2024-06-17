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

    def distribute_tasks(total_tasks, max_vms=25, max_tasks_per_vm=100, min_tasks_per_vm=1):
        if total_tasks <= max_tasks_per_vm:
            # If tasks are fewer than or equal to the max tasks per VM, use one VM
            return {0: total_tasks}

        # Calculate the required number of VMs
        required_vms = min((total_tasks + max_tasks_per_vm - 1) // max_tasks_per_vm, max_vms)
        
        # Distribute tasks across the required number of VMs
        tasks_per_vm = total_tasks // required_vms
        remainder_tasks = total_tasks % required_vms

        distribution = {}
        for vm in range(required_vms):
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
    
    distribution = distribute_tasks(len(tile_boundaries_list))
    
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
    parser.add_argument('--overlap', type = int)
    args = parser.parse_args()

    main(input_image = args.input_image,  
        tiles_dimension = args.tiles_dimension,
        overlap = args.overlap)
