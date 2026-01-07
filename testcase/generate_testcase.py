import json
import z3
import re
from collections import OrderedDict
import copy


"""
A->B真值表
A  B  A->B
----------
0  0   1
0  1   1
1  0   0   条件真，结论假为假
1  1   1   条件真，结论真为真

A^B -> C^D真值表
A  B  C  D  A^B  C^D  A^B -> C^D
-----------------------------------
0  0  0  0   0    0        1
0  0  0  1   0    0        1
0  0  1  0   0    0        1
0  0  1  1   0    1        0
0  1  0  0   0    0        1
0  1  0  1   0    0        1
0  1  1  0   0    0        1
0  1  1  1   0    1        0
1  0  0  0   0    0        1
1  0  0  1   0    0        1
1  0  1  0   0    0        1
1  0  1  1   0    1        0
1  1  0  0   1    0        0
1  1  0  1   1    0        0
1  1  1  0   1    0        0   条件真，无论几个结论为假，都为假
1  1  1  1   1    1        1   条件真，结论真，为真
"""

"""
生成测试用例时，我们不考虑条件为假的情况，因为这样没有意义。
在结果部分，我们只考虑为“时间”、“数量”、“价格”等数值类型的约束和“操作”生成反例，同时注意更改状态信息，其他枚举变量不变
"""



def is_time_key(key):
    if key[-1] == "日" or key[-2:] == "时间" or "期" in key:
        return True
    return False

def is_num_key(key):
    if "量" in key or "数" in key:
        return True
    return False

def is_price_key(key):
    if ("价" in key or "基准" == key or "金额" in key) and "要素" not in key and "指令" not in key and "类型" not in key and "方式" not in key:
        return True
    if any([t in key for t in ['速度', '距离', '金额', '电压', '频率', '预测精度', '功率响应']]):
        return True
    return False


def find_word(s, word):
    """在字符串s中查找word出现的所有位置"""
    locs = [s.find(word)]
    while locs[-1] != -1:
        locs.append(s.find(word, locs[-1]+1))
    return locs[:-1]


def time_preprocess(time):
    """
    处理时间，判断time中是否有类似9:00-10:00的时间段，以及类似前、后的表达，如果有，返回True和处理后的时间段，否则返回False和空字符串
    Args:
        time: 时间字符串，形如"每个交易日的9:00-10:00"
    Returns:
        valid: 是否是合法的时间段
        numerical_time: 处理后的时间段，形如"9:00-10:00,11:00-12:00"或""
    """
    time_vals = re.findall(r"\d+:\d+", time)  # 所有形似9:00的时间值
    vals_locs = [time.find(time_val) for time_val in time_vals]  # 时间值在time中的位置
    loc_before = sorted(find_word(time, "<") + find_word(time, "<="))  # 早于、晚于、至等比较词在time中的位置
    loc_after = sorted(find_word(time, ">") + find_word(time, ">="))
    loc_between = find_word(time, "-")
    locs = sorted(loc_before + loc_after + loc_between)
    if time_vals:
        time_vals = ["0" + time_val if len(time_val) == 4 else time_val for time_val in time_vals]
        t = ""
        # 考虑三种时间的情况，9:00至10:00，9:00后/晚于于9:00，9:00前/早于9:00，其他情况直接照抄
        if len(vals_locs) != len(loc_before) + len(loc_after) + 2*len(loc_between):
            return False, ""
        p = 0
        valid = True
        for loc in locs:
            if loc in loc_before:
                if time[loc:loc+1] == "<":
                    t += f"00:00:00-{time_vals[p]}:00,"
                    p += 1
                else:
                    valid = False
                    break
            elif loc in loc_after:
                if time[loc:loc+1] == ">":
                    t += f"{time_vals[p]}:00-24:00:00,"
                    p += 1
                else:
                    valid = False
                    break
            else:
                if p+1 < len(vals_locs) and vals_locs[p] < loc and vals_locs[p+1] > loc:
                    t += f"{time_vals[p]}:00-{time_vals[p+1]}:00,"
                    p += 2
                else:
                    valid = False
                    break
        if valid:
            return True, t[:-1]
        else:
            return False, ""
    else:
        return False, ""


def generate_time_testcase(consequence: list):
    """
    处理时间类型的约束，生成对应的测试用例
    Args:
        consequence: 形如["竞买日前", "<", "当日"], ["时间", "in", "9:00-10:00"]的时间约束
    Returns:
        time_testcase: 时间测试用例列表，要求生成的测试用例添加到这个列表中
    """
    time_testcase = []
    time = consequence[2] if consequence[1] in ["=", "==", "!=", "in", "notin"] else consequence[1] + consequence[2]
    time.replace("不晚于", "早于").replace("不早于", "晚于")
    valid, numerical_time = time_preprocess(time)
    if valid:  # time是一个类似9:00-10:00的时间段，生成对应的测试用例
        # [[9:00-10:00], ]数组，转化成[[09:00-10:00], ]数组，然后生成反例
        time_testcase.append([consequence[0], numerical_time])
        # 生成反例
        time_list = []
        for t in numerical_time.split(","):
            time_list.extend(t.split("-"))
        for i in range(len(time_list)):
            if len(time_list[i]) == 4:
                time_list[i] = "0" + time_list[i]
        new_time_list = []
        begin = "00:00:00"
        i = 0
        while i < len(time_list):
            if time_list[i] == begin:
                begin = time_list[i+1]
                i += 2
                continue
            new_time_list.append(f"{begin}-{time_list[i]}")
            begin = time_list[i+1]
            i += 2
        if begin != "24:00:00":
            new_time_list.append(f"{begin}-24:00:00")
        time_testcase.append([consequence[0], ",".join(new_time_list)])
        if consequence[1] in ["!=", "notin"]:
            time_testcase = time_testcase[1:] + time_testcase[:1]
    else:  # 没有数字时间，可能是“当日”、“竞买日前”这种
        if "<" in time or ">" in time or "<=" in time or ">=" in time:  # 生成正测试用例和反测试用例
            if "<" in time or "<=" in time:
                if "<=" in time:
                    time = time[2:]
                else:
                    time = time[1:]
                time_testcase.append([consequence[0], time])
                time_testcase.append([consequence[0], time + "后"])
            elif ">" in time or ">=" in time:
                if ">=" in time:
                    time = time[2:]
                else:
                    time = time[1:]
                time_testcase.append([consequence[0], time])
                time_testcase.append([consequence[0], time + "前"])
        else:  # 无需特殊处理
            time_testcase.append([consequence[0], time])
            time_testcase.append([consequence[0], "非" + time])
            if consequence[1] in ["!=", "notin"]:
                time_testcase = time_testcase[1:] + time_testcase[:1]
    return time_testcase

def judge_op(value):
    if "不低于" in value or "达到" in value or "以上" in value:
        return ">="
    if "不高于" in value or "以下" in value or "不超过" in value or "以内" in value:
        return "<="
    if "低于" in value or "未达到" in value or "不足" in value or "小于" in value:
        return "<"
    if "高于" in value or "超过" in value or "优于" in value or "大于" in value:
        return ">"
    if "不等于" in value:
        return "!="
    return "="


def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def generate_consequence_z3_expr(consequences_without_time, z3_variables):
    """
    将所有的consequence转换为z3表达式
    """
    # 避免key重复
    keys = []
    for consequence in consequences_without_time:
        if consequence[0] not in keys:
            keys.append(consequence[0])
        elif not is_num_key(consequence[0]) and not is_price_key(consequence[0]):
            i = 2
            while consequence[0] + str(i) in keys:
                i += 1
            consequence[0] = consequence[0] + str(i)
            keys.append(consequence[0])

    z3_expr = []
    for consequence in consequences_without_time:
        # x为z3变量
        if consequence[0] in z3_variables:
            x = z3_variables[consequence[0]]
        else:
            # 特殊处理：前收盘价的上下100%、不高于匹配成交最近成交价的100个基点、算术运算表达式（如前收盘价格-100元×本次偿还比例）
            if "%" == consequence[1]:
                x = z3.Int(consequence[0])
            elif "基点" in consequence[2] or any([op in consequence[2:] for op in ["+", "-", "*", "/", "="]]) or (not is_num_key(consequence[0]) and not is_price_key(consequence[0])):
                x = z3.String(consequence[0])
            elif re.findall(r"\d+\.\d+", consequence[2]):
                x = z3.Real(consequence[0])
            elif re.findall(r"\d+", consequence[2]):
                x = z3.Int(consequence[0])
            else:
                x = z3.String(consequence[0])
            z3_variables[consequence[0]] = x
        
        # 如果是数量或价格，需要特殊处理
        if is_num_key(consequence[0]):
            if len(consequence) == 3 and isnumber(consequence[2]):
                num = float(consequence[2]) if "." in consequence[2] else int(consequence[2])
                op = consequence[1]
                exp = None
                if op == ">=":
                    exp = x >= num
                elif op == "<=":
                    exp = x <= num
                elif op == "<":
                    exp = x < num
                elif op == ">":
                    exp = x > num
                elif op == "=":
                    exp = x == num
                elif op == "!=":
                    exp = x != num
                else:
                    exp = x == num
                z3_expr.append(exp)
            elif len(consequence) == 5 and isnumber(consequence[2]) and isnumber(consequence[4]) and consequence[1] == "%" and consequence[3] in ['=', '=='] and "." not in consequence[2] and "." not in consequence[4]:
                num1 = int(consequence[2])
                num2 = int(consequence[4])
                exp = x % num1 == num2
                z3_expr.append(exp)
            else:
                del z3_variables[consequence[0]]


        elif is_price_key(consequence[0]):
            if len(consequence) == 3 and isnumber(consequence[2]):
                num = float(consequence[2]) if "." in consequence[2] else int(consequence[2])
                op = consequence[1]
                exp = None
                if op == ">=":
                    exp = x >= num
                elif op == "<=":
                    exp = x <= num
                elif op == "<":
                    exp = x < num
                elif op == ">":
                    exp = x > num
                elif op == "=":
                    exp = x == num
                elif op == "!=":
                    exp = x != num
                else:
                    exp = x == num
                z3_expr.append(exp)
            elif len(consequence) == 5 and isnumber(consequence[2]) and isnumber(consequence[4]) and consequence[1] == "%" and consequence[3] in ['=', '=='] and "." not in consequence[2] and "." not in consequence[4]:
                num1 = int(consequence[2])
                num2 = int(consequence[4])
                exp = x % num1 == num2
                z3_expr.append(exp)
            else:
                del z3_variables[consequence[0]]
        elif "操作" in consequence[0] and (consequence[0][2:] == "" or consequence[0][2:].isdigit() and int(consequence[0][2:]) < 5):
            if consequence[1] in ["=", "==", "in"]:
                z3_expr.append(x == consequence[2])
            elif consequence[1] in ["!=", "notin"]:
                z3_expr.append(x != consequence[2])
        else:
            del z3_variables[consequence[0]]
    return z3_expr


def safe_decode(value):
    s = str(value)
    # 处理可能出现的 \\\\u{...}
    s = s.replace("\\\\", "\\")
    # 重点：处理 \u{xxxxxx}
    s = re.sub(r'\\u\{([0-9a-fA-F]+)\}', lambda m: chr(int(m.group(1), 16)), s)
    s = s.replace("\"", "").replace("{", "").replace("}", "")
    return s

def generate_consequence_case_list(solver, z3_variables, consequence_z3_expr, consequence_case_list, index):
    """
    递归函数，用以对consequence_z3_expr中的每项取反并进行笛卡尔积，生成所有可能的情况并添加到consequence_case_list中
    Args:
        solver: z3求解器
        z3_variables: z3变量字典
        consequence_z3_expr: z3表达式列表
        consequence_case_list: 结论测试用例列表
        index: 当前处理的consequences的索引
    """
    if index == len(consequence_z3_expr):
        if solver.check() == z3.sat:
            rs = solver.model()
            consequence_case = []
            for variable in z3_variables:
                key = z3_variables[variable]
                value = rs[key]

                if isinstance(value, z3.IntNumRef):
                    value = int(value.as_long())
                elif isinstance(value, z3.RatNumRef):
                    value = float(value.as_decimal(prec=6)[:6])
                else:  # z3.SeqRef
                    # value = str(value).replace("\\\\", "\\").replace("{", "").replace("}", "").replace("\"", "").encode("utf-8").decode("unicode_escape")
                    value = safe_decode(value)
                consequence_case.append([str(key), value])
            consequence_case_list.append(consequence_case)
        return
    
    expr = consequence_z3_expr[index]
    
    solver.push()
    solver.add(expr)
    generate_consequence_case_list(solver, z3_variables, consequence_z3_expr, consequence_case_list, index+1)
    solver.pop()

    solver.push()
    solver.add(z3.Not(expr))
    generate_consequence_case_list(solver, z3_variables, consequence_z3_expr, consequence_case_list, index+1)
    solver.pop()


def post_process_blank(consequence_case_list, consequences_without_time):
    """
    后处理，z3中string != "abc"会生成string为空白，处理这个空白
    """
    for case in consequence_case_list:
        for c in case:
            if c[1] == "":
                for consequence in consequences_without_time:
                    if consequence[0] == c[0]:
                        if consequence[2].startswith("不") or consequence[2].startswith("非"):
                            c[1] = consequence[2][1:]
                        else:
                            c[1] = "非" + consequence[2]
                        break





def cartesian_product(nums):
    """
    求笛卡尔组合
    例如: nums=[[1,2],[3,4]]，两两看作一组
    return: [[1,3], [1,4], [2,3], [2,4]]
    """
    if len(nums) == 0:
        return []
    if len(nums) == 1:
        return [[num] for num in nums[0]]
    sub_res = cartesian_product(nums[1:])
    res = []
    for num in nums[0]:
        for sub in sub_res:
            res.append([num] + sub)
    return res


def mydsl_to_rule(trl):
    """
    trl = {
        "rule": "停止接受买入申报的，当日不再恢复，本所另有规定的除外。",
        "answer": "rule 1\nif 时间 = 当日 and 约束 != 本所另有规定 and 事件 = 停止接受买入申报\nthen 结果状态 = 不恢复\nrule 2\nif 约束 = 本所另有规定 and 事件 = 停止接受买入申报\nthen 结果 = 不适用",
        "predict": "rule 1\nif 时间 = 当日 and 约束 != 本所另有规定 and 事件 = 停止接受买入申报\nthen 结果状态 = 不恢复\nrule 2\nif 约束 = 本所另有规定 and 事件 = 停止接受买入申报\nthen 结果 = 不适用"
    },
    rule = {
        "rule": text,
        "trl": [
            {
                "conditions": [
                    [key, op, value1, value2, ...],
                    ...
                ],
                "consequences": [
                    [key, op, value1, value2, ...],
                    ...
                ]
            }
        ]
    }
    """
    rule = {
        "rule": trl['rule']
    }
    trl = trl['predict']
    res = []
    for line in trl.split("\n"):
        l = line.strip().split(" ")
        if len(l) == 0:
            continue
        if l[0] == "rule":
            r = {}
            key_values = []
            key_values_consequences = []
        elif l[0] == "if" or l[0] == "then":
            i = 1
            while i < len(l):
                j = i
                while j < len(l) and l[j] != "and":
                    j += 1
                if j - i == 1:
                    key = "约束"
                    op = "="
                    values = [l[i]]
                else:
                    key = l[i]
                    op = l[i+1]
                    if op == "==":
                        op = "="
                    values = l[i+2:j]
                    if "true" in values:
                        values = [key]
                        key = "约束"
                        if op != "notin" and op != "!=":
                            op = "="
                        else:
                            op = "!="
                if key == "结果" or key == "结果状态":
                    key_values_consequences.append([key, op] + values)
                else:
                    key_values.append([key, op] + values)
                i = j + 1
            if l[0] == "then":
                r['conditions'] = key_values
                r['consequences'] = key_values_consequences
                # 去重，有的trl既说了成功的场景又反过来说了失败场景，重复
                cf = False
                for old_r in res:
                    # 检查
                    try:
                        old_keys, old_ops, old_values = zip(*old_r['conditions'])
                        new_keys, new_ops, new_values = zip(*r['conditions'])
                    except Exception as e:
                        print(f"解析trl出错，trl格式不规范，请检查或重新生成！\n{trl}\n", e)
                        exit(-1)
                    if old_keys == new_keys and old_values == new_values:
                        cf = True
                        break
                if not cf:
                    res.append(r)
    rule['trl'] = res
    return rule



def generate_testcase(trls):
    """
    生成测试用例
    """
    # rule = {
    #     "rule": text,
    #     "trl": [
    #         {
    #             "conditions": [
    #                 [key, op, value1, value2, ...],
    #                 ...
    #             ],
    #             "consequences": [
    #                 [key, op, value1, value2, ...],
    #                 ...
    #             ]
    #         }
    #     ]
    # }
    rules = []
    for trl in trls:
        rule = mydsl_to_rule(trl)
        rules.append(rule)


    for rule_i in rules:
        testcases = []
        for rule in rule_i['trl']:
            index = 1
            testcase = []
            result, resultstatus = "成功", ""
            for c in rule['consequences']:
                if c[0] == "结果":
                    result = c[2]
                elif c[0] == "结果状态":
                    resultstatus = c[2]

            # 自行处理时间
            time_testcase = []
            condition_without_time = []
            for condition in rule['conditions']:
                if is_time_key(condition[0]):
                    local_time_testcase = generate_time_testcase(condition)
                    time_testcase.append(local_time_testcase)
                else:
                    if condition[1] == "in" or condition[1] == "==":
                        condition[1] = "="
                    elif condition[1] == "notin" or condition[1] == "!=":
                        condition[1] = "!="
                    condition_without_time.append(condition)
            time_testcase = cartesian_product(time_testcase)

            # 数量预处理，如果要生成数值的数量key的数目>=2且不一样，则统一成数量
            num_keys = {}
            for condition in condition_without_time:
                if is_num_key(condition[0]) and re.findall(r"\d+", condition[2]):
                    if condition[0] in num_keys:
                        num_keys[condition[0]] += 1
                    else:
                        num_keys[condition[0]] = 1
            if len(list(num_keys.keys())) >= 2:
                for condition in condition_without_time:
                    if condition[0] in num_keys:
                        condition[0] = "数量"

            # 生成z3表达式
            z3_variables = {}
            consequence_z3_expr = generate_consequence_z3_expr(condition_without_time, z3_variables)
            # 使用z3递归生成测试用例
            consequence_case_list = []
            solver = z3.Solver()
            for v in z3_variables.values():
                if isinstance(v, z3.ArithRef):
                    solver.add(v > 0)
            generate_consequence_case_list(solver, z3_variables, consequence_z3_expr, consequence_case_list, 0)

            for consequence in condition_without_time:
                if consequence[0] not in z3_variables:
                    for c in consequence_case_list:
                        if consequence[1] == "=":
                            c.append([consequence[0], consequence[2]])
                        elif consequence[1] == "!=":
                            c.append([consequence[0], "非" + consequence[2]])
                        else:
                            c.append([consequence[0], consequence[1] + consequence[2]])
            
            # 后处理，z3中string != "abc"会生成string为空白，处理这个空白
            post_process_blank(consequence_case_list, condition_without_time)

            # 将时间测试用例添加到测试用例中
            if time_testcase:
                new_consequence_case_list = []
                for c in consequence_case_list:
                    for time_case in time_testcase:
                        new_case = c.copy()
                        for t in time_case:
                            # idx=2
                            # keys = [cc[0] for cc in new_case]
                            # if t[0] in keys:
                            #     while t[0] + str(idx) in keys:
                            #         idx += 1
                            #     t[0] = t[0] + str(idx)
                            new_case.append(t)
                        new_consequence_case_list.append(new_case)
                consequence_case_list = new_consequence_case_list


            # 将结果约束和条件约束组合
            testcase_of_this_rule = []
            for c in consequence_case_list:
                new_testcase = copy.deepcopy(testcase)
                new_testcase.extend(copy.deepcopy(c))
                
                final_testcase = OrderedDict()
                
                # 如果key在条件中且重复，分别设为key、key2、key3...
                # 如果key在结果中且重复，分别设为结果key、结果key2、结果key3...
                for tc in new_testcase:
                    if len(final_testcase) < len(testcase) and tc[0] in final_testcase:  # key在条件中且重复
                        key_index = 2
                        while tc[0] + str(key_index) in final_testcase:
                            key_index += 1
                        tc[0] = tc[0] + str(key_index)
                    final_testcase[tc[0]] = str(tc[1])
                
                if index == 1:
                    final_testcase['结果'] = result
                    if resultstatus != "":
                        final_testcase['结果状态'] = resultstatus
                else:
                    if result == "成功":
                        final_testcase['结果'] = "失败"
                        if resultstatus != "":
                            final_testcase['结果状态'] = final_testcase.get("状态", "非" + resultstatus)
                    else:
                        final_testcase['结果'] = "成功"
                        if resultstatus != "":
                            final_testcase['结果状态'] = resultstatus

                testcase_of_this_rule.append(final_testcase)
                index += 1
            testcases.extend(testcase_of_this_rule)
        rule_i['testcase'] = testcases
        # del rule_i['trl']
    return rules





if __name__ == "__main__":
    llm = ["deepseek", "grok", "gpt"]
    document = ["上海证券交易所交易规则", "深圳证券交易所债券交易规则", "深圳证券交易所证券投资基金交易和申购赎回"]
    for l in llm:
        for d in document:
            trls = json.load(open(f"data/postprocess_{l}_{d}.json", "r", encoding="utf-8"))
            testcase = generate_testcase(trls)
            json.dump(testcase, open(f"result/testcase_{l}_{d}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)