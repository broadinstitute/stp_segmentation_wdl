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
        docker: "jishar7/merge_polygons_for_terra@sha256:4bf76422069cef19b79dfd3117fab7a21f9333354d860a8889ee6697cb2d0e91"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}