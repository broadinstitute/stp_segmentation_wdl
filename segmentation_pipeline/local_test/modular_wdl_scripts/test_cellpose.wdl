version 1.0
task run_cellpose_nuclear {

	input {       
    	Array[File]? image_path
        Int? diameter
        Float? flow_thresh
        Float? cell_prob_thresh
        String? model_type
        Int? segment_channel
    }

    command <<<
        index=0

        IFS=', ' read -r -a combined_file_array <<< "~{sep=', ' image_path}"

        for value in "${combined_file_array[@]}"; do
            python -m cellpose --image_path "$value" \
                                --pretrained_model ~{model_type} \
                                --save_tif \
                                --save_txt \
                                --verbose \
                                --use_gpu \
                                --diameter ~{diameter} \
                                --flow_threshold ~{flow_thresh} \
                                --cellprob_threshold ~{cell_prob_thresh} \
                                --chan ~{segment_channel} \
                                --no_npy
            
            # hack to change asap

            mv *_cp_masks.tif "imageout_$index.tif"
            mv *_cp_outlines.txt "outlines_$index.txt"

            ((index++))
        done
    >>>

    output{

        Array[File] imageout = glob("imageout_*.tif")
        Array[File] outlines_text = glob("outlines_*.txt")

    }

    runtime {
        docker: "oppdataanalysis/cellpose:V1.0"
        memory: "100GB"
        preemptible: 2
        maxRetries: 0
        disks: "local-disk 200 HDD"

    }
    
}