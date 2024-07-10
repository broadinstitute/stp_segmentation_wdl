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
        docker: "jishar7/partition_transcripts_for_terra@sha256:cc4dc3fb1fdaf2011c7e313102eb4dbe7bf5df6cdd59ee08d9e9e2b9032d1221"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}