from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import json


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
tokenizer = None


def set_global(path):
    global model, tokenizer
    model = AutoModelForSequenceClassification.from_pretrained(path, num_labels=3, trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
    model.eval()
    model.to(device)


def classify(text):
    input_ids = tokenizer([text], padding="max_length", truncation=True, max_length=512, return_tensors="pt").input_ids
    input_ids = input_ids.to(device)

    with torch.no_grad():
        logits = model(input_ids).logits
        _, output = torch.max(logits, dim=1)
        output = output.cpu().numpy().tolist()
    
    return output[0] == 1


def classify_json(data):
    for d in data:
        d['testable'] = classify(d['rule_cn'])
    return data

def sequence_classification():
    set_global("../../model/mengzi_rule_filtering")
    for i in range(1, 7):
        data = json.load(open(f"deepseek_ours/dataset{i}.json", "r", encoding="utf-8"))
        data = classify_json(data)
        json.dump(data, open(f"deepseek_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
        json.dump(data, open(f"gpt_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
        json.dump(data, open(f"grok_ours/dataset{i}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)




if __name__ == "__main__":
    sequence_classification()

