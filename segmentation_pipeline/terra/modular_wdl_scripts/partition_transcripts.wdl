version 1.0
task partitioning_transcript_cell_by_gene {

    input {
        File transcript_file
        File cell_polygon_file
    }

    command <<<

        python /opt/partition_transcripts.py --transcript_file ~{transcript_file} \
                                --cell_polygon_file ~{cell_polygon_file}
    >>>

    output {
        File cell_by_gene_matrix = "cell_by_gene_matrix.csv"
    }

    runtime {
        docker: "jishar7/partition_transcripts_for_terra@sha256:5e9a9918319422b016d763a85a62fd20d9c4964fbd4657026f18c9bcd4caafd5"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}