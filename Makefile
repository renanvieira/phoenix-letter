run-tests:
	nosetests tests/ --with-coverage --cover-package=phoenix_letter -s

update-pypi:
	rm -rf dist/*
	python setup.py sdist
	twine upload dist/*