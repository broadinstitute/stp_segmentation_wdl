import cv2 as cv
import numpy as np
import tifffile as tf
import math
import matplotlib.pyplot as plt
import pandas as pd
import utils
import os
import seaborn as sns
import utils
import argparse

def main(tif_image, detected_transcripts, transform_mat, interval,
             out_path, show):

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



    # for each tile coords, save the tile as well as the relevant transcripts
    # current tile boundaries - parse from string and make int
    interval_list = interval.split(",")
    y_min, y_max, x_min, x_max = [int(i) for i in interval_list]

    meta = pd.DataFrame({"y_min": [y_min],
                "y_max": [y_max],
                "x_min": [x_min],
                "x_max": [x_max]})

    meta.to_csv(out_path + "/tile_metadata.csv")
        
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
    cv.imwrite(out_path + "/tiled_image.tiff", current_tile)
    current_tile_transc.to_csv(out_path + "/tiled_detected_transcript.csv")



    # plot an overlay of the tiff and detected transcripts if show 
    if show:
        plt.figure()
        plt.imshow(current_tile, origin='lower')
        sns.scatterplot(data = current_tile_transc, x = "x_px", y = "y_px",
                        s = 0.5, alpha = 0.3 , color = "red")
        plt.savefig(out_path + "/tiled_overlay.png")
        plt.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Tile merfish')
    parser.add_argument('--tif_image')
    parser.add_argument('--detected_transcripts')
    parser.add_argument('--transform_mat')
    parser.add_argument('--interval')
    parser.add_argument('--out_path')
    parser.add_argument('--show', type = bool)
    args = parser.parse_args()

    main(tif_image = args.tif_image,  
        detected_transcripts = args.detected_transcripts,
        transform_mat = args.transform_mat,
        interval=args.interval,
        out_path = args.out_path,
        show = args.show)