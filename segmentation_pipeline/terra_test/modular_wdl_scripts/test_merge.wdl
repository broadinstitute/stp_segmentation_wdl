version 1.0
task merge_segmentation_dfs {

    input {
        Array[Array[File]] segmentation
        Array[File] segmentation_files = flatten(segmentation)
        Array[Array[File]] segmentation_stats
        Array[File] segmentation_stats_files = flatten(segmentation_stats)
    }

    command <<<
        python /opt/merge_dfs.py --segmentation_paths ~{sep=',' segmentation_files} \
                                --segmentation_cell_stats_paths ~{sep=',' segmentation_stats_files}
    >>>

    output {
        File merged_segmentation = "merged_segmentation.csv"
        File merged_segmentation_counts = "merged_segmentation_counts.csv"
        File merged_segmentation_stats = "merged_segmentation_stats.csv"

    }

    runtime {
        docker: "oppdataanalysis/merge_segmentation:V1.0"
        preemptible: 2
        memory: "10GB"
        disks: "local-disk 200 HDD"
    }

}