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
        docker: "jishar7/merge_polygons_for_terra@sha256:3d3c7002d44b45474bfa27d48cbec573a5338c5cd30d8c8d78ec58dd8c9dcb73"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}