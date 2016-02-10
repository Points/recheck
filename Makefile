.PHONY: test build upload

test:
	py.test tests

build:
	python setup.py bdist_wheel

upload:
	python setup.py upload

testbuild:
	py.test tests && make build
	virtualenv2 .tmp
	.tmp/bin/pip install dist/*

clean:
	rm -fr .tmp/
	rm -fr dist/
	rm -fr build/
	find -name \*.pyc -delete