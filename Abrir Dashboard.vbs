' Abre o Dashboard de Radioterapia sem janela de console.
' O servidor fecha sozinho quando nenhuma aba do dashboard estiver aberta no navegador.
'
' Na primeira vez numa pasta nova (ex.: repositorio recem-clonado, sem .venv), cria o
' ambiente virtual e instala as dependencias numa janela visivel; depois disso abre sem console.
' Log do servidor: %LOCALAPPDATA%\rt-dash\dashboard.log
Option Explicit
Const TITULO = "Dashboard Radioterapia"
Dim fso, shell, pasta, pythonw, python, base, cmd, codigo

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
pasta = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = pasta
pythonw = pasta & "\.venv\Scripts\pythonw.exe"
python = pasta & "\.venv\Scripts\python.exe"

' Garante que o pacote seja achado mesmo sem "pip install -e ."
shell.Environment("PROCESS")("PYTHONPATH") = pasta & "\src"

If Not fso.FileExists(pythonw) Then
    base = AcharPython()
    If base = "" Then
        MsgBox "Python 3.10 ou mais novo nao foi encontrado." & vbCrLf & _
               "Instale pelo site python.org (marque 'Add python.exe to PATH') e tente de novo.", _
               vbCritical, TITULO
        WScript.Quit 1
    End If
    If MsgBox("Primeira execucao nesta pasta: vou criar o ambiente virtual (.venv)" & vbCrLf & _
              "e instalar as dependencias. Isso leva alguns minutos e precisa de internet." & vbCrLf & vbCrLf & _
              "Continuar?", vbOKCancel + vbInformation, TITULO) <> vbOK Then WScript.Quit 0
    cmd = "cmd /c ""title Preparando o dashboard && " & base & " -m venv .venv && " & _
          """" & python & """ -m pip install --upgrade pip && " & _
          """" & python & """ -m pip install -e . || (echo. & echo Falhou. Veja a mensagem acima. & pause & exit /b 1)"""
    codigo = shell.Run(cmd, 1, True)
    If codigo <> 0 Or Not fso.FileExists(pythonw) Then
        MsgBox "Nao foi possivel preparar o ambiente virtual (codigo " & codigo & ").", vbCritical, TITULO
        WScript.Quit 1
    End If
End If

' 0 = janela oculta; False = nao espera o processo terminar.
shell.Run """" & pythonw & """ -m rt_dash.app.desktop", 0, False

' Procura o Python do sistema: primeiro o lancador "py", depois "python" no PATH.
Function AcharPython()
    AcharPython = ""
    If shell.Run("cmd /c py -3 -c ""import sys; sys.exit(sys.version_info < (3, 10))""", 0, True) = 0 Then
        AcharPython = "py -3"
    ElseIf shell.Run("cmd /c python -c ""import sys; sys.exit(sys.version_info < (3, 10))""", 0, True) = 0 Then
        AcharPython = "python"
    End If
End Function
