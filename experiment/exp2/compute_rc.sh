#!/bin/bash

# bash compute_rc.sh
# ps -ef|grep python | grep compute_rc.py | awk '{print $2}' | xargs kill -9



datasets=("dataset1" "dataset2" "dataset3" "dataset4" "dataset5" "dataset6")
# methods=("ours_gpt" "ours_grok" "ours_deepseek" "gpt" "grok" "deepseek" "gpt_without_repr" "grok_without_repr" "deepseek_without_repr" "gpt_without_test" "grok_without_test" "deepseek_without_test")

methods=("gpt_without_repr" "grok_without_repr" "deepseek_without_repr")

mkdir -p log

for dataset in "${datasets[@]}"; do
    for method in "${methods[@]}"; do
        log_file="log/run_compute_rc_${method}_${dataset}.log"
        nohup python compute_rc.py --dataset "$dataset" --method "$method" > "$log_file" &
        sleep 0.1
    done
done
