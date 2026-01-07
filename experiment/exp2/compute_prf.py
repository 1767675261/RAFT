import json
from testcase.generate_testcase import judge_op, is_num_key, is_price_key, is_time_key
import copy
import os
from nltk import edit_distance
import re
import argparse
from tqdm import tqdm


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def str_same(s1, s2, threshold):
    """
    s1和s2的相似度大于threshold
    """
    if len(s1) == 0 or len(s2) == 0:
        return False
    return 1 - edit_distance(s1, s2) / max(len(s1), len(s2)) > threshold

def judge_same(t1, t2, threshold, strict=False):
    """
    t1和t2有threshold的元素相似，每个元素中value的相似度大于threshold
    """
    t1_keys, t1_values, t2_keys, t2_values = [], {}, [], {}
    for k, v in t1.items():
        if k == "testid" or k == "rule" or k == "id":
            continue
        # 将key结尾的数字去掉
        k = re.sub(r'\d+$', '', k)
        if k in t1_keys:
            t1_values[k].append(v)
        else:
            t1_keys.append(k)
            t1_values[k] = [v]
    for k, v in t2.items():
        if k == "testid" or k == "rule" or k == "id":
            continue
        k = re.sub(r'\d+$', '', k)
        if k in t2_keys:
            t2_values[k].append(v)
        else:
            t2_keys.append(k)
            t2_values[k] = [v]
    
    if not strict:
        # 模糊匹配法
        t1_like = 0
        for k1 in t1_keys:
            v1 = t1_values[k1]
            for k2 in t2_keys:
                v2 = t2_values[k2]
                if not str_same(k1, k2, threshold):
                    continue
                v1_like = 0
                for vi in v1:
                    for vj in v2:
                        if str_same(vi, vj, threshold):
                            v1_like += 1
                            break
                v1_like /= len(v1)
                if v1_like > threshold:
                    t1_like += 1
                    break
        return t1_like / len(t1_keys) > threshold
    else:
        t1_keys, t2_keys = sorted(t1_keys), sorted(t2_keys)
        if t1_keys != t2_keys:
            return False
        for k in t1_keys:
            if sorted(t1_values[k]) != sorted(t2_values[k]):
                return False
        return True



def eval_testcase(ours_testcases, label_testcases, metric_precision, metric_recall):
    """
    计算我们生成测试用例和标签测试用例的准确性
    """
    for t in ours_testcases:
        if not isinstance(t, dict):
            bug_file = open("bug.log", 'a', encoding='utf-8')
            bug_file.write(json.dumps(t, ensure_ascii=False, indent=4))
            bug_file.close()
            exit(-1)
        new_t = {}
        for k, v in t.items():
            if v == None:
                continue
            elif not isinstance(v, str):
                new_t[k] = json.dumps(v, ensure_ascii=False)
            else:
                new_t[k] = v
        t.clear()
        t.update(new_t)
    for t in label_testcases:
        if not isinstance(t, dict):
            bug_file = open("bug.log", 'a', encoding='utf-8')
            bug_file.write(json.dumps(t, ensure_ascii=False, indent=4))
            bug_file.close()
            exit(-1)
        new_t = {}
        for k, v in t.items():
            if v == None:
                continue
            elif not isinstance(v, str):
                new_t[k] = json.dumps(v, ensure_ascii=False)
            else:
                new_t[k] = v
        t.clear()
        t.update(new_t)
    find = [False for _ in range(len(label_testcases))]
    find_ = [False for _ in range(len(ours_testcases))]
    for i, testcase in enumerate(tqdm(label_testcases)):
        for j, t in enumerate(ours_testcases):
            if judge_same(testcase, t, metric_recall):
                find[i] = True
                break

    for j, t in enumerate(tqdm(ours_testcases)):
        for i, testcase in enumerate(label_testcases):
            if judge_same(testcase, t, metric_precision):
                find_[j] = True
                break

    recall = sum(find) / len(label_testcases)
    precision = sum(find_) / len(ours_testcases)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1


def compute_bsc_v1(testcases, scenarios, f):
    """
    这个函数的计算方法是，对于一条测试场景，一条用例，找用例中的每个要素在场景中是否出现了
    如果出现并且相似，认为正确，不相似认为冲突；如果没有出现，默认出现
    结果正确率偏高
    """
    # 预处理scenarios
    if_cover = [0] * len(scenarios)
    new_scenarios = []
    for scenario in scenarios:
        s = {}
        scs = scenario.split(";")
        for sc in scs:
            if "时间" not in sc:
                ss = sc.split(":")
                s[ss[0]] = ss[1]
            else:
                ss = sc.split(":")
                s[ss[0]] = ":".join(ss[1:])
        new_scenarios.append(s)
    scenarios = new_scenarios

    for testcase in testcases:
        for t in testcase:
            for iis, s in enumerate(scenarios):
                s_keys = list(s.keys())
                t_keys = list(t.keys())
                conflict = False
                find_time, find_num, find_price = False, False, False  # 匹配的数目
                # 统计s中的时间、数目、价格key
                s_time_keys = []
                for s_key in s_keys:
                    if "时间" in s_key:
                        s_time_keys.append(s_key)
                
                s_num_keys = []
                for s_key in s_keys:
                    if "数量" in s_key:
                        s_num_keys.append(s_key)
                
                s_price_keys = []
                for s_key in s_keys:
                    if "价格" in s_key or "金额" in s_key:
                        s_price_keys.append(s_key)

                for t_key in t_keys:
                    if t_key in ["rule", "测试关注点", "testid"]:
                        continue
                    if t_key == "结果":
                        # 必须相同
                        if t[t_key] != s[t_key]:
                            conflict = True
                            break
                    elif not is_time_key(t_key) and not is_num_key(t_key) and not is_price_key(t_key):
                        # 枚举约束
                        # 如果找到相同的value，就算相同
                        find = False
                        for s_key in s_keys:
                            for s_value in s[s_key].split(","):
                                if judge_same(t[t_key], s_value):
                                    find = True
                                    break
                            if find:
                                break
                        if find:
                            continue
                        # 没有找到相同的value，找是否冲突
                        if t_key not in s_keys:
                            continue
                        else:
                            conflict = True
                            break
                    elif is_time_key(t_key):
                        if len(s_time_keys) == 0:
                            conflict = True
                            break
                        find = False
                        for s_key in s_time_keys:
                            t_value = t[t_key]
                            s_value = s[s_key]
                            if ":" not in t_value and ":" not in s_value:  # 时间 is 上市首日
                                if judge_same(t_value, s_value):
                                    find = True
                                    break
                                else:
                                    continue
                            elif ":" not in t_value or ":" not in s_value:
                                continue
                            # t_value: 00:00:00-09:30:00 或 11:30:00-13:00:00 或 14:57:00-24:00:00
                            # s_value: 非9:15至11:30,13:00至15:30
                            # 将s_value、t_value格式转化
                            vs = [t.strip() for t in t_value.split("或")]
                            t_value = "{"
                            for v in vs:
                                t_value += f"[{v}],"
                            t_value = t_value[:-1] + "}"
                            fei = False
                            if "非" in s_value:
                                fei = True
                                s_value = s_value[1:]
                            vs = s_value.split(",")
                            time = []
                            for v in vs:
                                if "至" in v or "-" in v:
                                    t1 = v.split("至")[0] if "至" in v else v.split("-")[0]
                                    t2 = v.split("至")[1] if "至" in v else v.split("-")[1]
                                    if len(t1) == 4:
                                        t1 = "0" + t1 + ":00"
                                    elif len(t1) == 5:
                                        t1 = t1 + ":00"
                                    elif len(t1) == 7:
                                        t1 = "0" + t1
                                    if len(t2) == 4:
                                        t2 = "0" + t2 + ":00"
                                    elif len(t2) == 5:
                                        t2 = t2 + ":00"
                                    elif len(t2) == 7:
                                        t2 = "0" + t2
                                    time.append(t1)
                                    time.append(t2)
                                elif "前" in v or "后" in v:
                                    t = v[:-1]
                                    if len(t) == 4:
                                        t = "0" + t + ":00"
                                    elif len(t) == 5:
                                        t = t + ":00"
                                    elif len(t) == 7:
                                        t = "0" + t
                                    if "前" in v:
                                        time.append("00:00:00")
                                        time.append(t)
                                    else:
                                        time.append(t)
                                        time.append("24:00:00")
                            if fei:
                                if time[0] == "00:00:00":
                                    del time[0]
                                else:
                                    time.insert(0, "00:00:00")
                                if time[-1] == "24:00:00":
                                    del time[-1]
                                else:
                                    time.append("24:00:00")
                            s_value = "{"
                            for i in range(0, len(time), 2):
                                s_value += f"[{time[i]}-{time[i+1]}],"
                            s_value = s_value[:-1] + "}"
                            if s_value == t_value:
                                find = True
                                break
                        if find:
                            find_time = True

                    elif is_num_key(t_key):
                        if len(s_num_keys) == 0:
                            conflict = True
                            break
                        find = False
                        for s_key in s_num_keys:
                            t_value = t[t_key]
                            s_value = s[s_key]
                            if "一次性" in s_value and "(余额)" in t_value:
                                find = True
                                break
                            if "一次性" in s_value or "(余额)" in t_value:
                                continue
                            nums = [t.strip() for t in t_value.split("或")]
                            fei = False
                            if "非" in s_value:
                                s_value = s_value[1:]
                                fei = True
                            fulfill_all = True  # 这里假设满足所有约束
                            for sv in s_value.split(","):
                                fulfill = False
                                for num in nums:
                                    if is_number(num):
                                        num = int(num)
                                    else:
                                        if judge_same(num,sv):
                                            fulfill = True
                                            break
                                        else:
                                            continue
                                    if "整数倍" in sv:
                                        value = int(re.findall(r"\d+", sv)[0])  # value的整数倍
                                        if num % value == 0 and not fei or num % value != 0 and fei:
                                            # 满足条件
                                            fulfill = True
                                            break
                                    op = judge_op(sv)
                                    value = int(re.findall(r"\d+", sv)[0])  # op value
                                    constraint_fulfill = op == ">=" and num >= value or op == "<=" and num <= value or op == ">" and num > value or op == ">" and num > value or op == "==" and num == value or op == "!=" and num != value
                                    fulfill = constraint_fulfill and not fei or not constraint_fulfill and fei
                                    if fulfill:
                                        break
                                if not fulfill:
                                    fulfill_all = False
                                    break
                            if fulfill_all:
                                find = True
                                break
                        if find:
                            find_num = True

                    else:  # "价格"/"金额" in t_key
                        if len(s_price_keys) == 0:
                            conflict = True
                            break
                        find = False
                        for s_key in s_price_keys:
                            t_value = t[t_key]
                            s_value = s[s_key]
                            prices = [t.strip() for t in t_value.split("或")]
                            fei = False
                            if "非" in s_value:
                                s_value = s_value[1:]
                                fei = True
                            fulfill_all = True  # 这里假设满足所有约束
                            for sv in s_value.split(","):
                                fulfill = False
                                for price in prices:
                                    if is_number(price):
                                        price = float(price)
                                    else:
                                        if judge_same(price, sv):
                                            fulfill = True
                                            break
                                        else:
                                            continue
                                    op = judge_op(sv)
                                    value = float(re.findall(r"\d+", sv)[0])  # op value
                                    constraint_fulfill = op == ">=" and price >= value or op == "<=" and price <= value or op == ">" and price > value or op == ">" and price > value or op == "==" and price == value or op == "!=" and price != value
                                    fulfill = constraint_fulfill and not fei or not constraint_fulfill and fei
                                    if fulfill:
                                        break
                                if not fulfill:
                                    fulfill_all = False
                                    break
                            if fulfill_all:
                                find = True
                                break
                        if find:
                            find_price = True
                if (len(s_time_keys) == 0 or len(s_time_keys) > 0 and find_time) or (len(s_num_keys) == 0 or len(s_num_keys) > 0 and find_num) or (len(s_price_keys) == 0 or len(s_price_keys) > 0 and find_price):
                    ...
                else:
                    conflict = True
                if not conflict:
                    if_cover[iis] = 1

    for i, cover in enumerate(if_cover):
        if cover == 0:
            f.write(str(i+1))
            f.write("\n")
    return float(sum(if_cover)) / float(len(if_cover))
metric = json.load(open("../exp1/log/o_config.json", 'r', encoding='utf-8'))['exp1']

def compute_bsc_v3(testcases, scenarios):
    cover = []
    for scenario in scenarios:
        cover.append([False for _ in range(len(scenario))])
        for testcase in testcases:
            for key, value in testcase.items():
                if isinstance(value, list) or isinstance(value, dict):
                    continue
                value = str(value).strip()
                i = 0
                while key in scenario[i:]:
                    j = scenario.index(key, i)
                    i = j + 1
                    cover[-1][j:j + len(key)] = [True] * len(key)
                i = 0
                while value in scenario[i:]:
                    if value == "":
                        break
                    j = scenario.index(value, i)
                    i = j + 1
                    cover[-1][j:j + len(value)] = [True] * len(value)
    cover_rate = []
    for i, c in enumerate(cover):
        cover_rate.append(sum(c) / len(c))
    acc = sum(cover_rate) / len(cover_rate)
    return acc

def compute_bsc_v2(testcases, scenarios):
    """
    这个函数的计算方法是，对于一个场景，一条用例，判断场景的每个变量在用例中是否提及（值相同），
    然后这个场景覆盖率=提及的变量数/总变量数，取最高的覆盖率
    总体的覆盖率=所有场景覆盖率的均值
    """
    # 预处理scenarios
    new_scenarios = []  # new_scenarios[i]['交易市场']='深圳证券交易所'
    scenarios_variables = []  # scenario_variables[i]['交易市场'] = 0代表该元素未被覆盖，1代表覆盖
    max_cover_varnum = [0] * len(scenarios)  # 每个测试场景的最大覆盖变量数量
    cover_rate = 0

    for scenario in scenarios:
        s = {}
        variables = {}
        scs = scenario.split(";")
        for sc in scs:
            if "时间" not in sc:
                ss = sc.split(":")
                s[ss[0]] = ss[1]
                variables[ss[0]] = 0
            else:
                ss = sc.split(":")
                s[ss[0]] = ":".join(ss[1:])
                variables[ss[0]] = 0
        new_scenarios.append(s)
        scenarios_variables.append(variables)
    scenarios = new_scenarios


    for scenario_index, scenario in enumerate(scenarios):
        scenario_variables_total = copy.deepcopy(scenarios_variables[scenario_index])
        for testcase_index, testcase in enumerate(testcases):
            scenario_variables = copy.deepcopy(scenarios_variables[scenario_index])
            
            # 计算这个testcase在scenario中覆盖了多少
            for testcase_key, testcase_value in testcase.items():
                # 无关的测试用例key跳过
                if testcase_key in ['rule', '测试关注点', 'testid']:
                    continue
                if isinstance(testcase_value, list) or isinstance(testcase_value, dict):
                    # 如果是列表或字典，直接跳过
                    continue
                testcase_value = str(testcase_value).replace(" ", "").strip()
                for scenario_key, scenario_value in scenario.items():
                    # 同时为时间变量
                    if not judge_same(scenario_key, testcase_key):
                        continue
                    if is_time_key(testcase_key) and is_time_key(scenario_key):
                        if ":" not in testcase_value and ":" not in scenario_value:  # 时间 is 上市首日 这样的，按照枚举变量处理
                            for s_value in scenario_value.split(","):
                                if judge_same(testcase_value, s_value):
                                    scenario_variables[scenario_key] = 1
                                    break
                                # else: 如果时间冲突的话，不设置对应的变量被覆盖，继续比较
                            continue
                        elif ":" not in testcase_value or ":" not in scenario_value:
                            continue
                        # else: 两个时间变量，转成相同的格式比较
                        # testcase_value: 00:00:00-09:30:00 或 11:30:00-13:00:00 或 14:57:00-24:00:00
                        # scenario_value: 非9:15至11:30,13:00至15:30
                        vs = [t.strip() for t in testcase_value.split("或")]
                        t_value = "{"
                        for v in vs:
                            t_value += f"[{v}],"
                        t_value = t_value[:-1] + "}"
                        fei = False
                        if "非" == scenario_value[0]:
                            fei = True
                            scenario_value = scenario_value[1:]
                        vs = scenario_value.split(",")
                        time = []
                        for v in vs:
                            if "至" in v or "-" in v:
                                t1 = v.split("至")[0] if "至" in v else v.split("-")[0]
                                t2 = v.split("至")[1] if "至" in v else v.split("-")[1]
                                if len(t1) == 4:
                                    t1 = "0" + t1 + ":00"
                                elif len(t1) == 5:
                                    t1 = t1 + ":00"
                                elif len(t1) == 7:
                                    t1 = "0" + t1
                                if len(t2) == 4:
                                    t2 = "0" + t2 + ":00"
                                elif len(t2) == 5:
                                    t2 = t2 + ":00"
                                elif len(t2) == 7:
                                    t2 = "0" + t2
                                time.append(t1)
                                time.append(t2)
                            elif "前" in v or "后" in v:
                                t = v[:-1]
                                if len(t) == 4:
                                    t = "0" + t + ":00"
                                elif len(t) == 5:
                                    t = t + ":00"
                                elif len(t) == 7:
                                    t = "0" + t
                                if "前" in v:
                                    time.append("00:00:00")
                                    time.append(t)
                                else:
                                    time.append(t)
                                    time.append("24:00:00")
                        if fei:
                            if time[0] == "00:00:00":
                                del time[0]
                            else:
                                time.insert(0, "00:00:00")
                            if time[-1] == "24:00:00":
                                del time[-1]
                            else:
                                time.append("24:00:00")
                        s_value = "{"
                        for i in range(0, len(time), 2):
                            s_value += f"[{time[i]}-{time[i+1]}],"
                        s_value = s_value[:-1] + "}"
                        if s_value == t_value:
                            scenario_variables[scenario_key] = 1

                    # 同时为数量变量
                    elif is_num_key(testcase_key) and is_num_key(scenario_key):
                        
                        if "一次性" in scenario_value and "(余额" in testcase_value:
                            scenario_variables[scenario_key] = 1
                            continue
                        elif "一次性" in scenario_value or "(余额)" in testcase_value:
                            continue
                        # else: 常规数值约束或枚举约束
                        nums = [t.strip() for t in testcase_value.split("或")]
                        fei = False
                        if "非" == scenario_value[0]:
                            scenario_value = scenario_value[1:]
                            fei = True
                        fulfill_all = True  # 这里假设满足所有约束
                        for sv in scenario_value.split(","):
                            fulfill = False
                            for num in nums:
                                if is_number(num):
                                    num = int(num) if "." not in num else int(float(num))
                                else:  # 枚举约束
                                    if judge_same(num, sv):
                                        fulfill = True
                                        break
                                    else:
                                        continue
                                if "整数倍" in sv:
                                    if len(re.findall(r"\d+", sv)) > 0:
                                        value = int(re.findall(r"\d+", sv)[0])  # value的整数倍
                                        if num % value == 0 and not fei or num % value != 0 and fei:
                                            # 满足条件
                                            fulfill = True
                                            break
                                    else:
                                        continue
                                op = judge_op(sv)
                                all_v = re.findall(f"\d+", sv)
                                if len(all_v)>0:
                                    value = float(all_v[0])  # op value
                                else:  # 场景中的价格是一个枚举变量(但price不是)
                                    continue
                                if "万" in sv:
                                    value = value * 10000
                                if "亿" in sv:
                                    value = value * 100000000
                                constraint_fulfill = op == ">=" and num >= value or op == "<=" and num <= value or op == ">" and num > value or op == "<" and num < value or op == "==" and num == value or op == "!=" and num != value
                                fulfill = constraint_fulfill and not fei or not constraint_fulfill and fei
                                if fulfill:
                                    break
                            # 如果是正例，必须fulfill_all；如果是反例，只要有一个fulfill就算成功
                            if fei and fulfill:
                                fulfill_all = True
                                break
                            if not fulfill:
                                fulfill_all = False
                                break
                        if fulfill_all:
                            scenario_variables[scenario_key] = 1

                    # 同时为价格变量
                    elif is_price_key(testcase_key) and is_price_key(scenario_key):
                        prices = [t.strip() for t in testcase_value.split("或")]
                        fei = False
                        if "非" == scenario_value[0]:
                            scenario_value = scenario_value[1:]
                            fei = True
                        fulfill_all = True  # 这里假设满足所有约束
                        for sv in scenario_value.split(","):
                            fulfill = False
                            for price in prices:
                                if is_number(price):
                                    price = float(price)
                                else:
                                    if judge_same(price, sv):
                                        fulfill = True
                                        break
                                    else:
                                        continue
                                op = judge_op(sv)
                                if op == "":
                                    op = "=="
                                all_v = re.findall(r"\d+\.\d+|\d+", sv)
                                if len(all_v)>0:
                                    value = float(all_v[0])  # op value
                                else:  # 场景中的价格是一个枚举变量(但price不是)
                                    continue
                                if "万" in sv:
                                    value = value * 10000
                                if "亿" in sv:
                                    value = value * 100000000
                                constraint_fulfill = op == ">=" and price >= value or op == "<=" and price <= value or op == ">" and price > value or op == "<" and price < value or op == "==" and price == value or op == "!=" and price != value
                                fulfill = constraint_fulfill and not fei or not constraint_fulfill and fei
                                if fulfill:
                                    break
                            if fei and fulfill:
                                fulfill_all = True
                                break
                            if not fulfill:
                                fulfill_all = False
                                break
                        if fulfill_all:
                            scenario_variables[scenario_key] = 1

                    # 同时为枚举变量
                    elif not is_time_key(testcase_key) and not is_time_key(testcase_key) and not is_num_key(testcase_key) and not is_num_key(scenario_key) and not is_price_key(testcase_key) and not is_price_key(scenario_key):
                        
                        # 对于scenario中的一条枚举变量，如果在testcase中存在value相似的字符串，则算覆盖；否则不算
                        for s_value in scenario_value.split(","):
                            if judge_same(testcase_value, s_value):
                                scenario_variables[scenario_key] = 1
                                break
            
            if "testid" in testcase:
                print(f"## 测试场景\"{scenario_index+1}\", 测试用例\"{testcase['testid']}\", 覆盖变量数目为{sum(scenario_variables.values())}, 未覆盖的变量包括{[key for key in scenario_variables.keys() if scenario_variables[key] == 0]}\n")
            else:
                print(f"## 测试场景\"{scenario_index+1}\", 测试用例\"{testcase_index}\", 覆盖变量数目为{sum(scenario_variables.values())}, 未覆盖的变量包括{[key for key in scenario_variables.keys() if scenario_variables[key] == 0]}\n")
            
            for key in scenario_variables_total.keys():
                if scenario_variables[key] == 1:
                    scenario_variables_total[key] = 1
        
        max_cover_varnum[scenario_index] = sum(scenario_variables_total.values())
        if len(scenario_variables_total.keys()) > max_cover_varnum[scenario_index]:
            print(f"### 测试场景\"{scenario_index+1}\", 覆盖变量的最大数目为{max_cover_varnum[scenario_index]}, 整体未覆盖的变量包括{[key for key in scenario_variables_total.keys() if scenario_variables_total[key] == 0]}\n\n")
        else:
            print(f"### 测试场景\"{scenario_index+1}\", 覆盖变量的最大数目为{max_cover_varnum[scenario_index]}, 所有变量全部覆盖\n\n")
    
    max_cover_rate = [max_cover_varn / len(scenarios[i]) for i, max_cover_varn in enumerate(max_cover_varnum)]
    cover_rate += sum(max_cover_rate) / len(max_cover_rate)
    return cover_rate

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default="dataset1")
    parser.add_argument("--method", type=str, default="ours")
    args = parser.parse_args()
    dataset = args.dataset
    method = args.method
    if method == "ours_gpt":
        result = {}
        d = dataset
        for file in sorted(os.listdir("gpt_ours")):
            if d not in file:
                continue
            gpt_ours_testcases = json.load(open(f"gpt_ours/{file}", 'r', encoding='utf-8'))
            gpt_ours_testcases = [item['testcase'] for item in gpt_ours_testcases if item['testcase'] != []]
            gpt_ours_testcases = [tc for sublist in gpt_ours_testcases for tc in sublist]
            label_testcases = json.load(open(f"testcase/{dataset}.json", 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(gpt_ours_testcases, label_testcases, metric['ours_precision'], metric['ours_recall'])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase
        print(f"ours_gpt在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/ours_gpt_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    elif method == "ours_grok":
        d = dataset
        result = {}
        for file in sorted(os.listdir("grok_ours")):
            if d not in file:
                continue
            grok_ours_testcases = json.load(open(f"grok_ours/{file}", 'r', encoding='utf-8'))
            grok_ours_testcases = [item['testcase'] for item in grok_ours_testcases if item['testcase'] != []]
            grok_ours_testcases = [tc for sublist in grok_ours_testcases for tc in sublist]
            label_testcases = json.load(open(f"testcase/{dataset}.json", 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(grok_ours_testcases, label_testcases, metric['ours_precision'], metric['ours_recall'])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase
        print(f"ours_grok在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/ours_grok_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    elif method == "ours_deepseek":
        d = dataset
        result = {}
        for file in sorted(os.listdir("deepseek_ours")):
            if d not in file:
                continue
            deepseek_ours_testcases = json.load(open(f"deepseek_ours/{file}", 'r', encoding='utf-8'))
            deepseek_ours_testcases = [item['testcase'] for item in deepseek_ours_testcases if item['testcase'] != []]
            deepseek_ours_testcases = [tc for sublist in deepseek_ours_testcases for tc in sublist]
            label_testcases = json.load(open(f"testcase/{dataset}.json", 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(deepseek_ours_testcases, label_testcases, metric['ours_precision'], metric['ours_recall'])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase
        print(f"ours_deepseek在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/ours_deepseek_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    elif method == "deepseek":
        d = dataset
        result = {}
        for file in sorted(os.listdir("deepseek")):
            if d not in file:
                continue
            deepseek_testcase_file, label_testcase_file = f"deepseek/{file}", f"testcase/{dataset}.json"
            deepseek_testcases = json.load(open(deepseek_testcase_file, 'r', encoding='utf-8'))
            deepseek_testcases = [item['testcase'] for item in deepseek_testcases if item['testcase'] != []]
            deepseek_testcases = [tc for sublist in deepseek_testcases for tc in sublist]
            label_testcases = json.load(open(label_testcase_file, 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(deepseek_testcases, label_testcases, metric['llm_precision'], metric['llm_recall'])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase
        print(f"deepseek在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/deepseek_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    elif method == "gpt":
        d = dataset
        result = {}
        for file in sorted(os.listdir("gpt")):
            if d not in file:
                continue
            gpt_testcase_file, label_testcase_file = f"gpt/{file}", f"testcase/{dataset}.json"
            gpt_testcases = json.load(open(gpt_testcase_file, 'r', encoding='utf-8'))
            gpt_testcases = [item['testcase'] for item in gpt_testcases if item['testcase'] != []]
            gpt_testcases = [tc for sublist in gpt_testcases for tc in sublist]
            label_testcases = json.load(open(label_testcase_file, 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(gpt_testcases, label_testcases, metric['llm_precision'], metric['llm_recall'])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase

        print(f"gpt在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/gpt_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    elif method == "grok":
        d = dataset
        result = {}
        for file in sorted(os.listdir("grok")):
            if d not in file:
                continue
            grok_testcase_file, label_testcase_file = f"grok/{file}", f"testcase/{dataset}.json"
            grok_testcases = json.load(open(grok_testcase_file, 'r', encoding='utf-8'))
            grok_testcases = [item['testcase'] for item in grok_testcases if item['testcase'] != []]
            grok_testcases = [tc for sublist in grok_testcases for tc in sublist]
            label_testcases = json.load(open(label_testcase_file, 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(grok_testcases, label_testcases, metric['llm_precision'], metric['llm_recall'])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase

        print(f"grok在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/grok_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    

    elif method == "deepseek_without_repr":
        d = dataset
        result = {}
        for file in sorted(os.listdir("deepseek_without_representation")):
            if d not in file:
                continue
            deepseek_testcase_file, label_testcase_file = f"deepseek_without_representation/{file}", f"testcase/{dataset}.json"
            deepseek_testcases = json.load(open(deepseek_testcase_file, 'r', encoding='utf-8'))
            deepseek_testcases = [item['testcase'] for item in deepseek_testcases if item['testcase'] != []]
            deepseek_testcases = [tc for sublist in deepseek_testcases for tc in sublist]
            label_testcases = json.load(open(label_testcase_file, 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(deepseek_testcases, label_testcases, metric['llm_precision'], metric['llm_recall '])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase
        print(f"deepseek_without_repr在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/deepseek_without_repr_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    elif method == "gpt_without_repr":
        d = dataset
        result = {}
        for file in sorted(os.listdir("gpt_without_representation")):
            if d not in file:
                continue
            gpt_testcase_file, label_testcase_file = f"gpt_without_representation/{file}", f"testcase/{dataset}.json"
            gpt_testcases = json.load(open(gpt_testcase_file, 'r', encoding='utf-8'))
            gpt_testcases = [item['testcase'] for item in gpt_testcases if item['testcase'] != []]
            gpt_testcases = [tc for sublist in gpt_testcases for tc in sublist]
            label_testcases = json.load(open(label_testcase_file, 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(gpt_testcases, label_testcases, metric['llm_precision'], metric['llm_recall '])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase
        print(f"gpt_without_repr在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/gpt_without_repr_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    elif method == "grok_without_repr":
        d = dataset
        result = {}
        for file in sorted(os.listdir("grok_without_representation")):
            if d not in file:
                continue
            grok_testcase_file, label_testcase_file = f"grok_without_representation/{file}", f"testcase/{dataset}.json"
            grok_testcases = json.load(open(grok_testcase_file, 'r', encoding='utf-8'))
            grok_testcases = [item['testcase'] for item in grok_testcases if item['testcase'] != []]
            grok_testcases = [tc for sublist in grok_testcases for tc in sublist]
            label_testcases = json.load(open(label_testcase_file, 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(grok_testcases, label_testcases, metric['llm_precision'], metric['llm_recall '])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase
        print(f"grok_without_repr在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/grok_without_repr_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)


    elif method == "gpt_without_test":
        result = {}
        d = dataset
        for file in sorted(os.listdir("gpt_without_testability")):
            if d not in file:
                continue
            gpt_ours_testcases = json.load(open(f"gpt_without_testability/{file}", 'r', encoding='utf-8'))
            gpt_ours_testcases = [item['testcase'] for item in gpt_ours_testcases if item['testcase'] != []]
            gpt_ours_testcases = [tc for sublist in gpt_ours_testcases for tc in sublist]
            label_testcases = json.load(open(f"testcase/{dataset}.json", 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(gpt_ours_testcases, label_testcases, metric['llm_precision'], metric['llm_recall'])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase
        print(f"gpt_without_test在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/gpt_without_test_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    elif method == "grok_without_test":
        d = dataset
        result = {}
        for file in sorted(os.listdir("grok_without_testability")):
            if d not in file:
                continue
            grok_ours_testcases = json.load(open(f"grok_without_testability/{file}", 'r', encoding='utf-8'))
            grok_ours_testcases = [item['testcase'] for item in grok_ours_testcases if item['testcase'] != []]
            grok_ours_testcases = [tc for sublist in grok_ours_testcases for tc in sublist]
            label_testcases = json.load(open(f"testcase/{dataset}.json", 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(grok_ours_testcases, label_testcases, metric['llm_precision'], metric['llm_recall'])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase
        print(f"grok_without_test在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/grok_without_test_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    elif method == "deepseek_without_test":
        d = dataset
        result = {}
        for file in sorted(os.listdir("deepseek_without_testability")):
            if d not in file:
                continue
            deepseek_ours_testcases = json.load(open(f"deepseek_without_testability/{file}", 'r', encoding='utf-8'))
            deepseek_ours_testcases = [item['testcase'] for item in deepseek_ours_testcases if item['testcase'] != []]
            deepseek_ours_testcases = [tc for sublist in deepseek_ours_testcases for tc in sublist]
            label_testcases = json.load(open(f"testcase/{dataset}.json", 'r', encoding='utf-8'))
            precision_testcase, recall_testcase, f1_testcase = eval_testcase(deepseek_ours_testcases, label_testcases, metric['llm_precision'], metric['llm_recall'])
            result[dataset] = {}
            result[dataset]["precision_testcase"] = precision_testcase
            result[dataset]["recall_testcase"] = recall_testcase
            result[dataset]['f1_testcase'] = f1_testcase
        print(f"deepseek_without_test在{d}上的结果，testcase precision: {result[d]['precision_testcase']}, testcase recall: {result[d]['recall_testcase']}, testcase f1: {result[d]['f1_testcase']}")
        json.dump(result, open(f"log/deepseek_without_test_prf_{d}.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

