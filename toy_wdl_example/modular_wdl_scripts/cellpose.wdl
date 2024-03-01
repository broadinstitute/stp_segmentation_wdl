version 1.0
task run_cellpose_nuclear {

	input {       
    	File image_path
    }

    command {python -m cellpose --image_path ${image_path} \
                                --save_tif \
                                --verbose \
                                --use_gpu \
                                --savedir /cromwell_root/  \
                                --no_npy
             # hack to change asap 
             mv *_cp_masks.tif imageout.tif
    }

    output{
        File imageout="imageout.tif"
    }

    runtime {
        docker: "oppdataanalysis/cellpose:V1.0"
        memory: "100GB"
        maxRetries: 2
        disks: "local-disk 200 HDD"

    }
    
}