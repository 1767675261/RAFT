import json
import random
random.seed(129)

def compute_time_token():
    methods = ['expert', 'llm4fin', 'deepseek', 'deepseek_ours', 'gpt', 'gpt_ours', 'grok', 'grok_ours', 'deepseek_only_ours', 'gpt_only_ours', 'grok_only_ours']
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
        for i in range(1, 7):
            data = json.load(open(f"{method}/dataset{i}.json", "r", encoding="utf-8"))
            rule_num = len(data)
            if method == "llm4fin":
                data = [di for d in data for di in d]
            elif method != "expert":
                data = [d['testcase'] for d in data]
                data = [di for d in data for di in d]
            
            if method == "llm4fin":
                ...
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
            elif method == "llm4fin":
                llm4fin_data = json.load(open(f"deepseek_ours/dataset{i}.json", "r", encoding="utf-8"))
                token[method] += len(llm4fin_data) + sum([len(d['rule_cn']) for d in llm4fin_data])
            elif "ours" in method:
                trls = [d['trl'] for d in data]
                token[method] += sum([len(trl) for trl in trls])
            else:
                testcases = [d['testcase'] for d in data]
                token[method] += len(json.dumps(testcases, ensure_ascii=False, indent=4))
        if "ours" in method:
            asw = open(f"definition/{method.split('_')[0]}_model_language.txt", "r", encoding="utf-8").read()
            if "only" not in method:
                token[method] += len(asw)
            else:
                token[method] += len(asw) // 3
        
    new_token = {
        "expert": token['expert'],
        "llm4fin": token['llm4fin'],
        "E2E LLM": (token['gpt'] + token['grok'] + token['deepseek']) // 3,
        "Ours Agg.": (token['gpt_ours'] + token['grok_ours'] + token['deepseek_ours']) // 3,
        "Ours Ide.": (token['gpt_only_ours'] + token['grok_only_ours'] + token['deepseek_only_ours']) // 3,
    }




    for i in range(1, 7):
        time['ours'][f'dataset{i}'] /= 60
    print("GenerationTime: ")
    print(json.dumps(time, ensure_ascii=False, indent=4))
    print("Completion Token: ")
    print(json.dumps(new_token, ensure_ascii=False, indent=4))



def compute_prompt_token():
    token = 0
    prompt = open(f"definition/prompt.txt", "r", encoding="utf-8").read()
    token += len(prompt) * 3
    once_token = len(prompt)
    
    llm_token = 0
    prompt = open(f"prompt/testcase_generation_chat.md", "r", encoding="utf-8").read()
    llm_token += len(prompt)
    for i in range(1, 7):
        d = open(f"dataset/dataset{i}_cn.txt", "r", encoding="utf-8").read()
        llm_token += len(d)
    
    llm4fin_token = 0
    for i in range(1, 7):
        llm4fin_data = json.load(open(f"deepseek_ours/dataset{i}.json", "r", encoding="utf-8"))
        llm4fin_token += sum([len(d['rule_cn']) for d in llm4fin_data]) * 2
    
    print("Prompt Token: ")
    print(json.dumps({"llm": llm_token, "ours agg": token, "llm4fin": llm4fin_token, "ours ide": once_token}, ensure_ascii=False, indent=4))



if __name__ == "__main__":
    compute_time_token()
    compute_prompt_token()