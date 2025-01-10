version 1.0
task run_baysor {

    input {
        File detected_transcripts_file
        Int size
    }

	command <<<
        # not an ideal situation but its what worked
        julia -e 'show(Sys.CPU_NAME)'
        julia -e 'using Pkg; Pkg.add("IJulia"); Pkg.build(); using IJulia;'
        julia -e 'using Pkg; Pkg.add(Pkg.PackageSpec(;name="PackageCompiler", version="2.0.6"))'
        julia -e 'using Pkg; Pkg.add(PackageSpec(url="https://github.com/ayeaton/Baysor.git")); Pkg.build();'
        julia -e 'import Baysor, Pkg; Pkg.activate(dirname(dirname(pathof(Baysor)))); Pkg.instantiate();'
        printf "#!/usr/local/julia/bin/julia\n\nimport Baysor: run_cli\nrun_cli()" >> /cromwell_root/baysor && chmod +x /cromwell_root/baysor

        index=0

        IFS=', ' read -r -a combined_file_array_transcripts <<< "~{sep=', ' detected_transcripts_cellID_geo_csv}"

        for value in "${combined_file_array_transcripts[@]}"; do
            /cromwell_root/baysor run -x="global_x" \
                -y="global_y" \
                -z="global_z" \
                -g="barcode_id" \
                --no-ncv-estimation \
                -s=~{size} \
                "$value" ::cell
        
            mv segmentation.csv "segmentation_$index.csv"
            mv segmentation_counts.tsv "segmentation_counts_$index.tsv"  
            mv segmentation_cell_stats.csv "cell_stats_segmentation_$index.csv"

            ((index++))
        done
    >>>

    output {

        Array[File] baysor_out = glob("segmentation_*.csv")
        Array[File] baysor_counts = glob("segmentation_counts_*.tsv")
        Array[File] baysor_stat = glob("cell_stats_segmentation_*.csv")

    }

    runtime {
        docker: "vpetukhov/baysor@sha256:4bf0b232891b4be0358d41fac31fe3ef3e4c9194e15c7a15ea2132558a627995"
        memory: "100GB"
        continueOnReturnCode: [0, 1]
        preemptible: 2
        maxRetries: 0
        disks: "local-disk 250 HDD"

    }
    
}
