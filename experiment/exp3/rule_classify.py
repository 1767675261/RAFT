from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import traceback


model_dir = "../../model/Qwen3-8B"
tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_dir, trust_remote_code=True, torch_dtype=torch.float16, device_map="auto")
model.eval()


def chat(messages):
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
    print(f"Messages: {messages}\nResponse: {content}\n\n")
    return content


def classify(rule):
    messages = [
        {
            "role": "system",
            "content": "请帮我判断下面这条规则是否是软件/硬件需求。一条规则如果是需求，当且仅当它规定了如自动驾驶系统、车载系统、电力控制系统、能源系统等系统软硬件的功能、非功能需求，如地点、速度、时间、距离、频率、电压、操作、波动、故障、异常等。标题、背景、定义等与软硬件功能无关的规则不是需求。输出json包含两个项，is_requirement为bool类型，表示是否是需求，reason用一句话简单说明原因",
        },
        {
            "role": "user",
            "content": rule
        }
    ]
    response = chat(messages)
    try:
        response = "{" + response.split("{")[-1].split("}")[0] + "}"
        response = json.loads(response)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    return response['is_requirement']



def sequence_classification():
    for i in range(1, 6):
        data = json.load(open(f"deepseek_ours/dataset{i}.json", "r", encoding="utf-8"))
        for d in data:
            d['testable'] = classify(d['rule_cn'])
        json.dump(data, open(f"deepseek_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
        json.dump(data, open(f"gpt_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
        json.dump(data, open(f"grok_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)




if __name__ == "__main__":
    sequence_classification()

