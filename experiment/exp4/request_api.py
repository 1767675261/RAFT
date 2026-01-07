import requests
import json
import base64
from experiment.exp3.config.prompt import get_prompt

# 需要clash for windows等代理软件开启代理访问外网

api_key = open("config/apikey.txt", "r", encoding="utf-8").read().strip()


def encode_pdf_to_base64(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')



def request_api(model, task, metamodel=""):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # 有两个上传文件，一个是pdf，另一个是json
    pdf_path = "config/深圳证券交易所债券交易规则.pdf"
    base64_pdf = encode_pdf_to_base64(pdf_path)
    pdf_data_url = f"data:application/pdf;base64,{base64_pdf}"
    txt_path = "config/深圳证券交易所债券交易规则.txt"
    txt_content = open(txt_path, "r", encoding="utf-8").read()
    json_path = "config/testcase.json"
    json_content = json.load(open(json_path, "r", encoding="utf-8"))
    json_content = json.dumps(json_content, ensure_ascii=False)

    if task == "meta-model":
        prompts = get_prompt()
        prompt = prompts['meta_model']
    else:
        prompts = get_prompt(metamodel=metamodel)
        prompt = prompts['representation']
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                },
                # {
                #     "type": "file",
                #     "file": {
                #         "name": "regulation.pdf",
                #         "data_url": pdf_data_url
                #     }
                # },
                {
                    "type": "text",
                    "text": f"规则文本内容示例：{txt_content}"
                },
                {
                    "type": "text",
                    "text": f"测试用例数据示例：{json_content}"
                }
            ]
        }
    ]

    plugins = [
        {
            "id": "file_parser",
            "pdf": {
                "engine": "pdf-text"
            }
        }
    ]

    payload = {
        "model": model,
        "messages": messages,
        # "plugins": plugins,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50,
    }

    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890",
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), proxies=proxies)
    res = response.json()
    return res

if __name__ == "__main__":
    request_api()