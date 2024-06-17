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
        File intervals = "intervals.json"
        # File num_VMs_in_use_file = "num_VMs_in_use.txt"
    }

    runtime {
        docker: "jishar7/tiling_for_mac@sha256:8093c266c0c12396dea3ddbfdaa00e95378bad06edadf843cacea407741dbf8e"
        memory: "20GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }
    
}


task get_tile {
    input {
        File image_path
		File intervals
        String shard_index
    }

    command {
        python /opt/tiling_script.py --input_image=${image_path} \
                                    --out_path="$(pwd)" \
                                    --intervals=${intervals} \
                                    --shard_index=${shard_index}
    }

    output {
        Array[File] tile_metadata = glob("tile_metadata_*.csv")
        Array[File] tiled_image = glob("tiled_image_*.tiff")
    }

    runtime {
        docker: "jishar7/tiling_for_mac@sha256:8093c266c0c12396dea3ddbfdaa00e95378bad06edadf843cacea407741dbf8e"
        memory: "20GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }
    
}