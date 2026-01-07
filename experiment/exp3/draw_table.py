import json

s = "Method,Metrics,Dataset1,Dataset2,Dataset3,Dataset4,Dataset5,Average\n"
for method in ["expert", "deepseek", "gpt", "grok", "ours_deepseek", "ours_gpt", "ours_grok"]:
    p, r, f, c = [], [], [], []
    for i in range(1, 6):
        prf = json.load(open(f"log/{method}_prf_dataset{i}.json", "r", encoding="utf-8"))
        p.append(prf[f'dataset{i}']['precision_testcase'])
        r.append(prf[f'dataset{i}']['recall_testcase'])
        f.append(prf[f'dataset{i}']['f1_testcase'])
        rc = json.load(open(f"log/{method}_rc_dataset{i}.json", "r", encoding="utf-8"))
        c.append(rc[f'dataset{i}'])
    s += f"{method},Precision (%),{','.join([str(round(x*100,2)) for x in p])},{round(sum(p)/len(p)*100,2)}\n"
    s += f",Recall (%),{','.join([str(round(x*100,2)) for x in r])},{round(sum(r)/len(r)*100,2)}\n"
    s += f",F1 (%),{','.join([str(round(x*100,2)) for x in f])},{round(sum(f)/len(f)*100,2)}\n"
    s += f",Requirement Coverage (%),{','.join([str(round(x*100,2)) for x in c])},{round(sum(c)/len(c)*100,2)}\n"

with open("fig/table.csv", 'w', encoding='utf-8') as f:
    f.write(s)