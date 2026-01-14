import copy
import numpy as np
import matplotlib.pyplot as plt
import json


def draw_figure():
    # load data
    # data = {method: [values of 6 datasets]}
    data = {
        "Expert": {
            # "definition": 4 * 3600,
            "generation": (1.486+2.042+2.814+0.936+1.725+1.414) * 3600 / 2,
            "revise": 0.5 * 3600
        },
        "LLM4Fin": {
            "definition": 2*7*24*3600,
            "generation": 9.6 * 6,
            "revise": 3600 * 2
        },
        "E2E LLM": {
            "generation": (20.616667 * 6 * 60 + 33.45 * 6 * 60 + 29.516667 * 6 * 60) / 3 / 2,
            "revise": 3600 * 5
        },
        # "Ours Ind.": {
        #     "definition": 3.2 * 60,
        #     "generation": 11.5 * 60 * 6
        # },
        "Ours Agg.": {
            "definition": 19.6 * 60,
            "generation": 11.5 * 60 * 6,
            "revise": 3600
        },
    }
    for method in data:
        for metric in data[method]:
            data[method][metric] /= 60


    
    labels = list(data.keys())
    x = np.arange(len(labels))
    x = list(x)
    width = 0.35

    definition_times = [data[label].get("definition", 0) for label in labels]
    generation_times = [data[label].get("generation", 0) for label in labels]
    revise_times = [data[label].get("revise", 0) for label in labels]
    total_times = [definition_times[i] + generation_times[i] + revise_times[i] for i in range(len(labels))]


    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10,4), sharex=True, gridspec_kw={'height_ratios': [1, 3]})

    # 上半部分：展示极值范围
    ax1.bar(x[1] - width, definition_times[1], width, color="#369bff", label='Exp.')
    # ax1.plot(x, total_times, color='#d62728', marker='o', linestyle='-', linewidth=3, label='Total', markersize=13)
    ax1.hlines(y=total_times[1], xmin=x[1]-width*1.5, xmax=x[1]+width*1.5, colors='#d62728', linestyles='-', linewidth=3)
    ax1.plot(x[1], total_times[1], color='#d62728', marker='o', markersize=13, label="Total", linewidth=3)
    ax1.bar(x[1], generation_times[1], width, color='#ffb066', label='Gen.')
    ax1.bar(x[1] + width, revise_times[1], width, color='#438D42', label='Rev.')
    ax1.text(x[1], total_times[1]+80, 
                        f'2 weeks', ha='center', fontsize=20, color="#d62728")
    ax1.set_ylim(20000, 20550)
    ax1.set_yticks([20100, 20300])
    ax1.tick_params(axis='y', labelsize=22)
    ax1.spines['bottom'].set_visible(False)  # 隐藏下边框
    ax1.tick_params(axis='x', bottom=False)  # 隐藏x轴刻度
    ax1.grid(axis='y', linestyle='--', alpha=0.7)


    # 下半部分：展示常规数据
    for i, label in enumerate(labels):
        def_time = definition_times[i]
        gen_time = generation_times[i]
        rev_time = revise_times[i]
        
        if def_time > 0:
            if gen_time < 10:
                plt.text(x[i], gen_time+7, 
                        f'~{gen_time:.0f}m', ha='center', fontsize=20, color="#d62728")
            ax2.bar(x[i] - width, def_time, width, color="#369bff", label='Exp.' if i==1 else "")
            ax2.bar(x[i], gen_time, width, color='#ffb066', label='Gen.' if i==1 else "")
            ax2.bar(x[i] + width, rev_time, width, color='#438D42', label='Rev.' if i==1 else "")
        else:
            ax2.bar(x[i] - width / 2, gen_time, width, color='#ffb066', label='Gen.' if i==1 else "")
            ax2.bar(x[i] + width / 2, rev_time, width, color='#438D42', label='Rev.' if i==1 else "")


    # ax1.set_yscale('log')
    ax2.set_ylabel('Time (m)', fontsize=22)
    ax2.spines['top'].set_visible(False)  # 隐藏上边框
    ax2.set_xticks(x)
    ax2.set_xticklabels(["Expert", "LLM4Fin", "E2E LLM", "RAFT"], fontsize=22)
    # ax1.set_ylim(1, 10**7)
    # ax1.set_yticks([1, 10, 100, 1000, 10000, 100000, 1000000, 10000000])
    ax2.set_yticks([0, 100, 200, 300, 400])
    ax2.set_ylim(0, 450)
    ax2.tick_params(axis='y', labelsize=22)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    for i in [0, 2, 3]:
        if i == 3:
            ax2.hlines(y=total_times[i], xmin=x[i]-width*1.5, xmax=x[i]+width*1.5, colors='#d62728', linestyles='-', linewidth=3)
        else:
            ax2.hlines(y=total_times[i], xmin=x[i]-width, xmax=x[i]+width, colors='#d62728', linestyles='-', linewidth=3)
        ax2.plot(x[i], total_times[i], color='#d62728', marker='o', markersize=13, label="Total", linewidth=3)

    # 绘制一个好看的 legend，边距很小，阴影，紧凑
    fig.legend(handles=ax1.get_legend_handles_labels()[0],  # 获取ax1的图例元素
        labels=ax1.get_legend_handles_labels()[1],   # 获取ax1的图例标签
        loc='upper right', fontsize=22, frameon=True, shadow=True, ncol=1, borderpad=0.3, labelspacing=0.2, handletextpad=0.4, bbox_to_anchor=(0.96, 0.95))

    for i, val in enumerate(total_times):
        if i == 1:
            continue
        # 将秒数转换成小时或周数示例
        text = f"{val/60:.1f}h"
        ax2.text(x[i], val + 15, text, ha='center', va='bottom', fontsize=20, color='#d62728')
    
    d = 0.5
    kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
              linestyle="none", color='k', mec='k', mew=1, clip_on=False)
    ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
    ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

    plt.tight_layout()
    plt.savefig(f'fig/exp1_time.png', dpi=300, bbox_inches='tight')





if __name__ == "__main__":
    draw_figure()