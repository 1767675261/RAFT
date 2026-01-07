#!/bin/bash

# bash compute_rc.sh
# ps -ef|grep python | grep compute_rc.py | awk '{print $2}' | xargs kill -9

datasets=("dataset1" "dataset2" "dataset3" "dataset4" "dataset5" "dataset6")
methods=("ours_gpt" "ours_grok" "ours_deepseek")
xs=("1" "0.933" "0.867" "0.8" "0.733" "0.667" "0.6" "0.533" "0.467" "0.4" "0.333" "0.267" "0.2" "0.133" "0.067")

mkdir -p log

for dataset in "${datasets[@]}"; do
    for method in "${methods[@]}"; do
        for x in "${xs[@]}"; do
            log_file="log/run_compute_rc_${method}_${dataset}_${x}.log"
            nohup python compute_rc.py --dataset "$dataset" --method "$method" --x "$x" > "$log_file" &
            sleep 0.1
        done
    done
done