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

def main(input_image, detected_transcripts, transform_mat, intervals,
             out_path, show):

    # read in image file
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

    # for each tile coords, save the tile as well as the relevant transcripts
    # current tile boundaries - parse from string and make int
    
    result = list(ast.literal_eval(intervals))
    
    interval_range = 4
    j=0
    for i in range(0, len(result), interval_range):
	
        range_ = result[i:i+interval_range]
        y_min, y_max, x_min, x_max = [int(z) for z in range_]

        meta = pd.DataFrame({"y_min": [y_min], "y_max": [y_max],
                                "x_min": [x_min],
                                "x_max": [x_max]})

        meta.to_csv(out_path + f"/tile_metadata_{j}.csv")

                        # for each tile position, get the image 
        current_tile = image[y_min:y_max, x_min:x_max]

                        # get the spots within 
        current_tile_transc = detected_transcripts_df.loc[(detected_transcripts_df['x_px'] < x_max) \
                                                                        & (detected_transcripts_df['x_px'] > x_min)]

        current_tile_transc = current_tile_transc.loc[(current_tile_transc['y_px'] < y_max) \
                                                                        & (current_tile_transc['y_px'] > y_min)]

                        # re-center the coordinates
        current_tile_transc["x_px"] = [i - x_min for i in current_tile_transc["x_px"]]
        current_tile_transc["y_px"] = [i -  y_min for i in current_tile_transc["y_px"]]

                        # save the image and save the csv
        cv.imwrite(out_path + f"/tiled_image_{j}.tiff", current_tile)
        current_tile_transc.to_csv(out_path + f"/tiled_detected_transcript_{j}.csv")

                        # plot an overlay of the tiff and detected transcripts if show 
        if show:
            plt.figure()
            plt.imshow(current_tile, origin='lower')
            sns.scatterplot(data = current_tile_transc, x = "x_px", y = "y_px",
                                            s = 0.5, alpha = 0.3 , color = "red")
            plt.savefig(out_path + f"/tiled_overlay_{j}.png")
            plt.close()
        
        j=j+1


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tile merfish')
    parser.add_argument('--input_image')
    parser.add_argument('--detected_transcripts')
    parser.add_argument('--transform')
    parser.add_argument('--interval')
    parser.add_argument('--out_path')
    parser.add_argument('--show', type = bool)
    args = parser.parse_args()

    main(input_image = args.input_image,  
        detected_transcripts = args.detected_transcripts,
        transform_mat = args.transform,
        intervals=args.interval,
        out_path = args.out_path,
        show = args.show)
