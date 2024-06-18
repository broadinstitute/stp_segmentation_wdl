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
        File processed_cell_polygons = "processed_cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/merge_polygons_for_mac@sha256:f2a87696fac9ff57707a7d2d89f86b1e8a1459e9671fae0a7ccfbcd652a0846d"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}