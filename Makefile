all:
	@echo 'make clean | build | test'

clean:
	rm -rf *.pyc __pycache__
	rm -rf kwargs.egg-info build dist

build:
	python setup.py sdist bdist_wheel

publish_test:
	twine check dist/*
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish:
	twine check dist/*
	twine upload dist/*

test:
	python -m pytest
