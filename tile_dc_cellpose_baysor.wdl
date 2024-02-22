version 1.0
workflow tile_cellpose_baysor_merge_Workflow {
    input {
        Int ntiles_width # number of tiles on X axis
        Int ntiles_height # number of tiles on Y axis
        Int min_width # minimum tile size x axis
        Int min_height # minimum tile size y axis
        File image_path # path to DAPI image
        Int diameter # cellpose: size of cell
        Float flow_thresh # cellpose: parameter is the maximum allowed error of the flows for each mask. The default is flow_threshold=0.4. Increase this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, decrease this threshold if cellpose is returning too many ill-shaped ROIs.
        Float cell_prob_thresh # cellpose: the default is cellprob_threshold=0.0. Decrease this threshold if cellpose is not returning as many ROIs as you’d expect. Similarly, increase this threshold if cellpose is returning too ROIs particularly from dim areas.
        String model_type # cellpose : model_type='cyto' or model_type='nuclei'
        Int segment_channel # cellpose :  The first channel is the channel you want to segment. The second channel is an optional channel that is helpful in models trained with images with a nucleus channel. See more details in the models page.
        File detected_transcripts # path to the detected transcripts file
        File transform # path to micron to mosaic transform file 
        Int size # baysor: scale, or radius of cell
        Float prior_confidence # baysor: The value 0.0 makes the algorithm ignore the prior, while the value 1.0 restricts the algorithm from contradicting the prior.
    }


    call get_tile_intervals {input: image_path=image_path,
                                    detected_transcripts=detected_transcripts,
                                    transform=transform,
                                    ntiles_width=ntiles_width,
                                    ntiles_height=ntiles_height,
                                    min_width=min_width,
                                    min_height=min_height
                            }

    Array[String] calling_intervals = read_lines(get_tile_intervals.intervals)

    scatter(interval in calling_intervals) {

        call get_tile {input:   image_path=image_path,
                                detected_transcripts=detected_transcripts,
                                transform=transform,
								interval=interval        }
        
        
        call run_cellpose_nuclear {input: image_path=get_tile.tiled_image,
                                diameter=diameter, 
                                flow_thresh=flow_thresh, 
                                cell_prob_thresh=cell_prob_thresh,
                                model_type=model_type, 
                                segment_channel=segment_channel
                            }

        # make sure this can work with tiled images
        call get_transcripts_per_cell {input: mask=run_cellpose_nuclear.imageout,
                                detected_transcripts=get_tile.tiled_detected_transcript, 
                                transform = transform
                                }
    
        call run_baysor {input: detected_transcripts_cellID = get_transcripts_per_cell.detected_transcripts_cellID,
                            size=size,
                            prior_confidence=prior_confidence
                    }
    }
    call merge_segmentation_dfs { input: segmentation=run_baysor.baysor_out,
        segmentation_stats=run_baysor.baysor_stat
    }

}


task get_tile_intervals {
    input {
        File image_path
        File detected_transcripts
        File transform  
        Int ntiles_width
        Int ntiles_height
        Int min_width
        Int min_height
    }

    command {
        python /opt/tile_intervals.py --tif_image=${image_path} \
                                    --detected_transcripts=${detected_transcripts} \
                                    --transform_mat=${transform} \
                                    --out_path="/cromwell_root/" \
                                    --ntiles_width=${ntiles_width} \
                                    --ntiles_height=${ntiles_height} \
                                    --min_width=${min_width} \
                                    --min_height=${min_height}
    }

    output {
        File intervals = "intervals.csv"
    }

    runtime {
        docker: "oppdataanalysis/tiling:V1.0"
        memory: "20GB"
        disks: "local-disk 200 HDD"
    }
    
}


task get_tile {
    input {
        File image_path
        File detected_transcripts
        File transform 
		String interval
    }

    command {
        python /opt/tiling_script.py --tif_image=${image_path} \
                                    --detected_transcripts=${detected_transcripts} \
                                    --transform=${transform} \
                                    --out_path="/cromwell_root/" \
                                    --interval=${interval} \
                                    --show="False"
    }

    output {
        File tile_metadata = "tile_metadata.csv"
        File tiled_image = "tiled_image.tiff"
        File tiled_detected_transcript = "tiled_detected_transcript.csv"
    }

    runtime {
        docker: "oppdataanalysis/tiling:V1.0"
        memory: "20GB"
        disks: "local-disk 200 HDD"
    }
    
}



task run_deepcell_nuclear {
    input {
        File image_path
        Float image_mpp
        String pad_mode
        Int radius
        Float maxima_threshold
        Float interior_threshold
        Boolean exclude_border
        Float small_objects_threshold
    }

    command {
       python /opt/simple_deepcell_wrapper.py \
       --image_path ${image_path} \
       --image_mpp ${image_mpp} \
       --pad_mode ${pad_mode} \
       --radius ${radius} \
       --maxima_threshold ${maxima_threshold} \
       --interior_threshold ${interior_threshold} \
       --exclude_border ${exclude_border} \
       --small_objects_threshold ${small_objects_threshold}
    }

    output {
        File imageout = "imageout.tif"
    }

    runtime {
        docker: "oppdataanalysis/deepcell_nuclear:V1.0"
        memory: "20GB"
        maxRetries: 3
        disks: "local-disk 200 HDD"
    }
}

task get_transcripts_per_cell {

    input {
        File mask
        File detected_transcripts
        File transform
    }

    command {
       python /opt/mask_overlap.py \
       --mask ${mask} \
       --detected_transcripts ${detected_transcripts} \
       --transform ${transform} 
    }

    output {
        File detected_transcripts_cellID = "detected_transcripts_cellID.csv"
    }

    runtime {
        docker: "oppdataanalysis/image_seg_transcript:V1.0"
        memory: "20GB"
        maxRetries: 3
        disks: "local-disk 200 HDD"
    }

}

task run_baysor {

    input {
        File detected_transcripts_cellID
        Int size
        Float prior_confidence
    }

	command {
       
        if [[ $(wc -l <${detected_transcripts_cellID}) -ge 2 ]];then

            # not an ideal situation but its what worked
            julia -e 'show(Sys.CPU_NAME)'
            julia -e 'using Pkg; Pkg.add("IJulia"); Pkg.build(); using IJulia;'
            julia -e 'using Pkg; Pkg.add(Pkg.PackageSpec(;name="PackageCompiler", version="2.0.6"))'
            julia -e 'using Pkg; Pkg.add(PackageSpec(url="https://github.com/ayeaton/Baysor.git")); Pkg.build();'
            julia -e 'import Baysor, Pkg; Pkg.activate(dirname(dirname(pathof(Baysor)))); Pkg.instantiate();'
            printf "#!/usr/local/julia/bin/julia\n\nimport Baysor: run_cli\nrun_cli()" >> /cromwell_root/baysor && chmod +x /cromwell_root/baysor

            /cromwell_root/baysor run -x=global_x \
                -y=global_y \
                -z=global_z \
                -g=barcode_id \
                --no-ncv-estimation \
                -s=${size} \
                --prior-segmentation-confidence=${prior_confidence} \
                --save-polygons=geojson \
                ${detected_transcripts_cellID} ::cell
        else
            echo "too few lines in file"
            echo "too,few,lines" > segmentation.csv
            echo "too\tfew\tlines" > segmentation_counts.tsv
            echo "too,few,lines" > segmentation_cell_stats.csv
        fi
      
    }

    output {
        File baysor_out = "segmentation.csv"
        File baysor_counts = "segmentation_counts.tsv"
        File baysor_stat = "segmentation_cell_stats.csv"
    }

    runtime {
        docker: "oppdataanalysis/julia_baysor:V1.0"
        memory: "100GB"
        maxRetries: 2
        disks: "local-disk 200 HDD"

    }

}

task run_cellpose_nuclear {

	input {       
    	File image_path
        Int diameter
        Float flow_thresh
        Float cell_prob_thresh
        String model_type
        Int segment_channel

    }

    command {python -m cellpose --image_path ${image_path} \
                                --pretrained_model ${model_type} \
                                --save_tif \
                                --verbose \
                                --use_gpu \
                                --diameter ${diameter} \
                                --flow_threshold ${flow_thresh} \
                                --cellprob_threshold ${cell_prob_thresh} \
                                --chan ${segment_channel} \
                                --savedir /cromwell_root/  \
                                --no_npy
             # hack to change asap 
             mv *_cp_masks.tif imageout.tif
    }

    output{
        File imageout="imageout.tif"
    }

    runtime {
        docker: "oppdataanalysis/cellpose:V1.0"
        memory: "100GB"
        maxRetries: 2
        disks: "local-disk 200 HDD"

    }
    
}


task merge_segmentation_dfs {

    input {
        Array[File] segmentation
        Array[File] segmentation_stats
    }

    command {
        python /opt/merge_dfs.py --segmentation_paths ${sep=',' segmentation} \
                                --segmentation_cell_stats_paths ${sep=',' segmentation_stats}
    }

    output {
        File merged_segmentation = "merged_segmentation.csv"
        File merged_segmentation_counts = "merged_segmentation_counts.csv"
        File merged_segmentation_stats = "merged_segmentation_stats.csv"

    }

    runtime {
        docker: "oppdataanalysis/merge_segmentation:V1.0"
        memory: "10GB"
        disks: "local-disk 200 HDD"
    }

}
