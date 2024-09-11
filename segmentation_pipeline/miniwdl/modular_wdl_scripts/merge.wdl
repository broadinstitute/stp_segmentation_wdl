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
        File raw_cell_polygons = "raw_cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/merge_polygons_for_mac@sha256:7ef27b6ed4536b97a8214a96ea03960269e7ec41fc6074a8a7442fddaf342950"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}