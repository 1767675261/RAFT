#!/bin/bash

# bash compute_rc_only.sh
# ps -ef|grep python | grep compute_rc_only.py | awk '{print $2}' | xargs kill -9



nohup python compute_rc.py --dataset dataset1 --method ours_grok_only >log/run_compute_rc_ours_grok_only_dataset1.log &
nohup python compute_rc.py --dataset dataset2 --method ours_grok_only >log/run_compute_rc_ours_grok_only_dataset2.log &
nohup python compute_rc.py --dataset dataset3 --method ours_grok_only >log/run_compute_rc_ours_grok_only_dataset3.log &
nohup python compute_rc.py --dataset dataset4 --method ours_grok_only >log/run_compute_rc_ours_grok_only_dataset4.log &
nohup python compute_rc.py --dataset dataset5 --method ours_grok_only >log/run_compute_rc_ours_grok_only_dataset5.log &
nohup python compute_rc.py --dataset dataset6 --method ours_grok_only >log/run_compute_rc_ours_grok_only_dataset6.log &


nohup python compute_rc.py --dataset dataset1 --method ours_deepseek_only >log/run_compute_rc_ours_deepseek_only_dataset1.log &
nohup python compute_rc.py --dataset dataset2 --method ours_deepseek_only >log/run_compute_rc_ours_deepseek_only_dataset2.log &
nohup python compute_rc.py --dataset dataset3 --method ours_deepseek_only >log/run_compute_rc_ours_deepseek_only_dataset3.log &
nohup python compute_rc.py --dataset dataset4 --method ours_deepseek_only >log/run_compute_rc_ours_deepseek_only_dataset4.log &
nohup python compute_rc.py --dataset dataset5 --method ours_deepseek_only >log/run_compute_rc_ours_deepseek_only_dataset5.log &
nohup python compute_rc.py --dataset dataset6 --method ours_deepseek_only >log/run_compute_rc_ours_deepseek_only_dataset6.log &


nohup python compute_rc.py --dataset dataset1 --method ours_gpt_only >log/run_compute_rc_ours_gpt_only_dataset1.log &
nohup python compute_rc.py --dataset dataset2 --method ours_gpt_only >log/run_compute_rc_ours_gpt_only_dataset2.log &
nohup python compute_rc.py --dataset dataset3 --method ours_gpt_only >log/run_compute_rc_ours_gpt_only_dataset3.log &
nohup python compute_rc.py --dataset dataset4 --method ours_gpt_only >log/run_compute_rc_ours_gpt_only_dataset4.log &
nohup python compute_rc.py --dataset dataset5 --method ours_gpt_only >log/run_compute_rc_ours_gpt_only_dataset5.log &
nohup python compute_rc.py --dataset dataset6 --method ours_gpt_only >log/run_compute_rc_ours_gpt_only_dataset6.log &