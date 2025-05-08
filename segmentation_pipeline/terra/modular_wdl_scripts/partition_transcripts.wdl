version 1.0
task partitioning_transcript_cell_by_gene {

    input {
        File transcript_file
        File cell_polygon_file
        File pre_merged_cell_polygons
        Int transcript_chunk_size
        String technology
        File transform_file
        String algorithm
        String dataset_name
    }

    command <<<

        python /opt/partition_transcripts.py --transcript_file ~{transcript_file} \
                                --cell_polygon_file ~{cell_polygon_file} \
                                --transcript_chunk_size ~{transcript_chunk_size} \
                                --technology ~{technology} \
                                --transform_file ~{transform_file} \
                                --pre_merged_cell_polygons ~{pre_merged_cell_polygons} \
                                --algorithm ~{algorithm} \
                                --dataset_name ~{dataset_name}

    >>>

    output {
        File cell_by_gene_matrix_csv = "cell_by_gene_matrix.csv"
        File filtered_cell_polygon_file = "cell_polygons.parquet"
        File cell_polygons_metadata = "cell_metadata_micron_space.parquet"
        File partitioned_transcripts = "transcripts.parquet"
        File cell_by_gene_matrix_parquet = "cell_by_gene_matrix.parquet"
        File? moved_pre_merged_cell_polygons = "pre_merged_cell_polygons.parquet"
        File segmentation_parameters = "segmentation_parameters.json"
    }

    runtime {
        docker: "jishar7/partition_transcripts_for_terra@sha256:92479e8efaaa444fc686540ae3279b7a4260c6068aa17c737ec1a39e3cd0577b"
        memory: "100GB"
        preemptible: 10
        disks: "local-disk 200 HDD"
    }

}