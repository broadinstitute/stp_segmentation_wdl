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
        docker: "jishar7/merge_polygons_for_mac@sha256:3f8670dec76dc46530a787ad9ab79dd33d68542683ce13fc9084a52ecc5a7548"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}