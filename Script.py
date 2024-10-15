import fitz
import re
import json
import logging

# лог срипта
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def extract_structure_from_pdf(pdf_path):
    structure = {}
    current_chapter = None
    current_section = None
    current_subsection = None

    try:
        with fitz.open(pdf_path) as pdf:
            logging.info(f'Открыт PDF: {pdf_path}')


            full_text = ""
            for page_num in range(pdf.page_count):
                page = pdf.load_page(page_num)
                text = page.get_text("text") 
                full_text += text + '\n'

            lines = full_text.split('\n')
            i = 0
            while i < len(lines):
                line = clean_text(lines[i])
                if not line:
                    i += 1
                    continue


                chapter_match = re.match(r'^\s*Глава\s+(\d+)\s*(.*)', line, re.IGNORECASE)
                if chapter_match:
                    chapter_number = chapter_match.group(1)
                    chapter_title = chapter_match.group(2).strip()
                    i += 1
                    while i < len(lines):
                        next_line = clean_text(lines[i])
                        if not next_line or re.match(r'^\s*Глава\s+\d+', next_line, re.IGNORECASE) or re.match(r'^\d+\.\d+', next_line):
                            break
                        chapter_title += ' ' + next_line
                        i += 1
                    current_chapter = chapter_number
                    current_section = None 
                    structure[current_chapter] = {"title": chapter_title.strip(), "sections": {}}
                    logging.info(f'Найдена глава: {chapter_number} - {chapter_title.strip()}')
                    continue


                section_match = re.match(r'^(\d+\.\d+)(?!\.)\s*(.*)', line)
                if section_match and current_chapter:
                    section_number = section_match.group(1)
                    section_title = section_match.group(2).strip()
                    i += 1
                    while i < len(lines):
                        next_line = clean_text(lines[i])
                        if not next_line or re.match(r'^\s*Глава\s+\d+', next_line, re.IGNORECASE) or re.match(
                                r'^\d+\.\d+', next_line):
                            break
                        chapter_title += ' ' + next_line
                        i += 1
                    structure[current_chapter]["sections"][section_number] = {
                        "title": section_title.strip(), "subsections": {}
                    }
                    current_section = section_number
                    logging.info(f'Найден раздел: {section_number} - {section_title.strip()}')
                    continue


                subsection_match = re.match(r'^(\d+\.\d+\.\d+)(?!\.)\s*(.*)', line)
                if subsection_match and current_chapter and current_section:
                    subsection_number = subsection_match.group(1)
                    subsection_title = subsection_match.group(2).strip()
                    i += 1
                    while i < len(lines):
                        next_line = clean_text(lines[i])
                        if not next_line or re.match(r'^(\d+\.\d+\.\d+)(?!\.)', next_line):
                            break
                        subsection_title += ' ' + next_line
                        i += 1
                    structure[current_chapter]["sections"][current_section]["subsections"][subsection_number] = {
                        "title": subsection_title.strip()
                    }
                    logging.info(f'Найден подраздел: {subsection_number} - {subsection_title.strip()}')
                    continue

                i += 1

        return structure

    except Exception as e:
        logging.error(f'Ошибка при обработке PDF: {e}')
        return {}

def save_structure_to_json(structure, json_path):
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=4)
        logging.info(f'Структура сохранена в {json_path}')
    except Exception as e:
        logging.error(f'Ошибка при сохранении JSON: {e}')

# Пути к файлам
pdf_path = "Руководство_Бухгалтерия_для_Узбекистана_ред_3_0.pdf"
json_path = "structure.json"

# Извлечение и сохранение структуры
structure = extract_structure_from_pdf(pdf_path)
save_structure_to_json(structure, json_path)

print("Структура сохранена в structure.json")
