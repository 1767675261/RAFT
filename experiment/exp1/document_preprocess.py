import pdfplumber

def read_pdf_to_text(pdf_file):
    s = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            s += page.extract_text() + "\n"
    
    fixed_s = ""
    for line in s.split("\n"):
        if line == "":
            continue
        if len(line) >= 3 and line[0] == "(" and line[2] == ")" or line.startswith("Section") or line.startswith("Rule"):
            fixed_s += "\n"
        if line[-1] == ".":
            fixed_s += line + "\n"
        else:
            fixed_s += line + " "
    s = fixed_s.replace("\n\n", "\n")

    fixed_s = ""
    for line in s.split("\n"):
        if "amended" in line.lower() or "adopted" in line.lower() or "rescinded" in line.lower():
            continue
        if "all rights reserved" in line.lower():
            continue
        fixed_s += line + "\n"
    s = fixed_s
    
    return s.strip()



def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def read_pdf_to_text2(pdf_file):
    s = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            s += page.extract_text() + "\n"
    
    fixed_s = ""
    for i, line in enumerate(s.split("\n")):
        if i == 1:
            fixed_s += line + "\n"
            continue
        if line == "" or isnumber(line.strip()) or "—" in line and isnumber(line.replace("—", "").replace(" ", "")):
            continue
        if line.startswith("附件") or "目 录" in line or "................" in line:
            continue
        if "第" in line and ("章 " in line or "节 " in line):
            fixed_s += "\n"
        if isnumber(line.split(" ")[0].replace(".", "")):
            fixed_s += "\n"
        a, b = line.split(" ")[0], " ".join(line.split(" ")[1:])
        if isnumber(a.replace(".", "")):
            b = b.replace(" ", "")
            line = a + " " + b
        fixed_s += line
    s = fixed_s.replace("\n\n", "\n")

    fixed_s = ""
    for line in s.split("\n"):
        if "次修订" in line:
            continue
        fixed_s += line + "\n"
    s = fixed_s
    
    return s



def read_pdf_to_text3(pdf_file):
    s = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            s += page.extract_text() + "\n"
    
    fixed_s = ""
    for i, line in enumerate(s.split("\n")):
        if not line.strip() or "5 -" in line:
            continue
        firstword = line.split(" ")[0]
        if len(firstword) >= 2 and firstword[-1] == "." and isnumber(firstword[:-1]):
            fixed_s += "\n"
        if line[-1] == "。" or i in [0, 1, 2, 3]:
            fixed_s += line + "\n"
        else:
            fixed_s += line
    s = fixed_s.replace("\n\n", "\n")

    return s



def fix_txt(txt_file):
    s = open(txt_file, "r", encoding="utf-8").read()
    fixed_s = ""
    for line in s.split("\n"):
        if line == "" or "追加" in line or "一部改正" in line:
            continue
        if len(line) >= 3 and line[0] == "（" and line[-1] == "）" and line[2] != "）":
            continue
        fixed_s += line + "\n"
    
    s = fixed_s.replace("\n\n", "\n")
    return s



def is_id(str):
    # 判断一句话是否是id开头
    str = str.split(" ")[0].strip()
    if str == "":
        return False
    if str[0]=="第" and "条" in str:
        return True
    if str.isdigit():
        return True
    if "." not in str:
        return False
    ids = str.split(".")
    for id in ids:
        if not id.isdigit():
            return False
    return True



def read_txt_to_json(txt_data):
    '''
    将txt_data按句划分，写成sci的json格式
    txt_data: 输入数据
    data: 返回的sci数据
    '''
    data = []
    lines = txt_data.split("\n")
    for line in lines:
        if line.strip() == "":
            continue
        line = line.strip().replace("：", ":").replace("︰", ":")
        id = line.split(" ")[0]
        if is_id(id):
            text = "".join(line.split(" ")[1:])
            text = text.replace("。", "。\n")
            texts = text.split("\n")
            for index, text in enumerate(texts):
                if text.strip() != "":
                    d = {"rule": text.strip(), "rule_cn": text.strip(), "testable": True, "trl": "", "trl_postprocess": "", "testcase": []}
                    data.append(d)
        else:
            text = line.replace("。", "。\n")
            texts = text.split("\n")
            for index, text in enumerate(texts):
                if text.strip() != "":
                    d = {"rule": text.strip(), "rule_cn": text.strip(), "testable": True, "trl": "", "trl_postprocess": "", "testcase": []}
                    data.append(d)
    
    return data













if __name__ == "__main__":
    for i in range(5):
        pdf_file = f"dataset/dataset{i+1}.pdf"
        if i in [0, 1]:
            text = read_pdf_to_text(pdf_file)
        elif i in [4, 5]:
            text = read_pdf_to_text2(pdf_file)
        else:
            text = read_pdf_to_text3(pdf_file)
        with open(f"dataset/dataset{i+1}.txt", "w", encoding="utf-8") as f:
            f.write(text)
    
    txt_file = f"dataset/dataset6_ori.txt"
    text = fix_txt(txt_file)
    with open(f"dataset/dataset6.txt", "w", encoding="utf-8") as f:
        f.write(text)