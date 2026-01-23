"""
Скрипт для загрузки документов в векторную БД
"""
import os
import sys
from pathlib import Path
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.pdf_processor import PDFProcessor
from utils.docx_processor import DOCXProcessor
from rag.rag_engine import RAGEngine
from config import Config


class DocumentLoader:
    """Загрузчик документов в векторную БД"""
    
    def __init__(self, agent_type: str):
        """
        Args:
            agent_type: тип агента ('ntd' или 'docs')
        """
        self.agent_type = agent_type
        self.pdf_processor = PDFProcessor()
        self.docx_processor = DOCXProcessor()
        
        # Выбираем индекс в зависимости от типа агента
        if agent_type == 'ntd':
            self.index_name = Config.PINECONE_INDEX_NTD
        elif agent_type == 'docs':
            self.index_name = Config.PINECONE_INDEX_DOCS
        else:
            raise ValueError(f"Неизвестный тип агента: {agent_type}")
        
        # Инициализируем RAG engine
        self.rag = RAGEngine(
            ai_provider=Config.AI_PROVIDER,
            model=Config.AI_MODEL
        )
        
        # Подключаем Pinecone
        self.rag.initialize_pinecone(
            api_key=Config.PINECONE_API_KEY,
            environment=Config.PINECONE_ENVIRONMENT,
            index_name=self.index_name
        )
        
        # Подключаем embeddings
        self.rag.initialize_embeddings(api_key=Config.OPENAI_API_KEY)
        
        print(f"✓ DocumentLoader инициализирован для агента '{agent_type}'")
    
    def load_document(self, file_path: str) -> dict:
        """
        Загрузка одного документа
        
        Args:
            file_path: путь к файлу
            
        Returns:
            Информация о загруженном документе
        """
        file_ext = Path(file_path).suffix.lower()
        file_name = Path(file_path).name
        
        print(f"\n{'='*60}")
        print(f"Загрузка документа: {file_name}")
        print(f"{'='*60}")
        
        # Обрабатываем документ
        if file_ext == '.pdf':
            result = self.pdf_processor.process_document(
                file_path,
                chunk_size=Config.CHUNK_SIZE,
                overlap=Config.CHUNK_OVERLAP
            )
        elif file_ext == '.docx':
            result = self.docx_processor.process_document(
                file_path,
                chunk_size=Config.CHUNK_SIZE,
                overlap=Config.CHUNK_OVERLAP
            )
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {file_ext}")
        
        # Формируем метаданные для Pinecone
        doc_id = Path(file_path).stem
        
        metadata = {
            'agent_type': self.agent_type,
            'file_name': file_name,
            'file_path': file_path
        }
        
        # Добавляем специфичные метаданные
        if file_ext == '.pdf':
            metadata.update({
                'doc_type': result.get('doc_type', 'Неизвестно'),
                'doc_number': result.get('doc_number', ''),
                'pages': result['metadata'].get('pages', 0)
            })
        elif file_ext == '.docx':
            contract_info = result.get('contract_info', {})
            metadata.update({
                'doc_type': contract_info.get('type', 'Неизвестно'),
                'doc_number': contract_info.get('number', ''),
                'doc_date': contract_info.get('date', ''),
                'paragraphs': result['metadata'].get('paragraphs', 0)
            })
        
        print(f"Тип документа: {metadata['doc_type']}")
        print(f"Номер документа: {metadata.get('doc_number', 'не указан')}")
        print(f"Количество чанков: {result['chunks_count']}")
        
        # Загружаем в Pinecone
        print("Загрузка в векторную БД...")
        self.rag.upsert_document(
            doc_id=doc_id,
            chunks=result['chunks'],
            metadata=metadata
        )
        
        return {
            'file_name': file_name,
            'doc_id': doc_id,
            'doc_type': metadata['doc_type'],
            'chunks_count': result['chunks_count']
        }
    
    def load_directory(self, directory_path: str) -> List[dict]:
        """
        Загрузка всех документов из папки
        
        Args:
            directory_path: путь к папке с документами
            
        Returns:
            Список загруженных документов
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise ValueError(f"Папка не существует: {directory_path}")
        
        # Находим все PDF и DOCX файлы
        files = list(directory.glob("*.pdf")) + list(directory.glob("*.docx"))
        
        if not files:
            print(f"⚠️  В папке {directory_path} не найдено PDF или DOCX файлов")
            return []
        
        print(f"\n📁 Найдено файлов: {len(files)}")
        
        loaded_docs = []
        errors = []
        
        for file_path in files:
            try:
                result = self.load_document(str(file_path))
                loaded_docs.append(result)
            except Exception as e:
                errors.append({
                    'file': file_path.name,
                    'error': str(e)
                })
                print(f"❌ Ошибка загрузки {file_path.name}: {e}")
        
        # Итоговый отчет
        print(f"\n{'='*60}")
        print(f"ИТОГИ ЗАГРУЗКИ")
        print(f"{'='*60}")
        print(f"✓ Успешно загружено: {len(loaded_docs)}")
        print(f"✗ Ошибок: {len(errors)}")
        
        if errors:
            print(f"\nОшибки:")
            for err in errors:
                print(f"  - {err['file']}: {err['error']}")
        
        return loaded_docs


def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Загрузка документов в векторную БД')
    parser.add_argument('--agent', choices=['ntd', 'docs'], required=True,
                        help='Тип агента (ntd или docs)')
    parser.add_argument('--file', type=str, help='Путь к файлу для загрузки')
    parser.add_argument('--dir', type=str, help='Путь к папке с документами')
    
    args = parser.parse_args()
    
    if not args.file and not args.dir:
        print("❌ Ошибка: укажите --file или --dir")
        return
    
    # Валидация конфигурации
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return
    
    # Создаем загрузчик
    loader = DocumentLoader(agent_type=args.agent)
    
    # Загружаем документы
    if args.file:
        loader.load_document(args.file)
    elif args.dir:
        loader.load_directory(args.dir)


if __name__ == "__main__":
    main()
