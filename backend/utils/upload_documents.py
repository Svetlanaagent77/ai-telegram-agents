"""
Document Uploader - загрузка документов в векторную базу
"""
import sys
from pathlib import Path
import logging
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import Config
from backend.utils.document_processor import DocumentProcessor
from backend.rag.rag_engine import RAGEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentUploader:
    """Класс для загрузки документов в векторную базу"""
    
    def __init__(self, agent_type: str = "ntd"):
        """
        Args:
            agent_type: тип агента (ntd или docs)
        """
        self.agent_type = agent_type
        
        # Используем единый индекс для обоих агентов
        index_name = Config.PINECONE_INDEX
        
        # Инициализация компонентов
        self.processor = DocumentProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        
        self.rag = RAGEngine(
            api_key=Config.get_api_key(),
            pinecone_api_key=Config.PINECONE_API_KEY,
            index_name=index_name,
            agent_type=agent_type,
            embedding_model=Config.EMBEDDING_MODEL,
            embedding_dimension=Config.EMBEDDING_DIMENSION,
            base_url=Config.get_base_url(),
            ai_provider=Config.AI_PROVIDER,
            voyage_api_key=Config.VOYAGE_API_KEY,
            embedding_provider=Config.EMBEDDING_PROVIDER
        )
    
    def upload_file(self, file_path: str):
        """
        Загрузка одного файла
        
        Args:
            file_path: путь к файлу
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Обработка: {file_path}")
        logger.info('='*60)
        
        try:
            # Обработка документа
            result = self.processor.process_file(file_path)
            
            logger.info(f"✅ Документ обработан:")
            logger.info(f"   - Имя: {result['metadata']['filename']}")
            logger.info(f"   - Размер: {result['metadata']['size']} байт")
            logger.info(f"   - Длина текста: {result['metadata']['text_length']} символов")
            logger.info(f"   - Чанков: {len(result['chunks'])}")
            
            # Подготовка документов для загрузки
            documents = []
            filename = result['metadata']['filename']
            
            for chunk in result['chunks']:
                doc_id = f"{self.agent_type}_{filename}_chunk_{chunk['chunk_id']}"
                
                documents.append({
                    'id': doc_id,
                    'text': chunk['text'],
                    'metadata': {
                        'agent_type': self.agent_type,  # ВАЖНО! Для фильтрации
                        'filename': filename,
                        'chunk_id': chunk['chunk_id'],
                        'source': file_path,
                        **self.processor.extract_metadata_from_filename(filename)
                    }
                })
            
            # Загрузка в векторную БД
            logger.info(f"\n📤 Загрузка в векторную базу...")
            self.rag.add_documents(documents)
            logger.info(f"✅ Загружено {len(documents)} чанков")
        
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке файла: {e}")
            raise
    
    def upload_directory(self, directory_path: str):
        """
        Загрузка всех документов из директории
        
        Args:
            directory_path: путь к директории
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Директория не найдена: {directory}")
        
        # Поддерживаемые форматы
        patterns = ['*.pdf', '*.docx']
        files = []
        
        for pattern in patterns:
            files.extend(directory.glob(pattern))
        
        if not files:
            logger.warning(f"⚠️ В директории {directory} не найдено документов")
            return
        
        logger.info(f"\n📁 Найдено {len(files)} документов")
        
        success_count = 0
        error_count = 0
        
        for file_path in files:
            try:
                self.upload_file(str(file_path))
                success_count += 1
            except Exception as e:
                logger.error(f"❌ Ошибка при загрузке {file_path}: {e}")
                error_count += 1
        
        logger.info(f"\n" + "="*60)
        logger.info(f"📊 Итоги загрузки:")
        logger.info(f"   ✅ Успешно: {success_count}")
        logger.info(f"   ❌ Ошибок: {error_count}")
        logger.info("="*60)


def main():
    """Главная функция для запуска загрузчика"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Загрузка документов в векторную базу')
    parser.add_argument(
        '--agent',
        choices=['ntd', 'docs'],
        required=True,
        help='Тип агента (ntd или docs)'
    )
    parser.add_argument(
        '--file',
        help='Путь к файлу'
    )
    parser.add_argument(
        '--directory',
        help='Путь к директории с файлами'
    )
    
    args = parser.parse_args()
    
    if not args.file and not args.directory:
        parser.error('Укажите --file или --directory')
    
    # Проверка конфигурации
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        return
    
    # Создание загрузчика
    uploader = DocumentUploader(agent_type=args.agent)
    
    # Загрузка
    try:
        if args.file:
            uploader.upload_file(args.file)
        elif args.directory:
            uploader.upload_directory(args.directory)
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
