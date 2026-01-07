import json
import argparse



def gather():
    doc = ["上海证券交易所交易规则", "深圳证券交易所债券交易规则", "深圳证券交易所证券投资基金交易和申购赎回"]
    data = []
    for doci in doc:
        data_deepseek = json.load(open(f"result/postprocess_deepseek_{doci}.json", "r", encoding="utf-8"))
        data_gpt = json.load(open(f"result/postprocess_gpt_{doci}.json", "r", encoding="utf-8"))
        data_grok = json.load(open(f"result/postprocess_grok_{doci}.json", "r", encoding="utf-8"))
    
        for i in range(len(data_deepseek)):
            d = {}
            d['doc'] = doci
            d['rule'] = data_deepseek[i]['prompt']
            d['trl'] = data_deepseek[i]['answer']
            d['deepseek'] = data_deepseek[i]['predict']
            d['gpt'] = data_gpt[i]['predict']
            d['grok'] = data_grok[i]['predict']
            data.append(d)
    json.dump(data, open("result/trl.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)


def reduce():
    doc = ["上海证券交易所交易规则", "深圳证券交易所债券交易规则", "深圳证券交易所证券投资基金交易和申购赎回"]
    res = {
        "deepseek": {
            "上海证券交易所交易规则": [],
            "深圳证券交易所债券交易规则": [],
            "深圳证券交易所证券投资基金交易和申购赎回": []
        },
        "gpt": {
            "上海证券交易所交易规则": [],
            "深圳证券交易所债券交易规则": [],
            "深圳证券交易所证券投资基金交易和申购赎回": []
        },
        "grok": {
            "上海证券交易所交易规则": [],
            "深圳证券交易所债券交易规则": [],
            "深圳证券交易所证券投资基金交易和申购赎回": []
        }
    }
    data = json.load(open("result/trl.json", "r", encoding="utf-8"))
    for item in data:
        d_deepseek = {}
        d_deepseek['rule'] = item['rule']
        d_deepseek['answer'] = item['trl_refined']
        # d_deepseek['answer'] = item['trl']
        d_deepseek['predict'] = item['deepseek']
        res['deepseek'][item['doc']].append(d_deepseek)

        d_gpt = {}
        d_gpt['rule'] = item['rule']
        d_gpt['answer'] = item['trl_refined']
        # d_gpt['answer'] = item['trl']
        d_gpt['predict'] = item['gpt']
        res['gpt'][item['doc']].append(d_gpt)

        d_grok = {}
        d_grok['rule'] = item['rule']
        d_grok['answer'] = item['trl_refined']
        # d_grok['answer'] = item['trl']
        d_grok['predict'] = item['grok']
        res['grok'][item['doc']].append(d_grok)
    for model in res:
        for d in doc:
            json.dump(res[model][d], open(f"result/postprocess_{model}_{d}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default=None, choices=["gather", "reduce"], help="gather or reduce")
    args = parser.parse_args()
    if args.mode == "gather":
        gather()
    elif args.mode == "reduce":
        reduce()
    else:
        ...