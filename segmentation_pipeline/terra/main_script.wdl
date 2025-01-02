version 1.0

import "./modular_wdl_scripts/cellpose.wdl" as CELLPOSE
import "./modular_wdl_scripts/merge.wdl" as MERGE
import "./modular_wdl_scripts/partition_transcripts.wdl" as PARTITION
import "./modular_wdl_scripts/create_subset.wdl" as SUBSET
import "./modular_wdl_scripts/instanseg.wdl" as INSTANSEG

workflow MAIN_WORKFLOW {
    input {
        Float? tiles_dimension # tile width and height
        Float? overlap # overlap between tiles

        Int? diameter # cellpose: size of cell
        Float? flow_thresh # cellpose: parameter is the maximum allowed error of the flows for each mask. The default is flow_threshold=0.4. Increase this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, decrease this threshold if cellpose is returning too many ill-shaped ROIs.
        Float? cell_prob_thresh # cellpose: the default is cellprob_threshold=0.0. Decrease this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, increase this threshold if cellpose is returning too ROIs particularly from dim areas.
        File? pretrained_model # cellpose : if there is a pretrained cellpose2 model
        String? model_type # cellpose : if a default model is to be used, model_type='cyto' or model_type='nuclei'    
        
        Int? segment_channel # cellpose :  The first channel is the channel you want to segment. The second channel is an optional channel that is helpful in models trained with images with a nucleus channel. See more details in the models page.
        Int? optional_channel 
        Float amount_of_VMs 

        Int transcript_chunk_size 

        Array[Int]? subset_data_y_x_interval
        Float? image_pixel_size

        File? transform_file
        File detected_transcripts_file

        Array[File] image_paths_list  

        String technology # XENIUM or MERSCOPE
        String algorithm # CELLPOSE or INSTANSEG

        Int? transcript_plot_as_channel # 1 for yes, 0 for no
        Int? sigma
        Int? trim_amount
    }

    File dummy_pretrained_model = "gs://fc-42006ad5-3f3e-4396-94d8-ffa1e45e4a81/datasets/models/dummy_model"
    File dummy_pre_merged_cell_polygons = "gs://fc-42006ad5-3f3e-4396-94d8-ffa1e45e4a81/datasets/dummy_pre_merged_cell_polygons.parquet"

    if (algorithm == "INSTANSEG") {

        call SUBSET.create_subset as create_subset_IS {input: image_paths_list=image_paths_list,
                                        subset_data_y_x_interval=if defined(subset_data_y_x_interval) then select_first([subset_data_y_x_interval]) else [0],
                                        transform_file=if defined(transform_file) then select_first([transform_file]) else dummy_pretrained_model,
                                        detected_transcripts_file=detected_transcripts_file,
                                        technology=technology,
                                        tiles_dimension=if defined(tiles_dimension) then select_first([tiles_dimension]) else 0.0, 
                                        overlap=if defined(overlap) then select_first([overlap]) else 0.0, 
                                        amount_of_VMs=amount_of_VMs,
                                        transcript_plot_as_channel=if defined(transcript_plot_as_channel) then select_first([transcript_plot_as_channel]) else 0,
                                        sigma=if defined(sigma) then select_first([sigma]) else 0,
                                        trim_amount=if defined(trim_amount) then select_first([trim_amount]) else 0,
                                        algorithm=algorithm}
        
        call INSTANSEG.instanseg as instanseg {input: 
                image_paths_list=image_paths_list,
                image_pixel_size=if defined(image_pixel_size) then select_first([image_pixel_size]) else 1.0
        }

        call PARTITION.partitioning_transcript_cell_by_gene as partitioning_transcript_cell_by_gene_IS { 
            input: transcript_file=create_subset_IS.subset_coordinates, 
            cell_polygon_file=instanseg.processed_cell_polygons,
            pre_merged_cell_polygons=dummy_pre_merged_cell_polygons,
            transcript_chunk_size=transcript_chunk_size,
            technology=technology
        }
    }

    if (algorithm == "CELLPOSE") {

        call SUBSET.create_subset as create_subset {input: image_paths_list=image_paths_list,
                                        subset_data_y_x_interval=if defined(subset_data_y_x_interval) then select_first([subset_data_y_x_interval]) else [0],
                                        transform_file=if defined(transform_file) then select_first([transform_file]) else dummy_pretrained_model,
                                        detected_transcripts_file=detected_transcripts_file,
                                        technology=technology,
                                        tiles_dimension=if defined(tiles_dimension) then select_first([tiles_dimension]) else 0.0, 
                                        overlap=if defined(overlap) then select_first([overlap]) else 0.0, 
                                        amount_of_VMs=amount_of_VMs,
                                        transcript_plot_as_channel=if defined(transcript_plot_as_channel) then select_first([transcript_plot_as_channel]) else 0,
                                        sigma=if defined(sigma) then select_first([sigma]) else 0,
                                        trim_amount=if defined(trim_amount) then select_first([trim_amount]) else 0,
                                        algorithm=algorithm}

        
        File calling_intervals_file = if defined(create_subset.intervals) then select_first([create_subset.intervals]) else "gs://fc-42006ad5-3f3e-4396-94d8-ffa1e45e4a81/datasets/dummy_json.json"
        Map[String, Array[Array[Float]]] calling_intervals = read_json(calling_intervals_file)

        Int num_VMs_in_use = round(calling_intervals['number_of_VMs'][0][0])

        scatter (i in range(num_VMs_in_use)) {

            String index_for_intervals = "~{i}"

            call CELLPOSE.run_cellpose as run_cellpose {input: 
                            image_path=create_subset.tiled_image,
                            diameter= if defined(diameter) then select_first([diameter]) else 0, 
                            flow_thresh= if defined(flow_thresh) then select_first([flow_thresh]) else 0.0, 
                            cell_prob_thresh= if defined(cell_prob_thresh) then select_first([cell_prob_thresh]) else 0.0,
                            dummy_pretrained_model=dummy_pretrained_model,
                            pretrained_model= if defined(pretrained_model) then select_first([pretrained_model]) else dummy_pretrained_model,
                            model_type= if defined(model_type) then select_first([model_type]) else 'None',
                            segment_channel= if defined(segment_channel) then select_first([segment_channel]) else 0,
                            optional_channel = if defined(optional_channel) then select_first([optional_channel]) else 0,
                            shard_index=index_for_intervals
                            }
        }

        call MERGE.merge_segmentation_dfs as merge_segmentation_dfs { input: outlines=run_cellpose.outlines,
                    intervals=create_subset.intervals,
                    original_tile_polygons=create_subset.original_tile_polygons,
                    trimmed_tile_polygons=create_subset.trimmed_tile_polygons
        }

        call PARTITION.partitioning_transcript_cell_by_gene as partitioning_transcript_cell_by_gene_CP { 
            input: transcript_file=create_subset.subset_coordinates, 
            cell_polygon_file=merge_segmentation_dfs.processed_cell_polygons,
            pre_merged_cell_polygons= merge_segmentation_dfs.pre_merged_cell_polygons,
            transcript_chunk_size=transcript_chunk_size,
            technology=technology
        }
    }
    
}