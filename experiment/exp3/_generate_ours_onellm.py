import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from tqdm import tqdm


qwen3_model_path = "../../model/Qwen3-8B"

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
    
    with torch.no_grad():
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





def generate_testcase(absent_keys, add_keys, llm):
    message = [
        {
            "role": "system",
            "content": "你是一个领域专家，擅长理解领域知识和规则。现在我每次给你一条规则，以及一个标签，你判断规则中是否存在该标签对应的值，如果存在返回对应的值，如果不存在则返回空字符串。例如我给你的名词是“操作人”，规则是“用户A购买了股票”，你需要返回“用户A”；如果规则是“股票被卖出”，你需要返回空字符串。请严格按照要求返回对应的值，不要添加任何额外的信息。",
        }
    ]
    for i in range(1, 6):
        print(f"Processing dataset{i}.json for {llm}...")
        data = json.load(open(f"{llm}_ours/dataset{i}.json", 'r', encoding='utf-8'))
        for d in tqdm(data):
            testcase = d['testcase']
            if not testcase or len(testcase) == 0:
                continue
            for tc in testcase:
                for key in absent_keys:
                    if key in list(tc.keys()):
                        del tc[key]
            
            for key in add_keys:
                message.append({
                    "role": "user",
                    "content": f"请根据以下规则提取‘{key}’对应的值，如果规则中不存在该值，请返回空字符串。\n规则：{d['rule_cn']}\n请只返回对应的值，不要添加任何额外的信息。",
                })
                response = qwen_chat(message)
                if response == None or response.strip() == "":
                    continue
                for tc in testcase:
                    tc[key] = response.strip()
                message = message[:-1]  # 删除最后一条用户消息

        json.dump(data, open(f"{llm}_only_ours/dataset{i}.json", 'w', encoding='utf-8'), indent=4, ensure_ascii=False)



def generate_testcase_2(allkeys, llm):
    for i in range(1, 7):
        data = json.load(open(f"{llm}_ours/dataset{i}.json", 'r', encoding='utf-8'))
        for d in data:
            testcase = d['testcase']
            if not testcase or len(testcase) == 0:
                continue
            for tc in testcase:
                for key in list(tc.keys()):
                    if key not in allkeys:
                        del tc[key]
        json.dump(data, open(f"{llm}_only_ours/dataset{i}.json", 'w', encoding='utf-8'), indent=4, ensure_ascii=False)





if __name__ == "__main__":
    # generate_testcase(['事件'], ['约束', '载重'], "gpt")
    # generate_testcase(['事件', '时间', '限制'], ['限制'], "grok")
    # generate_testcase(['结果'], ['许可'], "deepseek")

    # generate_testcase([], ['功率', '合规标准'], "gpt")
    # generate_testcase(['故障类型', '状态'], ['低穿能力', '高穿能力', '结果'], "grok")
    # generate_testcase(['结果'], ['功率', '模型误差'], "deepseek")
    ...