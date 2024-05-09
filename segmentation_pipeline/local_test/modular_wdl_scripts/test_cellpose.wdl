version 1.0
task run_cellpose_nuclear {

	input {       
    	Array[File]+ image_path
        Int? diameter
        Float? flow_thresh
        Float? cell_prob_thresh
        String? model_type
        Int? segment_channel
    }

    command <<<
        index=0
        echo "The current working directory is: $(pwd)"
        IFS=', ' read -r -a combined_file_array <<< "~{sep=', ' image_path}"

        for value in "${combined_file_array[@]}"; do
            python -m cellpose --image_path "$value" \
                                --pretrained_model ~{model_type} \
                                --save_tif \
                                --save_txt \
                                --savedir="$(pwd)" \
                                --verbose \
                                --use_gpu \
                                --diameter ~{diameter} \
                                --flow_threshold ~{flow_thresh} \
                                --cellprob_threshold ~{cell_prob_thresh} \
                                --chan ~{segment_channel} \
                                --no_npy
            
            ((index++))
        done
    >>>

    output{
        Array[File]+ imageout = glob("*.tif")
        Array[File]+ outlines_text = glob("*.txt")
    }

    runtime {
        docker: "jishar7/cellpose_mac@sha256:6f6e625c90e35ace76f5b1da58c915dd244d0496104d47db673d209b69865efe"
        memory: "100GB"
        preemptible: 2
        continueOnReturnCode: [0, 1]
        maxRetries: 0
        disks: "local-disk 200 HDD"

    }
    
}