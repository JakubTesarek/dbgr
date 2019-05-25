all:
	@echo 'make clean | build | publish_test | publish | test'

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
	py.test tests/* -v
