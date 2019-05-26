all:
	@echo 'make clean | build | publish_test | publish | test | changelog'

clean:
	rm -rf *.pyc __pycache__
	rm -rf kwargs.egg-info build dist

build: clean
	python setup.py sdist bdist_wheel

publish_test:
	twine check dist/*
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish:
	twine check dist/*
	twine upload dist/*

lint:
	pylint app.py dbgr

test:
	py.test tests/* \
		--cov dbgr \
		--cov-config .coveragerc \
		--cov-report html \
		--cov-report term \
		--cov-fail-under=100

changelog:
	git log --pretty=format:"%s" --reverse `git describe --tags --abbrev=0`..HEAD
