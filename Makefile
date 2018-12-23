run-tests:
	nosetests tests/phoenix_letter_tests/main --with-coverage --cover-package=phoenix_letter -s

update-pypi:
	rm -rf dist/*
	python setup.py sdist
	twine upload dist/*