"""
Document Processor - парсинг и обработка документов
"""
import os
from typing import List, Dict
from pathlib import Path
import PyPDF2
import docx
import pdfplumber


class DocumentProcessor:
    """Класс для обработки документов"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_file(self, file_path: str) -> Dict:
        """
        Обработка файла и извлечение текста
        
        Args:
            file_path: путь к файлу
            
        Returns:
            dict с метаданными и текстом
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            text = self._extract_pdf(file_path)
        elif extension == '.docx':
            text = self._extract_docx(file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {extension}")
        
        # Метаданные документа
        metadata = {
            'filename': file_path.name,
            'filepath': str(file_path),
            'extension': extension,
            'size': file_path.stat().st_size,
            'text_length': len(text)
        }
        
        # Разбивка на чанки
        chunks = self._create_chunks(text)
        
        return {
            'metadata': metadata,
            'text': text,
            'chunks': chunks
        }
    
    def _extract_pdf(self, file_path: Path) -> str:
        """Извлечение текста из PDF"""
        text = ""
        
        try:
            # Используем pdfplumber для лучшего извлечения текста
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            # Fallback на PyPDF2
            print(f"pdfplumber failed, using PyPDF2: {e}")
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e2:
                raise ValueError(f"Не удалось извлечь текст из PDF: {e2}")
        
        return text.strip()
    
    def _extract_docx(self, file_path: Path) -> str:
        """Извлечение текста из DOCX"""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise ValueError(f"Не удалось извлечь текст из DOCX: {e}")
    
    def _create_chunks(self, text: str) -> List[Dict]:
        """
        Разбивка текста на чанки с перекрытием
        
        Args:
            text: исходный текст
            
        Returns:
            список словарей с чанками и метаданными
        """
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Определяем конец чанка
            end = start + self.chunk_size
            
            # Если это не последний чанк, пытаемся найти конец предложения
            if end < len(text):
                # Ищем ближайшую точку, восклицательный или вопросительный знак
                for i in range(end, max(start, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'length': len(chunk_text)
                })
                chunk_id += 1
            
            # Сдвигаем начало с учетом перекрытия
            start = end - self.chunk_overlap if end < len(text) else len(text)
        
        return chunks
    
    def extract_metadata_from_filename(self, filename: str) -> Dict:
        """
        Извлечение метаданных из имени файла
        Для документов типа "ГОСТ_12345-2020.pdf" или "Договор_№123_от_01.01.2024.pdf"
        """
        metadata = {}
        
        # Базовые паттерны для НТД
        if 'ГОСТ' in filename.upper():
            metadata['doc_type'] = 'ГОСТ'
        elif 'СНИП' in filename.upper() or 'СНиП' in filename:
            metadata['doc_type'] = 'СНиП'
        elif 'ТУ' in filename.upper():
            metadata['doc_type'] = 'ТУ'
        
        # Базовые паттерны для договоров
        elif 'ДОГОВОР' in filename.upper():
            metadata['doc_type'] = 'Договор'
        elif 'КОНТРАКТ' in filename.upper():
            metadata['doc_type'] = 'Контракт'
        elif 'СОГЛАШЕНИЕ' in filename.upper():
            metadata['doc_type'] = 'Соглашение'
        
        return metadata


# Пример использования
if __name__ == "__main__":
    processor = DocumentProcessor()
    
    # Тестирование на загруженных документах
    test_files = [
        "/mnt/user-data/uploads/36_Письмо_в_Минстрой-1.pdf",
        "/mnt/user-data/uploads/МР_судебная_экспертиза_Козин_Кузнецов_16дек_.pdf"
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\n{'='*60}")
            print(f"Обработка: {file_path}")
            print('='*60)
            
            result = processor.process_file(file_path)
            
            print(f"\nМетаданные:")
            for key, value in result['metadata'].items():
                print(f"  {key}: {value}")
            
            print(f"\nКоличество чанков: {len(result['chunks'])}")
            print(f"\nПервый чанк (первые 200 символов):")
            print(result['chunks'][0]['text'][:200] + "...")
