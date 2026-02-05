"""
Web Admin Panel - загрузка документов через браузер
"""
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
import os
import sys
from pathlib import Path
import logging
from typing import List
import uvicorn

sys.path.insert(0, str(Path(__file__).parent.parent))

# УДАЛЕНО: from backend.config import config
from backend.utils.document_processor import DocumentProcessor
from backend.rag.rag_engine import RAGEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Agents Admin Panel")

# Директории для загрузки
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Инициализация RAG engines
rag_engines = {}

def init_rag_engines():
    """Инициализация RAG систем"""
    try:
        rag_engines['ntd'] = RAGEngine(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            index_name=os.getenv("PINECONE_INDEX", "sveta1"),
            agent_type='ntd',
            embedding_model=os.getenv("EMBEDDING_MODEL", "voyage-multilingual-2"),
            embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "1024")),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip(),
            ai_provider=os.getenv("AI_PROVIDER", "deepseek"),
            voyage_api_key=os.getenv("VOYAGE_API_KEY"),
            embedding_provider=os.getenv("EMBEDDING_PROVIDER", "voyage")
        )
        logger.info("✅ RAG НТД инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка RAG НТД: {e}")

    try:
        rag_engines['docs'] = RAGEngine(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            index_name=os.getenv("PINECONE_INDEX", "sveta1"),
            agent_type='docs',
            embedding_model=os.getenv("EMBEDDING_MODEL", "voyage-multilingual-2"),
            embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "1024")),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip(),
            ai_provider=os.getenv("AI_PROVIDER", "deepseek"),
            voyage_api_key=os.getenv("VOYAGE_API_KEY"),
            embedding_provider=os.getenv("EMBEDDING_PROVIDER", "voyage")
        )
        logger.info("✅ RAG Договоры инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка RAG Договоры: {e}")

@app.on_event("startup")
async def startup_event():
    """При старте приложения"""
    logger.info("🚀 Запуск Admin Panel...")
    init_rag_engines()

@app.get("/", response_class=HTMLResponse)
async def admin_panel():
    """Главная страница админ-панели"""
    html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agents - Админ-панель</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            color: #333;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 16px;
        }
        
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .card h2 {
            color: #333;
            font-size: 24px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .icon {
            font-size: 32px;
        }
        
        .card p {
            color: #666;
            margin-bottom: 20px;
            line-height: 1.6;
        }
        
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }
        
        .upload-area:hover {
            border-color: #764ba2;
            background: #f8f9ff;
        }
        
        .upload-area.dragover {
            background: #e8eaff;
            border-color: #764ba2;
        }
        
        input[type="file"] {
            display: none;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-small {
            padding: 8px 15px;
            font-size: 14px;
            width: auto;
        }
        
        .file-list {
            margin-top: 20px;
        }
        
        .file-item {
            background: #f8f9ff;
            padding: 10px 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .file-name {
            color: #333;
            font-weight: 500;
        }
        
        .file-size {
            color: #666;
            font-size: 14px;
        }
        
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            display: block;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            display: block;
        }
        
        .status.loading {
            background: #d1ecf1;
            color: #0c5460;
            display: block;
        }
        
        .progress {
            margin-top: 15px;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s;
        }
        
        .files-list-container {
            max-height: 300px;
            overflow-y: auto;
            background: #f8f9ff;
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
        }
        
        .file-row {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .file-row:last-child {
            border-bottom: none;
        }
        
        .file-name-display {
            color: #333;
            font-weight: 500;
            flex-grow: 1;
        }
        
        .btn-delete-file {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            transition: transform 0.2s;
            white-space: nowrap;
        }
        
        .btn-delete-file:hover {
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Agents - Админ-панель</h1>
            <p>Загрузка документов в базы знаний</p>
        </div>
        
        <div class="cards">
            <!-- База НТД -->
            <div class="card">
                <h2><span class="icon">📚</span> База НТД</h2>
                <p>ГОСТы, СНиПы, технические условия, регламенты и стандарты</p>
                
                <div class="upload-area" id="upload-ntd" onclick="document.getElementById('file-ntd').click()">
                    <div style="font-size: 48px; margin-bottom: 15px;">📄</div>
                    <div style="color: #333; font-weight: 600; margin-bottom: 10px;">
                        Нажмите или перетащите файлы
                    </div>
                    <div style="color: #666; font-size: 14px;">
                        Поддерживаются PDF и DOCX
                    </div>
                </div>
                
                <input type="file" id="file-ntd" multiple accept=".pdf,.docx" onchange="handleFileSelect(event, 'ntd')">
                
                <div class="file-list" id="files-ntd"></div>
                
                <button class="btn" id="btn-ntd" onclick="uploadFiles('ntd')" disabled>
                    Загрузить в базу НТД
                </button>
                
                <div class="status" id="status-ntd"></div>
                <div class="progress" id="progress-ntd" style="display:none;">
                    <div class="progress-bar" id="progress-bar-ntd"></div>
                </div>
                
                <!-- Список файлов -->
                <div style="margin-top: 30px; padding-top: 30px; border-top: 2px solid #e9ecef;">
                    <h3 style="color: #666; font-size: 18px; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                        📁 Загруженные файлы
                        <button class="btn btn-small" onclick="loadFiles('ntd')">
                            🔄 Обновить
                        </button>
                    </h3>
                    <div id="files-list-ntd" class="files-list-container">
                        <div style="color: #999; text-align: center; padding: 20px;">
                            Нажмите "Обновить" для загрузки списка
                        </div>
                    </div>
                </div>
                
                <!-- Форма удаления -->
                <div style="margin-top: 20px; padding-top: 20px; border-top: 2px solid #e9ecef;">
                    <h3 style="color: #666; font-size: 18px; margin-bottom: 15px;">🗑️ Удалить документ</h3>
                    <input 
                        type="text" 
                        id="delete-filename-ntd" 
                        placeholder="Имя файла (например: ГОСТ_12345.pdf)"
                        style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 8px; font-size: 14px; margin-bottom: 10px;"
                    >
                    <button class="btn" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);" onclick="deleteDocument('ntd')">
                        Удалить из базы НТД
                    </button>
                    <div class="status" id="delete-status-ntd"></div>
                </div>
            </div>
            
            <!-- База Договоры -->
            <div class="card">
                <h2><span class="icon">📝</span> База Договоры</h2>
                <p>Договоры, контракты, методические рекомендации, служебная документация</p>
                
                <div class="upload-area" id="upload-docs" onclick="document.getElementById('file-docs').click()">
                    <div style="font-size: 48px; margin-bottom: 15px;">📄</div>
                    <div style="color: #333; font-weight: 600; margin-bottom: 10px;">
                        Нажмите или перетащите файлы
                    </div>
                    <div style="color: #666; font-size: 14px;">
                        Поддерживаются PDF и DOCX
                    </div>
                </div>
                
                <input type="file" id="file-docs" multiple accept=".pdf,.docx" onchange="handleFileSelect(event, 'docs')">
                
                <div class="file-list" id="files-docs"></div>
                
                <button class="btn" id="btn-docs" onclick="uploadFiles('docs')" disabled>
                    Загрузить в базу Договоры
                </button>
                
                <div class="status" id="status-docs"></div>
                <div class="progress" id="progress-docs" style="display:none;">
                    <div class="progress-bar" id="progress-bar-docs"></div>
                </div>
                
                <!-- Список файлов -->
                <div style="margin-top: 30px; padding-top: 30px; border-top: 2px solid #e9ecef;">
                    <h3 style="color: #666; font-size: 18px; margin-bottom: 15px; display: flex; align-items: center; gap: 8px;">
                        📁 Загруженные файлы
                        <button class="btn btn-small" onclick="loadFiles('docs')">
                            🔄 Обновить
                        </button>
                    </h3>
                    <div id="files-list-docs" class="files-list-container">
                        <div style="color: #999; text-align: center; padding: 20px;">
                            Нажмите "Обновить" для загрузки списка
                        </div>
                    </div>
                </div>
                
                <!-- Форма удаления -->
                <div style="margin-top: 20px; padding-top: 20px; border-top: 2px solid #e9ecef;">
                    <h3 style="color: #666; font-size: 18px; margin-bottom: 15px;">🗑️ Удалить документ</h3>
                    <input 
                        type="text" 
                        id="delete-filename-docs" 
                        placeholder="Имя файла (например: Договор_123.pdf)"
                        style="width: 100%; padding: 12px; border: 2px solid #e9ecef; border-radius: 8px; font-size: 14px; margin-bottom: 10px;"
                    >
                    <button class="btn" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);" onclick="deleteDocument('docs')">
                        Удалить из базы Договоры
                    </button>
                    <div class="status" id="delete-status-docs"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedFiles = {
            'ntd': [],
            'docs': []
        };
        
        // Drag & Drop
        ['ntd', 'docs'].forEach(type => {
            const area = document.getElementById(`upload-${type}`);
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                area.addEventListener(eventName, preventDefaults, false);
            });
            
            ['dragenter', 'dragover'].forEach(eventName => {
                area.addEventListener(eventName, () => area.classList.add('dragover'), false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                area.addEventListener(eventName, () => area.classList.remove('dragover'), false);
            });
            
            area.addEventListener('drop', (e) => handleDrop(e, type), false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        function handleDrop(e, type) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files, type);
        }
        
        function handleFileSelect(e, type) {
            handleFiles(e.target.files, type);
        }
        
        function handleFiles(files, type) {
            selectedFiles[type] = Array.from(files);
            displayFiles(type);
            document.getElementById(`btn-${type}`).disabled = selectedFiles[type].length === 0;
        }
        
        function displayFiles(type) {
            const container = document.getElementById(`files-${type}`);
            container.innerHTML = '';
            
            selectedFiles[type].forEach((file, index) => {
                const div = document.createElement('div');
                div.className = 'file-item';
                div.innerHTML = `
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${formatFileSize(file.size)}</span>
                `;
                container.appendChild(div);
            });
        }
        
        function formatFileSize(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
        
        async function uploadFiles(type) {
            const files = selectedFiles[type];
            if (files.length === 0) return;
            
            const statusDiv = document.getElementById(`status-${type}`);
            const progressDiv = document.getElementById(`progress-${type}`);
            const progressBar = document.getElementById(`progress-bar-${type}`);
            const btn = document.getElementById(`btn-${type}`);
            
            btn.disabled = true;
            statusDiv.className = 'status loading';
            statusDiv.textContent = '⏳ Загрузка и обработка файлов...';
            progressDiv.style.display = 'block';
            
            const formData = new FormData();
            files.forEach(file => formData.append('files', file));
            formData.append('agent_type', type);
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                progressBar.style.width = '100%';
                
                const result = await response.json();
                
                if (response.ok) {
                    statusDiv.className = 'status success';
                    statusDiv.innerHTML = `
                        ✅ Успешно загружено!<br>
                        📄 Документов: ${result.total}<br>
                        📦 Чанков: ${result.chunks}
                    `;
                    
                    // Очистить выбранные файлы
                    selectedFiles[type] = [];
                    document.getElementById(`files-${type}`).innerHTML = '';
                    document.getElementById(`file-${type}`).value = '';
                    
                    // Обновить список файлов
                    loadFiles(type);
                } else {
                    throw new Error(result.detail || 'Ошибка загрузки');
                }
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.textContent = `❌ Ошибка: ${error.message}`;
            } finally {
                btn.disabled = false;
                setTimeout(() => {
                    progressDiv.style.display = 'none';
                    progressBar.style.width = '0%';
                }, 2000);
            }
        }
        
        async function deleteDocument(type) {
            const filenameInput = document.getElementById(`delete-filename-${type}`);
            const filename = filenameInput.value.trim();
            const statusDiv = document.getElementById(`delete-status-${type}`);
            
            if (!filename) {
                statusDiv.className = 'status error';
                statusDiv.textContent = '❌ Введите имя файла';
                return;
            }
            
            if (!confirm(`Вы уверены, что хотите удалить "${filename}" из базы ${type}?`)) {
                return;
            }
            
            statusDiv.className = 'status loading';
            statusDiv.textContent = '⏳ Удаление...';
            
            const formData = new FormData();
            formData.append('filename', filename);
            formData.append('agent_type', type);
            
            try {
                const response = await fetch('/delete', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    statusDiv.className = 'status success';
                    statusDiv.textContent = `✅ Документ "${filename}" удалён!`;
                    filenameInput.value = '';
                    
                    // Обновить список файлов
                    loadFiles(type);
                } else {
                    throw new Error(result.detail || 'Ошибка удаления');
                }
            } catch (error) {
                statusDiv.className = 'status error';
                statusDiv.textContent = `❌ Ошибка: ${error.message}`;
            }
        }
        
        async function loadFiles(type) {
            const listDiv = document.getElementById(`files-list-${type}`);
            listDiv.innerHTML = '<div style="text-align: center; padding: 15px; color: #667eea;">⏳ Загрузка...</div>';
            
            try {
                const response = await fetch(`/list-files?agent_type=${type}`);
                const result = await response.json();
                
                if (response.ok && result.success) {
                    if (result.files.length === 0) {
                        listDiv.innerHTML = '<div style="color: #999; text-align: center; padding: 20px;">📁 Нет загруженных файлов</div>';
                    } else {
                        let html = `<div style="color: #666; font-size: 14px; margin-bottom: 10px; text-align: center;">
                            Всего: <strong>${result.count}</strong> файлов
                        </div>`;
                        html += '<div style="margin-top: 10px;">';
                        
                        result.files.forEach(filename => {
                            html += `
                                <div class="file-row">
                                    <span class="file-name-display">📄 ${filename}</span>
                                    <button 
                                        class="btn-delete-file"
                                        onclick="quickDelete('${type}', '${filename.replace(/'/g, "\\'")}')"
                                    >
                                        🗑️ Удалить
                                    </button>
                                </div>
                            `;
                        });
                        
                        html += '</div>';
                        listDiv.innerHTML = html;
                    }
                } else {
                    throw new Error(result.detail || 'Ошибка загрузки списка');
                }
            } catch (error) {
                listDiv.innerHTML = `<div style="color: #dc3545; text-align: center; padding: 20px;">❌ ${error.message}</div>`;
            }
        }
        
        function quickDelete(type, filename) {
            if (!confirm(`Удалить "${filename}" из базы ${type}?`)) return;
            
            const formData = new FormData();
            formData.append('filename', filename);
            formData.append('agent_type', type);
            
            fetch('/delete', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert(`✅ ${result.message}`);
                    loadFiles(type);
                } else {
                    alert(`❌ ${result.detail}`);
                }
            })
            .catch(error => {
                alert(`❌ Ошибка: ${error.message}`);
            });
        }
        
        // Автозагрузка при открытии страницы
        document.addEventListener('DOMContentLoaded', () => {
            loadFiles('ntd');
            loadFiles('docs');
        });
    </script>
</body>
</html>
    """
    return html

@app.post("/upload")
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    agent_type: str = Form(...)
):
    """Загрузка документов"""
    
    if agent_type not in ['ntd', 'docs']:
        return JSONResponse(
            status_code=400,
            content={"detail": "Неверный тип агента. Используйте 'ntd' или 'docs'"}
        )
    
    if agent_type not in rag_engines:
        return JSONResponse(
            status_code=500,
            content={"detail": f"RAG engine для {agent_type} не инициализирован"}
        )
    
    try:
        processor = DocumentProcessor(
            chunk_size=int(os.getenv("CHUNK_SIZE", "500")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "100"))
        )
        
        total_chunks = 0
        processed_files = 0
        
        for file in files:
            # Проверка формата
            if not (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
                continue
            
            # Сохранить файл
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, 'wb') as f:
                content = await file.read()
                f.write(content)
            
            logger.info(f"📄 Обработка: {file.filename}")
            
            # Обработка документа
            result = processor.process_file(str(file_path))
            
            # Подготовка документов для загрузки
            documents = []
            filename = result['metadata']['filename']
            
            for chunk in result['chunks']:
                doc_id = f"{agent_type}_{filename}_chunk_{chunk['chunk_id']}"
                
                documents.append({
                    'id': doc_id,
                    'text': chunk['text'],
                    'metadata': {
                        'agent_type': agent_type,
                        'filename': filename,
                        'chunk_id': chunk['chunk_id'],
                        'source': str(file_path),
                        **processor.extract_metadata_from_filename(filename)
                    }
                })
            
            # Загрузка в векторную БД
            logger.info(f"📤 Загрузка {len(documents)} чанков в {agent_type}...")
            rag_engines[agent_type].add_documents(documents)
            
            total_chunks += len(documents)
            processed_files += 1
            
            logger.info(f"✅ {file.filename} загружен ({len(documents)} чанков)")
        
        return {
            "success": True,
            "total": processed_files,
            "chunks": total_chunks,
            "agent_type": agent_type
        }
    
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@app.post("/delete")
async def delete_document(
    filename: str = Form(...),
    agent_type: str = Form(...)
):
    """Удаление документа"""
    
    if agent_type not in ['ntd', 'docs']:
        return JSONResponse(
            status_code=400,
            content={"detail": "Неверный тип агента"}
        )
    
    if agent_type not in rag_engines:
        return JSONResponse(
            status_code=500,
            content={"detail": f"RAG engine для {agent_type} не инициализирован"}
        )
    
    try:
        success = rag_engines[agent_type].delete_documents_by_filename(filename)
        
        if success:
            return {
                "success": True,
                "message": f"Документ {filename} удалён из базы {agent_type}"
            }
        else:
            return JSONResponse(
                status_code=500,
                content={"detail": "Ошибка при удалении"}
            )
    
    except Exception as e:
        logger.error(f"❌ Ошибка удаления: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@app.get("/list-files")
async def list_files(agent_type: str):
    """Получить список загруженных файлов"""
    if agent_type not in ['ntd', 'docs']:
        return JSONResponse(
            status_code=400,
            content={"detail": "Неверный тип агента. Используйте 'ntd' или 'docs'"}
        )
    
    if agent_type not in rag_engines:
        return JSONResponse(
            status_code=500,
            content={"detail": f"RAG engine для {agent_type} не инициализирован"}
        )
    
    try:
        # Инициализируем индекс, если он ещё не инициализирован
        if rag_engines[agent_type].index is None:
            rag_engines[agent_type].init_index()
        
        # Ищем все векторы с фильтром по типу агента
        search_filter = {"agent_type": agent_type}
        
        results = rag_engines[agent_type].index.query(
            vector=[0] * 1024,  # Нулевой вектор
            top_k=10000,
            include_metadata=True,
            filter=search_filter
        )
        
        # Извлекаем уникальные имена файлов
        filenames = set()
        for match in results['matches']:
            filename = match['metadata'].get('filename')
            if filename:
                filenames.add(filename)
        
        return {
            "success": True,
            "files": sorted(list(filenames)),
            "count": len(filenames),
            "agent_type": agent_type
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения списка файлов: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

if __name__ == "__main__":
    print("="*60)
    print("🚀 Запуск Admin Panel")
    print("="*60)
    print("\n📱 Откройте в браузере:")
    print("   http://localhost:8000")
    print("\n⏹  Остановка: Ctrl+C")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
