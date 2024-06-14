version 1.0
task run_cellpose_nuclear {

	input {       
    	Array[File] image_path
        Int diameter
        Float flow_thresh
        Float cell_prob_thresh
        String model_type
        Int segment_channel
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
                                --savedir "$(pwd)"  \
                                --no_npy
            
            ((index++))
        done
    >>>

    output {

        Array[File] imageout = glob("*.tif")
        Array[File] outlines = glob("*.txt")

    }

    runtime {
        continueOnReturnCode: [0, 1]
        docker: "jishar7/cellpose_for_terra@sha256:3ac418181abd6d532112e405ffa7c2c002a27691048ecfadbedc41ea9376da7a"
        memory: "100GB"
        preemptible: 2
        maxRetries: 0
        disks: "local-disk 200 HDD"

    }
    
}