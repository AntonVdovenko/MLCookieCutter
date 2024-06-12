create_env:
	@echo "Shell activate"
	poetry shell

start_project:
	@echo "Git init"
	git init
	@echo "Installing..."
	poetry install --no-root
	@echo "Pre Hooks commit Installing"
	poetry run pre-commit install

test:
	pytest

python_src:
	export PYTHONPATH=$(PWD)

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache