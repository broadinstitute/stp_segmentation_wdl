version 1.0
task run_cellpose {

	input {       
    	Array[File] image_path
        Int diameter
        Float flow_thresh
        Float cell_prob_thresh
        File? pretrained_model
        String? model_type
        Int segment_channel
        Int optional_channel
        String shard_index
        File dummy_pretrained_model
    }

    command <<<

        IFS=', ' read -r -a combined_file_array <<< "$(echo "~{sep=', ' image_path}" | tr ', ' '\n' | grep "tiled_image_~{shard_index}_.*\.tiff" | tr '\n' ', ')"
                
        for value in "${combined_file_array[@]}"; do

            if [ ~{pretrained_model} == ~{dummy_pretrained_model} ]; then
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
                                    --chan2 ~{optional_channel} \
                                    --savedir "$(pwd)"  \
                                    --no_npy
            else
                python -m cellpose --image_path "$value" \
                                --pretrained_model ~{pretrained_model} \
                                --save_tif \
                                --save_txt \
                                --verbose \
                                --use_gpu \
                                --diameter ~{diameter} \
                                --flow_threshold ~{flow_thresh} \
                                --cellprob_threshold ~{cell_prob_thresh} \
                                --chan ~{segment_channel} \
                                --chan2 ~{optional_channel} \
                                --savedir "$(pwd)"  \
                                --no_npy
            fi
        done
    >>>

    output {

        Array[File] imageout = glob("*.tif")
        Array[File] outlines = glob("*.txt")

    }

    runtime {
        continueOnReturnCode: [0, 1]
        docker: "jishar7/cellpose_for_mac@sha256:e3614459dd29e98a1864e710045e3e52888e7d96753a659b74511f73b19eca66"
        memory: "100GB"
        preemptible: 2
        maxRetries: 0
        disks: "local-disk 200 HDD"

    }
    
}