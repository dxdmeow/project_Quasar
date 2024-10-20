import concurrent.futures
from pathlib import Path
from PyPDF2 import PdfWriter, PdfReader
import fitz 
import json
import logging
import re

logging.basicConfig(level=logging.INFO)

def pdf_extract(pdf: Path, segments: list[tuple[int]], together: bool = False) -> None:
    """
    Извлечение страниц из PDF файла.
    Path - Путь к PDF
    segments: [(start, end), ...] - Диапазоны страниц для извлечения
    
    """
    pdf_writer = PdfWriter()

    with open(pdf, 'rb') as read_stream:
        pdf_reader = PdfReader(read_stream)

        for start_page, end_page in segments:
            pdf_writer_segment = PdfWriter() if not together else None

            for page_num in range(start_page - 1, end_page):
                if together:
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                else:
                    pdf_writer_segment.add_page(pdf_reader.pages[page_num])

            output = pdf.with_name(f"{pdf.stem}_pages_{start_page}-{end_page}.pdf")
            if not together:
                with open(output, 'wb') as out:
                    pdf_writer_segment.write(out)
                logging.info(f"Сохранены извлеченные страницы в {output}")

    if together:
        output = pdf.with_name(f"{pdf.stem}_extracted.pdf")
        with open(output, 'wb') as out:
            pdf_writer.write(out)
        logging.info(f"Сохранены извлеченные страницы в {output}")

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Извлечение текста из PDF файла с помощью fitz"""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text("text") + "\n"
    except Exception as e:
        logging.error(f"Ошибка при извлечении текста из {pdf_path}: {e}")
    return text.strip()

def save_structure_to_json(structure: dict, json_path: Path) -> None:
    """Сохранение извлеченной структуры в JSON файл"""
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=4)
        logging.info(f"Структура сохранена в {json_path}")
    except Exception as e:
        logging.error(f"Ошибка при сохранении JSON: {e}")

def extract_structure_from_text(text: str) -> dict:
    """Извлечение структуры глав, разделов и подпунктов из текста"""
    structure = {}
    current_chapter, current_section, current_subsection = None, None, None

    chapter_pattern = re.compile(r"Глава\s\d+")
    section_pattern = re.compile(r"\d+\.\s*\w+")
    subsection_pattern = re.compile(r"\d+\.\d+\.\s*\w+")

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        logging.info(f"Текущая строка: {line}")  # Логирование текущей строки

        if chapter_pattern.match(line):
            current_chapter = {"title": line, "sections": {}, "text": ""}
            structure[line] = current_chapter
            current_section, current_subsection = None, None

        elif section_pattern.match(line):
            current_section = {"title": line, "subsections": {}, "text": ""}
            if current_chapter:
                current_chapter['sections'][line] = current_section
            current_subsection = None

        elif subsection_pattern.match(line):
            current_subsection = {"title": line, "text": ""}
            if current_section:
                current_section['subsections'][line] = current_subsection

        else:
            if current_subsection:
                current_subsection['text'] += line + "\n"
            elif current_section:
                current_section['text'] += line + "\n"
            elif current_chapter:
                current_chapter['text'] += line + "\n"

    return structure

def pdf_extract_batch(pdfs: dict[str, list[tuple[int]]], workers: int = 20) -> None:
    """Обработка нескольких PDF файлов с параллельным выполнением"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(__pdf_extract, pdfs.items())

def __pdf_extract(pair: tuple[str, list[tuple[int]]]) -> None:
    return pdf_extract(Path(pair[0]), pair[1])

def main():
    # Путь к PDF файлу и диапазоны страниц для извлечения
    pdf_name = Path("Руководство_Бухгалтерия_для_Узбекистана_ред_3_0.pdf")

    # Оглавление (TOC) с 4 по 10 страницу
    toc_segments = [(4, 10)]  
    pdf_extract(pdf_name, toc_segments, together=True)  # Сохраняем TOC в отдельный PDF

    # Основной контент с 11 по 358 страницу
    content_segments = [(11, 358)] 
    pdf_extract(pdf_name, content_segments)

    # Извлекаем текст из полученных файлов
    extracted_toc_file = pdf_name.with_name(f"{pdf_name.stem}_pages_{toc_segments[0][0]}-{toc_segments[0][1]}.pdf")
    extracted_content_files = [pdf_name.with_name(f"{pdf_name.stem}_pages_{start}-{end}.pdf")
                               for start, end in content_segments]
    
    structure = {}

    # Извлекаем структуру из TOC
    toc_text = extract_text_from_pdf(extracted_toc_file)
    structure['Оглавление'] = extract_structure_from_text(toc_text)

    # Извлекаем структуру из основного контента
    for pdf in extracted_content_files:
        text = extract_text_from_pdf(pdf)
        structure[pdf.name] = extract_structure_from_text(text)

    json_path = Path("structure.json")
    save_structure_to_json(structure, json_path)

if __name__ == '__main__':
    main()
