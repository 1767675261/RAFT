import copy
import numpy as np
import matplotlib.pyplot as plt
import json


def draw_figure(metric):
    x = [0.067, 0.133, 0.2, 0.267, 0.333, 0.4, 0.467, 0.533, 0.6, 0.667, 0.733, 0.8, 0.867, 0.933, 1]
    y = [0 for _ in range(len(x))]
    for llm in ["deepseek", "gpt", "grok"]:
        for i in range(1, 7):
            for j, xi in enumerate(x):
                if "rc" not in metric:
                    data = json.load(open(f"log/ours_{llm}_prf_dataset{i}_{xi}.json", "r", encoding="utf-8"))
                    y[j] += data[f"dataset{i}"][f"{xi}"][metric]
                else:
                    data = json.load(open(f"log/ours_{llm}_rc_dataset{i}_{xi}.json", "r", encoding="utf-8"))
                    y[j] += data[f"dataset{i}"][f"{xi}"]
    y = [yi / (6 * 3) * 100 for yi in y]
    x.insert(0, 0)
    y.insert(0, 0)

    plt.figure(figsize=(6, 3.5))
    plt.plot(x, y, label="Ours", color="#2979FF", marker='o', markersize=13)
    plt.xlabel("Knowledge Completeness", fontsize=25)
    if "rc" not in metric:
        yl = metric.split("_")[0].capitalize()  # capitalize the first letter
    else:
        yl = "BSC"
    plt.ylabel(yl + " (%)", fontsize=25)
    plt.xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0], fontsize=25)
    plt.yticks(fontsize=25)
    plt.ylim(-5, 100)
    plt.grid(True, which="both", ls="--", linewidth=0.5)
    plt.tight_layout()
    plt.savefig(f"fig/exp4_ours_{metric}.png")

if __name__ == "__main__":
    draw_figure("precision_testcase")
    draw_figure("recall_testcase")
    draw_figure("f1_testcase")
    draw_figure("rc")