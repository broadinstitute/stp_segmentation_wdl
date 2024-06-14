version 1.0
task get_tile_intervals {
    input {
        File image_path
        Int tiles_dimension
        Int overlap
    }

    command {
        python /opt/tile_intervals.py --input_image=${image_path} \
                                    --tiles_dimension=${tiles_dimension} \
                                    --overlap=${overlap}
    }

    output {
        File intervals = "data.json"
        # File num_VMs_in_use_file = "num_VMs_in_use.txt"
    }

    runtime {
        docker: "jishar7/tiling_for_mac@sha256:81a389ce4c5c09eaea81814048d4025fdaea656981ccfb9460fb5f1fc5f70095"
        memory: "20GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }
    
}


task get_tile {
    input {
        File image_path
		Array[String] interval
        String shard_index
    }

    command {
        python /opt/tiling_script.py --input_image=${image_path} \
                                    --out_path="$(pwd)" \
                                    --interval="~{sep=', ' interval}" \
                                    --shard_index=${shard_index}
    }

    output {
        Array[File] tile_metadata = glob("tile_metadata_*.csv")
        Array[File] tiled_image = glob("tiled_image_*.tiff")
    }

    runtime {
        docker: "jishar7/tiling_for_mac@sha256:81a389ce4c5c09eaea81814048d4025fdaea656981ccfb9460fb5f1fc5f70095"
        memory: "20GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }
    
}