

.venv: .venv/freezed_after_create.log
	
.venv/freezed_after_create.log: requirements*.txt
	./make_venv.sh build

clean:
	find -name .pytest_cache -type d -not -path "./.venv/*" -exec rm -rf {} \; || true
	find -name __pycache__ -type d -not -path "./.venv/*" -exec rm -rf {} \; || true
	rm -rf build
	rm -rf dist
	rm -rf siripo_rule_engine.egg-info

distclean: uninstall clean


test: export PYTHONPATH=$(PWD)
test: .venv
	.venv/bin/pytest


build: test
	.venv/bin/python setup.py bdist_wheel

install: build
	.venv/bin/python -m pip install dist/*.whl

uninstall:
	.venv/bin/python -m pip uninstall -y siripo-rule-engine