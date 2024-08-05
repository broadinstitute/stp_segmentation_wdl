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
        docker: "jishar7/merge_polygons_for_mac@sha256:d8c6ae8cff9c49c365b57ae1592fb7a238f728f551d079e3c8cb38c82c021bb1"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}