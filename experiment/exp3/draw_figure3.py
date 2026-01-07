import matplotlib.pyplot as plt
import json
import numpy as np


def draw_figure():
    # x轴为3个领域，y为metric的值，每个领域有4个柱子
    domain = ["finance", "automotive", "power"]
    datasets = ["dataset1", "dataset2", "dataset3", "dataset4", "dataset5", "dataset6"]
    llms = ["deepseek", "gpt", "grok"]
    metric = ["precision", "recall", "f1", "rc"]

    # 每个值是6个数据集3个LLM的平均值
    data = {d: {m: [] for m in metric} for d in domain}
    
    # 金融
    for dataset in datasets:
        for llm in llms:
            dataraw = json.load(open(f"../exp1/log/ours_{llm}_prf_{dataset}.json", "r", encoding="utf-8"))
            data['finance']['precision'].append(dataraw[dataset]['precision_testcase'])
            data['finance']['recall'].append(dataraw[dataset]['recall_testcase'])
            data['finance']['f1'].append(dataraw[dataset]['f1_testcase'])
            dataraw = json.load(open(f"../exp1/log/ours_{llm}_rc_{dataset}.json", "r", encoding="utf-8"))
            data['finance']['rc'].append(dataraw[dataset])
    # 汽车
    for dataset in datasets[:3]:
        for llm in llms:
            dataraw = json.load(open(f"log/ours_{llm}_prf_{dataset}.json", "r", encoding="utf-8"))
            data['automotive']['precision'].append(dataraw[dataset]['precision_testcase'])
            data['automotive']['recall'].append(dataraw[dataset]['recall_testcase'])
            data['automotive']['f1'].append(dataraw[dataset]['f1_testcase'])
            dataraw = json.load(open(f"log/ours_{llm}_rc_{dataset}.json", "r", encoding="utf-8"))
            data['automotive']['rc'].append(dataraw[dataset])
    # 电力
    for dataset in datasets[3:5]:
        for llm in llms:
            dataraw = json.load(open(f"log/ours_{llm}_prf_{dataset}.json", "r", encoding="utf-8"))
            data['power']['precision'].append(dataraw[dataset]['precision_testcase'])
            data['power']['recall'].append(dataraw[dataset]['recall_testcase'])
            data['power']['f1'].append(dataraw[dataset]['f1_testcase'])
            dataraw = json.load(open(f"log/ours_{llm}_rc_{dataset}.json", "r", encoding="utf-8"))
            data['power']['rc'].append(dataraw[dataset])

    
    # print(json.dumps(data, indent=4, ensure_ascii=False))

    x = np.arange(len(domain))              # 领域位置
    bar_width = 0.18                        # 柱子宽度
    fig, ax = plt.subplots(figsize=(6, 3))
    # 颜色（四种对比强烈）
    # colors = ["#3E7D9E", "#E8926F", "#69A17A", "#8E6C8A"]
    colors = ["#3A86A8", "#F4A261", "#6AB47C", "#9D6B9E"]
    # colors = ["#2C5F7D", "#D87C5F", "#4E7D5F", "#7D5F7D"]
    # 画每个指标
    labels = ["Precision", "Recall", "F1", "BSC"]

    for m in metric:
        for d in domain:
            for i in range(len(data[d][m])):
                data[d][m][i] = data[d][m][i] * 100

    for i, m in enumerate(metric):
        values = [np.mean(data[d][m]) for d in domain]
        ax.bar(x + i * bar_width, values, width=bar_width, color=colors[i], label=labels[i], capsize=5)
        
        if m == "rc":
            for d in domain:
                data[d][m].remove(min(data[d][m]))
                break

        ax.scatter(x + i * bar_width, [min(data[d][m]) for d in domain], marker='_', s=200, color='black', linewidth=1.5)
        ax.scatter(x + i * bar_width, [max(data[d][m]) for d in domain], marker='_', s=200, color='black', linewidth=1.5)
        for xi in x:
            ax.vlines(xi + i * bar_width, min(data[domain[xi]][m]), max(data[domain[xi]][m]), colors='black', linestyles='-', linewidth=1.5)
        
    ax.set_xlabel("Domain", fontsize=15)
    ax.set_ylabel("Metric (%)", fontsize=15)
    ax.set_xticks(x + bar_width * (len(metric) - 1) / 2)
    ax.set_xticklabels([d.capitalize() for d in domain], fontsize=13)
    ax.tick_params(axis='y', labelsize=13)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.set_ylim(0, 105)
    ax.legend(fontsize=13, ncol=4, loc='upper center', bbox_to_anchor=(0.5, 1.25), handletextpad=0.2, columnspacing=0.5)
    ax.grid(axis="y", linestyle="--", alpha=0.5)


    plt.tight_layout()
    plt.savefig("fig/exp3.png", dpi=300)



if __name__ == "__main__":
    draw_figure()