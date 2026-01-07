import json
import re

def domain_concept_coverage():
    datas = json.load(open("../corpus/extraction_data/extraction_data.json", "r", encoding="utf-8"))
    substantive_token = 0  # 总共的实词数
    total_token = 0  # 总共的词数
    ours_substantive_token = 0  # 我们的方法提取出的实词数
    other_substantive_token = 0  # 我们的方法范围外的实词数
    for data in datas:
        rule = data['prompt'].split("\n规则:")[1]
        trl = data['answer']
        total_token += len(rule)
        cover = [0 for _ in range(len(rule))]
        ours_cover = [0 for _ in range(len(rule))]
        other_cover = [0 for _ in range(len(rule))]
        lines = trl.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("if") or line.startswith("then"):
                words = line.split(" ")
                i = 1
                while i < len(words):
                    key, op, values = words[i], words[i + 1], [words[i + 2]]
                    i += 3
                    while i < len(words) and words[i] != "and":
                        values.append(words[i])
                        i += 1
                    
                    start_idx = 0
                    while key in rule[start_idx:]:
                        idx = rule.index(key, start_idx)
                        cover[idx:idx + len(key)] = [1] * len(key)
                        if key != "约束":
                            ours_cover[idx:idx + len(key)] = [1] * len(key)
                        else:
                            other_cover[idx:idx + len(key)] = [1] * len(key)
                        start_idx = idx + len(key)

                    start_idx = 0
                    while op in rule[start_idx:]:
                        idx = rule.index(op, start_idx)
                        cover[idx:idx + len(op)] = [1] * len(op)
                        if key != "约束":
                            ours_cover[idx:idx + len(op)] = [1] * len(op)
                        else:
                            other_cover[idx:idx + len(op)] = [1] * len(op)
                        start_idx = idx + len(op)
                    
                    for value in values:
                        start_idx = 0
                        while value in rule[start_idx:]:
                            idx = rule.index(value, start_idx)
                            cover[idx:idx + len(value)] = [1] * len(value)
                            if key != "约束":
                                ours_cover[idx:idx + len(value)] = [1] * len(value)
                            else:
                                other_cover[idx:idx + len(value)] = [1] * len(value)
                            start_idx = idx + len(value)
                    i += 1
        substantive_token += sum(cover)
        ours_substantive_token += sum(ours_cover)
        other_substantive_token += sum(other_cover)
    
    print("总词数:", total_token)
    print("实词数:", substantive_token)
    print("我们方法提取出的实词数:", ours_substantive_token)
    print("我们方法范围外的实词数:", other_substantive_token)
    print("实词占比: {:.2f}%".format(substantive_token / total_token * 100))
    print("我们方法提取出的实词覆盖率: {:.2f}%".format(ours_substantive_token / substantive_token * 100))
    print("我们方法范围外的实词覆盖率: {:.2f}%".format(other_substantive_token / substantive_token * 100))




def expression_support():
    # 统计每种表达方式的数量、占比
    datas = json.load(open("../corpus/extraction_data/extraction_data.json", "r", encoding="utf-8"))
    a, b, c = 0, 0, 0
    total = len(datas)
    for data in datas:
        rule = data['prompt'].split("\n规则:")[1]
        trl = data['answer']
        if any([op in rule for op in ["不低于", "达到", "以上", "不高于", "以下", "不超过", "低于", "未达到", "不足", "小于", "高于", "超过", "优于", "大于"]]):
            b += 1
        # 匹配时间，例如09:00, 9:00, 09:00:00等格式
        if re.findall(r'\d{1,2}:\d{2}(?::\d{2})?', rule):
            c += 1
        if "is" in trl:
            a += 1
    print("总规则数:", total)
    print("使用比较表达的规则数:", b)
    print("使用比较表达的规则占比: {:.2f}%".format(b / total * 100))
    print("使用in表达的规则数:", c)
    print("使用in表达的规则占比: {:.2f}%".format(c / total * 100))
    print("使用=表达的规则数:", a)
    print("使用=表达的规则占比: {:.2f}%".format(a / total * 100))




def condition_composition():
    # 具有或关系的规则数、占比，具有not的规则数、占比
    datas = json.load(open("../corpus/extraction_data/extraction_data.json", "r", encoding="utf-8"))
    total_rules = len(datas)
    op_rules = 0
    or_rules = 0
    not_rules = 0
    for data in datas:
        rule = data['prompt'].split("\n规则:")[1]
        if "或" in rule:
            or_rules += 1
        if "不" in rule:
            not_rules += 1
        if any([op in rule for op in ["+", "-", "*", "/", "%", "整数倍"]]):
            op_rules += 1
    print("总规则数:", total_rules)
    print("具有或关系的规则数:", or_rules)
    print("具有或关系的规则占比: {:.2f}%".format(or_rules / total_rules * 100))
    print("具有not的规则数:", not_rules)
    print("具有not的规则占比: {:.2f}%".format(not_rules / total_rules * 100))
    print("具有运算符的规则数:", op_rules)
    print("具有运算符的规则占比: {:.2f}%".format(op_rules / total_rules * 100))





def model():
    data = json.load(open("../corpus/extraction_data/extraction_data.json", "r", encoding="utf-8"))
    has_cond_op_res = 0
    has_op_res = 0
    has_cond_res = 0
    for d in data:
        trl = d['answer']
        trl_ = d['answer'].replace("\n", " ").split(" ")
        has_cond = not "if\nthen" in trl
        has_op = "操作" in trl_
        if has_cond and has_op:
            has_cond_op_res += 1
        if not has_cond:
            has_op_res += 1
        if not has_op:
            has_cond_res += 1
    total = len(data)
    print("总规则数:", total)
    print("没有操作的规则数:", has_cond_res)
    print("没有操作的规则占比: {:.2f}%".format(has_cond_res / total * 100))
    print("没有条件的规则数:", has_op_res)
    print("没有条件的规则占比: {:.2f}%".format(has_op_res / total * 100))
    print("同时具有条件和操作的规则数:", has_cond_op_res)
    print("同时具有条件和操作的规则占比: {:.2f}%".format(has_cond_op_res / total * 100))



if __name__ == "__main__":
    domain_concept_coverage()
    expression_support()
    condition_composition()
    model()