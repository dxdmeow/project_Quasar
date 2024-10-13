import PyPDF2
import json

def extract_pdf_content(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def update_structure_with_text(text, structure):
    lines = text.split('\n')  
    for line in lines:
        line = line.strip()
        if line.startswith('Глава') and line in structure:
            structure[line] = structure.get(line, {})  
 
            for chapter in structure:
                if line in structure[chapter]:
                    structure[chapter][line] = structure[chapter].get(line, {}) 
    return structure


def main(pdf_path, structure_json):
    pdf_text = extract_pdf_content(pdf_path)
    with open(structure_json, 'r', encoding='utf-8') as json_file:
        structure = json.load(json_file)

    updated_structure = update_structure_with_text(pdf_text, structure)

    with open(structure_json, 'w', encoding='utf-8') as json_file:
        json.dump(updated_structure, json_file, ensure_ascii=False, indent=4)

    print(f"Структура успешно обновлена и сохранена в файл {structure_json}")

pdf_file = 'Руководство_Бухгалтерия_для_Узбекистана_ред_3_0.pdf' 
structure_file = 'structure.json'


main(pdf_file, structure_file)
