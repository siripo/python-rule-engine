export PYTHONPATH=$(PWD)

.venv: .venv/freezed_after_create.log
	
.venv/freezed_after_create.log: requirements*.txt
	./make_venv.sh build

clean:
	find -name .pytest_cache -type d -not -path "./.venv/*" -exec rm -rf {} \;
	find -name __pycache__ -type d -not -path "./.venv/*" -exec rm -rf {} \;

test: .venv
	.venv/bin/pytest
