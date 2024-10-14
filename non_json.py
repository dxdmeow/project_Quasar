import fitz
import re
import json

def clean_text(text):
    return re.sub(r'\s+[\.\s]+', ' ', text).strip()

def extract_structure_from_pdf(pdf_path):
    structure = {}
    current_chapter = None
    current_section = None

    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            text = page.get_text()

            lines = text.split('\n')

            for line in lines:
                cleaned_line = clean_text(line)


                if re.match(r'^\d+(\.\d+)?$', cleaned_line):
                    continue


                chapter_match = re.match(r'Глава\s(\d+)\s+(.+)', cleaned_line)
                if chapter_match:
                    chapter_number = chapter_match.group(1)
                    chapter_title = chapter_match.group(2).strip()
                    current_chapter = chapter_number
                    structure[current_chapter] = {"title": chapter_title, "sections": {}}
                    continue


                section_match = re.match(r'(\d+\.\d+)\s+(.+)', cleaned_line)
                if section_match and current_chapter:
                    section_number = section_match.group(1)
                    section_title = section_match.group(2).strip()
                    structure[current_chapter]["sections"][section_number] = {
                        "title": section_title,
                        "subsections": {}
                    }
                    current_section = section_number
                    continue


                subsection_match = re.match(r'(\d+\.\d+\.\d+)\s+(.+)', cleaned_line)
                if subsection_match and current_chapter and current_section:
                    subsection_number = subsection_match.group(1)
                    subsection_title = subsection_match.group(2).strip()
                    structure[current_chapter]["sections"][current_section]["subsections"][subsection_number] = {
                        "title": subsection_title
                    }

    return structure

def save_structure_to_json(structure, json_path):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(structure, f, ensure_ascii=False, indent=4)

# Пути к файлам
pdf_path = "Руководство_Бухгалтерия_для_Узбекистана_ред_3_0.pdf"
json_path = "improved_structure.json"

# Извлечение и сохранение структуры
structure = extract_structure_from_pdf(pdf_path)
save_structure_to_json(structure, json_path)

print("Структура сохранена в improved_structure.json")

