import os
from openai import OpenAI
import json
import time
from experiment.exp1.document_preprocess import read_pdf_to_text2, read_txt_to_json
from experiment.exp1.rule_classify import classify_json, set_global
from trl.post_process import post_process
from testcase.generate_testcase import generate_testcase
import argparse




api_config = json.load(open("data/config/api_config.json", "r", encoding="utf-8"))


def request(system_prompt, user_prompt):
    client = OpenAI(
        base_url=api_config["base_url"],
        api_key=api_config["api_key"]
    )

    response = client.chat.completions.create(
        model="gpt-5-2025-08-07",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content


def generate_meta_model(document_path="data/config/document.txt", testcase_path="data/config/testcase.json"):
    documents = open(document_path, "r", encoding="utf-8").read()
    testcase = json.load(open(testcase_path, "r", encoding="utf-8"))
    system_prompt = open("data/config/meta_model_generation.md", "r", encoding="utf-8").read()
    user_prompt = "Generate a PlantUML meta model based on the provided regulatory documents and test cases.\n\n"
    user_prompt += "Regulatory Documents:\n" + documents + "\n\n"
    user_prompt += "Test Cases:\n" + json.dumps(testcase, indent=2, ensure_ascii=False) + "\n\n"
    meta_model = request(system_prompt, user_prompt)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    with open(f"data/knowledge/meta_model_{timestamp}.puml", "w", encoding="utf-8") as f:
        f.write(meta_model)
    print(f"Meta model generated and saved to data/knowledge/meta_model_{timestamp}.puml")


def generate_testable_requirement_representation(document_path="data/config/document.txt", testcase_path="data/config/testcase.json"):
    documents = open(document_path, "r", encoding="utf-8").read()
    testcase = json.load(open(testcase_path, "r", encoding="utf-8"))
    system_prompt = open("data/config/testable_requirement_representation_generation.md", "r", encoding="utf-8").read()
    if os.path.exists("data/knowledge/meta_model.puml"):
        meta_model = open("data/knowledge/meta_model.puml", "r", encoding="utf-8").read()
    else:
        raise FileNotFoundError("Meta model file not found. Please generate the meta model first.")
    system_prompt = system_prompt.replace("{}", meta_model)

    user_prompt = "Generate a testable requirement representation based on the provided regulatory documents and test cases.\n\n"
    user_prompt += "Regulatory Documents:\n" + documents + "\n\n"
    user_prompt += "Test Cases:\n" + json.dumps(testcase, indent=2, ensure_ascii=False) + "\n\n"
    testable_requirement_representation = request(system_prompt, user_prompt)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    with open(f"data/knowledge/testable_requirement_representation_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write(testable_requirement_representation)
    print(f"Testable requirement representation generated and saved to data/knowledge/testable_requirement_representation_{timestamp}.txt")


def generate_testcase_main(document_path="data/testcase/dataset.pdf", testcase_path="data/testcase/testcase.json"):
    set_global("model/mengzi_rule_filtering")

    # generate structured requirement
    file = document_path
    txt = read_pdf_to_text2(file)
    json_data = read_txt_to_json(txt)
    data = classify_json(json_data)

    system_prompt = open("data/config/requirement_generation.md", "r", encoding="utf-8").read()
    user_prompt = "Generate structured requirements for the following regulatory rule:\n\n"
    for d in data:
        if not d['testable']:
            continue
        user_prompt += f"Rule: {d['rule_cn']}\n\n"
        structured_requirement = request(system_prompt, user_prompt)
        d['trl'] = structured_requirement
    json.dump(data, open("data/testcase/formal_requirements.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    
    preds = []
    for d in data:
        if not d['testable'] or d['trl'] == "":
            continue
        preds.append(d['trl'])
    new_preds = post_process(preds)
    i = 0
    for d in data:
        if not d['testable'] or d['trl'] == "":
            continue
        d['trl_postprocess'] = new_preds[i]
        i += 1
    json.dump(data, open("data/testcase/formal_requirements_postprocess.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)

    formatted_data = []
    for d in data:
        if not d['testable'] or d['trl'] == "":
            continue
        formatted_data.append({
            "rule": d['rule_cn'],
            "predict": d['trl_postprocess']
        })
    testcases = generate_testcase(formatted_data)
    i = 0
    for d in data:
        if i >= len(testcases):
            break
        if not d['testable'] or d['trl'] == "":
            continue
        del d['testcase']
        d['testcase'] = testcases[i]['testcase']
        i += 1
    json.dump(data, open(testcase_path, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    print(f"Test cases generated and saved to {testcase_path}")
    




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=str, choices=["meta_model_gen", "requirement_representation_gen", "testcase_gen"], required=True)

    # e.g. --document data/config/document.txt | data/testcase/dataset.pdf
    parser.add_argument("--document", type=str, help="Path to the regulatory document file. If task = meta_model or requirement_representation, this file is used for RAG; if task = testcase, this file is used for testcase generation input", default="data/config/document.txt")
    # e.g. --testcase data/config/testcase.json | data/testcase/testcase.json
    parser.add_argument("--testcase", type=str, help="Path to the testcase file. If task = meta_model or requirement_representation, this file is used for RAG; if task = testcase, this file is used for testcase generation output", default="data/config/testcase.json")
    args = parser.parse_args()

    if args.task == "meta_model_gen":
        generate_meta_model(document_path=args.document, testcase_path=args.testcase)
    elif args.task == "requirement_representation_gen":
        generate_testable_requirement_representation(document_path=args.document, testcase_path=args.testcase)
    elif args.task == "testcase_gen":
        generate_testcase_main(document_path=args.document, testcase_path=args.testcase)