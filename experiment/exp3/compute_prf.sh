#!/bin/bash

# bash compute_prf.sh
# ps -ef|grep python | grep compute_prf.py | awk '{print $2}' | xargs kill -9

nohup python compute_prf.py --dataset dataset1 --method ours_gpt >log/run_compute_prf_ours_gpt_dataset1.log &
nohup python compute_prf.py --dataset dataset1 --method ours_grok >log/run_compute_prf_ours_grok_dataset1.log &
nohup python compute_prf.py --dataset dataset1 --method ours_deepseek >log/run_compute_prf_ours_deepseek_dataset1.log &
nohup python compute_prf.py --dataset dataset2 --method ours_gpt >log/run_compute_prf_ours_gpt_dataset2.log &
nohup python compute_prf.py --dataset dataset2 --method ours_grok >log/run_compute_prf_ours_grok_dataset2.log &
nohup python compute_prf.py --dataset dataset2 --method ours_deepseek >log/run_compute_prf_ours_deepseek_dataset2.log &
nohup python compute_prf.py --dataset dataset3 --method ours_gpt >log/run_compute_prf_ours_gpt_dataset3.log &
nohup python compute_prf.py --dataset dataset3 --method ours_grok >log/run_compute_prf_ours_grok_dataset3.log &
nohup python compute_prf.py --dataset dataset3 --method ours_deepseek >log/run_compute_prf_ours_deepseek_dataset3.log &
nohup python compute_prf.py --dataset dataset4 --method ours_gpt >log/run_compute_prf_ours_gpt_dataset4.log &
nohup python compute_prf.py --dataset dataset4 --method ours_grok >log/run_compute_prf_ours_grok_dataset4.log &
nohup python compute_prf.py --dataset dataset4 --method ours_deepseek >log/run_compute_prf_ours_deepseek_dataset4.log &
nohup python compute_prf.py --dataset dataset5 --method ours_gpt >log/run_compute_prf_ours_gpt_dataset5.log &
nohup python compute_prf.py --dataset dataset5 --method ours_grok >log/run_compute_prf_ours_grok_dataset5.log &
nohup python compute_prf.py --dataset dataset5 --method ours_deepseek >log/run_compute_prf_ours_deepseek_dataset5.log &


nohup python compute_prf.py --dataset dataset1 --method ours_gpt_only >log/run_compute_prf_ours_gpt_only_dataset1.log &
nohup python compute_prf.py --dataset dataset1 --method ours_grok_only >log/run_compute_prf_ours_grok_only_dataset1.log &
nohup python compute_prf.py --dataset dataset1 --method ours_deepseek_only >log/run_compute_prf_ours_deepseek_only_dataset1.log &
nohup python compute_prf.py --dataset dataset2 --method ours_gpt_only >log/run_compute_prf_ours_gpt_only_dataset2.log &
nohup python compute_prf.py --dataset dataset2 --method ours_grok_only >log/run_compute_prf_ours_grok_only_dataset2.log &
nohup python compute_prf.py --dataset dataset2 --method ours_deepseek_only >log/run_compute_prf_ours_deepseek_only_dataset2.log &
nohup python compute_prf.py --dataset dataset3 --method ours_gpt_only >log/run_compute_prf_ours_gpt_only_dataset3.log &
nohup python compute_prf.py --dataset dataset3 --method ours_grok_only >log/run_compute_prf_ours_grok_only_dataset3.log &
nohup python compute_prf.py --dataset dataset3 --method ours_deepseek_only >log/run_compute_prf_ours_deepseek_only_dataset3.log &
nohup python compute_prf.py --dataset dataset4 --method ours_gpt_only >log/run_compute_prf_ours_gpt_only_dataset4.log &
nohup python compute_prf.py --dataset dataset4 --method ours_grok_only >log/run_compute_prf_ours_grok_only_dataset4.log &
nohup python compute_prf.py --dataset dataset4 --method ours_deepseek_only >log/run_compute_prf_ours_deepseek_only_dataset4.log &
nohup python compute_prf.py --dataset dataset5 --method ours_gpt_only >log/run_compute_prf_ours_gpt_only_dataset5.log &
nohup python compute_prf.py --dataset dataset5 --method ours_grok_only >log/run_compute_prf_ours_grok_only_dataset5.log &
nohup python compute_prf.py --dataset dataset5 --method ours_deepseek_only >log/run_compute_prf_ours_deepseek_only_dataset5.log &


nohup python compute_prf.py --dataset dataset1 --method gpt >log/run_compute_prf_gpt_dataset1.log &
nohup python compute_prf.py --dataset dataset2 --method gpt >log/run_compute_prf_gpt_dataset2.log &
nohup python compute_prf.py --dataset dataset3 --method gpt >log/run_compute_prf_gpt_dataset3.log &
nohup python compute_prf.py --dataset dataset4 --method gpt >log/run_compute_prf_gpt_dataset4.log &
nohup python compute_prf.py --dataset dataset5 --method gpt >log/run_compute_prf_gpt_dataset5.log &


nohup python compute_prf.py --dataset dataset1 --method grok >log/run_compute_prf_grok_dataset1.log &
nohup python compute_prf.py --dataset dataset2 --method grok >log/run_compute_prf_grok_dataset2.log &
nohup python compute_prf.py --dataset dataset3 --method grok >log/run_compute_prf_grok_dataset3.log &
nohup python compute_prf.py --dataset dataset4 --method grok >log/run_compute_prf_grok_dataset4.log &
nohup python compute_prf.py --dataset dataset5 --method grok >log/run_compute_prf_grok_dataset5.log &


nohup python compute_prf.py --dataset dataset1 --method deepseek >log/run_compute_prf_deepseek_dataset1.log &
nohup python compute_prf.py --dataset dataset2 --method deepseek >log/run_compute_prf_deepseek_dataset2.log &
nohup python compute_prf.py --dataset dataset3 --method deepseek >log/run_compute_prf_deepseek_dataset3.log &
nohup python compute_prf.py --dataset dataset4 --method deepseek >log/run_compute_prf_deepseek_dataset4.log &
nohup python compute_prf.py --dataset dataset5 --method deepseek >log/run_compute_prf_deepseek_dataset5.log &


nohup python compute_prf.py --dataset dataset1 --method expert >log/run_compute_prf_expert_dataset1.log &
nohup python compute_prf.py --dataset dataset2 --method expert >log/run_compute_prf_expert_dataset2.log &
nohup python compute_prf.py --dataset dataset3 --method expert >log/run_compute_prf_expert_dataset3.log &
nohup python compute_prf.py --dataset dataset4 --method expert >log/run_compute_prf_expert_dataset4.log &
nohup python compute_prf.py --dataset dataset5 --method expert >log/run_compute_prf_expert_dataset5.log &



nohup python compute_prf.py --dataset dataset1 --method target >log/run_compute_prf_target_dataset1.log &
nohup python compute_prf.py --dataset dataset2 --method target >log/run_compute_prf_target_dataset2.log &
nohup python compute_prf.py --dataset dataset3 --method target >log/run_compute_prf_target_dataset3.log &