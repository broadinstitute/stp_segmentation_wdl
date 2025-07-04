version 1.0
task merge_segmentation_dfs {

    input {
        Array[Array[File]] outlines
        File intervals
        File original_tile_polygons
        File trimmed_tile_polygons
        String merge_approach
    }

    Array[File] outline_files = flatten(outlines)

    command <<<

        python /opt/merge_polygons.py --cell_outlines ~{sep=',' outline_files} \
                                --intervals ~{intervals} \
                                --original_tile_polygons ~{original_tile_polygons} \
                                --trimmed_tile_polygons ~{trimmed_tile_polygons} \
                                --merge_approach ~{merge_approach}
    >>>

    output {
        File processed_cell_polygons = "cell_polygons.parquet"
        File pre_merged_cell_polygons = "pre_merged_cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/merge_polygons_for_terra@sha256:3db1d9dc0750068332c5fdcb91fb7d760c7e544829878be9ddbb4ea53ab58c00"
        memory: "200GB"
        preemptible: 0
        disks: "local-disk 400 HDD"
    }

}