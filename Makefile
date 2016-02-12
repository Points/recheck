.PHONY: test build upload

test:
	py.test tests

tag:
	git tag releases/$(shell cat VERSION)
	git push --tags

build:
	python setup.py sdist bdist_wheel

upload:
	python setup.py bdist_wheel upload

clean:
	rm -fr .tmp/
	rm -fr dist/
	rm -fr build/
	find -name \*.pyc -delete

lint:
	flake8 --max-line-length=120 recheck
