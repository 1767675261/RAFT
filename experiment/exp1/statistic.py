import json


def count_rule_num():
    for i in range(1, 7):
        data = json.load(open(f"deepseek_ours/dataset{i}.json", "r", encoding="utf-8"))
        print(f"Dataset {i}: {len(data)} rules.")


def compute_requirement_num():
    for i in range(1, 7):
        data = open(f"requirement/dataset{i}.txt", "r", encoding="utf-8").read()
        lines = data.split("\n")
        print(f"Dataset {i}: {len(lines)} requirements.")

def count_testcase_num():
    for i in range(1, 7):
        data = json.load(open(f"testcase/dataset{i}.json", "r", encoding="utf-8"))
        print(f"Dataset {i} Testcases: {len(data)} cases.")



if __name__ == "__main__":
    count_rule_num()
    compute_requirement_num()
    count_testcase_num()