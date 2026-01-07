import json
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_dir = "../model/Qwen3-8B"
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


def consistency():
    data = json.load(open("../corpus/extraction_data/extraction_data.json", "r", encoding="utf-8"))
    system_prompt_trl2nl = """现在我已知规则的形式化表达，我希望你能够将规则的形式化表达转换为自然语言的描述。请注意，转换后的描述应当清晰、准确地表达规则的含义，并且能够被人类理解。为了方便转换，请遵循以下模板：

### 模板结构
当[条件描述]时，[主体]可以[操作描述]，[预期结果描述]。

#### 1. 条件部分 (Precondition)
格式: 当[条件描述]时
转换规则:
- Actor → "[Actor值]"
- TradingInstrument → "交易品种为[TradingInstrument值]"
- TradingMarket → "在[TradingMarket值]市场"
- Time → "在[Time值]时间"
- Event → "当[Event值]事件发生时"
- Constraint → "[Constraint值]"
组合规则:
- 多个条件用"且"连接
- 如果有Time条件，放在最前面
- 其他条件按重要性排序：Actor > TradingInstrument > TradingMarket > Event > Constraint

#### 2. 主体部分
确定规则:
- 优先使用Actor值作为主体
- 如果没有Actor，使用OperationPart值作为主体
- 如果都没有，不写主体

#### 3. 操作部分 (Operation)
转换规则:
- Action → "[Action值]"
- TradingDirection → "[TradingDirection值]方向"
- TradingMethod → "通过[TradingMethod值]方式"
- Quantity → "数量为[Quantity值]"
- Price → "价格为[Price值]"
- OperationPart → "[OperationPart值]"
- Status → "状态为[Status值]"
组合规则:
- 核心结构: [TradingDirection] [Action] [TradingInstrument]
- TradingMethod作为方式描述
- Quantity和Price作为参数描述
- 如果没有TradingInstrument，在Action前加"进行"

#### 4. 预期结果部分 (ExpectedOutcome)
转换规则:
- ResultStatus → "，结果状态应为[ResultStatus值]"
- Result → "，预期结果为[Result值]"
- Constraint → "，需满足[Constraint值]约束"

### 要求：
1. 生成的自然语言应该自然、连贯，逻辑正确，并且符合中文表达习惯。
2. 按照key-value的出现先后次序来组织自然语言描述，一般只需要保留value不要key。
3. 只输出自然语言描述，不要输出其他任何内容。

### 示例
输入：
rule 1
if 操作主体 is 会员经纪客户
then 约束 is 以同一证券账户在单个或者多个会员的不同证券营业部 and 操作 is 买入 and 交易品种 is 债券
rule 2  
if 操作部分 is 买入的债券
then 约束 is 在单个或者多个会员的不同证券营业部之间 and 操作 is 托管转移

输出：
会员经纪客户可以以同一证券账户在单个或者多个会员的不同证券营业部买入债券，买入的债券可以在单个或者多个会员的不同证券营业部之间进行托管转移。
"""

    system_prompt_judge_nl_same = """现在我有一条自然语言描述的原始规则，我通过LLM提取规则中的关键信息，然后依据关键信息倒推得到了一条新的自然语言描述的规则。请你判断这两条自然语言描述的规则在语义上是否相同，输出true或false。如果不同，在下一行给出理由。要求：
1. 两条自然语言描述的规则在语义上相同，要求它们表达的含义、条件、操作、结果等信息一致。
2. 如果两条自然语言描述的规则在语义上不同，要求给出明确的理由。
3. 如果相同，仅输出true；如果不同，输出false并在下一行一句话给出理由，理由简洁明了。
示例输入：
rule1: 融资买入、融券卖出债券的，申报数量应当为10万元面额或者其整数倍。
rule2: 当融资买入债券时，申报数量应当为10万元面额或者其整数倍；当融券卖出债券时，申报数量也应当为10万元面额或者其整数倍。
示例输出：
true
**注意：语义大致一致即可，绝大多数情况下都是一致的。**
"""

    new_data = []
    for i, item in enumerate(data):
        trl = item["answer"]
        notsame = True
        idx = 0
        generation_messages = [{"role": "system", "content": system_prompt_trl2nl}]
        judge_messages = [{"role": "system", "content": system_prompt_judge_nl_same}]
        generation_messages.append({"role": "user", "content": f"{trl}"})
        while notsame and idx < 10:
            nl = chat(generation_messages)
            generation_messages.append({"role": "assistant", "content": nl})

            rule = item['prompt'].split("\n规则:")[-1].strip()
            judge_messages.append({"role": "user", "content": f"rule1: {rule}\nrule2: {nl}"})
            judge = chat(judge_messages)

            if "false" in judge.lower():
                notsame = True
                generation_messages.append({"role": "user", "content": f"生成的不好，请根据以下理由修正或重新生成自然语言描述的规则：{judge.splitlines()[1]}\n只输出修正或重新生成的自然语言描述，不要输出分析等其他任何内容。"})
                judge_messages.pop(-1)
            else:
                notsame = False
            idx += 1

        new_item = {
            "rule": item['prompt'].split("\n规则:")[-1].strip(),
            "trl": trl,
            "reverse_rule": nl,
            "judge": str(not notsame).lower()
        }
        new_data.append(new_item)
    json.dump(new_data, open("trl2nl.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)





if __name__ == "__main__":
    consistency()