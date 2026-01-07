from testcase.generate_testcase import generate_testcase
from trl.post_process import post_process
import json
import time


# 前置操作：生成TRL，自行使用模型和OpenAI API生成，略

def generate_testcase_ours():
    for j in range(1, 7):
        for l in ['deepseek', 'gpt', 'grok']:
            begin_time = time.time()

            print(f"Generating Testcase for {l} dataset {j}...")
            print(f"Post-processing {l} dataset {j}...")
            data = json.load(open(f"{l}_ours/dataset{j}.json", "r", encoding="utf-8"))
            preds = []
            for d in data:
                if not d['testable'] or d['trl'] == "":
                    continue
                preds.append(d['trl'])
            new_preds = post_process(preds)
            i = 0
            for d in data:
                if not d['testable'] or d['trl'] == "":
                    continue
                d['trl_postprocess'] = new_preds[i]
                i += 1
            json.dump(data, open(f"{l}_ours/dataset{j}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)



            data = json.load(open(f"{l}_ours/dataset{j}.json", "r", encoding="utf-8"))
            formatted_data = []
            for d in data:
                if not d['testable'] or d['trl'] == "":
                    continue
                formatted_data.append({
                    "rule": d['rule_cn'],
                    "predict": d['trl_postprocess']
                })
            testcases = generate_testcase(formatted_data)
            i = 0
            for d in data:
                if i >= len(testcases):
                    break
                if not d['testable'] or d['trl'] == "":
                    continue
                del d['testcase']
                d['testcase'] = testcases[i]['testcase']
                i += 1
            json.dump(data, open(f"{l}_ours/dataset{j}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
            
            time_spend = time.time() - begin_time
            print(f"Done. Time Spend: {time_spend}")


if __name__ == "__main__":
    generate_testcase_ours()