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
        File merged_cell_polygons = "merged_cell_polygons.shp"
    }

    runtime {
        docker: "jishar7/merge_polygons_mac@sha256:c69027d14871959c81fc86030075c99eaf9747713e06c454849a452f5055f966"
        memory: "100GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}