import json

def eval_acc(preds, labels):
    acc = 0
    for p, l in zip(preds, labels):
        if p == l:
            acc += 1
    
    return acc / len(labels)


if __name__ == "__main__":
    llm = ["deepseek", "grok", "gpt"]
    file = ["上海证券交易所交易规则", "深圳证券交易所债券交易规则", "深圳证券交易所证券投资基金交易和申购赎回"]

    for l in llm:
        all_preds = []
        all_labels = []
        for f in file:
            data = json.load(open(f"result/raw/{l}_{f}.json", "r", encoding="utf-8"))
            preds = [d['predict'] for d in data]
            labels = [d['label'] for d in data]
            all_preds.extend(preds)
            all_labels.extend(labels)

        accuracy = eval_acc(all_preds, all_labels)
        print(f"RAW {l} => Accuracy: {accuracy:.4f}")

    for l in llm:
        all_preds = []
        all_labels = []
        for f in file:
            data = json.load(open(f"result/five_step/{l}_{f}_5step.json", "r", encoding="utf-8"))
            preds = [d['predict'] for d in data]
            labels = [d['label'] for d in data]
            all_preds.extend(preds)
            all_labels.extend(labels)

        accuracy = eval_acc(all_preds, all_labels)
        print(f"5STEP {l} => Accuracy: {accuracy:.4f}")
    

    for l in llm:
        all_preds = []
        all_labels = []
        for f in file:
            data = json.load(open(f"result/no_trl/{l}_{f}_notrl.json", "r", encoding="utf-8"))
            preds = [d['predict'] for d in data]
            labels = [d['label'] for d in data]
            all_preds.extend(preds)
            all_labels.extend(labels)

        accuracy = eval_acc(all_preds, all_labels)
        print(f"NOTRL {l} => Accuracy: {accuracy:.4f}")