version 1.0

import "./modular_wdl_scripts/test_tile.wdl" as TILE
import "./modular_wdl_scripts/test_transcripts_per_cell.wdl" as TRANSCRIPTS
import "./modular_wdl_scripts/test_cellpose.wdl" as CELLPOSE
import "./modular_wdl_scripts/test_deepcell.wdl" as DEEPCELL
import "./modular_wdl_scripts/test_baysor.wdl" as BAYSOR
import "./modular_wdl_scripts/test_merge.wdl" as MERGE

workflow MAIN_WORKFLOW {
    input {
        Int ntiles_width # number of tiles on X axis
        Int ntiles_height # number of tiles on Y axis
        Int min_width # minimum tile size x axis
        Int min_height # minimum tile size y axis

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

        Int size # baysor: scale, or radius of cell
        Float prior_confidence # baysor: The value 0.0 makes the algorithm ignore the prior, while the value 1.0 restricts the algorithm from contradicting the prior.

    }

    call TILE.get_tile_intervals as get_tile_intervals {input: image_path=image_path,
                                    detected_transcripts=detected_transcripts,
                                    transform=transform,
                                    ntiles_width=ntiles_width,
                                    ntiles_height=ntiles_height,
                                    min_width=min_width,
                                    min_height=min_height
                            }

    Array[String] calling_intervals = read_lines(get_tile_intervals.intervals)

    Int max_VMs = 25
    Int min_VM = 1
    Int intervals_per_VMs = 5

    Int num_VMs_in_use_unbounded = length(calling_intervals) / intervals_per_VMs
    Int num_VMs_in_use = if num_VMs_in_use_unbounded > max_VMs then max_VMs else if num_VMs_in_use_unbounded < min_VM then min_VM else num_VMs_in_use_unbounded

    scatter (i in range(num_VMs_in_use)) {

        Int start_index = i * intervals_per_VMs
        Int end_index = (i + 1) * intervals_per_VMs - 1

        scatter (j in range(start_index, end_index)) {
        inputsForVM = calling_intervals[j]
        }
    
        call TILE.get_tile as get_tile {input: image_path=image_path,
                                detected_transcripts=detected_transcripts,
                                transform=transform,
								interval=inputsForVM        }
        

        if (segmentation_algorithm == "CELLPOSE") {
          call CELLPOSE.run_cellpose_nuclear as run_cellpose_nuclear {input: 
                            image_path=get_tile.tiled_image,
                            diameter= if defined(diameter) then select_first([diameter]) else 0, 
                            flow_thresh= if defined(flow_thresh) then select_first([flow_thresh]) else 0.0, 
                            cell_prob_thresh= if defined(cell_prob_thresh) then select_first([cell_prob_thresh]) else 0.0,
                            model_type= if defined(model_type) then select_first([model_type]) else 'None', 
                            segment_channel= if defined(segment_channel) then select_first([segment_channel]) else 0
                            }
        }

        if (segmentation_algorithm == "DEEPCELL") {
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
        }
        call TRANSCRIPTS.get_transcripts_per_cell as get_transcripts_per_cell {input: 
                                mask=select_first([run_cellpose_nuclear.imageout, run_deepcell_nuclear.imageout]),
                                detected_transcripts=get_tile.tiled_detected_transcript, 
                                transform = transform
                                }

        call BAYSOR.run_baysor as run_baysor {input: detected_transcripts_cellID = get_transcripts_per_cell.detected_transcripts_cellID,
                            size=size,
                            prior_confidence=prior_confidence
                    }
    }

    call MERGE.merge_segmentation_dfs { input: segmentation=run_baysor.baysor_out,
        segmentation_stats=run_baysor.baysor_stat
    }

}