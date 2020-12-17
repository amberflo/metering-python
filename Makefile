test:
	pylint --rcfile=.pylintrc --reports=y --exit-zero metering | tee pylint.out
	flake8 --max-complexity=10 --statistics metering > flake8.out || true
	coverage run --branch --include=metering/\* --omit=*/test* setup.py test

release:
	python setup.py sdist bdist_wheel
	twine upload dist/*

e2e_test:
	.buildscripts/e2e.sh

.PHONY: test release e2e_test
