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
        docker: "jishar7/merge_polygons_for_mac@sha256:602f352e4e36bdf8729eceeb0985980e44e1ebe5d740b2a0c7e4ff30c61e5fc0"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}