clean:
	find . -name "*.py[co]" -o -name __pycache__ -exec rm -rf {} +

run-tests: clean
	nosetests tests/ --with-coverage --cover-package=phoenix_letter -s

lint-check: clean
	black --check . && isort --check .
