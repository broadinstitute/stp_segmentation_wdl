version 1.0
task partitioning_transcript_cell_by_gene {

    input {
        File transcript_file
        File original_transcript_file
        File cell_polygon_file
        File pre_merged_cell_polygons
        Int transcript_chunk_size 
        String technology
        File transform_file
    }

    command <<<

        python /opt/partition_transcripts.py --transcript_file ~{transcript_file} \
                                --original_transcript_file ~{original_transcript_file} \
                                --cell_polygon_file ~{cell_polygon_file} \
                                --transcript_chunk_size ~{transcript_chunk_size} \
                                --technology ~{technology} \
                                --transform_file ~{transform_file}

        pre_merged_cell_polygons_filename=$(basename ~{pre_merged_cell_polygons})

        if [ ${pre_merged_cell_polygons_filename} == "dummy_pre_merged_cell_polygons.parquet" ]; then
            echo "pre_merged_cell_polygons variable is undefined or empty"
        else
            cp ~{pre_merged_cell_polygons} "pre_merged_cell_polygons.parquet"
        fi 

    >>>

    output {
        File cell_by_gene_matrix_csv = "cell_by_gene_matrix.csv"
        File filtered_cell_polygon_file = "cell_polygons.parquet"
        File cell_polygons_metadata = "cell_metadata_micron_space.parquet"
        File partitioned_transcripts = "transcripts.parquet"
        File cell_by_gene_matrix_parquet = "cell_by_gene_matrix.parquet"
        File? moved_pre_merged_cell_polygons = "pre_merged_cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/partition_transcripts_for_terra@sha256:76a7446c8dabac863a842e7e1bfb53028a8b83b63bec4689571ced1f6b8dcd74"
        memory: "100GB"
        preemptible: 10
        disks: "local-disk 200 HDD"
    }

}