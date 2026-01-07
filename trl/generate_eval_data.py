import json
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_dir = "../model/Qwen3-8B"
tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_dir, trust_remote_code=True, torch_dtype=torch.float16, device_map="auto")
model.eval()

def chat(trl):
    system_prompt = """
我会给你一种结构化表达的语句，每个语句为“key op value”的形式，请你帮我生成一些key-value的枚举。你在生成枚举的时候，可以根据语句中的条件进行组合（即可以枚举所有的key，也可以省略一些key），如果是时间、数量、价格等具体的数值，请生成具体的数值而不是抽象的描述。请确保生成的枚举内容符合逻辑且多样化。
请将生成的枚举内容以JSON数组的形式返回，每个枚举项为一个JSON对象，包含所有相关的key-value对，并添加一个"结果"字段，表示该枚举的结果（例如“成功”或“失败”）。请确保输出的JSON格式正确且易于解析。
以下是一个示例：
输入：
rule 1
if 操作 is 停止接受 and 操作部分 is 买入申报
then 时间 is 当日 and 操作 is 不再恢复
输出：
[
    {
        "操作": "停止接受",
        "操作部分": "买入申报",
        "时间": "当日",
        "操作部分": "不再恢复",
        "结果": "成功"
    },
    {
        "操作": "停止接受",
        "操作部分": "卖出申报",
        "时间": "次日",
        "操作部分": "不再恢复",
        "结果": "失败"
    },
    ...
]
"""
    user_prompt = trl
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    text = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False, enable_thinking=False)
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=4096
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
    try:
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0
    
    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
    print(f"Rule: {trl}\nResponse: {content}\n\n")
    testcases = []
    try:
        testcases = json.loads(content)
    except json.JSONDecodeError:
        lines = content.split("\n")
        testcase = {}
        for line in lines:
            line = line.strip()
            if "{" in line or "}" in line:
                if testcase:
                    testcases.append(testcase)
                    testcase = {}
            else:
                key, value = line.split(":")[0].strip(), ":".join(line.split(":")[1:]).strip()
                key, value = key.replace("\"", ""), value.replace("\"", "")
                testcase[key] = value
        if testcase:
            testcases.append(testcase)
    return testcases



def generate_eval_data(trl_file, output_file):
    datas = json.load(open(trl_file, "r", encoding="utf-8"))
    for data in datas:
        trl = data['answer'].split("or relation")[0].strip()
        response = chat(trl)
        data['testcase'] = response
        del data['predict']
    json.dump(datas, open(output_file, "w", encoding="utf-8"), ensure_ascii=False, indent=4)




if __name__ == "__main__":
    for file in os.listdir("result"):
        if "postprocess_deepseek" in file:
            input_file = os.path.join("result", file)
            output_file = os.path.join("eval_data", file.split("_")[-1].replace(".json", "_eval.json"))
            generate_eval_data(input_file, output_file)

