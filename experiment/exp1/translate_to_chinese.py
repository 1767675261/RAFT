from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import os

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



def translate_to_chinese():
    for i in range(1, 7):
        data = json.load(open(f"deepseek/dataset{i}.json", "r", encoding="utf-8"))
        if i == 4 or i == 5:
            for d in data:
                del d['text']
                del d['testcase']
                d['rule_cn'] = d['rule']
                d['testable'] = False
                d['trl'] = ""
                d['testcase'] = []
            json.dump(data, open(f"deepseek_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
            json.dump(data, open(f"gpt_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
            json.dump(data, open(f"grok_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)

        else:
            for d in data:
                del d['text']
                del d['testcase']
                messages = [
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate the following rule text into Simplified Chinese accurately and fluently."
                    },
                    {
                        "role": "user",
                        "content": d['rule']
                    }
                ]
                response = chat(messages)
                d['rule_cn'] = response
                d['testable'] = False
                d['trl'] = ""
                d['testcase'] = []
            json.dump(data, open(f"deepseek_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
            json.dump(data, open(f"gpt_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
            json.dump(data, open(f"grok_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)






if __name__ == "__main__":
    translate_to_chinese()