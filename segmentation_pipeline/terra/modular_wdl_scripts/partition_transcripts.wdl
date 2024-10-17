version 1.0
task partitioning_transcript_cell_by_gene {

    input {
        File transcript_file
        File cell_polygon_file
        File pre_merged_cell_polygons
        Int transcript_chunk_size 
        String technology
    }

    command <<<

        python /opt/partition_transcripts.py --transcript_file ~{transcript_file} \
                                --cell_polygon_file ~{cell_polygon_file} \
                                --transcript_chunk_size ~{transcript_chunk_size} \
                                --technology ~{technology}

        cp ~{pre_merged_cell_polygons} "pre_merged_cell_polygons.parquet"

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
        docker: "jishar7/partition_transcripts_for_terra@sha256:33d23edb27b398be79d27ced5e90fd52bb40587e8bf9e8f1d7940e2af4acf8d7"
        memory: "100GB"
        preemptible: 10
        disks: "local-disk 200 HDD"
    }

}