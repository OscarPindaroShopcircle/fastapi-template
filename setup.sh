# precommit
VENV_PATH=".venv"
if [ -z "$VIRTUAL_ENV" ]; then
    source "$VENV_PATH/bin/activate"
fi
pre-commit install

uv sync --dev
