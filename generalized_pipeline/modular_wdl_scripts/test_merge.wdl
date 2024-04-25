version 1.0
task merge_segmentation_dfs {

    input {
        Array[Array[File]] segmentation
        Array[Array[File]] segmentation_stats
    }

    command <<<
        python /opt/merge_dfs.py --segmentation_paths ~{sep=',' segmentation} \
                                --segmentation_cell_stats_paths ~{sep=',' segmentation_stats}
    >>>

    output {
        File merged_segmentation = "merged_segmentation.csv"
        File merged_segmentation_counts = "merged_segmentation_counts.csv"
        File merged_segmentation_stats = "merged_segmentation_stats.csv"

    }

    runtime {
        docker: "oppdataanalysis/merge_segmentation:V1.0"
        memory: "10GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }

}