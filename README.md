# MyProject (Poetry)

This project runs inside a VS Code Devcontainer (Ubuntu 22.04, Python 3.11).  
It uses **Poetry** for dependency management and installs dependencies from `poetry.lock` for reproducibility.

## Getting Started

1. Open this folder in **VS Code**  
2. Run `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**  
3. Poetry will install all dependencies from `poetry.lock`  
4. Run the example script:
   ```bash
   poetry run python main.py
