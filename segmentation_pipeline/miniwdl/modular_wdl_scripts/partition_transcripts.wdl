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
        docker: "jishar7/partition_transcripts_for_mac@sha256:ec84ba9c49e193f3224bea09a43f45794ad57d2ce54cc1e987820b37399a0e22"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}