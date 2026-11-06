' Abre o Dashboard de Radioterapia sem janela de console.
' O servidor fecha sozinho quando nenhuma aba do dashboard estiver aberta no navegador.
' Para ver mensagens de erro use "Lancar Dashboard.bat" (com console) ou o log em
' %LOCALAPPDATA%\rt-dash\dashboard.log
Option Explicit
Dim fso, shell, pasta, pythonw
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
pasta = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = pasta & "\.venv\Scripts\pythonw.exe"
If Not fso.FileExists(pythonw) Then
    MsgBox "Ambiente virtual nao encontrado em:" & vbCrLf & pythonw, vbCritical, "Dashboard Radioterapia"
    WScript.Quit 1
End If
shell.CurrentDirectory = pasta
' 0 = janela oculta; False = nao espera o processo terminar.
shell.Run """" & pythonw & """ -m rt_dash.app.desktop", 0, False
