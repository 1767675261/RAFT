import json

def generate_testcase_framework_chat():
    for i in range(1, 7):
        data = open(f"dataset/dataset{i}.txt", "r", encoding="utf-8").read()
        res_data = []
        for line in data.split("\n"):
            line = line.strip()
            if not line:
                continue
            res_data.append({
                "rule": line,
                "text": "",
                "testcase": []
            })
        json.dump(res_data, open(f"deepseek/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
        json.dump(res_data, open(f"gpt/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
        json.dump(res_data, open(f"grok/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)


# 后续操作：生成测试用例，自行使用模型OpenAI API生成，略


if __name__ == "__main__":
    generate_testcase_framework_chat()