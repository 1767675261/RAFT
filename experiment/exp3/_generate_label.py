import json
import random

rate = [0.33, 0.33, 0.34]
rate2 = [0.33, 0.33, 0.34]
random.seed(42)

def generate_testcase():
    for i in range(1, 6):
        if i != 4:
            continue
        ours_deepseek = json.load(open(f"deepseek_ours/dataset{i}.json", "r", encoding="utf-8"))
        ours_deepseek = [item['testcase'] for item in ours_deepseek if item['testcase'] != []]
        ours_deepseek = [tc for sublist in ours_deepseek for tc in sublist]
        ours_gpt = json.load(open(f"gpt_ours/dataset{i}.json", "r", encoding="utf-8"))
        ours_gpt = [item['testcase'] for item in ours_gpt if item['testcase'] != []]
        ours_gpt = [tc for sublist in ours_gpt for tc in sublist]
        ours_grok = json.load(open(f"grok_ours/dataset{i}.json", "r", encoding="utf-8"))
        ours_grok = [item['testcase'] for item in ours_grok if item['testcase'] != []]
        ours_grok = [tc for sublist in ours_grok for tc in sublist]
        total = (len(ours_deepseek) + len(ours_gpt) + len(ours_grok)) // 3
        num_deepseek = int(total * rate[0])
        num_gpt = int(total * rate[1])
        num_grok = total - num_deepseek - num_gpt
        sampled_deepseek = random.sample(ours_deepseek, min(num_deepseek, len(ours_deepseek)))
        sampled_gpt = random.sample(ours_gpt, min(num_gpt, len(ours_gpt)))
        sampled_grok = random.sample(ours_grok, min(num_grok, len(ours_grok)))
        print(total, len(sampled_deepseek), len(sampled_gpt), len(sampled_grok), len(ours_deepseek), len(ours_gpt), len(ours_grok))
        final_testcases = sampled_deepseek + sampled_gpt + sampled_grok
        random.shuffle(final_testcases)
        with open(f"testcase/dataset{i}.json", "w", encoding="utf-8") as f:
            json.dump(final_testcases, f, ensure_ascii=False, indent=4)


def generate_requirement():
    for i in range(1, 6):
        # if i not in [3,4,5]:
        #     continue
        ours_deepseek = json.load(open(f"deepseek_ours/dataset{i}.json", "r", encoding="utf-8"))
        trl_ours_deepseek = [item['trl_postprocess'] for item in ours_deepseek if 'trl_postprocess' in item]
        ours_gpt = json.load(open(f"gpt_ours/dataset{i}.json", "r", encoding="utf-8"))
        trl_ours_gpt = [item['trl_postprocess'] for item in ours_gpt if 'trl_postprocess' in item]
        ours_grok = json.load(open(f"grok_ours/dataset{i}.json", "r", encoding="utf-8"))
        trl_ours_grok = [item['trl_postprocess'] for item in ours_grok if 'trl_postprocess' in item]

        def generate_req(trl):
            lines = trl.split("\n")
            req = {}
            s = []
            for line in lines:
                if line.strip() == "":
                    continue
                if "if" in line or "then" in line:
                    words = line.split(" ")
                    i = 1
                    while i < len(words):
                        j = i + 1
                        while j < len(words) and words[j] != "and":
                            j += 1
                        if i+2 >= j:
                            i = j + 1
                            continue
                        key, op, values = words[i], words[i+1], words[i+2:j]
                        value = " ".join(values)
                        if op not in ["=", "!="]:
                            value = op + value
                        if key not in req:
                            req[key] = value
                        else:
                            req[key] = req[key] + "," + value
                        i = j + 1
                    if "then" in line:
                        si = ""
                        for key in req:
                            si += f"{key}:{req[key]};"
                        si = si[:-1]
                        s.append(si)
                        req = {}
            return s

        req_ours_deepseek = []
        for trl in trl_ours_deepseek:
            req_ours_deepseek.extend(generate_req(trl))
        req_ours_gpt = []
        for trl in trl_ours_gpt:
            req_ours_gpt.extend(generate_req(trl))
        req_ours_grok = []
        for trl in trl_ours_grok:
            req_ours_grok.extend(generate_req(trl))
        n1, n2, n3 = len(req_ours_deepseek), len(req_ours_gpt), len(req_ours_grok)
        total = (n1 + n2 + n3) // 3
        num_deepseek = int(total * rate2[0])
        num_gpt = int(total * rate2[1])
        num_grok = total - num_deepseek - num_gpt
        sampled_deepseek = random.sample(req_ours_deepseek, min(num_deepseek, len(req_ours_deepseek)))
        sampled_gpt = random.sample(req_ours_gpt, min(num_gpt, len(req_ours_gpt)))
        sampled_grok = random.sample(req_ours_grok, min(num_grok, len(req_ours_grok)))
        print(total, len(sampled_deepseek), len(sampled_gpt), len(sampled_grok), len(req_ours_deepseek), len(req_ours_gpt), len(req_ours_grok))
        final_reqs = sampled_deepseek + sampled_gpt + sampled_grok
        random.shuffle(final_reqs)
        s = "\n".join(final_reqs).replace("\n\n", "\n")
        with open(f"requirement/dataset{i}.txt", "w", encoding="utf-8") as f:
            f.write(s)




if __name__ == "__main__":
    # generate_testcase()
    generate_requirement()


    # for i in range(1, 7):
    #     data = json.load(open(f"deepseek_ours/dataset{i}.json", "r", encoding="utf-8"))
    #     rules = []
    #     for d in data:
    #         if d['testable'] == True:
    #             rules.append(d['rule_cn'])
    #     scenario = "\n".join(rules)
    #     with open(f"requirement/dataset{i}_req.txt", "w", encoding="utf-8") as f:
    #         f.write(scenario)
