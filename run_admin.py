"""
Запуск Admin Panel через uvicorn
"""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting Admin Panel on port {port}")
    uvicorn.run("admin_panel:app", host="0.0.0.0", port=port)
