import PyPDF2
import re
import json
import pandas as pd

def extract_titles_from_pdf(pdf_path):
    structure = {}

    # Чтение PDF файла
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        current_section = None
        current_subsection = None

        for page in range(len(reader.pages)):
            text = reader.pages[page].extract_text() 
            if not isinstance(text, str):
                continue  

            lines = [line.strip() for line in text.splitlines()]

            # Извлечение глав
            for line in lines:
                chapter_match = re.match(r'Глава\s+(\d+)\s+(.+)', line)
                if chapter_match:
                    chapter_number = chapter_match.group(1)
                    chapter_title = chapter_match.group(2).strip()
                    structure[chapter_number] = {
                        "title": chapter_title,
                        "sections": {}
                    }
                    current_section = structure[chapter_number]["sections"]

            # Извлечение разделов и подразделов
            for line in lines:
                section_match = re.match(r'(\d+\.\d+)\s+(.+)', line)
                subsection_match = re.match(r'(\d+\.\d+\.\d+)\s+(.+)', line)

                if section_match:
                    section_number = section_match.group(1)
                    section_title = section_match.group(2).strip()
                    current_section[section_number] = {
                        "title": section_title,
                        "subsections": {}
                    }
                    current_subsection = current_section[section_number]["subsections"]

                elif subsection_match and current_subsection is not None:
                    subsection_number = subsection_match.group(1)
                    subsection_title = subsection_match.group(2).strip()
                    current_subsection[subsection_number] = {
                        "title": subsection_title
                    }

    return structure

def save_titles_to_json(structure, json_path):
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(structure, json_file, ensure_ascii=False, indent=4)

# Путь к файлу
pdf_path = 'Руководство_Бухгалтерия_для_Узбекистана_ред_3_0.pdf'

titles_structure = extract_titles_from_pdf(pdf_path)

json_path = f'titles_structure{pd.Timestamp("now").microsecond}.json'

save_titles_to_json(titles_structure, json_path)

print(f"Структура сохранена в {json_path}.")
