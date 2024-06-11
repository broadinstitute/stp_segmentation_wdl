version 1.0
task merge_segmentation_dfs {

    input {
        Array[Array[File]]+ outlines
        File intervals
    }

    command <<<
        python /opt/merge_polygons.py --cell_outlines ~{sep=',' outlines} \
                                --intervals ~{intervals}
    >>>

    output {
        File merged_cell_polygons = "merged_cell_polygons.shp"
    }

    runtime {
        docker: "jishar7/merge_polygons_mac@sha256:e1511d561372c8260522bf8b956ae5a5207092d6753284cfad6229da71816d77"
        memory: "100GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}