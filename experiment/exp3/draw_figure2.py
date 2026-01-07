import copy
import numpy as np
import matplotlib.pyplot as plt
import json


def draw_figure():
    # load data
    # data = {method: [values of 6 datasets]}
    data = {
        "Expert": {
            "definition": 4 * 3600,
            "generation": (3.917+5.303+7.825+1.75+3.269) * 3600
        },
        "TARGET": {
            "definition": 4*3600,
            "generation": (9.2+22.8+17.4) / 3 * 5 * 60
        },
        "E2E LLM": {
            "generation": (11.15+22.42+21.15+14+18.65+13.2+18.93+20.23+12.03+15.37+14.32+25.28+27.4+16.13+21.17) * 60 / 3
        },
        "Ours Ind.": {
            "definition": 3.2 * 60,
            "generation": (3.17+12.32+6.67+5.15+11.77) * 60
        },
        "Ours Agg.": {
            "definition": 9.6 * 60,
            "generation": (11.5+12.3+10.2+9.8+13.1) * 60
        },
    }


    
    labels = list(data.keys())
    x = np.arange(len(labels))
    x = list(x)
    width = 0.35

    definition_times = [data[label].get("definition", 0) for label in labels]
    generation_times = [data[label].get("generation", 0) for label in labels]
    total_times = [definition_times[i] + generation_times[i] for i in range(len(labels))]

    fig, ax1 = plt.subplots(figsize=(10,5))

    # 绘制柱状图，动态调整位置
    for i, label in enumerate(labels):
        def_time = definition_times[i]
        gen_time = generation_times[i]
        
        if def_time > 0:
            ax1.bar(x[i] - width/2, def_time, width, color='#69b3ff', label='Ext. Time' if i==0 else "")
            ax1.bar(x[i] + width/2, gen_time, width, color='#ffb066', label='Gen. Time' if i==0 else "")
        else:
            ax1.bar(x[i], gen_time, width, color='#ffb066', label='Gen. Time' if i==0 else "")


    ax1.set_yscale('log')
    ax1.set_ylabel('Ext. & Gen. Time (s)', fontsize=22)
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(["Expert", "TARGET", "E2E LLM", "Ours Ind.", "Ours Agg."], fontsize=22)
    ax1.set_ylim(1, 10**7)
    ax1.set_yticks([1, 10, 100, 1000, 10000, 100000, 1000000, 10000000])
    ax1.tick_params(axis='y', labelsize=22)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # 右轴显示总时间折线
    ax2 = ax1.twinx()
    ax2.plot(x, total_times, color='#d62728', marker='o', linestyle='-', linewidth=3, label='Total Time', markersize=10)
    ax2.set_yscale('log')
    # ax2.set_ylabel('Total Time (s)', fontsize=25)
    ax2.set_ylim(1, 10**7)
    ax2.tick_params(axis='y', which='both', length=0, labelleft=False, labelright=False)  # 不要右边的刻度线

    # 获取左轴 legend 对象
    handles1, labels1 = ax1.get_legend_handles_labels()
    # 获取右轴 legend 对象
    handles2, labels2 = ax2.get_legend_handles_labels()

    # 合并
    handles = handles1 + handles2
    labels = labels1 + labels2

    # 绘制一个好看的 legend，边距很小，阴影，紧凑
    ax1.legend(handles, labels, loc='upper right', fontsize=22, frameon=True, shadow=True)

    for i, val in enumerate(total_times):
        # 将秒数转换成小时或周数示例
        if val >= 7*24*3600:  # 大于一周
            text = f"{val/(7*24*3600):.0f} weeks"
        elif val >= 3600*4:  # 大于一小时
            text = f"{val/3600:.0f}h"
        else:
            text = f"{val/60:.0f}m"
        if i == 0:
            x[i] -= 0.1
        elif i ==2:
            x[i] += 0.23
        ax1.text(x[i], val*1.3, text, ha='center', va='bottom', fontsize=20, color='#d62728')

    plt.tight_layout()
    plt.savefig(f'fig/exp3_time.png', dpi=300, bbox_inches='tight')





if __name__ == "__main__":
    draw_figure()