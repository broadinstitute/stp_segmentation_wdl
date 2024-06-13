version 1.0

import "./modular_wdl_scripts/test_tile.wdl" as TILE
import "./modular_wdl_scripts/test_transcripts_per_cell.wdl" as TRANSCRIPTS
import "./modular_wdl_scripts/test_cellpose.wdl" as CELLPOSE
import "./modular_wdl_scripts/test_deepcell.wdl" as DEEPCELL
import "./modular_wdl_scripts/test_baysor.wdl" as BAYSOR
import "./modular_wdl_scripts/test_merge.wdl" as MERGE

workflow MAIN_WORKFLOW {
    input {
        Int tiles_dimension # tile width and height
        Int overlap # overlap between tiles

        File image_path # path to DAPI image

        String segmentation_algorithm # type in all caps, either CELLPOSE or DEEPCELL 

        Int? diameter # cellpose: size of cell
        Float? flow_thresh # cellpose: parameter is the maximum allowed error of the flows for each mask. The default is flow_threshold=0.4. Increase this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, decrease this threshold if cellpose is returning too many ill-shaped ROIs.
        Float? cell_prob_thresh # cellpose: the default is cellprob_threshold=0.0. Decrease this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, increase this threshold if cellpose is returning too ROIs particularly from dim areas.
        String? model_type # cellpose : model_type='cyto' or model_type='nuclei'
        Int? segment_channel # cellpose :  The first channel is the channel you want to segment. The second channel is an optional channel that is helpful in models trained with images with a nucleus channel. See more details in the models page.

        Float? image_mpp # deepcell: Microns per pixel for image 
        String? pad_mode # deepcell: The padding mode, one of "constant" or "reflect".
        Int? radius # deepcell: size of cell
        Float? maxima_threshold # deepcell: This controls what the model considers a unique cell. Lower values will result in more separate cells being predicted, whereas higher values will result in fewer cells.
        Float? interior_threshold # deepcell: This controls how conservative the model is in estimating what is a cell vs what is background. Lower values of interior_threshold will result in larger cells, whereas higher values will result in smaller smalls.
        Boolean? exclude_border # deepcell: default False
        Float? small_objects_threshold # deepcell: default 0
        
        File detected_transcripts # path to the detected transcripts file
        File transform # path to micron to mosaic transform file 

        Int? size # baysor: scale, or radius of cell
        Float? prior_confidence # baysor: The value 0.0 makes the algorithm ignore the prior, while the value 1.0 restricts the algorithm from contradicting the prior.

    }

    call TILE.get_tile_intervals as get_tile_intervals {input: image_path=image_path,
                                    detected_transcripts=detected_transcripts,
                                    transform=transform,
                                    tiles_dimension=tiles_dimension,
                                    overlap=overlap
                            }

    Map[String, Array[String]] calling_intervals = read_json(get_tile_intervals.intervals)
    
    # Int num_VMs_in_use = read_int(get_tile_intervals.num_VMs_in_use_file)

    Int num_VMs_in_use = 6

    scatter (i in range(num_VMs_in_use)) {

        String index_for_intervals = "~{i}"

        call TILE.get_tile as get_tile {input: image_path=image_path,
                                detected_transcripts=detected_transcripts,
                                transform=transform,
								interval=calling_intervals[index_for_intervals],
                                shard_index=index_for_intervals}

        call containsSubstring as containsSubstring_for_cellpose {input:
                text = segmentation_algorithm,
                substring = "CELLPOSE"
        }

        if (containsSubstring_for_cellpose.result) {
        call CELLPOSE.run_cellpose_nuclear as run_cellpose_nuclear {input: 
                            image_path=get_tile.tiled_image,
                            diameter= if defined(diameter) then select_first([diameter]) else 0, 
                            flow_thresh= if defined(flow_thresh) then select_first([flow_thresh]) else 0.0, 
                            cell_prob_thresh= if defined(cell_prob_thresh) then select_first([cell_prob_thresh]) else 0.0,
                            model_type= if defined(model_type) then select_first([model_type]) else 'None', 
                            segment_channel= if defined(segment_channel) then select_first([segment_channel]) else 0
        }
          
        call containsSubstring as containsSubstring_for_baysor {input:
                text = segmentation_algorithm,
                substring = "BAYSOR"
        }

        if (containsSubstring_for_baysor.result) {
          
          call TRANSCRIPTS.get_transcripts_per_cell as get_transcripts_per_cell_cellpose {input: 
                                outlines=run_cellpose_nuclear.outlines,
                                detected_transcripts=get_tile.tiled_detected_transcript, 
                                transform = transform}

          call BAYSOR.run_baysor as run_baysor_cellpose {input: detected_transcripts_cellID_geo_csv = get_transcripts_per_cell_cellpose.detected_transcripts_cellID_geo_csv,
                            size= if defined(size) then select_first([size]) else 0,
                            prior_confidence= if defined(prior_confidence) then select_first([prior_confidence]) else 0.0
                            }
        }}

        if (segmentation_algorithm == "DEEPCELL+BAYSOR") {
          call DEEPCELL.run_deepcell_nuclear as run_deepcell_nuclear {input: 
                                image_path=get_tile.tiled_image,
                                image_mpp= if defined(image_mpp) then select_first([image_mpp]) else 0.0,
                                pad_mode= if defined(pad_mode) then select_first([pad_mode]) else 'None',
                                radius= if defined(radius) then select_first([radius]) else 0,
                                maxima_threshold= if defined(maxima_threshold) then select_first([maxima_threshold]) else 0.0,
                                interior_threshold= if defined(interior_threshold) then select_first([interior_threshold]) else 0.0,
                                exclude_border= if defined(exclude_border) then select_first([exclude_border]) else false,
                                small_objects_threshold= if defined(small_objects_threshold) then select_first([small_objects_threshold]) else 0.0
                                }

          call TRANSCRIPTS.get_transcripts_per_cell as get_transcripts_per_cell_deepcell {input: 
                                outlines=run_deepcell_nuclear.imageout,
                                detected_transcripts=get_tile.tiled_detected_transcript, 
                                transform = transform
                                }

          call BAYSOR.run_baysor as run_baysor_deepcell {input: detected_transcripts_cellID_geo_csv = get_transcripts_per_cell_deepcell.detected_transcripts_cellID_geo_csv,
                            size= if defined(size) then select_first([size]) else 0,
                            prior_confidence= if defined(prior_confidence) then select_first([prior_confidence]) else 0.0
        }}
    }

    call MERGE.merge_segmentation_dfs as merge_segmentation_dfs { input: outlines=run_cellpose_nuclear.outlines,
                intervals=get_tile_intervals.intervals
    }
}

task containsSubstring {
    input {
        String text
        String substring
    }

    command {
        if [[ "${text}" == *"${substring}"* ]]; then
            echo "true"
        else
            echo "false"
        fi
    }

    output {
        Boolean result = read_boolean(stdout())
    }

}