import copy
import numpy as np
import matplotlib.pyplot as plt
import json


def draw_figure(item):
    data = json.load(open("result/eval_result.json", "r", encoding="utf-8"))
    x_ind, y_ind = [], []
    x_agg, y_agg = [], []

    for record in data["individual"]:
        x_ind.append(float(record["params"][:-1]))
        if item == "metamodel":
            y_ind.append(record["metamodel_complete"])
        else:
            y_ind.append(record["representation_complete"])
    for record in data["aggregated"]:
        x_agg.append(float(record["params"][:-1]))
        if item == "metamodel":
            y_agg.append(record["metamodel_complete"])
        else:
            y_agg.append(record["representation_complete"])
    
    plt.figure(figsize=(6, 3.5))
    plt.plot(x_ind, y_ind, label="Ind. LLMs", color="#2979FF", marker='o', markersize=13)
    plt.plot(x_agg, y_agg, label="Agg. LLMs", color="#ff7f0e", marker='s', markersize=13)
    plt.xscale('log')
    plt.xlabel("Parameters (B)", fontsize=25)
    plt.ylabel("Completion (%)", fontsize=25)
    # 紧凑一些
    plt.legend(fontsize=20, loc='upper left', markerscale=1.2, handletextpad=0.2, columnspacing=0.2, borderpad=0.2, labelspacing=0.2, handlelength=1.5, borderaxespad=0.1, shadow=False)
    plt.xlim(0, 1500)
    plt.xticks([1, 10, 100, 1000], fontsize=25)
    if item == "metamodel":
        plt.yticks([30, 50, 70, 90], fontsize=25)
    else:
        plt.yticks([50, 60, 70, 80, 90, 100], fontsize=25)
    plt.grid(True, which="both", ls="--", linewidth=0.5)
    plt.tight_layout()
    plt.savefig(f"fig/exp3_{item}_completion.png")


if __name__ == "__main__":
    draw_figure("metamodel")
    draw_figure("representation")