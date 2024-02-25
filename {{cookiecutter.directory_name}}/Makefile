install: 
	@echo "Installing..."
	poetry install --no-root
	poetry run pre-commit install

activate:
	@echo "Activating virtual environment"
	poetry shell

initialize_git:
	git init 

test:
	pytest

python_src:
	export PYTHONPATH=$(PWD)

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache