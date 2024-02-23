version 1.0

import "tile.wdl" as TILE
import "transcripts_per_cell.wdl" as TRANSCRIPTS
import "baysor.wdl" as BAYSOR
import "merge.wdl" as MERGE

workflow MAIN_WORKFLOW {
    input {
        Int ntiles_width # number of tiles on X axis
        Int ntiles_height # number of tiles on Y axis
        Int min_width # minimum tile size x axis
        Int min_height # minimum tile size y axis

        File image_path # path to DAPI image

        String segmentation_algorithm # type in all caps, either CELLPOSE or DEEPCELL 

        Float? image_mpp # deepcell: Microns per pixel for image 
        String? pad_mode # deepcell: The padding mode, one of "constant" or "reflect".
        Int? radius # deepcell: size of cell
        Float? maxima_threshold # deepcell: This controls what the model considers a unique cell. Lower values will result in more separate cells being predicted, whereas higher values will result in fewer cells.
        Float? interior_threshold # deepcell: This controls how conservative the model is in estimating what is a cell vs what is background. Lower values of interior_threshold will result in larger cells, whereas higher values will result in smaller smalls.
        Boolean? exclude_border # deepcell: default False
        Float? small_objects_threshold # deepcell: default 0

        Int? diameter # cellpose: size of cell
        Float? flow_thresh # cellpose: parameter is the maximum allowed error of the flows for each mask. The default is flow_threshold=0.4. Increase this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, decrease this threshold if cellpose is returning too many ill-shaped ROIs.
        Float? cell_prob_thresh # cellpose: the default is cellprob_threshold=0.0. Decrease this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, increase this threshold if cellpose is returning too ROIs particularly from dim areas.
        String? model_type # cellpose : model_type='cyto' or model_type='nuclei'
        Int? segment_channel # cellpose :  The first channel is the channel you want to segment. The second channel is an optional channel that is helpful in models trained with images with a nucleus channel. See more details in the models page.
        
        File detected_transcripts # path to the detected transcripts file
        File transform # path to micron to mosaic transform file 

        Int size # baysor: scale, or radius of cell
        Float prior_confidence # baysor: The value 0.0 makes the algorithm ignore the prior, while the value 1.0 restricts the algorithm from contradicting the prior.

    }


    call TILE.get_tile_intervals {input: image_path=image_path,
                                    detected_transcripts=detected_transcripts,
                                    transform=transform,
                                    ntiles_width=ntiles_width,
                                    ntiles_height=ntiles_height,
                                    min_width=min_width,
                                    min_height=min_height
                            }

    Array[String] calling_intervals = read_lines(TILE.get_tile_intervals.intervals)

    scatter(interval in calling_intervals) {

        call TILE.get_tile {input: image_path=image_path,
                                detected_transcripts=detected_transcripts,
                                transform=transform,
								interval=interval        }
        

        if (segmentation_algorithm == "CELLPOSE") {
          import "cellpose.wdl" as CELLPOSE
          call CELLPOSE.run_cellpose_nuclear {input: image_path=get_tile.tiled_image,
                                diameter=diameter, 
                                flow_thresh=flow_thresh, 
                                cell_prob_thresh=cell_prob_thresh,
                                model_type=model_type, 
                                segment_channel=segment_channel
                            }
        }

        if (segmentation_algorithm == "DEEPCELL") {
          import "deepcell.wdl" as DEEPCELL
          call DEEPCELL.run_deepcell_nuclear {input: image_path=get_tile.tiled_image,
                                    image_mpp=image_mpp, 
                                    pad_mode=pad_mode, 
                                    radius=radius, 
                                    maxima_threshold=maxima_threshold, 
                                    interior_threshold=interior_threshold,
                                    exclude_border=exclude_border, 
                                    small_objects_threshold=small_objects_threshold
                                    }
        }
        

        # make sure this can work with tiled images
        call TRANSCRIPTS.get_transcripts_per_cell {input: mask=run_cellpose_nuclear.imageout,
                                detected_transcripts=get_tile.tiled_detected_transcript, 
                                transform = transform
                                }
    
        call BAYSOR.run_baysor {input: detected_transcripts_cellID = get_transcripts_per_cell.detected_transcripts_cellID,
                            size=size,
                            prior_confidence=prior_confidence
                    }
    }
    call MERGE.merge_segmentation_dfs { input: segmentation=run_baysor.baysor_out,
        segmentation_stats=run_baysor.baysor_stat
    }

}