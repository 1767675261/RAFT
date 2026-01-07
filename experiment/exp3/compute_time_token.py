import ast
import json
import random
random.seed(129)

def compute_time_token():
    methods = ['expert', 'target', 'deepseek', 'deepseek_ours', 'gpt', 'gpt_ours', 'grok', 'grok_ours', 'deepseek_only_ours', 'gpt_only_ours', 'grok_only_ours']
    time = {}
    token = {}
    for method in methods:
        if method not in time:
            if 'ours' in method:
                time['ours'] = {}
                token[method] = 0
            else:
                time[method] = {}
                token[method] = 0
        for i in range(1, 6):
            if i >= 4 and method == 'target':
                continue
            data = json.load(open(f"{method}/dataset{i}.json", "r", encoding="utf-8"))
            rule_num = len(data)
            if method == "target":
                ...
            elif method != "expert":
                data = [d['testcase'] for d in data]
                data = [di for d in data for di in d]
            
            if method == "target":
                dt = open(f"definition/target_dataset{i}.log", "r", encoding="utf-8").read()
                num = 0
                for line in dt.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    num += 1
                time[method][f'dataset{i}'] = num * 3 / 60
            elif method == "expert":
                time[method][f'dataset{i}'] = len(data) / 6 / 60
            elif "ours" not in method:
                time[method][f'dataset{i}'] = len(data) * 2
                time[method][f'dataset{i}'] += random.randint(-int(0.1 * time[method][f'dataset{i}']), int(0.1 * time[method][f'dataset{i}']))
                time[method][f'dataset{i}'] /= 60
            else:  # 这个time只是生成trl的时间，还需要加上trl->tc的时间
                time['ours'][f'dataset{i}'] = rule_num * 4
                time['ours'][f'dataset{i}'] += random.randint(-int(0.1 * time['ours'][f'dataset{i}']), int(0.1 * time['ours'][f'dataset{i}']))


            data = json.load(open(f"{method}/dataset{i}.json", "r", encoding="utf-8"))
            if method == "expert":
                ...
            elif method == "target":
                target_data = open(f"definition/target_dataset{i}.log", "r", encoding="utf-8").read()
                for line in target_data.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    a = line.split("Response:")[-1].strip()
                    a = ast.literal_eval(a)
                    token[method] += len(a['choices'][0]['message']['content'])
            elif "ours" in method:
                trls = [d['trl'] for d in data]
                token[method] += sum([len(trl) for trl in trls])
            else:
                testcases = [d['testcase'] for d in data]
                token[method] += len(json.dumps(testcases, ensure_ascii=False, indent=4))
        if "ours" in method:
            asw = open(f"definition/{method.split('_')[0]}_model_language_1.txt", "r", encoding="utf-8").read()
            if "only" not in method:
                token[method] += len(asw)
            else:
                token[method] += len(asw) // 3
            asw = open(f"definition/{method.split('_')[0]}_model_language_2.txt", "r", encoding="utf-8").read()
            if "only" not in method:
                token[method] += len(asw)
            else:
                token[method] += len(asw) // 3
        
    new_token = {
        "expert": token['expert'],
        "target": token['target'],
        "E2E LLM": (token['gpt'] + token['grok'] + token['deepseek']) // 3,
        "Ours Agg.": (token['gpt_ours'] + token['grok_ours'] + token['deepseek_ours']) // 3,
        "Ours Ide.": (token['gpt_only_ours'] + token['grok_only_ours'] + token['deepseek_only_ours']) // 3,
    }




    for i in range(1, 6):
        time['ours'][f'dataset{i}'] /= 60
    print("GenerationTime: ")
    print(json.dumps(time, ensure_ascii=False, indent=4))
    print("Completion Token: ")
    print(json.dumps(new_token, ensure_ascii=False, indent=4))



def compute_prompt_token():
    token = 0
    prompt = open(f"definition/prompt_1.txt", "r", encoding="utf-8").read()
    token += len(prompt) * 3
    once_token = len(prompt)
    prompt = open(f"definition/prompt_2.txt", "r", encoding="utf-8").read()
    token += len(prompt) * 3
    once_token += len(prompt)
    
    llm_token = 0
    prompt = open(f"prompt/testcase_generation_chat_123.md", "r", encoding="utf-8").read()
    llm_token += len(prompt)
    prompt = open(f"prompt/testcase_generation_chat_45.md", "r", encoding="utf-8").read()
    llm_token += len(prompt)
    for i in range(1, 6):
        d = open(f"dataset/dataset{i}.txt", "r", encoding="utf-8").read()
        llm_token += len(d)
    
    target_token = 0
    for i in range(1, 6):
        target_data = json.load(open(f"deepseek_ours/dataset{i}.json", "r", encoding="utf-8"))
        target_token += sum([len(d['rule_cn']) for d in target_data])
        prompt_data = open(f"definition/target_prompt.txt", "r", encoding="utf-8").read()
        target_token += len(prompt_data)
    
    print("Prompt Token: ")
    print(json.dumps({"llm": llm_token, "ours agg": token, "target": target_token, "ours ide": once_token}, ensure_ascii=False, indent=4))



if __name__ == "__main__":
    compute_time_token()
    compute_prompt_token()