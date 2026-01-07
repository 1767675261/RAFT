import json

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False



if __name__ == "__main__":
    for i in range(1, 6):
        data = open(f"dataset/dataset{i}.txt", "r", encoding="utf-8").read()
        if i == 1:
            rules = data.split("\n\n")
        elif i == 2 or i == 4 or i == 5:
            rules = data.split("\n")
        elif i == 3:
            rules = []
            s = ""
            for line in data.split("\n"):
                if len(line) > 3 and line[0] == "第" and (line[2] == "条" or line[3] == "条"):
                    num = line.split("第")[1].split("条")[0]
                    if not is_number(num):
                        s += line + "\n"
                    else:
                        if s != "":
                            rules.append(s.strip())
                        s = line + "\n"
                else:
                    s += line + "\n"
            if s != "":
                rules.append(s.strip())

        real_data = []
        for rule in rules:
            real_data.append({
                "rule": rule,
                "testcase": []
            })
        json.dump(real_data, open(f"deepseek/dataset{i}.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)
        json.dump(real_data, open(f"gpt/dataset{i}.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)
        json.dump(real_data, open(f"grok/dataset{i}.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)
        for d in real_data:
            d['trl'] = ""
        json.dump(real_data, open(f"deepseek_ours/dataset{i}.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)
        json.dump(real_data, open(f"gpt_ours/dataset{i}.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)
        json.dump(real_data, open(f"grok_ours/dataset{i}.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)