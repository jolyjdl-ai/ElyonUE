REM VBScript pour lancer ÉlyonEU Premium sans fenêtre console visible
REM Créé pour Windows Desktop Shortcut
REM Usage: double-click sur ce fichier ou depuis un raccourci

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Obtenir le répertoire du script
strScriptPath = WScript.ScriptFullName
strScriptDir = objFSO.GetParentFolderName(strScriptPath)
strRootDir = objFSO.GetParentFolderName(strScriptDir)

' Changer le répertoire courant
objShell.CurrentDirectory = strRootDir

' Message de démarrage
objShell.Popup "Démarrage d'ÉlyonEU Desktop Premium..." & vbCrLf & "Veuillez patienter...", 2, "ÉlyonEU", 64

' Lancer l'app de manière invisible
Set objExec = objShell.Exec("cmd.exe /c """ & strRootDir & "\scripts\Start-Premium.bat""")

' Attendre que le processus se termine
objExec.Status
