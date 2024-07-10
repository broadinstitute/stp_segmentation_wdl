version 1.0

import "./modular_wdl_scripts/tile.wdl" as TILE
import "./modular_wdl_scripts/cellpose.wdl" as CELLPOSE
import "./modular_wdl_scripts/merge.wdl" as MERGE
import "./modular_wdl_scripts/partition_transcripts.wdl" as PARTITION
import "./modular_wdl_scripts/create_toy_data.wdl" as TOY

workflow MAIN_WORKFLOW {
    input {
        Int tiles_dimension # tile width and height
        Int overlap # overlap between tiles

        Int diameter # cellpose: size of cell
        Float flow_thresh # cellpose: parameter is the maximum allowed error of the flows for each mask. The default is flow_threshold=0.4. Increase this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, decrease this threshold if cellpose is returning too many ill-shaped ROIs.
        Float cell_prob_thresh # cellpose: the default is cellprob_threshold=0.0. Decrease this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, increase this threshold if cellpose is returning too ROIs particularly from dim areas.
        String model_type # cellpose : model_type='cyto' or model_type='nuclei'
        Int segment_channel # cellpose :  The first channel is the channel you want to segment. The second channel is an optional channel that is helpful in models trained with images with a nucleus channel. See more details in the models page.
        Int optional_channel 
        Int amount_of_VMs 

        Int transcript_chunk_size 

        Array[Int] toy_data_x_interval
        Array[Int] toy_data_y_interval
        File transform_file
        File detected_transcripts_file

        Array[File] image_paths_list  
    }
    
    call TOY.create_toy_data as create_toy_data {input: image_paths_list=image_paths_list,
                                    toy_data_x_interval=toy_data_x_interval,
                                    toy_data_y_interval=toy_data_y_interval,
                                    transform_file=transform_file,
                                    detected_transcripts_file=detected_transcripts_file}

    call TILE.get_tile_intervals as get_tile_intervals {input: image_path=create_toy_data.toy_multi_channel_image,
                                    tiles_dimension=tiles_dimension,
                                    overlap=overlap,
                                    amount_of_VMs=amount_of_VMs}

    Map[String, Array[Array[Int]]] calling_intervals = read_json(get_tile_intervals.intervals)
    
    # Int num_VMs_in_use = read_int(get_tile_intervals.num_VMs_in_use_file)

    Int num_VMs_in_use = calling_intervals['number_of_VMs'][0][0]
    
    scatter (i in range(num_VMs_in_use)) {

        String index_for_intervals = "~{i}"

        call TILE.get_tile as get_tile {input: image_path=create_toy_data.toy_multi_channel_image,
								intervals=get_tile_intervals.intervals,
                                shard_index=index_for_intervals}

        call CELLPOSE.run_cellpose_nuclear as run_cellpose_nuclear {input: 
                            image_path=get_tile.tiled_image,
                            diameter= diameter, 
                            flow_thresh= flow_thresh, 
                            cell_prob_thresh= cell_prob_thresh,
                            model_type= model_type, 
                            segment_channel= segment_channel,
                            optional_channel = optional_channel
        }
          
    }

    call MERGE.merge_segmentation_dfs as merge_segmentation_dfs { input: outlines=run_cellpose_nuclear.outlines,
                intervals=get_tile_intervals.intervals
    }

    call PARTITION.partitioning_transcript_cell_by_gene as partitioning_transcript_cell_by_gene { 
        input: transcript_file = create_toy_data.toy_coordinates, 
        cell_polygon_file = merge_segmentation_dfs.processed_cell_polygons,
        transcript_chunk_size = transcript_chunk_size
    }
    
}

