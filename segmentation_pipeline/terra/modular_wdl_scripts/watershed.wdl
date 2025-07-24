version 1.0
task run_watershed {

    input {
        Array[File] image_paths
    }

    command <<<

            python /opt/watershed.py --image_paths ~{sep=',' image_paths}

    >>>

    output {
        Array[File] outlines = glob("*.parquet")
    }

    runtime {
        docker: "jishar7/watershed_for_terra@sha256:2451b1995c7d62694a5ff0889928c16d4a8891cb5791881920369b03ece32848"
        memory: "200GB"
        preemptible: 0
        disks: "local-disk 300 HDD"
    }

}