import copy
from functools import cmp_to_key
import json



keymap = {
    "Actor": "操作主体",
    "TradingInstrument": "交易品种",
    "TradingMarket": "交易市场",
    "Time": "时间",
    "Constraint": "约束",
    "Event": "事件",
    "Action": "操作",
    "TradingDirection": "交易方向",
    "TradingMethod": "交易方式",
    "Quantity": "数量",
    "Price": "价格",
    "OperationPart": "操作部分",
    "Status": "状态",
    "ResultStatus": "结果状态",
    "Result": "结果",
    "VehicleType": "车辆类型",
    "Precondition": "前置条件",
    "Condition": "条件",
    "Location": "地点",
    "Credential": "凭证",
    "Speed": "速度",
    "Distance": "距离",
    "Amount": "金额",
    "Voltage": "电压",
    "Frequency": "频率",
    "Operator": "操作人",
    "Target": "操作对象",
    "Fault": "故障类型",
    "Protection": "保护机制",
    "Harmonic": "谐波",
    "Flicker": "电压闪变",
    "PredictionAccuracy": "预测精度",
    "PowerResponse": "功率响应",
    "Outcome": "结果"
}

keylist = list(keymap.values())
keylist = ['操作主体', '交易品种', '交易市场', '时间', '约束', '事件', '操作', '交易方向', '交易方式', '数量', '价格', '操作部分', '状态', '结果状态', '结果', 
    
    '车辆类型', '条件', '地点', '凭证', '速度', '距离', '金额',
    '电压', '频率', '操作人', '操作对象', '故障类型', '保护机制', '谐波', '电压闪变', '预测精度', '功率响应'

    '价格类型', '证券类型', '操作状态', '集中申报簿中本方申报数量', '集中申报簿中对手方申报数量', '申报数量', '买入（卖出）基准价格', '相应价格', '约定号、证券代码、买卖方向、价格、数量等要素均匹配', '操作对象', '本所另有规定', '基准', '时间先后顺序', '债券品种', '申报价格', '结算方式', '交易方法', '最近成交价', '有效申报价格范围下限', '有效申报价格范围上限', '最高买入申报价', '最低卖出申报价', '可实现最大成交量的价格存在', '买入申报累计数量', '卖出申报累计数量', '价格最接近前收盘价', '价格最接近最近成交价', '最高买入申报价格', '买入申报价格', '卖出申报价格', '显示数量', '单笔成交数量', '剩余申报数量', '结算周期', '其他申报要素', '报价方', '成交价格', '操作方式', '应价申报累计数量', '应价申报价格', '成交数量', '分配方式', '分配阶段', '全部成交', '分配原则', '分配结果', '申报要素', '实施方式', '债券持仓数量', '债券实际面额', '除权参考价格', '本次偿还比例', '计算结果', '减少数量', '显示内容', '除息参考价', '基金品种', '指数成份证券包含', '对价', '对价类型', '有效申报价格', '交易阶段', '成交状态', '操作阶段', '交易', '交易数量', '交易价格', '发送对象', '依据', '申报累计数量', '最低价格', '边际价格', '操作数量', '赎回方式', '分期方式', '已偿还比例', '债券发行人', '提出申请', '本所同意', '即时行情', '偿还方式', '债券面额', '交易系统', '登记结算机构', '开盘价', '时间范围', '收盘价', '当日收盘价', '申报价格最小变动单位', '责任', '余额', '交易金额', '申报单位', '当日', '价格涨跌幅限制比例', '限价', '当日额度']


def transfer_or(s):
    # key1 op1 value1 or key2 op2 value2
    # (key1 op1 value1 or key2 op2 value2)
    # key1 op1 value1 or (key2 op2 value2 and key3 op3 value3)
    # (key1 op1 value1 and key2 op2 value2) or (key3 op3 value3 and key4 op4 value4)
    # (key1 op1 value1 and key2 op2 value2 or key3 op3 value3)

    if "or" not in s:
        return s
    words = s.split(" ")
    rules = []
    begin = 0  # rules[begin:]为当前需要添加元素的rule
    i = 0
    left = -1
    while i < len(words):
        word = words[i]
        if not word:
            i += 1
            continue
        if word == "if" or word == "rule":
            rules.append([word])
            begin = len(rules)-1
            i += 1
        elif word == "or":
            new_rule = copy.deepcopy(rules[-1])
            if left == -1:  # 1个clause
                j = i-1
                while j >= 0 and words[j] not in ["and", "if", "then", "or", "rule"]:
                    j -= 1
                new_rule = new_rule[:-(i - j -1)]
                j = i+1
                while j < len(words) and words[j] not in ["then", "if", "or", "and", "rule"]:
                    j += 1
                new_rule.extend(words[i+1:j])
                i = j
                rules.append(new_rule)
            else:
                j = i-1
                while j >= left and words[j] != "or" and new_rule:
                    new_rule.pop()
                    j -= 1
                j = i+1
                while j < len(words) and words[j][-1] != ")" and words[j] != "or":
                    j += 1
                if j < len(words) and words[j][-1] == ")":
                    new_rule.extend(words[i+1:j+1])
                    i = j + 1
                elif j < len(words) and words[j] == "or":
                    new_rule.extend(words[i+1:j])
                    i = j
                else:  # j == len(words)
                    new_rule.extend(words[i+1:j])
                    i = j
                rules.append(new_rule)
                if i < len(words) and words[i] == "or":
                    new_left = i - 1
                    while new_left > left and words[new_left][0] != "(":
                        new_left -= 1
                    left = new_left
                else:
                    left = -1
        else:
            if word[0] == "(" and not (len(word) >= 2 and word[1].isdigit()) and not (len(word) >= 3 and word[2] == ")"):
                left = i
            for rule in rules[begin:]:
                rule.append(word)
            i += 1
    for i, rule in enumerate(rules):
        rules[i] = " ".join(rule)
    return " ".join(rules)



def transfer_not(s):
    # not key op value
    # not (key1 op1 value1 and key2 op2 value2)
    words = s.split(" ")
    not_begin = False
    has_range = False
    new_words = []
    for i, word in enumerate(words):
        if word == "not":
            not_begin = True
        else:
            if not_begin:
                if word in ["=", "!=", "<", "<=", ">", ">=", "in", "notin"]:
                    if word == "=":
                        new_words.append("!=")
                    elif word == "!=":
                        new_words.append("=")
                    elif word == "<":
                        new_words.append(">=")
                    elif word == ">":
                        new_words.append("<=")
                    elif word == "<=":
                        new_words.append(">")
                    elif word == ">=":
                        new_words.append("<")
                    elif word == "in":
                        new_words.append("notin")
                    elif word == "notin":
                        new_words.append("in")
                elif word == "and":
                    if not has_range:  # 没有括号，一个not就可
                        not_begin = False
                        new_words.append(word)
                    else:  # 有括号，and转or
                        new_words.append("or")
                else:  # 处理key、value部分
                    if "(" in word:
                        has_range = True
                    if ")" in word:
                        not_begin = False
                    new_words.append(word)
            else:
                new_words.append(word)

    return " ".join(new_words)


def add_rule(s):
    """
    添加rule 1、rule 2作为开头，同时删掉原有rule，确保正确
    """
    ss = [si.strip() for si in s.split("if") if si.strip()]
    if "rule" in ss[0]:
        ss = ss[1:]
    i = 1
    res = []
    for si in ss:
        si = si.replace(" then", "\nthen")
        if "rule" in si:
            si = si.split("rule")[0].strip()
        rule = f"rule {i}\nif {si}\n"
        res.append(rule)
        i += 1
    return "".join(res)


def compare(a, b):
    a, b = a[0], b[0]
    if a not in keylist:
        keylist.append(a)
    if b not in keylist:
        keylist.append(b)
    return keylist.index(a) - keylist.index(b)

def judge_seq(s):
    lines = s.strip().split("\n")
    for i, line in enumerate(lines):
        if "if" in line or "then" in line:
            ls = []
            words = line.split(" ")
            # 将[a, b, c]这种情况合并为一个word：[a,b,c]
            new_words = []
            cont = False
            for word in words:
                if "[" == word[0]:
                    if "]" == word[-1]:
                        ...
                    else:
                        cont = True
                    new_words.append(word)
                elif "]" == word[-1]:
                    new_words[-1] += word
                    cont = False
                else:
                    if cont:
                        new_words[-1] += word
                    else:
                        new_words.append(word)
            words = new_words
            # 提取clause并排序
            j = 1
            while j < len(words):
                k = j + 1
                while k < len(words) and words[k] != "and":
                    k += 1
                ls.append(words[j:k])
                j = k + 1
            ls = sorted(ls, key=cmp_to_key(compare))
            # 恢复line
            new_line = words[0] + " "
            for l in ls:
                new_line += " ".join(l) + " and "
            new_line = new_line[:-5]
            lines[i] = new_line
    return "\n".join(lines)


def transfer_constraint(s):
    """
    如果遇到“约束 = key op value”或“结果 = key op value”这些情况，改为key op value
    """
    words = s.split(" ")
    i = 0
    new_words = []
    while i < len(words):
        word = words[i]
        if word in ["约束", "(约束", "结果", "(结果"]:
            a = words[i+1]
            if a in ["in", "notin"]:
                new_words.append(word)
                i += 1
                continue
            j = i + 2
            while j < len(words) and words[j] not in ["and", "or", "then", "if", "rule", ")"]:
                j += 1
            b = words[i+2:j]
            if len(b) >= 2:
                if b[1] in ["=", "!=", "<", "<=", ">", ">=", "in", "notin", "%"]:
                    new_words.extend(b)
                else:
                    new_words.append("".join(b))
                i = j
                if "结果" in word:
                    new_words.extend(["and", "结果", "=", "成功"])
            else:
                new_words.append(word)
                i += 1
        else:
            new_words.append(word)
            i += 1
    return " ".join(new_words)


def post_process(preds):
    """
    1、去掉转义
    2、中英文转换
    3、大小写转换
    4、转化constraint格式
    5、处理not
    6、处理or
    7、添加rule
    8、调整条件顺序
    """

    for i, pred in enumerate(preds):
        pred = pred.replace("\"", "")
        for key in keymap:
            pred = pred.replace(key, keymap[key]).replace(key.lower(), keymap[key]).replace(key.upper(), keymap[key]).replace(key[0].lower() + key[1:], keymap[key])
        pred = pred.replace("IF", "if").replace("If", "if")
        pred = pred.replace("THEN", "then").replace("Then", "then")
        pred = pred.replace("AND", "and").replace("And", "and")
        pred = pred.replace("OR", "or").replace("Or", "or")
        pred = pred.replace("NOT", "not").replace("Not", "not")
        pred = pred.replace("\n", " ")
        pred = pred.replace("and if", "if")
        pred = pred.replace("RULE", "rule").replace("Rule", "rule")
        pred = pred.replace("is", "=")
        pred = pred.replace("rule", "rule ")
        new_pred = pred.replace("  ", " ")
        while new_pred != pred:
            pred = new_pred
            new_pred = pred.replace("  ", " ")

        pred = transfer_constraint(pred)
        # print(pred)

        pred = transfer_not(pred)
        # print(pred)

        pred = transfer_or(pred)
        pred = pred.replace("(", "").replace(")", "")
        new_pred = pred.replace("  ", " ")
        while new_pred != pred:
            pred = new_pred
            new_pred = pred.replace("  ", " ")
        # print(pred)
        
        pred = add_rule(pred)
        # print(pred)

        pred = judge_seq(pred)
        # print(pred)
        # exit(0)

        preds[i] = pred
    return preds




if __name__ == "__main__":
    files = [
        "deepseek_上海证券交易所交易规则", 
        "deepseek_深圳证券交易所债券交易规则", 
        "deepseek_深圳证券交易所证券投资基金交易和申购赎回", 
        "grok_上海证券交易所交易规则", 
        "grok_深圳证券交易所债券交易规则", 
        "grok_深圳证券交易所证券投资基金交易和申购赎回", 
        "gpt_上海证券交易所交易规则", 
        "gpt_深圳证券交易所债券交易规则", 
        "gpt_深圳证券交易所证券投资基金交易和申购赎回"
    ]
    for file in files:
        res = json.load(open(f"result/{file}.json", "r", encoding="utf-8"))
        preds = [r['predict'] for r in res]
        new_preds = post_process(preds)
        for i in range(len(res)):
            res[i]['predict'] = new_preds[i]
        json.dump(res, open(f"result/postprocess_{file}.json", "w", encoding="utf-8"), indent=4, ensure_ascii=False)
