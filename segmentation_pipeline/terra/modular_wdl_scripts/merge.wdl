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
        docker: "jishar7/merge_polygons_for_terra@sha256:ea7e1401c4620028b3af0717a09f5c24162078d63cef6cd6f4c1b20427e02366"
        memory: "50GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}