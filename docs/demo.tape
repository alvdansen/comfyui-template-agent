Output docs/demo.gif

Set Shell "bash"
Set FontSize 14
Set Width 900
Set Height 500
Set Padding 20
Set Theme "Dracula"
Set TypingSpeed 40ms

Hide
Type "export PS1='$ '"
Enter
Type "source .venv/bin/activate && export PS1='$ '"
Enter
Sleep 1s
Type "clear"
Enter
Sleep 500ms
Show

Type "# ComfyUI Template Agent - Quick Demo"
Enter
Sleep 1s

Type "pytest -x -q"
Enter
Sleep 4s

Type "python -m src.registry.highlights --mode trending --limit 5"
Enter
Sleep 5s

Type "python -m src.templates.coverage gap --limit 5"
Enter
Sleep 5s

Sleep 2s
