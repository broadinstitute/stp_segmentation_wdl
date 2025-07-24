version 1.0
task run_watershed {

    input {
        Array[File] image_files_path
        String? shard_index
    }

    command <<<

        IFS=', ' read -r -a image_paths <<< "$(echo "~{sep=', ' image_files_path}" | tr ', ' '\n' | grep "tiled_image_~{shard_index}_.*\.tiff" | tr '\n' ', ')"

        python /opt/watershed.py --image_paths ${sep=',' image_paths}

    >>>

    output {
        Array[File] outlines = glob("*.parquet")
    }

    runtime {
        docker: "jishar7/watershed_for_terra@sha256:116ee09b1cba36f7178e21d35c56a03dc0b19664c2d0412be9b6d9786563ddbc"
        memory: "200GB"
        preemptible: 0
        disks: "local-disk 300 HDD"
    }

}