.DEFAULT_GOAL := check

project_name = pginv

.PHONY: check
check:
	env/bin/mypy $(project_name)

.PHONY: prepenv
prepenv:
	rm -fr env
	virtualenv -p python3 env
	source env/bin/activate && poetry install

.PHONY: inventory
inventory:
	env/bin/ansible-inventory -i demo.pginv.yaml --list -vvvv
