Set WshShell = CreateObject("WScript.Shell")

' Запуск START.bat в скрытом режиме
WshShell.Run "START.bat", 0, False

' Показываем сообщение
MsgBox "AI Telegram Agents запущены!" & vbCrLf & vbCrLf & _
       "Telegram боты работают" & vbCrLf & _
       "Веб-админка: http://localhost:8000" & vbCrLf & vbCrLf & _
       "Для остановки закройте окна Python", _
       vbInformation, "AI Agents"
