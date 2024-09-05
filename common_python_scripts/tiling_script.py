import cv2 as cv
import tifffile as tf
import pandas as pd

def tiling_script(subset_multi_channel_image, listed_intervals, shard_index, out_path):

    # read in image file
    #if subset_multi_channel_image.lower().endswith(('.tif', '.tiff')):
    #    image = tf.imread(subset_multi_channel_image)
    #elif subset_multi_channel_image.lower().endswith(('.jpg', '.jpeg')):
    #    image = cv.imread(subset_multi_channel_image)
    #else:
    #    print("Unsupported image format. Please provide a TIFF (.tif/.tiff) or JPEG (.jpg/.jpeg) image.") 
    
    #result = list(ast.literal_eval(intervals))
    #with open(intervals, 'r') as file:
    #    data_json = json.load(file)
        
    #interval_range = 4
    #j=0
    # del data_json['number_of_VMs']

    for index, value in enumerate(listed_intervals[str(shard_index)]):
        #for i in range(0, len(result), interval_range):
    
        #range_ = result[i:i+interval_range]
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