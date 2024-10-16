version 1.0
task merge_segmentation_dfs {

    input {
        Array[Array[File]] outlines
        Array[File] outline_files = flatten(outlines)
        File intervals
        File original_tile_polygons
        File trimmed_tile_polygons
    }

    command <<<

        python /opt/merge_polygons.py --cell_outlines ~{sep=',' outline_files} \
                                --intervals ~{intervals} \
                                --original_tile_polygons ~{original_tile_polygons} \
                                --trimmed_tile_polygons ~{trimmed_tile_polygons}
    >>>

    output {
        File processed_cell_polygons = "cell_polygons.parquet"
        File pre_merged_cell_polygons = "pre_merged_cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/merge_polygons_for_terra@sha256:f0b12e34fb66d57ee059e3bbb06fb86abff633218baf3f6a4021a4b7b9d412f2"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}