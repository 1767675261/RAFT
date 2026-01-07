import matplotlib.pyplot as plt
import json

import numpy as np

# colors = ["#1663A9", "#4995C6", "#92C2DD", "#D1D1D1"]
colors = ["#4d7cc5", "#f58e38", "#5AB05C", "#B8B8B8"]


# 画分组柱状图
def draw_figure(metric):
    # x轴为6个数据集，y轴为metric的值，每个数据集有4个柱子
    datasets = ['dataset1', 'dataset2', 'dataset3', 'dataset4', 'dataset5', 'dataset6']
    llms = ["deepseek", "gpt", "grok"]
    if metric in ["precision", "recall", "f1"]:
        methods = ["ours", "without_test", "without_repr", ""]
    else:
        methods = ["ours", "without_testability", "without_representation", ""]
    
    data = {dataset: {method: 0 for method in methods} for dataset in datasets}
    for dataset in datasets:
        for method in methods:
            for llm in llms:
                if method == "ours":
                    if metric in ["precision", "recall", "f1"]:
                        dataraw = json.load(open(f"log/{method}_{llm}_prf_{dataset}.json", "r", encoding="utf-8"))
                    else:
                        dataraw = json.load(open(f"log/{method}_{llm}_rc_{dataset}.json", "r", encoding="utf-8"))
                elif method == "":
                    if metric in ["precision", "recall", "f1"]:
                        dataraw = json.load(open(f"log/{llm}_prf_{dataset}.json", "r", encoding="utf-8"))
                    else:
                        dataraw = json.load(open(f"log/{llm}_rc_{dataset}.json", "r", encoding="utf-8"))
                else:
                    if metric in ["precision", "recall", "f1"]:
                        dataraw = json.load(open(f"log/{llm}_{method}_prf_{dataset}.json", "r", encoding="utf-8"))
                    else:
                        dataraw = json.load(open(f"log/{llm}_{method}_rc_{dataset}.json", "r", encoding="utf-8"))
                if metric in ["precision", "recall", "f1"]:
                    data[dataset][method] += dataraw[dataset][metric + "_testcase"] / len(llms)
                else:
                    data[dataset][method] += dataraw[dataset] / len(llms)
    
    for dataset in datasets:
        for method in methods:
            data[dataset][method] *= 100  # 转为百分比

    
    # 画图参数
    x = np.arange(len(datasets))              # 数据集位置
    bar_width = 0.22                           # 柱子宽度

    fig, ax = plt.subplots(figsize=(7, 4.5))

    # 画每个方法
    # labels = ["Full Knowledge (M+R+T)", "Representation Only (M+R)", "Testability Only (T)", "No Knowledge"]
    labels = ["M+R+T", "M+R", "T", "No Know."]
    for i, method in enumerate(methods):
        values = [data[ds][method] for ds in datasets]
        ax.bar(
            x + i * bar_width,
            values,
            width=bar_width,
            label=labels[i],
            color=colors[i],
            # edgecolor='black',
        )

    # 坐标轴与标签
    ax.set_xlabel("Dataset", fontsize=35)
    if metric == "rc":
        metric = "BSC"
    else:
        metric = metric.capitalize()
    # ax.set_ylabel(f"{metric} (%)", fontsize=35)
    ax.set_xticks(x + bar_width * (len(methods) - 1) / 2)
    ax.set_xticklabels([i for i in range(1, 7)], fontsize=35)
    ax.tick_params(axis='y', labelsize=35)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.set_ylim(0, 100)


    # 美化
    ax.grid(axis="both", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(f"fig/exp2_{metric}.pdf", dpi=300)



def draw_legend():
    labels = ["M+R+T", "M+R", "T", "No Know."]
    fig = plt.figure(figsize=(1, 2))
    ax = fig.add_subplot(111)
    bars = [ax.bar([0], [0], color=c, label=l) for c, l in zip(colors, labels)]
    legend = ax.legend(fontsize=30, ncol=4, loc="center", handletextpad=0.4, # 颜色块到文字的距离
        columnspacing=1.5, # 列与列之间的距离
        edgecolor='black',
        frameon=True)
    legend.get_frame().set_linewidth(1.0)
    ax.axis('off')
    fig.canvas.draw()
    bbox = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

    plt.savefig("fig/exp2_legend.pdf", dpi=300, bbox_inches=bbox.expanded(1.005, 1.02))


def draw_figure2():
    datasets = [f"dataset{i}" for i in range(1, 7)]
    metrics = ["precision", "recall", "f1", "rc"]
    llms = ["deepseek", "gpt", "grok"]
    methods = ["ours", "without_test", "without_repr", ""]
    labels = ["M+R+T", "M+R", "T", "No Know."]

    num_datasets = len(datasets)
    gap = 0.46
    bar_width = 0.23
    fig, ax = plt.subplots(figsize=(26, 6.5))

    xticks = []
    xtick_labels = []
    base_x = 0

    data = {dataset: {method: {metric: 0 for metric in metrics} for method in methods} for dataset in datasets}
    for dataset in datasets:
        for method in methods:
            for llm in llms:
                for metric in metrics:
                    if method == "ours":
                        dataraw = json.load(open(f"log/{method}_{llm}_{'prf' if metric != 'rc' else 'rc'}_{dataset}.json", "r", encoding="utf-8"))
                    elif method == "":
                        dataraw = json.load(open(f"log/{llm}_{'prf' if metric != 'rc' else 'rc'}_{dataset}.json", "r", encoding="utf-8"))
                    else:
                        if metric == "rc":
                            if method == "without_test":
                                method_file = "without_testability"
                            elif method == "without_repr":
                                method_file = "without_representation"
                            else:
                                method_file = method
                        else:
                            method_file = method
                        dataraw = json.load(open(f"log/{llm}_{method_file}_{'prf' if metric != 'rc' else 'rc'}_{dataset}.json", "r", encoding="utf-8"))
                    if metric in ["precision", "recall", "f1"]:
                        data[dataset][method][metric] += dataraw[dataset][metric + "_testcase"] / len(llms)
                    else:
                        data[dataset][method][metric] += dataraw[dataset] / len(llms)
            for metric in metrics:
                data[dataset][method][metric] *= 100  # 转为百分比
    
    for metric_id, metric in enumerate(metrics):
        d = {ds: {m:0 for m in methods} for ds in datasets}
        for dataset in datasets:
            for method in methods:
                d[dataset][method] = data[dataset][method][metric]
        
        x = np.arange(num_datasets) + base_x
        for i, method in enumerate(methods):
            values = [d[ds][method] for ds in datasets]
            ax.bar(
                x + i * bar_width,
                values,
                width=bar_width,
                label=labels[i] if metric_id == 0 else None,
                color=colors[i],
            )
        
        xticks.extend(x + bar_width*(len(methods)-1)/2)
        xtick_labels.extend([str(i) for i in range(1, num_datasets + 1)])

        center = x.mean() + bar_width * (len(methods) - 1) / 2
        if metric == "rc":
            metric_name = "BSC"
        else:
            metric_name = metric.capitalize()
        ax.text(center, 104, metric_name, ha='center', va='bottom', fontsize=35)

        base_x += num_datasets + gap
        ax.axvline(x=base_x - gap + 0.07, color='black', linestyle='-', linewidth=1)
            
    ax.set_xticks(xticks)
    ax.set_xticklabels(xtick_labels, fontsize=30)
    ax.set_ylim(0, 105)
    ax.set_yticks(np.arange(0, 101, 20))
    ax.tick_params(axis='y', labelsize=30)
    ax.set_xlabel("Dataset", fontsize=35)
    ax.set_ylabel("Metrics (%)", fontsize=35)
    ax.grid(axis="both", linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    left, right = -bar_width/2*3, base_x-gap
    ax.set_xlim(left, right)

    ax.legend(fontsize=30, loc='upper center', ncol=4, bbox_to_anchor=(0.5, 1.5), edgecolor='black')
    plt.tight_layout()
    plt.savefig(f"fig/exp2_all_metrics.png", dpi=300)







if __name__ == "__main__":
    # metrics = ["precision", "recall", "f1", "rc"]
    # for metric in metrics:
    #     draw_figure(metric)
    # draw_legend()


    draw_figure2()