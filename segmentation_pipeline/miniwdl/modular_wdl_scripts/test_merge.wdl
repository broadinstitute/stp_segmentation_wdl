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
        File merged_cell_polygons = "merged_cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/merge_polygons_for_mac@sha256:fdd4e1f94c0773b946faca4c39ef710ffd3c967f302c82361d6c20cb33e4b835"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}