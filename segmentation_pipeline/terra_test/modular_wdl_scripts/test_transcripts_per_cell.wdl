version 1.0
task get_transcripts_per_cell {

    input {
        Array[File] mask
        Array[File] detected_transcripts
        File transform
    }

    command <<<

       index = 0

       IFS=', ' read -r -a combined_file_array_mask <<< "~{sep=', ' mask}"
       IFS=', ' read -r -a combined_file_array_transcripts <<< "~{sep=', ' detected_transcripts}"

       length=${#combined_file_array_mask[@]}

       for ((i=0; i<$length; i++)); do
            mask_file=${combined_file_array_mask[i]}  
            detected_transcripts_file=${combined_file_array_transcripts[i]} 

            python /opt/mask_overlap.py \
                --mask "$mask_file" \
                --detected_transcripts "$detected_transcripts_file" \
                --transform ~{transform}

            mv detected_transcripts_cellID.csv "detected_transcripts_cellID_$index.csv"
            mv detected_transcripts_cellID_geo.csv "detected_transcripts_cellID_geo_$index.csv"
            mv detected_transcripts_cellID_geo.parquet "detected_transcripts_cellID_geo_$index.parquet"

            ((index++))
       done
    >>>

    output {
        Array[File] detected_transcripts_cellID = glob("detected_transcripts_cellID_*.csv")
        Array[File] detected_transcripts_cellID_geo_csv = glob("detected_transcripts_cellID_geo_*.csv")
        Array[File] detected_transcripts_cellID_geo_parquet = glob("detected_transcripts_cellID_geo_*.parquet")
    }

    runtime {
        docker: "jishar7/mask_cellpose:V3.0"
        memory: "20GB"
        preemptible: 2
        maxRetries: 0
        disks: "local-disk 200 HDD"
    }

}