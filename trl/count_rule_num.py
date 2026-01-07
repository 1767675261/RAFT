import json

def count_rule_num(file_path):
    data = json.load(open(file_path, 'r', encoding='utf-8'))
    print(f"文件路径: {file_path}, 规则数量: {len(data)}")




if __name__ == "__main__":
    count_rule_num("data/上海证券交易所交易规则.json")
    count_rule_num("data/深圳证券交易所债券交易规则.json")
    count_rule_num("data/深圳证券交易所证券投资基金交易和申购赎回.json")