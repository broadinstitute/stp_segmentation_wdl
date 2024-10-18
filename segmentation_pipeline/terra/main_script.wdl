version 1.0

import "./modular_wdl_scripts/cellpose.wdl" as CELLPOSE
import "./modular_wdl_scripts/merge.wdl" as MERGE
import "./modular_wdl_scripts/partition_transcripts.wdl" as PARTITION
import "./modular_wdl_scripts/create_subset.wdl" as SUBSET

workflow MAIN_WORKFLOW {
    input {
        Float tiles_dimension # tile width and height
        Float overlap # overlap between tiles

        Int diameter # cellpose: size of cell
        Float flow_thresh # cellpose: parameter is the maximum allowed error of the flows for each mask. The default is flow_threshold=0.4. Increase this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, decrease this threshold if cellpose is returning too many ill-shaped ROIs.
        Float cell_prob_thresh # cellpose: the default is cellprob_threshold=0.0. Decrease this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, increase this threshold if cellpose is returning too ROIs particularly from dim areas.
        
        File? pretrained_model # cellpose : if there is a pretrained cellpose2 model
        String? model_type # cellpose : if a default model is to be used, model_type='cyto' or model_type='nuclei'    
        File dummy_pretrained_model = "gs://fc-42006ad5-3f3e-4396-94d8-ffa1e45e4a81/datasets/models/dummy_model"
        
        Int segment_channel # cellpose :  The first channel is the channel you want to segment. The second channel is an optional channel that is helpful in models trained with images with a nucleus channel. See more details in the models page.
        Int optional_channel 
        Float amount_of_VMs 

        Int transcript_chunk_size 

        Array[Int] subset_data_y_x_interval
        File transform_file
        File detected_transcripts_file

        Array[File] image_paths_list  

        String technology # XENIUM or MERSCOPE

        Int transcript_plot_as_channel # 1 for yes, 0 for no
        Int sigma
        Int trim_amount
    }

    call SUBSET.create_subset as create_subset {input: image_paths_list=image_paths_list,
                                    subset_data_y_x_interval=subset_data_y_x_interval,
                                    transform_file=transform_file,
                                    detected_transcripts_file=detected_transcripts_file,
                                    technology=technology,
                                    tiles_dimension=tiles_dimension, 
                                    overlap=overlap, 
                                    amount_of_VMs=amount_of_VMs,
                                    transcript_plot_as_channel=transcript_plot_as_channel,
                                    sigma=sigma,
                                    trim_amount=trim_amount}

    Map[String, Array[Array[Float]]] calling_intervals = read_json(create_subset.intervals)
    Int num_VMs_in_use = round(calling_intervals['number_of_VMs'][0][0])
    
    scatter (i in range(num_VMs_in_use)) {

        String index_for_intervals = "~{i}"

        call CELLPOSE.run_cellpose as run_cellpose {input: 
                        image_path=create_subset.tiled_image,
                        diameter= diameter, 
                        flow_thresh= flow_thresh, 
                        cell_prob_thresh= cell_prob_thresh,
                        dummy_pretrained_model=dummy_pretrained_model,
                        pretrained_model= if defined(pretrained_model) then select_first([pretrained_model]) else dummy_pretrained_model,
                        model_type= if defined(model_type) then select_first([model_type]) else 'None',
                        segment_channel= segment_channel,
                        optional_channel = optional_channel,
                        shard_index=index_for_intervals
                        }
    }

    call MERGE.merge_segmentation_dfs as merge_segmentation_dfs { input: outlines=run_cellpose.outlines,
                intervals=create_subset.intervals,
                original_tile_polygons=create_subset.original_tile_polygons,
                trimmed_tile_polygons=create_subset.trimmed_tile_polygons
    }

    call PARTITION.partitioning_transcript_cell_by_gene as partitioning_transcript_cell_by_gene { 
        input: transcript_file = create_subset.subset_coordinates, 
        cell_polygon_file = merge_segmentation_dfs.processed_cell_polygons,
        pre_merged_cell_polygons = merge_segmentation_dfs.pre_merged_cell_polygons,
        transcript_chunk_size = transcript_chunk_size,
        technology = technology
    }
    
}