import pdfplumber

def read_pdf_to_text(pdf_file):
    s = ""
    i = 0
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            print(i)
            i += 1
            s += page.extract_text() + "\n"
    
    
    
    return s.strip()



def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False





if __name__ == "__main__":
    for i in range(6):
        if i != 0:
            continue
        pdf_file = f"dataset/dataset{i+1}.pdf"
        text = read_pdf_to_text(pdf_file)
        with open(f"dataset/dataset{i+1}.txt", "w", encoding="utf-8") as f:
            f.write(text)
