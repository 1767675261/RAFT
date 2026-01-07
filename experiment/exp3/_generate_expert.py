import json
import random
random.seed(1024)


def generate_expert():
    for i in range(1, 6):
        expert = []
        for llm in ['gpt', 'grok', 'deepseek']:
            ours_data = json.load(open(f"{llm}_ours/dataset{i}.json", "r", encoding="utf-8"))
            ours_case = []
            for d in ours_data:
                ours_case.extend(d['testcase'])
            sel_case = random.sample(ours_case, int(len(ours_case) * 0.2))
            expert.extend(sel_case)

            llm_data = json.load(open(f"{llm}/dataset{i}.json", "r", encoding="utf-8"))
            llm_case = []
            for d in llm_data:
                llm_case.extend(d['testcase'])
            sel_case = random.sample(llm_case, int(len(ours_case) * 0.1))
            expert.extend(sel_case)
        for d in expert:
            if "id" in d:
                del d['id']
        json.dump(expert, open(f"expert/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)



if __name__ == "__main__":
    generate_expert()