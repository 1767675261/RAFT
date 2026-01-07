import os
import json
from experiment.exp3.request_api import request_api

model_list = json.load(open("config/model_list.json", "r", encoding="utf-8"))
# Kimik2在这里会出问题(超出上下文长度)，需要手动处理

def construct_metamodel():
    for model in model_list:
        if not os.path.exists(f"result/{model['name']}"):
            os.makedirs(f"result/{model['name']}")

        # Step 1: Get Meta-Model Information
        meta_model_response = request_api(model=model['api_name'], task="meta-model")
        print(f"Meta-Model Response for {model['name']}:\n{meta_model_response}\n\n\n")
        meta_model_info = meta_model_response['choices'][0]['message']['content'].strip()
        with open(f"result/{model['name']}/meta_model.txt", "w", encoding="utf-8") as f:
            f.write(meta_model_info)


def postporcess_metamodel():
    for model in model_list:
        with open(f"result/{model['name']}/meta_model.txt", "r", encoding="utf-8") as f:
            meta_model_info = f.read()

        if "```plantuml" in meta_model_info:
            processed_info = meta_model_info.strip().split("```plantuml")[1].strip().split("```")[0].strip()
        else:
            print("No plantuml code block found, need manual processing for model:", model['name'])

        with open(f"result/{model['name']}/meta_model_processed.txt", "w", encoding="utf-8") as f:
            f.write(processed_info)

def define_language():
    for model in model_list:
        meta_model = open(f"result/{model['name']}/meta_model_processed.txt", "r", encoding="utf-8").read()
        # Step 2: Get Representation Information
        representation_response = request_api(model=model['api_name'], task="representation", metamodel=meta_model)
        print(f"Representation Response for {model['name']}:\n{representation_response}\n\n\n")
        representation_info = representation_response['choices'][0]['message']['content']
        with open(f"result/{model['name']}/representation.txt", "w", encoding="utf-8") as f:
            f.write(representation_info)


def define_language_aggregated():
    for i, model in enumerate(model_list):
        idx = i // 3 + 1
        meta_model = open(f"result/group{idx}/meta_model.txt", "r", encoding="utf-8").read()
        # Step 2: Get Representation Information
        representation_response = request_api(model=model['api_name'], task="representation", metamodel=meta_model)
        print(f"Representation Response for {model['name']}:\n{representation_response}\n\n\n")
        representation_info = representation_response['choices'][0]['message']['content']
        with open(f"result/{model['name']}/representation_aggregated.txt", "w", encoding="utf-8") as f:
            f.write(representation_info)


if __name__ == "__main__":
    construct_metamodel()
    postporcess_metamodel()
    define_language()
    define_language_aggregated()