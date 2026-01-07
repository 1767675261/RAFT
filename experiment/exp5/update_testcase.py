import json


def update_testcase(keys, x):
    for llm in ["deepseek", "gpt", "grok"]:
        for i in range(1, 7):
            data = json.load(open(f"{llm}_ours/dataset{i}_1.json", "r", encoding="utf-8"))
            for d in data:
                for j, tc in enumerate(d['testcase']):
                    new_tc = {}
                    for key in keys:
                        if key in tc:
                            new_tc[key] = tc[key]
                            k = 2
                            while f"{key}{k}" in tc:
                                new_tc[f"{key}{k}"] = tc[f"{key}{k}"]
                                k += 1
                    d['testcase'][j] = new_tc
            json.dump(data, open(f"{llm}_ours/dataset{i}_{x}.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)



if __name__ == "__main__":
    config = json.load(open("config.json", "r", encoding="utf-8"))
    c = config[0]
    n = len(c)
    for keys in config[1:]:
        x = round(len(keys) / n, 3)
        update_testcase(keys, x)


