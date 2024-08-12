version 1.0
task merge_segmentation_dfs {

    input {
        Array[Array[File]] outlines
        Array[File] outline_files = flatten(outlines)
        File intervals
    }

    command <<<

        python /opt/merge_polygons.py --cell_outlines ~{sep=',' outline_files} \
                                --intervals ~{intervals}
    >>>

    output {
        File processed_cell_polygons = "cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/merge_polygons_for_mac@sha256:9bfc60cad9ba233712e1d1b77ed0123cb66fde7690ea6f86744b46ba2ebf1786"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}