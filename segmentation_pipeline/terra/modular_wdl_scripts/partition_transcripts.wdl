version 1.0
task partitioning_transcript_cell_by_gene {

    input {
        File transcript_file
        File cell_polygon_file
        File? pre_merged_cell_polygons
        Int transcript_chunk_size 
        String technology
    }

    command <<<

        python /opt/partition_transcripts.py --transcript_file ~{transcript_file} \
                                --cell_polygon_file ~{cell_polygon_file} \
                                --transcript_chunk_size ~{transcript_chunk_size} \
                                --technology ~{technology}

        if [ -z "${my_var}" ]; then
            echo "pre_merged_cell_polygons variable is undefined or empty"
        else
            cp ~{pre_merged_cell_polygons} "pre_merged_cell_polygons.parquet"
        fi 

    >>>

    output {
        File cell_by_gene_matrix_csv = "cell_by_gene_matrix.csv"
        File filtered_cell_polygon_file = "cell_polygons.parquet"
        File cell_polygons_metadata = "cell_metadata.parquet"
        File partitioned_transcripts_metadata = "partitioned_transcripts_metadata.parquet"
        File cell_by_gene_matrix_parquet = "cell_by_gene_matrix.parquet"
        File moved_pre_merged_cell_polygons = "pre_merged_cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/partition_transcripts_for_terra@sha256:b2d1047fd69d41c89cb2438c70d36ceb4efb54e8160b62d07bbb0b9eead74ea5"
        memory: "100GB"
        preemptible: 10
        disks: "local-disk 200 HDD"
    }

}