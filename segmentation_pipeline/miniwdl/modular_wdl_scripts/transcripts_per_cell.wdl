version 1.0
task get_transcripts_per_cell {

    input {
        Array[File] outlines
        Array[File] detected_transcripts
        File transform
    }

    command <<<

        index=0

        IFS=', ' read -r -a combined_file_array_outlines <<< "~{sep=', ' outlines}"
        IFS=', ' read -r -a combined_file_array_transcripts <<< "~{sep=', ' detected_transcripts}"

        length=${#combined_file_array_outlines[@]}

        for ((i=0; i<$length; i++)); do
            outlines_file=${combined_file_array_outlines[i]}  
            detected_transcripts_file=${combined_file_array_transcripts[i]} 

            python /opt/mask_overlap.py \
                --outlines "$outlines_file" \
                --out_path="" \
                --detected_transcripts "$detected_transcripts_file" \
                --transform ~{transform}

            mv detected_transcripts_cellID_geo.csv "detected_transcripts_cellID_geo_$index.csv"
            mv detected_transcripts_cellID_geo.parquet "detected_transcripts_cellID_geo_$index.parquet"

            ((index++))
        done
    >>>

    output {
        Array[File] detected_transcripts_cellID_geo_csv = glob("detected_transcripts_cellID_geo_*.csv")
        Array[File] detected_transcripts_cellID_geo_parquet = glob("detected_transcripts_cellID_geo_*.parquet")
    }

    runtime {
        continueOnReturnCode: [0, 1]
        docker: "jishar7/mask_cellpose@sha256:c4f96e0a445648fcd10155611e2695777b2dd605f4791c820173344261a112c8"
        memory: "20GB"
        preemptible: 2
        maxRetries: 0
        disks: "local-disk 200 HDD"
    }

}