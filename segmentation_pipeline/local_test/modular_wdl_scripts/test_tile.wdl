version 1.0
task get_tile_intervals {
    input {
        File image_path
        File detected_transcripts
        File transform  
        Int tiles_dimension
        Int overlap
    }

    command {
        python /opt/tile_intervals.py --input_image=${image_path} \
                                    --detected_transcripts=${detected_transcripts} \
                                    --transform=${transform} \
                                    --tiles_dimension=${tiles_dimension} \
                                    --overlap=${overlap}
    }

    output {
        File intervals = "data.json"
        # File num_VMs_in_use_file = "num_VMs_in_use.txt"
    }

    runtime {
        docker: "jishar7/tile_test@sha256:37b1abb6c65622a53b2d9277dde53d5aaa9bf18f3652b7931fa1efc88239bc16"
        memory: "20GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }
    
}


task get_tile {
    input {
        File image_path
        File detected_transcripts
        File transform 
	Array[String]+ interval
    }

    command {
        python /opt/tiling_script.py --input_image=${image_path} \
                                    --detected_transcripts=${detected_transcripts} \
                                    --transform=${transform} \
                                    --interval="~{sep=', ' interval}" \
                                    --show="False"
    }

    output {
        Array[File]+ tile_metadata = glob("tile_metadata_*.csv")
        Array[File]+ tiled_image = glob("tiled_image_*.tiff")
        Array[File]+ tiled_detected_transcript = glob("tiled_detected_transcript_*.csv")
    }

    runtime {
        docker: "jishar7/tile_test@sha256:37b1abb6c65622a53b2d9277dde53d5aaa9bf18f3652b7931fa1efc88239bc16"
        memory: "20GB"
        preemptible: 2
        disks: "local-disk 200 HDD"
    }
    
}