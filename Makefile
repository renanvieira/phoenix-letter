clean:
	find . -name "*.py[co]" -o -name __pycache__ -exec rm -rf {} +

run-tests: clean
	PYTHONPATH=src/ coverage run --source=src/phoenix_letter -m unittest discover
	coverage report -m

lint-check: clean
	black --check . && isort --check .
