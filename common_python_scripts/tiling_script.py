import cv2 as cv
import tifffile as tf
import pandas as pd

def tiling_script(subset_multi_channel_image, listed_intervals, shard_index, out_path):

    for index, value in enumerate(listed_intervals[str(shard_index)]):
        y_min, y_max, x_min, x_max = [int(z) for z in value]

        meta = pd.DataFrame({"y_min": [y_min], "y_max": [y_max],
                                "x_min": [x_min],
                                "x_max": [x_max]})

        meta.to_csv(out_path + f"/tile_metadata_{shard_index}_{index}.csv")

        if len(subset_multi_channel_image.shape) == 2:
            current_tile = subset_multi_channel_image[y_min:y_max, x_min:x_max]
            cv.imwrite(out_path + f"/tiled_image_{shard_index}_{index}.tiff", current_tile)   

        elif len(subset_multi_channel_image.shape) > 2:
            current_tile = subset_multi_channel_image[:, y_min:y_max, x_min:x_max]
            tf.imwrite(out_path + f"/tiled_image_{shard_index}_{index}.tiff", current_tile, photometric='minisblack')