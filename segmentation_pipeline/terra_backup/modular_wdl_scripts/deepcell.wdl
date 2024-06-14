version 1.0
task run_deepcell_nuclear {
    input {
        File? image_path
        Float? image_mpp
        String? pad_mode
        Int? radius
        Float? maxima_threshold
        Float? interior_threshold
        Boolean? exclude_border
        Float? small_objects_threshold
    }

    command {
       python /opt/simple_deepcell_wrapper.py \
       --image_path ${image_path} \
       --image_mpp ${image_mpp} \
       --pad_mode ${pad_mode} \
       --radius ${radius} \
       --maxima_threshold ${maxima_threshold} \
       --interior_threshold ${interior_threshold} \
       --exclude_border ${exclude_border} \
       --small_objects_threshold ${small_objects_threshold}
    }

    output {
        File imageout = "imageout.tif"
    }

    runtime {
        docker: "oppdataanalysis/deepcell_nuclear:V1.0"
        memory: "20GB"
        preemptible: 2
        maxRetries: 0
        disks: "local-disk 200 HDD"
    }
}
