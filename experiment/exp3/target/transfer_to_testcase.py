import yaml
import json



from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


qwen3_model_path = "../../../model/Qwen3-8B"

model = AutoModelForCausalLM.from_pretrained(qwen3_model_path, device_map="auto", torch_dtype=torch.float16, trust_remote_code=True)
model.eval()
tokenizer = AutoTokenizer.from_pretrained(qwen3_model_path, trust_remote_code=True)



def qwen_chat(message, **kwargs):
    text = tokenizer.apply_chat_template(
        message,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=4096,
        **kwargs
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

    # parsing thinking content
    try:
        # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
    return content





for i in range(1, 4):
    data = json.load(open(f"dataset{i}.json", "r", encoding="utf-8"))
    for d in data:
        if 'scenario' not in d:
            continue
        scenario = d['scenario']
        scenario = yaml.safe_load(scenario)
        # 获得所有叶子节点的key-value
        def dfs(root, res):
            if isinstance(root, dict):
                for k, v in root.items():
                    if isinstance(v, dict):
                        dfs(v, res)
                    else:
                        if k in res:
                            i = 2
                            while f"{k}{i}" in res:
                                i += 1
                            res[f"{k}{i}"] = v
                        else:
                            res[k] = v
            return res
        res = dfs(scenario, {})
        if 'testable' in d:
            del d['testable']
        if "trl" in d:
            del d['trl']
        if "testcase" in d:
            del d['testcase']
        

        message = [
            {
                "role": "system",
                "content": "你是一个金融领域的专家，擅长理解领域知识和规则。现在我给你一条英文表述的json格式的测试用例，请帮我转为中文表述的测试用例，并严格按照我给你的json格式返回，不要添加任何额外的信息。",
            },
            {
                "role": "user",
                "content": f"请将以下json格式的测试用例的所有key和value都转为中文表述的测试用例，并严格按照我给你的json格式返回，不要添加任何额外的信息。\n测试用例：{json.dumps(res, ensure_ascii=False)}",
            }
        ]
        cn_res = qwen_chat(message)
        cn_res = json.loads(cn_res if "```" not in cn_res else cn_res.split("```json")[1].strip().split("```")[0].strip())
        print(cn_res)

        d['testcase_en'] = res
        d['testcase'] = cn_res

    json.dump(data, open(f"dataset{i}.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)


