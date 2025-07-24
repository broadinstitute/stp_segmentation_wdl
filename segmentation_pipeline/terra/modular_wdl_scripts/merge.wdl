version 1.0
task merge_segmentation_dfs {

    input {
        Array[Array[File]] outlines
        File intervals
        File original_tile_polygons
        File trimmed_tile_polygons
        String merge_approach
        String algorithm
    }

    Array[File] outline_files = flatten(outlines)

    command <<<

        python /opt/merge_polygons.py --cell_outlines ~{sep=',' outline_files} \
                                --intervals ~{intervals} \
                                --original_tile_polygons ~{original_tile_polygons} \
                                --trimmed_tile_polygons ~{trimmed_tile_polygons} \
                                --algorithm ~{algorithm} \
                                --merge_approach ~{merge_approach}
    >>>

    output {
        File processed_cell_polygons = "cell_polygons.parquet"
        File pre_merged_cell_polygons = "pre_merged_cell_polygons.parquet"
    }

    runtime {
        docker: "jishar7/merge_polygons_for_terra@sha256:06a5f12bbc3ec2544e130d7e4fafd96e5445a3913dbd7a57e5a87c68f1d46ede"
        memory: "200GB"
        preemptible: 0
        disks: "local-disk 400 HDD"
    }

}