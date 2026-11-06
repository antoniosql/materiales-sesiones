# Configuración de Claude Code

- `settings.json`: hook `PostToolUse` que ejecuta `scripts/agente_lint.py` cada vez que Claude crea o edita un
  fichero. Si los linters encuentran algo, el error vuelve a Claude, que lo corrige antes de seguir.
  En Windows, Claude Code ejecuta los hooks con Git Bash: `python` debe estar en el PATH con `pip install -e ".[dev]"`.
- `commands/`: envoltorios de `.github/prompts/`, que es la única fuente. Edita los prompts allí, no aquí.
