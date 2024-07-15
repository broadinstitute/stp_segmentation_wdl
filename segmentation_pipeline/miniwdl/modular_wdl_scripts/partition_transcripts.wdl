version 1.0
task partitioning_transcript_cell_by_gene {

    input {
        File transcript_file
        File cell_polygon_file
        Int transcript_chunk_size 
        String technology
    }

    command <<<

        python /opt/partition_transcripts.py --transcript_file ~{transcript_file} \
                                --cell_polygon_file ~{cell_polygon_file} \
                                --transcript_chunk_size ~{transcript_chunk_size} \
                                --technology ~{technology}

        cp ~{cell_polygon_file} "processed_cell_polygons.parquet"

    >>>

    output {
        File cell_by_gene_matrix_csv = "cell_by_gene_matrix.csv"
        File moved_cell_polygon_file = "processed_cell_polygons.parquet"
        File cell_polygons_metadata = "cell_polygons_metadata.parquet"
        File partitioned_transcripts = "partitioned_transcripts.parquet"
        File partitioned_transcripts_metadata = "partitioned_transcripts_metadata.parquet"
        File cell_by_gene_matrix_parquet = "cell_by_gene_matrix.parquet"
    }

    runtime {
        docker: "jishar7/partition_transcripts_for_mac@sha256:982c17b82eeea4cee1b15da2d0e102338f5944a84f44d00146ec6727393a5f3b"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}