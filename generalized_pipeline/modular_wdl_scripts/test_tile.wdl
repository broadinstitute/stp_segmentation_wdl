version 1.0
task get_tile_intervals {
    input {
        File image_path
        File detected_transcripts
        File transform  
        Int ntiles_width
        Int ntiles_height
        Int min_width
        Int min_height
    }

    command {
        python /opt/tile_intervals.py --input_image=${image_path} \
                                    --detected_transcripts=${detected_transcripts} \
                                    --transform_mat=${transform} \
                                    --out_path="/cromwell_root/" \
                                    --ntiles_width=${ntiles_width} \
                                    --ntiles_height=${ntiles_height} \
                                    --min_width=${min_width} \
                                    --min_height=${min_height}
    }

    output {
        File intervals = "intervals.csv"
    }

    runtime {
        docker: "oppdataanalysis/tiling:V1.0"
        memory: "20GB"
        disks: "local-disk 200 HDD"
    }
    
}


task get_tile {
    input {
        File image_path
        File detected_transcripts
        File transform 
		Array[String] interval
    }

    command <<<

        for index, value in enumerate(${interval}):
            python /opt/tiling_script.py --input_image=${image_path} \
                                        --detected_transcripts=${detected_transcripts} \
                                        --transform=${transform} \
                                        --out_path="/cromwell_root/" \
                                        --ind=${index} \
                                        --interval=${value} \
                                        --show="False"
    >>>

    output {
        Array[File] tile_metadata = glob("tile_metadata_*.csv")
        Array[File] tiled_image = glob("tiled_image_*.tiff")
        Array[File] tiled_detected_transcript = glob("tiled_detected_transcript_*.csv")
    }

    runtime {
        docker: "oppdataanalysis/tiling:V1.0"
        memory: "20GB"
        disks: "local-disk 200 HDD"
    }
    
}