run-tests:
	nosetests tests/phoenix_letter_tests/main --with-coverage --cover-package=phoenix_letter -s
	coverage-badge -o coverage.svg