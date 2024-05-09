version 1.0
task run_baysor {

    input {
        Array[File]+ detected_transcripts_cellID
        Int size
        Float prior_confidence
    }

	command <<<
        # not an ideal situation but its what worked
        julia -e 'show(Sys.CPU_NAME)'
        julia -e 'using Pkg; Pkg.add("IJulia"); Pkg.build(); using IJulia;'
        julia -e 'using Pkg; Pkg.add(Pkg.PackageSpec(;name="PackageCompiler", version="2.0.6"))'
        julia -e 'using Pkg; Pkg.add(PackageSpec(url="https://github.com/ayeaton/Baysor.git")); Pkg.build();'
        julia -e 'import Baysor, Pkg; Pkg.activate(dirname(dirname(pathof(Baysor)))); Pkg.instantiate();'
        printf "#!/usr/local/julia/bin/julia\n\nimport Baysor: run_cli\nrun_cli()" >> /baysor && chmod +x /baysor

        index=0

        IFS=', ' read -r -a combined_file_array_transcripts <<< "~{sep=', ' detected_transcripts_cellID}"

        for value in "${combined_file_array_transcripts[@]}"; do
            /baysor run -x="global_x" \
                -y="global_y" \
                -z="global_z" \
                -g="barcode_id" \
                --no-ncv-estimation \
                -s=~{size} \
                --prior-segmentation-confidence=~{prior_confidence} \
                "$value" ::cell
        
            mv segmentation.csv "segmentation_$index.csv"
            mv segmentation_counts.tsv "segmentation_counts_$index.tsv"  
            mv segmentation_cell_stats.csv "segmentation_cell_stats_$index.csv"

            ((index++))
        done
    >>>

    output {

        Array[File]+ baysor_out = glob("segmentation_*.csv")
        Array[File]+ baysor_counts = glob("segmentation_counts_*.tsv")
        Array[File]+ baysor_stat = glob("segmentation_cell_stats_*.csv")

    }

    runtime {
        docker: "oppdataanalysis/julia_baysor@sha256:33eaa04015d42c9baa93ba3243b927679cd8c2d31f5bc1fcb68561dec549e858"
        memory: "100GB"
        preemptible: 2
        continueOnReturnCode: [0, 1]
        maxRetries: 0
        disks: "local-disk 200 HDD"

    }
    
}
