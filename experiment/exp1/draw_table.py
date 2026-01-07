import json
import numpy as np

s = "Method,Metrics,Dataset1,Dataset2,Dataset3,Dataset4,Dataset5,Dataset6,Average,Variance\n"

ours = {
    "precision": {
        "dataset1": [],
        "dataset2": [],
        "dataset3": [],
        "dataset4": [],
        "dataset5": [],
        "dataset6": []
    },
    "recall": {
        "dataset1": [],
        "dataset2": [],
        "dataset3": [],
        "dataset4": [],
        "dataset5": [],
        "dataset6": []
    },
    "f1": {
        "dataset1": [],
        "dataset2": [],
        "dataset3": [],
        "dataset4": [],
        "dataset5": [],
        "dataset6": []
    },
    "coverage": {
        "dataset1": [],
        "dataset2": [],
        "dataset3": [],
        "dataset4": [],
        "dataset5": [],
        "dataset6": []
    }
}
llm = {
    "precision": {
        "dataset1": [],
        "dataset2": [],
        "dataset3": [],
        "dataset4": [],
        "dataset5": [],
        "dataset6": []
    },
    "recall": {
        "dataset1": [],
        "dataset2": [],
        "dataset3": [],
        "dataset4": [],
        "dataset5": [],
        "dataset6": []
    },
    "f1": {
        "dataset1": [],
        "dataset2": [],
        "dataset3": [],
        "dataset4": [],
        "dataset5": [],
        "dataset6": []
    },
    "coverage": {
        "dataset1": [],
        "dataset2": [],
        "dataset3": [],
        "dataset4": [],
        "dataset5": [],
        "dataset6": []
    }
}

for method in ["expert", "llm4fin", "deepseek", "gpt", "grok", "ours_deepseek", "ours_gpt", "ours_grok"]:
    p, r, f, c = [], [], [], []
    for i in range(1, 7):
        prf = json.load(open(f"log/{method}_prf_dataset{i}.json", "r", encoding="utf-8"))
        p.append(prf[f'dataset{i}']['precision_testcase'])
        r.append(prf[f'dataset{i}']['recall_testcase'])
        f.append(prf[f'dataset{i}']['f1_testcase'])
        rc = json.load(open(f"log/{method}_rc_dataset{i}.json", "r", encoding="utf-8"))
        c.append(rc[f'dataset{i}'])
        if method == "gpt" or method == "grok" or method == "deepseek":
            llm['precision'][f'dataset{i}'].append(prf[f'dataset{i}']['precision_testcase'])
            llm['recall'][f'dataset{i}'].append(prf[f'dataset{i}']['recall_testcase'])
            llm['f1'][f'dataset{i}'].append(prf[f'dataset{i}']['f1_testcase'])
            llm['coverage'][f'dataset{i}'].append(rc[f'dataset{i}'])
        if method == "ours_gpt" or method == "ours_grok" or method == "ours_deepseek":
            ours['precision'][f'dataset{i}'].append(prf[f'dataset{i}']['precision_testcase'])
            ours['recall'][f'dataset{i}'].append(prf[f'dataset{i}']['recall_testcase'])
            ours['f1'][f'dataset{i}'].append(prf[f'dataset{i}']['f1_testcase'])
            ours['coverage'][f'dataset{i}'].append(rc[f'dataset{i}'])
    s += f"{method},Precision (%),{','.join([str(round(x*100,2)) for x in p])},{round(sum(p)/len(p)*100,2)},{round(np.var([pi * 100 for pi in p]),2)}\n"
    s += f",Recall (%),{','.join([str(round(x*100,2)) for x in r])},{round(sum(r)/len(r)*100,2)},{round(np.var([ri * 100 for ri in r]),2)}\n"
    s += f",F1 (%),{','.join([str(round(x*100,2)) for x in f])},{round(sum(f)/len(f)*100,2)},{round(np.var([fi * 100 for fi in f]),2)}\n"
    s += f",Requirement Coverage (%),{','.join([str(round(x*100,2)) for x in c])},{round(sum(c)/len(c)*100,2)},{round(np.var([ci * 100 for ci in c]),2)}\n"

ours_agg_p, ours_agg_r, ours_agg_f, ours_agg_c = [], [], [], []
llm_agg_p, llm_agg_r, llm_agg_f, llm_agg_c = [], [], [], []
for k1 in ours:
    for k2 in ours[k1]:
        ours[k1][k2] = sum(ours[k1][k2]) / len(ours[k1][k2])
        if k1 == "precision":
            ours_agg_p.append(ours[k1][k2])
        elif k1 == "recall":
            ours_agg_r.append(ours[k1][k2])
        elif k1 == "f1":
            ours_agg_f.append(ours[k1][k2])
        elif k1 == "coverage":
            ours_agg_c.append(ours[k1][k2])
for k1 in llm:
    for k2 in llm[k1]:
        llm[k1][k2] = sum(llm[k1][k2]) / len(llm[k1][k2])
        if k1 == "precision":
            llm_agg_p.append(llm[k1][k2])
        elif k1 == "recall":
            llm_agg_r.append(llm[k1][k2])
        elif k1 == "f1":
            llm_agg_f.append(llm[k1][k2])
        elif k1 == "coverage":
            llm_agg_c.append(llm[k1][k2])

s += f"Ours_Aggregated,Precision (%),{','.join([str(round(x*100,2)) for x in ours_agg_p])},{round(sum(ours_agg_p)/len(ours_agg_p)*100,2)},{round(np.var([pi * 100 for pi in ours_agg_p]),2)}\n"
s += f",Recall (%),{','.join([str(round(x*100,2)) for x in ours_agg_r])},{round(sum(ours_agg_r)/len(ours_agg_r)*100,2)},{round(np.var([ri * 100 for ri in ours_agg_r]),2)}\n"
s += f",F1 (%),{','.join([str(round(x*100,2)) for x in ours_agg_f])},{round(sum(ours_agg_f)/len(ours_agg_f)*100,2)},{round(np.var([fi * 100 for fi in ours_agg_f]),2)}\n"
s += f",Requirement Coverage (%),{','.join([str(round(x*100,2)) for x in ours_agg_c])},{round(sum(ours_agg_c)/len(ours_agg_c)*100,2)},{round(np.var([ci * 100 for ci in ours_agg_c]),2)}\n"
s += f"LLM_Aggregated,Precision (%),{','.join([str(round(x*100,2)) for x in llm_agg_p])},{round(sum(llm_agg_p)/len(llm_agg_p)*100,2)},{round(np.var([pi * 100 for pi in llm_agg_p]),2)}\n"
s += f",Recall (%),{','.join([str(round(x*100,2)) for x in llm_agg_r])},{round(sum(llm_agg_r)/len(llm_agg_r)*100,2)},{round(np.var([ri * 100 for ri in llm_agg_r]),2)}\n"
s += f",F1 (%),{','.join([str(round(x*100,2)) for x in llm_agg_f])},{round(sum(llm_agg_f)/len(llm_agg_f)*100,2)},{round(np.var([fi * 100 for fi in llm_agg_f]),2)}\n"
s += f",Requirement Coverage (%),{','.join([str(round(x*100,2)) for x in llm_agg_c])},{round(sum(llm_agg_c)/len(llm_agg_c)*100,2)},{round(np.var([ci * 100 for ci in llm_agg_c]),2)}\n"






with open("fig/table.csv", 'w', encoding='utf-8') as f:
    f.write(s)