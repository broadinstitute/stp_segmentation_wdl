version 1.0
task partitioning_transcript_cell_by_gene {

    input {
        File transcript_file
        File cell_polygon_file
        Int transcript_chunk_size 
    }

    command <<<

        python /opt/partition_transcripts.py --transcript_file ~{transcript_file} \
                                --cell_polygon_file ~{cell_polygon_file} \
                                --transcript_chunk_size ~{transcript_chunk_size}
    >>>

    output {
        File cell_by_gene_matrix = "cell_by_gene_matrix.csv"
    }

    runtime {
        docker: "jishar7/partition_transcripts_for_mac@sha256:be4243ddff6f66350d883534bb45f3a49513e23fc8735765cab9d3130a5ab5e7"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}