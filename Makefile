.PHONY: develop test coverage clean lint pre-commit upload-package

default: coverage

develop:
	python setup.py develop
	pip install -r test-requirements.txt
	pip install flake8 restructuredtext_lint
	@echo "#!/bin/bash\nmake pre-commit" > .git/hooks/pre-push
	@chmod a+x .git/hooks/pre-push
	@echo
	@echo "Added pre-push hook! To run manually: make pre-commit"

test:
	tox

coverage:
	py.test --cov=gocd_cli tests

coverage-html: coverage clean-coverage-html
	coverage html

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-coverage-html:
	rm -rf htmlcov

clean: clean-pyc clean-build clean-coverage-html

lint-rst:
	rst-lint README.rst CHANGELOG.rst

lint-pep8:
	flake8 gocd_cli tests

lint: lint-rst lint-pep8

pre-commit: coverage lint

upload-package: test lint clean
	pip install twine wheel
	python setup.py sdist bdist_wheel
	twine upload dist/*

rpm: clean
	python setup.py bdist_rpm --requires 'Python(gocd)' --provides 'Python(gocd-cli)'
